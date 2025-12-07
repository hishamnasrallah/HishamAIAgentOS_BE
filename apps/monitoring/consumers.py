"""
WebSocket consumers for HishamOS monitoring dashboard.
Handles real-time updates for agent status, workflows, and system metrics.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class DashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time dashboard updates.
    
    Clients connect to receive live updates about:
    - Agent status changes
    - Workflow execution progress
    - System metrics
    - Alerts and notifications
    """
    
    async def connect(self):
        """Accept WebSocket connection and join dashboard room"""
        try:
            logger.info(f"[DashboardConsumer] Connection attempt")
            logger.info(f"[DashboardConsumer] Path: {self.scope.get('path')}")
            logger.info(f"[DashboardConsumer] Query string: {self.scope.get('query_string', b'').decode()}")
            logger.info(f"[DashboardConsumer] User: {self.scope.get('user')}")
            
            # Get user - handle both authenticated and anonymous
            user = self.scope.get('user')
            is_authenticated = user and hasattr(user, 'is_authenticated') and user.is_authenticated
            
            logger.info(f"[DashboardConsumer] Is authenticated: {is_authenticated}")
            
            # Set room group name before accepting
            self.room_group_name = 'dashboard'
            
            # Join room group before accepting (like chat consumer)
            if self.channel_layer is None:
                logger.warning(f"[DashboardConsumer] No channel layer available - continuing without group")
            else:
                try:
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    logger.info(f"[DashboardConsumer] Joined group: {self.room_group_name}")
                except Exception as group_error:
                    logger.error(f"[DashboardConsumer] Error joining group: {str(group_error)}", exc_info=True)
                    # Continue anyway - we'll accept the connection
            
            # Accept connection
            logger.info(f"[DashboardConsumer] Accepting WebSocket connection")
            await self.accept()
            logger.info(f"[DashboardConsumer] Connection accepted successfully")
            
            # Send connection confirmation immediately (like chat consumer)
            try:
                user_email = user.email if (user and hasattr(user, 'email') and is_authenticated) else 'anonymous'
                await self.send(text_data=json.dumps({
                    'type': 'connection',
                    'message': 'Connected to dashboard',
                    'user': user_email
                }))
                logger.info(f"[DashboardConsumer] Connection confirmation sent")
            except Exception as send_error:
                logger.error(f"[DashboardConsumer] Error sending confirmation: {str(send_error)}", exc_info=True)
                
        except Exception as e:
            logger.error(f"[DashboardConsumer] CRITICAL ERROR in connect: {str(e)}", exc_info=True)
            logger.error(f"[DashboardConsumer] Exception type: {type(e).__name__}")
            try:
                await self.close(code=4000)
            except:
                pass
    
    async def disconnect(self, close_code):
        """Leave room group on disconnect"""
        logger.info(f"[DashboardConsumer] Disconnecting with code: {close_code}")
        try:
            if self.channel_layer:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        except Exception as e:
            logger.error(f"[DashboardConsumer] Error leaving group: {str(e)}", exc_info=True)
    
    # Receive message from WebSocket (client → server)
    async def receive(self, text_data):
        """
        Handle messages from WebSocket client.
        Currently just echo for testing.
        """
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        # Echo back for now
        await self.send(text_data=json.dumps({
            'type': 'echo',
            'message': f'Received: {message_type}'
        }))
    
    # Receive message from room group (server → client)
    async def dashboard_update(self, event):
        """
        Handle dashboard update events from channel layer.
        Sends update to WebSocket client.
        
        Event format:
        {
            'type': 'dashboard_update',
            'data': {
                'update_type': 'agent_status_change' | 'workflow_update' | 'system_alert',
                'payload': {...}
            }
        }
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))
