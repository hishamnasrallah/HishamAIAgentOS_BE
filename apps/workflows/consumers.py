"""
WebSocket consumer for real-time workflow execution updates.
"""

import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from .models import WorkflowExecution
from apps.core.services.roles import RoleService

logger = logging.getLogger(__name__)
User = get_user_model()


class WorkflowExecutionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming workflow execution updates in real-time.
    
    URL: ws/workflows/execution/<execution_id>/
    
    Message types:
    - Server -> Client: {"type": "execution_update", "status": "...", "data": {...}}
    - Server -> Client: {"type": "step_started", "step_id": "...", "step_name": "..."}
    - Server -> Client: {"type": "step_completed", "step_id": "...", "result": {...}}
    - Server -> Client: {"type": "execution_complete", "execution_id": "...", "result": {...}}
    - Server -> Client: {"type": "execution_error", "message": "..."}
    - Server -> Client: {"type": "progress", "percentage": 50, "current_step": 2, "total_steps": 5}
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        import time
        start_time = time.time()
        
        try:
            self.execution_id = self.scope['url_route']['kwargs']['execution_id']
            logger.info(f"[WorkflowExecutionConsumer] Step 1: Extracted execution_id: {self.execution_id}")
        except KeyError:
            logger.error(f"[WorkflowExecutionConsumer] No execution_id in URL route")
            return
            
        self.execution_group = f'workflow_execution_{self.execution_id}'
        
        logger.info(f"[WorkflowExecutionConsumer] Step 2: Connection attempt for execution: {self.execution_id} (t={time.time()-start_time:.3f}s)")
        
        # Get user from scope
        user = self.scope.get('user')
        logger.info(f"[WorkflowExecutionConsumer] Step 3: User check - user={user}, authenticated={user.is_authenticated if user and hasattr(user, 'is_authenticated') else False} (t={time.time()-start_time:.3f}s)")
        
        # Verify user is authenticated
        if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            logger.error(f"[WorkflowExecutionConsumer] Rejecting unauthenticated user")
            return
        
        # Verify user has access to this execution
        try:
            has_access = await self.verify_execution_access()
            logger.info(f"[WorkflowExecutionConsumer] Step 4: Access verification - has_access={has_access} (t={time.time()-start_time:.3f}s)")
        except Exception as e:
            logger.error(f"[WorkflowExecutionConsumer] Error verifying access: {e}", exc_info=True)
            return
        
        if not has_access:
            logger.error(f"[WorkflowExecutionConsumer] User {self.scope['user']} does not have access to execution {self.execution_id}")
            return
        
        # Join execution group
        try:
            if self.channel_layer is None:
                logger.warning(f"[WorkflowExecutionConsumer] Channel layer is None - continuing without group messaging")
            else:
                await self.channel_layer.group_add(
                    self.execution_group,
                    self.channel_name
                )
                logger.info(f"[WorkflowExecutionConsumer] Step 5: Joined channel group {self.execution_group} (t={time.time()-start_time:.3f}s)")
        except Exception as e:
            logger.error(f"[WorkflowExecutionConsumer] Error joining channel group: {e}", exc_info=True)
            # Continue anyway - we can still send direct messages
        
        logger.info(f"[WorkflowExecutionConsumer] Step 6: Accepting WebSocket connection (t={time.time()-start_time:.3f}s)")
        try:
            await self.accept()
            logger.info(f"[WorkflowExecutionConsumer] Step 7: Connection accepted successfully (t={time.time()-start_time:.3f}s)")
        except Exception as e:
            logger.error(f"[WorkflowExecutionConsumer] Error accepting connection: {e}", exc_info=True)
            return
        
        # Send current execution status
        # Try to get execution, with retry for race condition (execution might not exist yet)
        execution = None
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[WorkflowExecutionConsumer] Step 8 (attempt {attempt+1}/{max_retries}): Fetching execution from database (t={time.time()-start_time:.3f}s)")
                execution = await self.get_execution()
                logger.info(f"[WorkflowExecutionConsumer] Step 9: Execution fetched - id={execution.id}, status={execution.status} (t={time.time()-start_time:.3f}s)")
                break
            except WorkflowExecution.DoesNotExist:
                if attempt < max_retries - 1:
                    logger.warning(f"[WorkflowExecutionConsumer] Execution {self.execution_id} not found, retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"[WorkflowExecutionConsumer] Execution {self.execution_id} does not exist after {max_retries} attempts (t={time.time()-start_time:.3f}s)")
                    try:
                        fallback_message = json.dumps({
                            'type': 'connection',
                            'message': 'Connected to workflow execution',
                            'execution': {
                                'id': self.execution_id,
                                'status': 'not_found',
                            },
                            'warning': 'Execution not found - it may not exist yet or may have been deleted'
                        })
                        await self.send(text_data=fallback_message)
                        logger.info(f"[WorkflowExecutionConsumer] Fallback message sent (t={time.time()-start_time:.3f}s)")
                    except Exception as send_error:
                        logger.error(f"[WorkflowExecutionConsumer] Error sending fallback message: {send_error}", exc_info=True)
                    return
            except Exception as e:
                logger.error(f"[WorkflowExecutionConsumer] Error fetching execution: {e} (t={time.time()-start_time:.3f}s)", exc_info=True)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    # Send error message
                    try:
                        error_message = json.dumps({
                            'type': 'connection',
                            'message': 'Connected to workflow execution',
                            'execution': {
                                'id': self.execution_id,
                                'status': 'error',
                                'error': str(e)
                            }
                        })
                        await self.send(text_data=error_message)
                        logger.info(f"[WorkflowExecutionConsumer] Error message sent (t={time.time()-start_time:.3f}s)")
                    except Exception as send_error:
                        logger.error(f"[WorkflowExecutionConsumer] Error sending error message: {send_error}", exc_info=True)
                    return
        
        # If we have execution, send connection message
        if execution:
            try:
                workflow_name = execution.workflow.name if execution.workflow else 'Unknown'
                connection_message = {
                    'type': 'connection',
                    'message': 'Connected to workflow execution',
                    'execution': {
                        'id': str(execution.id),
                        'status': execution.status,
                        'workflow': workflow_name,
                        'current_step': execution.current_step or '',
                    }
                }
                
                logger.info(f"[WorkflowExecutionConsumer] Step 10: Preparing to send connection message (t={time.time()-start_time:.3f}s)")
                message_json = json.dumps(connection_message)
                logger.info(f"[WorkflowExecutionConsumer] Step 11: JSON serialized, length={len(message_json)} (t={time.time()-start_time:.3f}s)")
                
                await self.send(text_data=message_json)
                logger.info(f"[WorkflowExecutionConsumer] Step 12: Connection message sent successfully (t={time.time()-start_time:.3f}s)")
            except Exception as e:
                logger.error(f"[WorkflowExecutionConsumer] Error sending connection message: {e} (t={time.time()-start_time:.3f}s)", exc_info=True)
        
        logger.info(f"[WorkflowExecutionConsumer] Step 13: Connect method completed (total_time={time.time()-start_time:.3f}s)")
        # Connection should remain open - do not return or close here
        # The connection will stay alive until explicitly closed by client or server error
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        execution_id = getattr(self, 'execution_id', 'unknown')
        logger.info(f"[WorkflowExecutionConsumer] Disconnect called - code={close_code}, execution_id={execution_id}")
        try:
            if self.channel_layer is not None:
                await self.channel_layer.group_discard(
                    self.execution_group,
                    self.channel_name
                )
                logger.info(f"[WorkflowExecutionConsumer] Removed from channel group {self.execution_group}")
            else:
                logger.warning(f"[WorkflowExecutionConsumer] Channel layer is None - skipping group discard")
        except Exception as e:
            logger.error(f"[WorkflowExecutionConsumer] Error removing from channel group: {e}", exc_info=True)
        logger.info(f"[WorkflowExecutionConsumer] Disconnected from execution {execution_id}")
    
    async def receive(self, text_data):
        """Handle messages from client."""
        try:
            logger.info(f"[WorkflowExecutionConsumer] Received message: {text_data[:200]}")
            data = json.loads(text_data)
            message_type = data.get('type')
            logger.info(f"[WorkflowExecutionConsumer] Processing message type: {message_type}")
            
            if message_type == 'ping':
                # Respond to ping with pong
                logger.info(f"[WorkflowExecutionConsumer] Responding to ping with pong")
                pong_message = json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                })
                await self.send(text_data=pong_message)
                logger.info(f"[WorkflowExecutionConsumer] Pong sent successfully")
            elif message_type == 'get_status':
                # Send current execution status
                logger.info(f"[WorkflowExecutionConsumer] Sending execution status")
                execution = await self.get_execution()
                await self.send_execution_status(execution)
                logger.info(f"[WorkflowExecutionConsumer] Execution status sent")
            else:
                logger.warning(f"[WorkflowExecutionConsumer] Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"[WorkflowExecutionConsumer] Invalid JSON received: {text_data}", exc_info=True)
        except Exception as e:
            logger.error(f"[WorkflowExecutionConsumer] Error handling message: {e}", exc_info=True)
    
    # Handler methods for group messages
    async def execution_update(self, event):
        """Send execution status update to client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_update',
            'status': event.get('status'),
            'data': event.get('data', {})
        }))
    
    async def step_started(self, event):
        """Send step started notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'step_started',
            'step_id': event.get('step_id'),
            'step_name': event.get('step_name'),
            'step_order': event.get('step_order'),
            'total_steps': event.get('total_steps'),
            'timestamp': event.get('timestamp')
        }))
    
    async def step_completed(self, event):
        """Send step completed notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'step_completed',
            'step_id': event.get('step_id'),
            'step_name': event.get('step_name'),
            'success': event.get('success', True),
            'result': event.get('result'),
            'timestamp': event.get('timestamp')
        }))
    
    async def execution_complete(self, event):
        """Send execution complete notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_complete',
            'execution_id': event.get('execution_id'),
            'success': event.get('success', True),
            'result': event.get('result'),
            'output': event.get('output'),
            'timestamp': event.get('timestamp')
        }))
    
    async def execution_error(self, event):
        """Send execution error notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_error',
            'message': event.get('message'),
            'error': event.get('error'),
            'step_id': event.get('step_id'),
            'timestamp': event.get('timestamp')
        }))
    
    async def progress_update(self, event):
        """Send progress update to client."""
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'percentage': event.get('percentage', 0),
            'current_step': event.get('current_step', 0),
            'total_steps': event.get('total_steps', 0),
            'message': event.get('message', ''),
            'timestamp': event.get('timestamp')
        }))
    
    # Helper methods
    @database_sync_to_async
    def verify_execution_access(self):
        """Verify user has access to this execution."""
        user = self.scope['user']
        if not user or not user.is_authenticated:
            return False
        
        # Admins can access all executions
        if RoleService.is_admin(user):
            return True
        
        # Users can only access their own executions
        try:
            execution = WorkflowExecution.objects.get(id=self.execution_id)
            return execution.user == user
        except WorkflowExecution.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_execution(self):
        """Get execution instance."""
        return WorkflowExecution.objects.select_related('workflow', 'user').get(id=self.execution_id)
    
    async def send_execution_status(self, execution):
        """Send current execution status to client."""
        await self.send(text_data=json.dumps({
            'type': 'execution_status',
            'execution': {
                'id': str(execution.id),
                'status': execution.status,
                'workflow': {
                    'id': str(execution.workflow.id),
                    'name': execution.workflow.name
                },
                'current_step': execution.current_step,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'error_message': execution.error_message,
            }
        }))

