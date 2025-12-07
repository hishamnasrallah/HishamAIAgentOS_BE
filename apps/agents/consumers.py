"""
WebSocket consumer for real-time agent execution updates.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import Agent, AgentExecution

logger = logging.getLogger(__name__)
User = get_user_model()


class AgentExecutionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming agent execution updates in real-time.
    
    URL: ws/agents/execution/<execution_id>/
    
    Message types:
    - Server -> Client: {"type": "execution_update", "status": "...", "data": {...}}
    - Server -> Client: {"type": "execution_complete", "execution_id": "...", "result": {...}}
    - Server -> Client: {"type": "execution_error", "message": "..."}
    - Server -> Client: {"type": "progress", "percentage": 50, "message": "..."}
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.execution_id = self.scope['url_route']['kwargs']['execution_id']
        self.execution_group = f'agent_execution_{self.execution_id}'
        
        logger.info(f"[AgentExecutionConsumer] Connection attempt for execution: {self.execution_id}")
        logger.info(f"[AgentExecutionConsumer] User: {self.scope.get('user')}")
        
        # Verify user is authenticated
        if not self.scope['user'].is_authenticated:
            logger.error(f"[AgentExecutionConsumer] Rejecting unauthenticated user")
            await self.close(code=4001)
            return
        
        # Verify user has access to this execution
        has_access = await self.verify_execution_access()
        logger.info(f"[AgentExecutionConsumer] User has access: {has_access}")
        
        if not has_access:
            logger.error(f"[AgentExecutionConsumer] User {self.scope['user']} does not have access to execution {self.execution_id}")
            await self.close(code=4003)
            return
        
        # Join execution group
        await self.channel_layer.group_add(
            self.execution_group,
            self.channel_name
        )
        
        logger.info(f"[AgentExecutionConsumer] Accepting WebSocket connection")
        await self.accept()
        
        # Send current execution status
        execution = await self.get_execution()
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to agent execution',
            'execution': {
                'id': str(execution.id),
                'status': execution.status,
                'agent': execution.agent.name,
            }
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.execution_group,
            self.channel_name
        )
        logger.info(f"[AgentExecutionConsumer] Disconnected from execution {self.execution_id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_status':
                await self.send_current_status()
            elif message_type == 'cancel_execution':
                await self.cancel_execution()
            else:
                await self.send_error(f'Unknown message type: {message_type}')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"[AgentExecutionConsumer] Error handling message: {str(e)}", exc_info=True)
            await self.send_error(str(e))
    
    async def send_current_status(self):
        """Send current execution status to client."""
        execution = await self.get_execution()
        await self.send(text_data=json.dumps({
            'type': 'execution_update',
            'status': execution.status,
            'data': {
                'id': str(execution.id),
                'status': execution.status,
                'platform_used': execution.platform_used,
                'model_used': execution.model_used,
                'tokens_used': execution.tokens_used,
                'cost': str(execution.cost),
                'execution_time': execution.execution_time,
                'output_data': execution.output_data,
                'error_message': execution.error_message,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            }
        }))
    
    async def cancel_execution(self):
        """Cancel the execution."""
        execution = await self.get_execution()
        if execution.status in ['pending', 'running']:
            execution = await database_sync_to_async(self._cancel_execution)(execution.id)
            # Broadcast cancellation to all clients
            await self.channel_layer.group_send(
                self.execution_group,
                {
                    'type': 'execution_update',
                    'status': 'cancelled',
                    'data': {
                        'id': str(execution.id),
                        'status': 'cancelled',
                    }
                }
            )
    
    def _cancel_execution(self, execution_id):
        """Cancel execution (sync)."""
        execution = AgentExecution.objects.get(id=execution_id)
        execution.status = 'cancelled'
        execution.save()
        return execution
    
    async def execution_update(self, event):
        """Handle execution update event from group."""
        """Broadcast execution update to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_update',
            'status': event.get('status'),
            'data': event.get('data', {})
        }))
    
    async def execution_complete(self, event):
        """Handle execution complete event from group."""
        """Broadcast execution completion to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_complete',
            'execution_id': event.get('execution_id'),
            'result': event.get('result', {})
        }))
    
    async def execution_error(self, event):
        """Handle execution error event from group."""
        """Broadcast execution error to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_error',
            'message': event.get('message', 'Unknown error')
        }))
    
    async def progress_update(self, event):
        """Handle progress update event from group."""
        """Broadcast progress update to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'percentage': event.get('percentage', 0),
            'message': event.get('message', '')
        }))
    
    async def send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def verify_execution_access(self):
        """Verify user has access to execution."""
        try:
            execution = AgentExecution.objects.select_related('user', 'agent').get(id=self.execution_id)
            # User can access if they own it or are staff
            user = self.scope['user']
            return execution.user.id == user.id or user.is_staff
        except AgentExecution.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_execution(self):
        """Get execution object."""
        return AgentExecution.objects.select_related('agent', 'user').get(id=self.execution_id)

