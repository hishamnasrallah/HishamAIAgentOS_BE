"""
Conversation Summarizer Service.

Handles automatic summarization of conversation history to maintain context
in long conversations while reducing token costs.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from django.utils import timezone
from apps.chat.models import Conversation, Message
from apps.agents.models import Agent

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    Service for summarizing conversation history.
    
    Uses AI to create condensed summaries of older messages, allowing
    the system to maintain context from very long conversations while
    reducing token costs.
    """
    
    @staticmethod
    def should_summarize(conversation: Conversation) -> bool:
        """
        Determine if conversation should be summarized.
        
        Triggers summarization when:
        - Message count exceeds threshold
        - Estimated token count exceeds threshold
        - Summary is outdated (older messages exist after last summary)
        
        Args:
            conversation: Conversation instance
            
        Returns:
            True if summarization should be triggered
        """
        # Get message count
        message_count = conversation.messages.count()
        
        # Get summary metadata
        summary_meta = conversation.summary_metadata or {}
        last_summarized_count = summary_meta.get('messages_summarized_count', 0)
        
        # Check message count threshold
        if message_count >= conversation.summarize_at_message_count:
            # Check if we've summarized recently
            if message_count - last_summarized_count >= conversation.summarize_at_message_count * 0.7:
                # 70% of threshold worth of new messages since last summary
                logger.info(
                    f"[ConversationSummarizer] Should summarize: "
                    f"message_count={message_count}, last_summarized={last_summarized_count}, "
                    f"threshold={conversation.summarize_at_message_count}"
                )
                return True
        
        # Check token count threshold (approximate)
        # Estimate ~100 tokens per message on average
        estimated_tokens = message_count * 100
        if estimated_tokens >= conversation.summarize_at_token_count:
            if not conversation.conversation_summary:
                # Never summarized and exceeds token threshold
                logger.info(
                    f"[ConversationSummarizer] Should summarize: "
                    f"estimated_tokens={estimated_tokens}, threshold={conversation.summarize_at_token_count}"
                )
                return True
        
        return False
    
    @staticmethod
    async def summarize_conversation(
        conversation: Conversation,
        agent: Optional[Agent] = None,
        messages_to_summarize: Optional[List[Message]] = None
    ) -> Dict[str, Any]:
        """
        Summarize conversation history using AI.
        
        Args:
            conversation: Conversation to summarize
            agent: Agent instance (optional, uses conversation.agent if not provided)
            messages_to_summarize: Specific messages to summarize (optional, summarizes all except recent if not provided)
            
        Returns:
            Dict with summary and metadata
        """
        if agent is None:
            agent = conversation.agent
        
        # Determine which messages to summarize
        if messages_to_summarize is None:
            # Get messages before the recent window (to keep recent messages unsummarized)
            all_messages = list(conversation.messages.all().order_by('created_at'))
            
            # Keep recent messages unsummarized
            recent_count = conversation.max_recent_messages
            if len(all_messages) > recent_count:
                messages_to_summarize = all_messages[:-recent_count]
            else:
                # Not enough messages to summarize
                logger.info(f"[ConversationSummarizer] Not enough messages to summarize: {len(all_messages)}")
                return {
                    'success': False,
                    'reason': 'Not enough messages to summarize'
                }
        
        if not messages_to_summarize:
            logger.info("[ConversationSummarizer] No messages to summarize")
            return {
                'success': False,
                'reason': 'No messages to summarize'
            }
        
        logger.info(
            f"[ConversationSummarizer] Summarizing {len(messages_to_summarize)} messages "
            f"for conversation {conversation.id}"
        )
        
        # Format messages for summarization prompt
        messages_text = ConversationSummarizer._format_messages_for_summary(messages_to_summarize)
        
        # Get existing summary to include in new summary
        existing_summary = conversation.conversation_summary or ""
        
        # Create summarization prompt
        if existing_summary:
            prompt = f"""You are a conversation summarization assistant. Given an existing conversation summary and new messages, create an updated comprehensive summary.

EXISTING SUMMARY:
{existing_summary}

NEW MESSAGES TO ADD TO SUMMARY:
{messages_text}

Please create an updated summary that:
1. Incorporates the key information from the existing summary
2. Adds important details from the new messages
3. Maintains context about the conversation topic and important decisions
4. Is concise but comprehensive (aim for 200-400 words)
5. Preserves specific facts, numbers, and important details mentioned

UPDATED SUMMARY:"""
        else:
            prompt = f"""You are a conversation summarization assistant. Please create a comprehensive summary of the following conversation.

CONVERSATION MESSAGES:
{messages_text}

Please create a summary that:
1. Captures the main topic and purpose of the conversation
2. Includes key decisions, agreements, or conclusions
3. Preserves important facts, numbers, and specific details
4. Maintains context about the relationship between messages
5. Is concise but comprehensive (aim for 200-400 words)

CONVERSATION SUMMARY:"""
        
        # Use the agent's preferred platform to generate summary
        try:
            from apps.integrations.services import get_registry
            
            # Get adapter for summarization
            registry = await get_registry()
            adapter = registry.get_adapter(agent.preferred_platform)
            
            if not adapter:
                logger.error(f"[ConversationSummarizer] No adapter available for platform {agent.preferred_platform}")
                return {
                    'success': False,
                    'reason': f'No adapter available for platform {agent.preferred_platform}'
                }
            
            # Create summarization request using messages format (more consistent with adapters)
            from apps.integrations.adapters.base import CompletionRequest
            
            # Build messages array with system prompt and summarization prompt
            summary_messages = [
                {
                    'role': 'system',
                    'content': 'You are a helpful assistant that creates concise, accurate summaries of conversations.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
            
            summary_request = CompletionRequest(
                prompt="",  # Empty, we use messages instead
                system_prompt=None,  # Already in messages
                messages=summary_messages,
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=500,  # Limit summary length
            )
            
            # Generate summary using the agent's model
            response = await adapter.generate_completion(summary_request, agent.model_name)
            new_summary = response.content.strip()
            
            # Update conversation
            conversation.conversation_summary = new_summary
            conversation.summary_metadata = {
                'last_summarized_at': timezone.now().isoformat(),
                'messages_summarized_count': len(messages_to_summarize),
                'summary_version': (conversation.summary_metadata.get('summary_version', 0) + 1) if conversation.summary_metadata else 1,
                'summary_tokens': response.tokens_used,
                'model_used': response.model,
            }
            conversation.save(update_fields=['conversation_summary', 'summary_metadata'])
            
            logger.info(
                f"[ConversationSummarizer] Successfully summarized conversation {conversation.id}: "
                f"{len(new_summary)} chars, {response.tokens_used} tokens"
            )
            
            return {
                'success': True,
                'summary': new_summary,
                'metadata': conversation.summary_metadata,
                'tokens_used': response.tokens_used,
            }
            
        except Exception as e:
            logger.error(
                f"[ConversationSummarizer] Error summarizing conversation {conversation.id}: {str(e)}",
                exc_info=True
            )
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _format_messages_for_summary(messages: List[Message]) -> str:
        """Format messages for summarization prompt, including code context."""
        formatted = []
        for msg in messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            content = msg.content
            
            # Include code blocks if present (for better summary)
            # Code blocks are already in the content, so we just format them
            formatted.append(f"{role_label}: {content}")
        
        return "\n\n".join(formatted)
    
    @staticmethod
    def get_messages_with_summary(
        conversation: Conversation,
        recent_messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get message list that includes summary + recent messages.
        
        Args:
            conversation: Conversation instance
            recent_messages: List of recent message dicts (role, content)
            system_prompt: Optional system prompt (will be prepended)
            
        Returns:
            List of message dicts ready for API
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add conversation summary as system message if available
        if conversation.conversation_summary:
            summary_text = (
                "Previous conversation summary:\n"
                f"{conversation.conversation_summary}\n\n"
                "Below are the recent messages continuing from this summary."
            )
            messages.append({
                'role': 'system',
                'content': summary_text
            })
        
        # Add recent messages
        messages.extend(recent_messages)
        
        return messages


