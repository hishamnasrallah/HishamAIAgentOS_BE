"""
WebSocket consumer for real-time chat streaming.
"""

import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Conversation, Message, MemberConversation, MemberMessage
from apps.agents.engine.conversational_agent import ConversationalAgent
from apps.agents.engine.base_agent import AgentContext

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming agent responses in real-time.
    
    URL: ws/chat/<conversation_id>/
    
    Message types:
    - Client -> Server: {"type": "user_message", "content": "..."}
    - Server -> Client: {"type": "message_chunk", "content": "..."}
    - Server -> Client: {"type": "message_complete", "message_id": "..."}
    - Server -> Client: {"type": "error", "message": "..."}
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group = f'chat_{self.conversation_id}'
        self.processing_message = False  # Track if currently processing a message
        self.last_message_hash = None  # Track last message to prevent duplicates
        
        logger.info(f"[ChatConsumer] Connection attempt for conversation: {self.conversation_id}")
        logger.info(f"[ChatConsumer] User: {self.scope.get('user')}")
        logger.info(f"[ChatConsumer] Is authenticated: {self.scope['user'].is_authenticated}")
        
        # Verify user is authenticated
        if not self.scope['user'].is_authenticated:
            logger.error(f"[ChatConsumer] Rejecting unauthenticated user")
            await self.close(code=4001)
            return
        
        # Verify user has access to this conversation
        has_access = await self.verify_conversation_access()
        logger.info(f"[ChatConsumer] User has access: {has_access}")
        
        if not has_access:
            logger.error(f"[ChatConsumer] User {self.scope['user']} does not have access to conversation {self.conversation_id}")
            await self.close(code=4003)
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group,
            self.channel_name
        )
        
        logger.info(f"[ChatConsumer] Accepting WebSocket connection")
        await self.accept()
        
        # Send connection confirmation
        logger.info(f"[ChatConsumer] Sending connection confirmation")
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to chat'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info(f"[ChatConsumer] WebSocket disconnecting (conversation: {self.conversation_id}, close_code: {close_code})")
        await self.channel_layer.group_discard(
            self.conversation_group,
            self.channel_name
        )
        logger.info(f"[ChatConsumer] WebSocket disconnected (conversation: {self.conversation_id})")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        logger.info(f"[ChatConsumer] Received WebSocket message (conversation: {self.conversation_id}), length: {len(text_data)}")
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            logger.info(f"[ChatConsumer] Message type: {message_type}, data keys: {list(data.keys())}")
            
            if message_type == 'user_message':
                await self.handle_user_message(data)
            else:
                logger.warning(f"[ChatConsumer] Unknown message type: {message_type}")
                await self.send_error(f'Unknown message type: {message_type}')
                
        except json.JSONDecodeError as json_error:
            logger.error(f"[ChatConsumer] Invalid JSON: {json_error}, text_data: {text_data[:100]}")
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"[ChatConsumer] Error in receive: {str(e)}", exc_info=True)
            await self.send_error(str(e))
    
    async def handle_user_message(self, data):
        """
        Handle user message and generate agent response.
        """
        logger.info(f"[ChatConsumer] Received user message on WebSocket (conversation: {self.conversation_id})")
        
        # Prevent duplicate processing - check if already processing
        if self.processing_message:
            logger.warning(f"[ChatConsumer] Ignoring duplicate message - already processing a message")
            await self.send_error('Please wait for the current message to complete before sending another.')
            return
        
        content = data.get('content', '').strip()
        if not content:
            logger.warning(f"[ChatConsumer] Empty message content received")
            await self.send_error('Message content cannot be empty')
            return
        
        # Create hash of message content to detect exact duplicates (within last 5 seconds)
        import hashlib
        import time
        message_hash = hashlib.md5(f"{content}{time.time()//5}".encode()).hexdigest()  # Hash changes every 5 seconds
        
        # Check for duplicate messages (exact same content sent twice quickly)
        if message_hash == self.last_message_hash:
            logger.warning(f"[ChatConsumer] Ignoring duplicate message (same content)")
            await self.send_error('Duplicate message detected. Please wait before sending again.')
            return
        
        # Mark as processing and store message hash
        self.processing_message = True
        self.last_message_hash = message_hash
        
        logger.info(f"[ChatConsumer] Processing message: '{content[:50]}...' (length: {len(content)})")
        
        # Save user message
        try:
            user_message = await self.save_message('user', content)
            logger.info(f"[ChatConsumer] User message saved with ID: {user_message.id}")
            
            # Extract code context from the new message (non-blocking, best effort)
            # Do this after getting conversation to avoid async issues
            try:
                from apps.chat.services.code_context_extractor import CodeContextExtractor
                # Extract code blocks and files (pure computation, no DB)
                code_blocks = CodeContextExtractor.extract_code_blocks(content)
                file_references = CodeContextExtractor.extract_file_references(content)
                
                logger.debug(
                    f"[ChatConsumer] Code extraction result: "
                    f"{len(code_blocks)} blocks, {len(file_references)} files from message"
                )
                
                # Warn if backticks found but no code blocks extracted (possible formatting issue)
                if '```' in content and not code_blocks:
                    logger.warning(
                        f"[ChatConsumer] Code block markers (```) found in message but extraction failed. "
                        f"Message preview: {content[:100]}... "
                        f"This may indicate malformed markdown formatting."
                    )
                
                # Only update DB if we found something
                if code_blocks or file_references:
                    # Update conversation code context (async-safe)
                    conversation = await self.get_conversation()
                    
                    # Get existing context
                    existing_files = set(conversation.referenced_files or [])
                    existing_blocks = conversation.referenced_code_blocks or []
                    
                    # Add new file references
                    updated_files = list(existing_files | file_references)
                    
                    # Add new code blocks with message ID
                    new_blocks = []
                    for block in code_blocks:
                        block_entry = {
                            'message_id': str(user_message.id),
                            'message_role': user_message.role,
                            'extracted_at': timezone.now().isoformat(),
                            **block
                        }
                        new_blocks.append(block_entry)
                    
                    # Merge with existing blocks (keep recent ones, limit to 50)
                    all_blocks = existing_blocks + new_blocks
                    if len(all_blocks) > 50:
                        all_blocks = sorted(all_blocks, key=lambda x: x.get('extracted_at', ''), reverse=True)[:50]
                    
                    # Update metadata
                    total_blocks = len(all_blocks)
                    total_code_tokens = sum(block.get('tokens', 0) for block in all_blocks)
                    
                    metadata = conversation.code_context_metadata or {}
                    metadata.update({
                        'total_blocks': total_blocks,
                        'total_code_tokens': total_code_tokens,
                        'last_updated': timezone.now().isoformat(),
                        'unique_files_count': len(updated_files)
                    })
                    
                    # Save to conversation (async-safe)
                    conversation.referenced_files = updated_files
                    conversation.referenced_code_blocks = all_blocks
                    conversation.code_context_metadata = metadata
                    await database_sync_to_async(conversation.save)(update_fields=['referenced_files', 'referenced_code_blocks', 'code_context_metadata'])
                    
                    logger.info(
                        f"[ChatConsumer] Extracted code context: "
                        f"{len(new_blocks)} blocks, {len(file_references)} files"
                    )
                else:
                    logger.debug(
                        f"[ChatConsumer] No code context found in message "
                        f"(content length: {len(content) if content else 0})"
                    )
            except Exception as extract_error:
                logger.error(
                    f"[ChatConsumer] Failed to extract code context: {extract_error}",
                    exc_info=True
                )
        except Exception as save_error:
            logger.error(f"[ChatConsumer] Failed to save user message: {save_error}", exc_info=True)
            await self.send_error('Failed to save message. Please try again.')
            return
        
        # Broadcast user message to all clients in the conversation group
        # Also send directly to this client so message appears immediately
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': {
                'id': str(user_message.id),
                'role': 'user',
                'content': content,
                'created_at': user_message.created_at.isoformat(),
            }
        }))
        await self.channel_layer.group_send(
            self.conversation_group,
            {
                'type': 'new_message',
                'message': {
                    'id': str(user_message.id),
                    'role': 'user',
                    'content': content,
                    'created_at': user_message.created_at.isoformat(),
                }
            }
        )
        
        # Get conversation and agent
        conversation = await self.get_conversation()
        agent_model = await database_sync_to_async(lambda: conversation.agent)()
        
        # Get conversation history
        history = await self.get_conversation_history()
        
        # Get AI provider context (thread_id, conversation_id, etc.) from conversation
        ai_provider_context = conversation.ai_provider_context or {}
        
        # Get platform config for conversation strategy
        from apps.integrations.models import AIPlatform
        platform_name = agent_model.preferred_platform
        platform_config_obj = await database_sync_to_async(
            lambda: AIPlatform.objects.filter(platform_name=platform_name, is_enabled=True).first()
        )()
        
        # Serialize platform config to dict for JSON storage (avoiding model instance in JSON field)
        platform_config = None
        if platform_config_obj:
            platform_config = {
                'platform_name': platform_config_obj.platform_name,
                'conversation_strategy': platform_config_obj.conversation_strategy,
                'conversation_id_field': platform_config_obj.conversation_id_field,
                'returns_conversation_id': platform_config_obj.returns_conversation_id,
                'conversation_id_path': platform_config_obj.conversation_id_path,
                'api_stateful': platform_config_obj.api_stateful,
                'sdk_session_support': platform_config_obj.sdk_session_support,
                'supported_identifiers': platform_config_obj.supported_identifiers or [],
                'identifier_extraction_paths': platform_config_obj.identifier_extraction_paths or {},
                'metadata_fields': platform_config_obj.metadata_fields or [],
            }
        
        # Extract code context from conversation
        from apps.chat.services.code_context_extractor import CodeContextExtractor
        code_context = CodeContextExtractor.get_code_context_for_conversation(conversation)
        
        # Prepare conversation context for ConversationManager
        conversation_context = {
            'ai_provider_context': ai_provider_context,
            'max_recent_messages': conversation.max_recent_messages or 20,
            'total_message_count': len(history),
            'conversation_summary': conversation.conversation_summary,  # Include summary if available
            'code_blocks': code_context.get('code_blocks', []),  # Include code blocks
            'referenced_files': code_context.get('referenced_files', []),  # Include file references
        }
        
        # Check if summarization is needed (async, non-blocking)
        from apps.chat.services.conversation_summarizer import ConversationSummarizer
        try:
            should_summarize = await database_sync_to_async(
                ConversationSummarizer.should_summarize
            )(conversation)
            if should_summarize:
                # Trigger async summarization (non-blocking)
                try:
                    from apps.chat.tasks import summarize_conversation_task
                    summarize_conversation_task.delay(str(conversation.id))
                    logger.info(f"[ChatConsumer] Triggered async summarization for conversation {conversation.id}")
                except Exception as e:
                    logger.warning(f"[ChatConsumer] Failed to trigger summarization task: {e}")
        except Exception as check_error:
            logger.warning(f"[ChatConsumer] Failed to check if summarization needed: {check_error}")
        
        # Create agent context with metadata
        context = AgentContext(
            user=self.scope['user'],
            conversation_history=history,
            metadata={
                'conversation_id': str(conversation.id),
                'conversation_context': conversation_context,
                'platform_config': platform_config,  # Pass platform config for strategy determination
                'model_name': agent_model.model_name,  # Pass model name for token limit calculation
                'total_message_count': len(history)
            }
        )
        
        # Generate agent response (streaming)
        logger.info(f"[ChatConsumer] About to start agent response generation")
        try:
            # Use streaming execution if available
            from apps.agents.services import execution_engine
            logger.info(f"[ChatConsumer] Execution engine imported successfully")
            
            # Try streaming first
            try:
                full_response = ""
                # Convert context to dict format for execution engine
                context_dict = {
                    'conversation_history': history,
                    'conversation_id': str(conversation.id),
                    'conversation_context': conversation_context,
                    'platform_config': platform_config,  # Pass platform config for strategy (already serialized)
                    'total_message_count': len(history)
                }
                
                logger.info(f"[ChatConsumer] Starting streaming execution for agent {agent_model.name}")
                logger.info(f"[ChatConsumer] Agent ID: {agent_model.agent_id}, Platform: {agent_model.preferred_platform}")
                logger.info(f"[ChatConsumer] Context: conversation_history={len(history)} messages")
                logger.info(f"[ChatConsumer] Input data: prompt='{content[:50]}...', message='{content[:50]}...'")
                chunk_count = 0
                first_chunk_received = False
                
                try:
                    async for chunk in execution_engine.execute_streaming(
                        agent=agent_model,
                        input_data={'prompt': content, 'message': content},
                        user=self.scope['user'],
                        context=context_dict
                    ):
                        if chunk:
                            if not first_chunk_received:
                                logger.info(f"[ChatConsumer] First chunk received, length: {len(chunk)}, content: {repr(chunk[:50])}")
                                first_chunk_received = True
                            chunk_count += 1
                            full_response += chunk
                            
                            # Log first few chunks to debug short responses
                            if chunk_count <= 3:
                                logger.info(f"[ChatConsumer] Chunk {chunk_count}: length={len(chunk)}, content={repr(chunk[:100])}, total_so_far={len(full_response)}")
                            
                            # Send chunk immediately
                            chunk_data = {
                                'type': 'message_chunk',
                                'content': chunk
                            }
                            try:
                                await self.send(text_data=json.dumps(chunk_data))
                                if chunk_count % 10 == 0:  # Log every 10th chunk to avoid spam
                                    logger.debug(f"[ChatConsumer] Sent chunk {chunk_count}, total chars: {len(full_response)}")
                            except Exception as send_error:
                                logger.error(f"[ChatConsumer] Error sending chunk {chunk_count}: {send_error}", exc_info=True)
                                # Continue processing even if send fails
                            
                            # Broadcast to group
                            try:
                                await self.channel_layer.group_send(
                                    self.conversation_group,
                                    {
                                        'type': 'message_chunk',
                                        'data': chunk_data
                                    }
                                )
                            except Exception as broadcast_error:
                                logger.error(f"[ChatConsumer] Error broadcasting chunk: {broadcast_error}", exc_info=True)
                except Exception as stream_exception:
                    logger.error(f"[ChatConsumer] Error during streaming loop: {stream_exception}", exc_info=True)
                    raise
                
                logger.info(f"[ChatConsumer] Streaming completed: {chunk_count} chunks, {len(full_response)} total chars")
                if not first_chunk_received:
                    logger.warning(f"[ChatConsumer] WARNING: No chunks were received from streaming execution!")
                
                agent_response = full_response.strip()
                
                # Log the actual response content for debugging
                logger.info(f"[ChatConsumer] Raw response (before strip): length={len(full_response)}, content={repr(full_response[:100])}")
                logger.info(f"[ChatConsumer] Stripped response: length={len(agent_response)}, content={repr(agent_response[:100])}")
                
                # If response is empty after stripping, provide a fallback
                if not agent_response:
                    logger.warning(f"[ChatConsumer] Response is empty after stripping. Raw content was: {repr(full_response)}")
                    agent_response = "I'm sorry, I didn't receive a proper response. Please try again."
                # If response is too short (less than 2 chars), log it but still use it
                elif len(agent_response) < 2:
                    logger.warning(f"[ChatConsumer] Response is very short ({len(agent_response)} chars): {repr(agent_response)}. This might be an incomplete response.")
                    
            except PermissionError as perm_error:
                # Handle permission/organization/subscription/usage limit errors
                logger.warning(f"[ChatConsumer] Permission denied: {perm_error}")
                error_msg = str(perm_error)
                self.processing_message = False  # Reset processing state
                # Send error via message_complete only (not send_error to avoid duplicate)
                await self.send(text_data=json.dumps({
                    'type': 'message_complete',
                    'message_id': None,
                    'status': 'error',
                    'error': f'Access denied: {error_msg}'
                }))
                return  # Exit early - don't try to save message
            except Exception as stream_error:
                # Check if it's a rate limit or API error with specific handling
                from apps.integrations.utils.exceptions import OpenAIError
                
                error_msg = str(stream_error)
                error_type = type(stream_error).__name__
                
                # Extract user-friendly error message
                if isinstance(stream_error, OpenAIError):
                    error_msg = str(stream_error)
                    # Rate limit errors are expected with free tier - provide helpful message
                    if 'rate limit' in error_msg.lower() or '429' in error_msg:
                        user_message = (
                            "The AI service is currently rate-limited (this is normal with free tier). "
                            "Please wait a moment and try again. "
                            "You can add your own API key in settings for higher limits."
                        )
                        logger.warning(f"[ChatConsumer] Rate limit error: {error_msg}")
                        # Send error via message_complete only (not send_error to avoid duplicate)
                        await self.send(text_data=json.dumps({
                            'type': 'message_complete',
                            'message_id': None,
                            'status': 'error',
                            'error': user_message,
                            'error_type': 'rate_limit'
                        }))
                        self.processing_message = False  # Reset processing state
                        return
                    else:
                        # Other API errors
                        logger.error(f"[ChatConsumer] API error during streaming: {error_msg}", exc_info=True)
                        # Send error via message_complete only (not send_error to avoid duplicate)
                        await self.send(text_data=json.dumps({
                            'type': 'message_complete',
                            'message_id': None,
                            'status': 'error',
                            'error': error_msg,
                            'error_type': 'api_error'
                        }))
                        self.processing_message = False  # Reset processing state
                        return
                
                # For other errors, try fallback to non-streaming
                logger.error(f"[ChatConsumer] Streaming failed, falling back to non-streaming: {error_type} - {error_msg}", exc_info=True)
                import traceback
                logger.debug(f"[ChatConsumer] Traceback: {''.join(traceback.format_exception(type(stream_error), stream_error, stream_error.__traceback__))}")
                
                try:
                    logger.info(f"[ChatConsumer] Attempting non-streaming execution")
                    agent_response = await self.generate_agent_response(
                        agent_model,
                        content,
                        context
                    )
                    logger.info(f"[ChatConsumer] Non-streaming execution completed, response length: {len(agent_response)}")
                    
                    # Stream response in chunks
                    await self.stream_response(agent_response)
                except PermissionError as fallback_perm_error:
                    logger.warning(f"[ChatConsumer] Fallback also denied permission: {fallback_perm_error}")
                    error_msg = str(fallback_perm_error)
                    # Send error via message_complete only (not send_error to avoid duplicate)
                    await self.send(text_data=json.dumps({
                        'type': 'message_complete',
                        'message_id': None,
                        'status': 'error',
                        'error': error_msg
                    }))
                    self.processing_message = False  # Reset processing state
                    return
                except OpenAIError as fallback_api_error:
                    # Handle API errors in fallback too
                    error_msg = str(fallback_api_error)
                    if 'rate limit' in error_msg.lower() or '429' in error_msg:
                        user_message = (
                            "The AI service is currently rate-limited. "
                            "Please wait a moment and try again."
                        )
                        # Send error via message_complete only (not send_error to avoid duplicate)
                        await self.send(text_data=json.dumps({
                            'type': 'message_complete',
                            'message_id': None,
                            'status': 'error',
                            'error': user_message,
                            'error_type': 'rate_limit'
                        }))
                        self.processing_message = False  # Reset processing state
                        return
                    else:
                        logger.error(f"[ChatConsumer] Fallback API error: {error_msg}", exc_info=True)
                        # Send error via message_complete only (not send_error to avoid duplicate)
                        await self.send(text_data=json.dumps({
                            'type': 'message_complete',
                            'message_id': None,
                            'status': 'error',
                            'error': error_msg,
                            'error_type': 'api_error'
                        }))
                        self.processing_message = False  # Reset processing state
                        return
                except Exception as fallback_error:
                    logger.error(f"[ChatConsumer] Fallback also failed: {fallback_error}", exc_info=True)
                    error_msg = f"Sorry, I encountered an error: {str(fallback_error)}"
                    # Send error via message_complete only (not send_error to avoid duplicate)
                    await self.send(text_data=json.dumps({
                        'type': 'message_complete',
                        'message_id': None,
                        'status': 'error',
                        'error': error_msg
                    }))
                    self.processing_message = False  # Reset processing state
                    return
            
            # Save assistant message
            try:
                assistant_message = await self.save_message('assistant', agent_response)
                
                # Broadcast assistant message to all clients in the conversation group
                await self.channel_layer.group_send(
                    self.conversation_group,
                    {
                        'type': 'new_message',
                        'message': {
                            'id': str(assistant_message.id),
                            'role': 'assistant',
                            'content': agent_response,
                            'created_at': assistant_message.created_at.isoformat(),
                            'tokens_used': assistant_message.tokens_used if hasattr(assistant_message, 'tokens_used') else 0,
                        }
                    }
                )
                
                # Mark as not processing - allow new messages
                self.processing_message = False
                
                # Send completion message - CRITICAL: This tells the frontend it's ready for the next message
                await self.send(text_data=json.dumps({
                    'type': 'message_complete',
                    'message_id': str(assistant_message.id),
                    'status': 'success'
                }))
                logger.info(f"[ChatConsumer] Message complete signal sent for message {assistant_message.id}")
                
            except Exception as save_error:
                logger.error(f"[ChatConsumer] Error saving message: {save_error}", exc_info=True)
                self.processing_message = False  # Reset processing state
                # Still send completion signal even if save failed
                await self.send(text_data=json.dumps({
                    'type': 'message_complete',
                    'message_id': None,
                    'status': 'error',
                    'error': str(save_error)
                }))
            
        except Exception as e:
            logger.error(f"[ChatConsumer] Error generating response: {str(e)}", exc_info=True)
            self.processing_message = False  # Reset processing state
            # Send error via message_complete only (not send_error to avoid duplicate)
            await self.send(text_data=json.dumps({
                'type': 'message_complete',
                'message_id': None,
                'status': 'error',
                'error': f'Agent error: {str(e)}'
            }))
    
    async def stream_response(self, response):
        """Stream response text in chunks."""
        chunk_size = 10  # words per chunk
        words = response.split()
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunk_data = {
                'type': 'message_chunk',
                'content': chunk + ' '
            }
            # Send to this client
            await self.send(text_data=json.dumps(chunk_data))
            # Broadcast to all clients in the group
            await self.channel_layer.group_send(
                self.conversation_group,
                {
                    'type': 'message_chunk',
                    'data': chunk_data
                }
            )
            await asyncio.sleep(0.05)  # Small delay between chunks
    
    async def new_message(self, event):
        """Handle new message event from group."""
        """Broadcast new message to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def message_chunk(self, event):
        """Handle message chunk event from group."""
        """Broadcast message chunk to WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))
    
    async def generate_agent_response(self, agent_model, user_input, context):
        """
        Generate agent response using execution engine.
        
        This is a fallback method when streaming fails.
        """
        try:
            from apps.agents.services import execution_engine
            
            # Execute agent synchronously
            result = await execution_engine.execute_agent(
                agent=agent_model,
                input_data={'prompt': user_input, 'message': user_input},
                user=self.scope['user'],
                context=context.metadata if hasattr(context, 'metadata') else (context if isinstance(context, dict) else {})
            )
            
            if result.success and result.output:
                return result.output
            else:
                return f"Sorry, I encountered an error: {result.error or 'Unknown error'}"
        except Exception as e:
            logger.error(f"Error generating agent response: {str(e)}", exc_info=True)
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
    
    async def send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def verify_conversation_access(self):
        """Verify user has access to conversation."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.user.id == self.scope['user'].id
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_conversation(self):
        """Get conversation object."""
        return Conversation.objects.select_related('agent').get(id=self.conversation_id)
    
    @database_sync_to_async
    def save_message(self, role, content):
        """Save message to database."""
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content
        )
        return message
    
    @database_sync_to_async
    def get_conversation_history(self):
        """Get conversation history for agent context."""
        conversation = Conversation.objects.get(id=self.conversation_id)
        messages = conversation.messages.all().order_by('created_at')
        
        history = []
        for msg in messages:
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        return history


class MemberChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time member-to-member chat.
    
    URL: ws/member-chat/<conversation_id>/
    
    Message types:
    - Server -> Client: {"type": "member_message", "message": {...}}
    - Server -> Client: {"type": "connection", "message": "..."}
    - Client -> Server: {"type": "mark_read", "message_id": "..."}
    """
    
    # Class-level dictionary to track active connections
    # Format: {(conversation_id, user_id): channel_name}
    active_connections = {}
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group = f'member_chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        logger.info(f"[MemberChatConsumer] Connection attempt for conversation: {self.conversation_id}")
        
        # Verify user is authenticated
        if not self.user.is_authenticated:
            logger.error(f"[MemberChatConsumer] Rejecting unauthenticated user")
            await self.close(code=4001)
            return
        
        # Verify user has access to this conversation
        has_access = await self.verify_member_conversation_access()
        logger.info(f"[MemberChatConsumer] User has access: {has_access}")
        
        if not has_access:
            logger.error(f"[MemberChatConsumer] User {self.user} does not have access to conversation {self.conversation_id}")
            await self.close(code=4003)
            return
        
        # Track this connection as active
        connection_key = (self.conversation_id, str(self.user.id))
        MemberChatConsumer.active_connections[connection_key] = self.channel_name
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group,
            self.channel_name
        )
        
        # Mark all unread messages as read when user opens conversation
        await self.mark_all_messages_as_read()
        
        logger.info(f"[MemberChatConsumer] Accepting WebSocket connection")
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to member chat'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info(f"[MemberChatConsumer] WebSocket disconnecting (conversation: {self.conversation_id})")
        
        # Remove from active connections
        connection_key = (self.conversation_id, str(self.user.id))
        MemberChatConsumer.active_connections.pop(connection_key, None)
        
        await self.channel_layer.group_discard(
            self.conversation_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_read':
                message_id = data.get('message_id')
                if message_id:
                    await self.mark_message_as_read(message_id)
            else:
                logger.warning(f"[MemberChatConsumer] Unknown message type: {message_type}")
        except json.JSONDecodeError:
            logger.error(f"[MemberChatConsumer] Invalid JSON received")
        except Exception as e:
            logger.error(f"[MemberChatConsumer] Error handling message: {e}", exc_info=True)
    
    async def member_message(self, event):
        """Handle member message broadcast."""
        message = event['message']
        message_id = message.get('id')
        
        # Mark message as delivered since recipient is connected
        if message_id and message.get('sender') != str(self.user.id):
            await self.mark_message_as_delivered(message_id)
            # Also mark as read since user has conversation open
            await self.mark_message_as_read(message_id)
        
        await self.send(text_data=json.dumps({
            'type': 'member_message',
            'message': message
        }))
    
    @database_sync_to_async
    def verify_member_conversation_access(self):
        """Verify user is a participant in the member conversation."""
        try:
            conversation = MemberConversation.objects.get(id=self.conversation_id)
            user = self.scope['user']
            return user in [conversation.participant1, conversation.participant2]
        except MemberConversation.DoesNotExist:
            logger.error(f"[MemberChatConsumer] Conversation {self.conversation_id} not found")
            return False
        except Exception as e:
            logger.error(f"[MemberChatConsumer] Error verifying access: {e}", exc_info=True)
            return False
    
    @database_sync_to_async
    def mark_message_as_delivered(self, message_id):
        """Mark a message as delivered."""
        try:
            message = MemberMessage.objects.get(id=message_id)
            if not message.is_delivered:
                message.is_delivered = True
                message.delivered_at = timezone.now()
                message.save(update_fields=['is_delivered', 'delivered_at'])
                
                # Notify sender about delivery
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()
                if channel_layer:
                    # Find sender's active connection for this conversation
                    sender_key = (self.conversation_id, str(message.sender.id))
                    sender_channel = MemberChatConsumer.active_connections.get(sender_key)
                    if sender_channel:
                        # Send delivery confirmation to sender
                        asyncio.create_task(channel_layer.send(sender_channel, {
                            'type': 'message_delivered',
                            'message_id': str(message_id)
                        }))
        except MemberMessage.DoesNotExist:
            logger.error(f"[MemberChatConsumer] Message {message_id} not found")
        except Exception as e:
            logger.error(f"[MemberChatConsumer] Error marking message as delivered: {e}", exc_info=True)
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark a message as read."""
        try:
            message = MemberMessage.objects.get(id=message_id)
            # Only mark as read if user is the recipient (not the sender)
            if message.sender != self.user and not message.is_read:
                message.is_read = True
                message.read_at = timezone.now()
                message.save(update_fields=['is_read', 'read_at'])
                
                # Notify sender about read status
                from channels.layers import get_channel_layer
                channel_layer = get_channel_layer()
                if channel_layer:
                    sender_key = (self.conversation_id, str(message.sender.id))
                    sender_channel = MemberChatConsumer.active_connections.get(sender_key)
                    if sender_channel:
                        asyncio.create_task(channel_layer.send(sender_channel, {
                            'type': 'message_read',
                            'message_id': str(message_id)
                        }))
        except MemberMessage.DoesNotExist:
            logger.error(f"[MemberChatConsumer] Message {message_id} not found")
        except Exception as e:
            logger.error(f"[MemberChatConsumer] Error marking message as read: {e}", exc_info=True)
    
    @database_sync_to_async
    def mark_all_messages_as_read(self):
        """Mark all unread messages in conversation as read."""
        try:
            conversation = MemberConversation.objects.get(id=self.conversation_id)
            updated = MemberMessage.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(
                sender=self.user  # Exclude messages from current user
            ).update(
                is_read=True,
                read_at=timezone.now()
            )
            if updated > 0:
                logger.info(f"[MemberChatConsumer] Marked {updated} messages as read for conversation {self.conversation_id}")
        except Exception as e:
            logger.error(f"[MemberChatConsumer] Error marking all messages as read: {e}", exc_info=True)
    
    async def message_delivered(self, event):
        """Handle message delivery confirmation."""
        await self.send(text_data=json.dumps({
            'type': 'message_delivered',
            'message_id': event['message_id']
        }))
    
    async def message_read(self, event):
        """Handle message read confirmation."""
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id']
        }))
    
    @classmethod
    def is_conversation_open(cls, conversation_id, user_id):
        """Check if a conversation is currently open for a user."""
        connection_key = (conversation_id, str(user_id))
        return connection_key in cls.active_connections
