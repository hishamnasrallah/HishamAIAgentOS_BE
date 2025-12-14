"""
Celery tasks for chat/conversation operations.

Provides background processing for conversation summarization and other
long-running chat-related tasks.
"""

import logging
from celery import shared_task
from django.db import models
from django.utils import timezone

from apps.chat.models import Conversation
from apps.chat.services.conversation_summarizer import ConversationSummarizer

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def summarize_conversation_task(self, conversation_id: str):
    """
    Background task to summarize a conversation when it exceeds thresholds.
    
    This task runs asynchronously in the background to avoid blocking
    user interactions. It checks if summarization is still needed, then
    generates and stores a summary of older messages.
    
    Args:
        conversation_id: UUID of the conversation to summarize
    """
    try:
        # Get conversation from database
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Check if summarization is still needed (may have been done by another task)
        if not ConversationSummarizer.should_summarize(conversation):
            logger.info(
                f"[summarize_conversation_task] Conversation {conversation_id} "
                "no longer needs summarization"
            )
            return {
                'success': True,
                'skipped': True,
                'reason': 'Summarization no longer needed'
            }
        
        # Get agent
        agent = conversation.agent
        
        # Run async summarization in sync context
        import asyncio
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async summarization
        result = loop.run_until_complete(
            ConversationSummarizer.summarize_conversation(conversation, agent)
        )
        
        if result.get('success'):
            logger.info(
                f"[summarize_conversation_task] Successfully summarized conversation {conversation_id}: "
                f"{result.get('tokens_used', 0)} tokens used"
            )
        else:
            logger.warning(
                f"[summarize_conversation_task] Summarization failed for conversation {conversation_id}: "
                f"{result.get('error', result.get('reason', 'Unknown error'))}"
            )
        
        return result
        
    except Conversation.DoesNotExist:
        logger.error(
            f"[summarize_conversation_task] Conversation {conversation_id} not found"
        )
        return {
            'success': False,
            'error': 'Conversation not found'
        }
    except Exception as e:
        logger.error(
            f"[summarize_conversation_task] Error summarizing conversation {conversation_id}: {str(e)}",
            exc_info=True
        )
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(bind=True)
def check_conversations_for_summarization(self):
    """
    Periodic task to check conversations that may need summarization.
    
    This can be run on a schedule (e.g., every hour) to find conversations
    that have exceeded thresholds but haven't been summarized yet.
    
    Useful for catching conversations that may have been missed or for
    bulk summarization during low-traffic periods.
    """
    try:
        # Find conversations that exceed message count threshold
        conversations_to_summarize = Conversation.objects.filter(
            messages__isnull=False
        ).annotate(
            message_count=models.Count('messages')
        ).filter(
            message_count__gte=models.F('summarize_at_message_count')
        )
        
        summarized_count = 0
        skipped_count = 0
        error_count = 0
        
        for conversation in conversations_to_summarize[:50]:  # Limit to 50 per run
            try:
                if ConversationSummarizer.should_summarize(conversation):
                    # Trigger summarization task
                    summarize_conversation_task.delay(str(conversation.id))
                    summarized_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                logger.error(
                    f"[check_conversations_for_summarization] Error processing conversation {conversation.id}: {e}"
                )
                error_count += 1
        
        logger.info(
            f"[check_conversations_for_summarization] Processed {summarized_count + skipped_count} conversations: "
            f"{summarized_count} queued for summarization, {skipped_count} skipped, {error_count} errors"
        )
        
        return {
            'success': True,
            'queued': summarized_count,
            'skipped': skipped_count,
            'errors': error_count
        }
        
    except Exception as e:
        logger.error(
            f"[check_conversations_for_summarization] Error: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'error': str(e)
        }

