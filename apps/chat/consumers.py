"""
WebSocket consumer for real-time chat streaming.
"""

import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Conversation, Message
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
        await self.channel_layer.group_discard(
            self.conversation_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'user_message':
                await self.handle_user_message(data)
            else:
                await self.send_error(f'Unknown message type: {message_type}')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_user_message(self, data):
        """
        Handle user message and generate agent response.
        """
        content = data.get('content', '').strip()
        if not content:
            await self.send_error('Message content cannot be empty')
            return
        
        # Save user message
        user_message = await self.save_message('user', content)
        
        # Broadcast user message to all clients in the conversation group
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
        
        # Create agent context
        context = AgentContext(
            user=self.scope['user'],
            conversation_history=history
        )
        
        # Generate agent response (streaming)
        try:
            # Use streaming execution if available
            from apps.agents.services import execution_engine
            
            # Try streaming first
            try:
                full_response = ""
                context_dict = {}
                if hasattr(context, 'metadata'):
                    context_dict = context.metadata
                elif isinstance(context, dict):
                    context_dict = context
                
                async for chunk in execution_engine.execute_streaming(
                    agent=agent_model,
                    input_data={'prompt': content, 'message': content},
                    user=self.scope['user'],
                    context=context_dict
                ):
                    if chunk:
                        full_response += chunk
                        # Send chunk immediately
                        chunk_data = {
                            'type': 'message_chunk',
                            'content': chunk
                        }
                        await self.send(text_data=json.dumps(chunk_data))
                        # Broadcast to group
                        await self.channel_layer.group_send(
                            self.conversation_group,
                            {
                                'type': 'message_chunk',
                                'data': chunk_data
                            }
                        )
                
                agent_response = full_response
            except Exception as stream_error:
                # Fallback to non-streaming
                logger.warning(f"Streaming failed, using non-streaming: {stream_error}")
                agent_response = await self.generate_agent_response(
                    agent_model,
                    content,
                    context
                )
                
                # Stream response in chunks
                await self.stream_response(agent_response)
            
            # Save assistant message
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
                        'tokens_used': assistant_message.tokens_used,
                    }
                }
            )
            
            # Send completion message
            await self.send(text_data=json.dumps({
                'type': 'message_complete',
                'message_id': str(assistant_message.id)
            }))
            
        except Exception as e:
            logger.error(f"[ChatConsumer] Error generating response: {str(e)}", exc_info=True)
            await self.send_error(f'Agent error: {str(e)}')
    
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
