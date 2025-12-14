"""
WebSocket consumer for collaborative editing in projects.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import Project, UserStory, Task, Bug, Issue
from apps.core.services.roles import RoleService

logger = logging.getLogger(__name__)
User = get_user_model()


class CollaborativeEditingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing.
    
    URL: ws/projects/<project_id>/collaborate/
    
    Message types:
    - Client -> Server: {"type": "join", "content_type": "story", "object_id": "..."}
    - Client -> Server: {"type": "edit", "field": "title", "value": "...", "version": 1}
    - Client -> Server: {"type": "cursor", "position": {...}}
    - Server -> Client: {"type": "user_joined", "user": {...}}
    - Server -> Client: {"type": "edit_applied", "field": "...", "value": "...", "user": {...}}
    - Server -> Client: {"type": "cursor_update", "user": {...}, "position": {...}}
    - Server -> Client: {"type": "user_left", "user": {...}}
    - Server -> Client: {"type": "error", "message": "..."}
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope['user']
        
        logger.info(f"[CollaborativeEditing] Connection attempt for project: {self.project_id}, user: {self.user}")
        
        # Verify user is authenticated
        if not self.user.is_authenticated:
            logger.error("[CollaborativeEditing] Rejecting unauthenticated user")
            await self.close(code=4001)
            return
        
        # Verify user has access to this project
        has_access = await self.verify_project_access()
        if not has_access:
            logger.error(f"[CollaborativeEditing] User {self.user} does not have access to project {self.project_id}")
            await self.close(code=4003)
            return
        
        # Join project group
        self.project_group = f'project_{self.project_id}'
        await self.channel_layer.group_add(
            self.project_group,
            self.channel_name
        )
        
        # Track active editors
        self.editing_objects = {}  # {content_type_object_id: set of user_ids}
        
        logger.info("[CollaborativeEditing] Accepting WebSocket connection")
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to collaborative editing',
            'project_id': self.project_id
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Notify other users that this user left
        for content_type_id, object_id in self.editing_objects.keys():
            await self.channel_layer.group_send(
                f'object_{content_type_id}_{object_id}',
                {
                    'type': 'user_left',
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username,
                        'email': self.user.email
                    }
                }
            )
            await self.channel_layer.group_discard(
                f'object_{content_type_id}_{object_id}',
                self.channel_name
            )
        
        await self.channel_layer.group_discard(
            self.project_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'join':
                await self.handle_join(data)
            elif message_type == 'edit':
                await self.handle_edit(data)
            elif message_type == 'cursor':
                await self.handle_cursor(data)
            elif message_type == 'leave':
                await self.handle_leave(data)
            else:
                await self.send_error(f'Unknown message type: {message_type}')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"[CollaborativeEditing] Error handling message: {str(e)}", exc_info=True)
            await self.send_error(str(e))
    
    async def handle_join(self, data):
        """Handle user joining an object for editing."""
        content_type = data.get('content_type')  # 'story', 'task', 'bug', 'issue'
        object_id = data.get('object_id')
        
        if not content_type or not object_id:
            await self.send_error('content_type and object_id are required')
            return
        
        # Verify object exists and user has access
        has_access = await self.verify_object_access(content_type, object_id)
        if not has_access:
            await self.send_error('You do not have access to this object')
            return
        
        # Join object-specific group
        object_group = f'object_{content_type}_{object_id}'
        await self.channel_layer.group_add(
            object_group,
            self.channel_name
        )
        
        # Track that this user is editing this object
        key = (content_type, object_id)
        if key not in self.editing_objects:
            self.editing_objects[key] = set()
        self.editing_objects[key].add(self.user.id)
        
        # Notify other users
        await self.channel_layer.group_send(
            object_group,
            {
                'type': 'user_joined',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'email': self.user.email,
                    'full_name': self.user.get_full_name() or self.user.username
                }
            }
        )
        
        # Get current editors and send to user
        current_editors = await self.get_current_editors(content_type, object_id)
        await self.send(text_data=json.dumps({
            'type': 'joined',
            'content_type': content_type,
            'object_id': object_id,
            'current_editors': current_editors
        }))
    
    async def handle_edit(self, data):
        """Handle edit operation."""
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        field = data.get('field')
        value = data.get('value')
        version = data.get('version', 0)
        
        if not all([content_type, object_id, field]):
            await self.send_error('content_type, object_id, and field are required')
            return
        
        # Verify user is editing this object
        key = (content_type, object_id)
        if key not in self.editing_objects or self.user.id not in self.editing_objects[key]:
            await self.send_error('You must join the object before editing')
            return
        
        # Apply edit to database
        success = await self.apply_edit(content_type, object_id, field, value, version)
        
        if success:
            # Broadcast edit to all users editing this object
            object_group = f'object_{content_type}_{object_id}'
            await self.channel_layer.group_send(
                object_group,
                {
                    'type': 'edit_applied',
                    'field': field,
                    'value': value,
                    'version': version + 1,
                    'user': {
                        'id': str(self.user.id),
                        'username': self.user.username,
                        'email': self.user.email,
                        'full_name': self.user.get_full_name() or self.user.username
                    }
                }
            )
        else:
            await self.send_error('Failed to apply edit. Object may have been modified by another user.')
    
    async def handle_cursor(self, data):
        """Handle cursor position update."""
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        position = data.get('position', {})
        
        if not content_type or not object_id:
            return
        
        # Broadcast cursor position to other users
        object_group = f'object_{content_type}_{object_id}'
        await self.channel_layer.group_send(
            object_group,
            {
                'type': 'cursor_update',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'email': self.user.email
                },
                'position': position
            }
        )
    
    async def handle_leave(self, data):
        """Handle user leaving an object."""
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        
        if content_type and object_id:
            await self.leave_object(content_type, object_id)
    
    async def leave_object(self, content_type, object_id):
        """Leave an object editing session."""
        key = (content_type, object_id)
        if key in self.editing_objects:
            self.editing_objects[key].discard(self.user.id)
            if not self.editing_objects[key]:
                del self.editing_objects[key]
        
        object_group = f'object_{content_type}_{object_id}'
        await self.channel_layer.group_discard(
            object_group,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            object_group,
            {
                'type': 'user_left',
                'user': {
                    'id': str(self.user.id),
                    'username': self.user.username,
                    'email': self.user.email
                }
            }
        )
    
    # Event handlers for group messages
    async def user_joined(self, event):
        """Handle user joined event."""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user']
        }))
    
    async def user_left(self, event):
        """Handle user left event."""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user']
        }))
    
    async def edit_applied(self, event):
        """Handle edit applied event."""
        # Don't send back to the user who made the edit
        if event['user']['id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'edit_applied',
                'field': event['field'],
                'value': event['value'],
                'version': event['version'],
                'user': event['user']
            }))
    
    async def cursor_update(self, event):
        """Handle cursor update event."""
        # Don't send back to the user who moved the cursor
        if event['user']['id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'cursor_update',
                'user': event['user'],
                'position': event['position']
            }))
    
    async def send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    @database_sync_to_async
    def verify_project_access(self):
        """Verify user has access to project."""
        try:
            project = Project.objects.get(id=self.project_id)
            # Check if user is owner, member, or admin
            return (
                project.owner_id == self.user.id or
                project.members.filter(id=self.user.id).exists() or
                RoleService.is_admin(self.user)
            )
        except Project.DoesNotExist:
            return False
    
    @database_sync_to_async
    def verify_object_access(self, content_type, object_id):
        """Verify user has access to object."""
        try:
            if content_type == 'story':
                obj = UserStory.objects.select_related('project').get(id=object_id)
            elif content_type == 'task':
                obj = Task.objects.select_related('project').get(id=object_id)
            elif content_type == 'bug':
                obj = Bug.objects.select_related('project').get(id=object_id)
            elif content_type == 'issue':
                obj = Issue.objects.select_related('project').get(id=object_id)
            else:
                return False
            
            # Check if user has access to the project
            project = obj.project
            return (
                project.owner_id == self.user.id or
                project.members.filter(id=self.user.id).exists() or
                RoleService.is_admin(self.user)
            )
        except (UserStory.DoesNotExist, Task.DoesNotExist, Bug.DoesNotExist, Issue.DoesNotExist):
            return False
    
    @database_sync_to_async
    def apply_edit(self, content_type, object_id, field, value, version):
        """Apply edit to database."""
        try:
            if content_type == 'story':
                obj = UserStory.objects.get(id=object_id)
            elif content_type == 'task':
                obj = Task.objects.get(id=object_id)
            elif content_type == 'bug':
                obj = Bug.objects.get(id=object_id)
            elif content_type == 'issue':
                obj = Issue.objects.get(id=object_id)
            else:
                return False
            
            # Check version to prevent conflicts (simple optimistic locking)
            # In a production system, you'd want more sophisticated conflict resolution
            if hasattr(obj, 'version') and obj.version != version:
                return False
            
            # Apply edit
            if hasattr(obj, field):
                setattr(obj, field, value)
                obj.save(update_fields=[field])
                return True
            
            return False
        except Exception as e:
            logger.error(f"[CollaborativeEditing] Error applying edit: {str(e)}", exc_info=True)
            return False
    
    @database_sync_to_async
    def get_current_editors(self, content_type, object_id):
        """Get list of users currently editing an object."""
        # This is a simplified version - in production, you'd track this in Redis or database
        object_group = f'object_{content_type}_{object_id}'
        # For now, return empty list - could be enhanced with Redis tracking
        return []


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    
    URL: ws/notifications/
    
    Clients connect to receive real-time notifications for the authenticated user.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope['user']
        
        logger.info(f"[NotificationConsumer] Connection attempt for user: {self.user}")
        
        # Verify user is authenticated
        if not self.user.is_authenticated:
            logger.error("[NotificationConsumer] Rejecting unauthenticated user")
            await self.close(code=4001)
            return
        
        # Join user's personal notification group
        self.user_group = f'user_{self.user.id}_notifications'
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        logger.info(f"[NotificationConsumer] Accepting WebSocket connection for user {self.user.id}")
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to notification stream',
            'user_id': str(self.user.id)
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            else:
                await self.send_error(f'Unknown message type: {message_type}')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"[NotificationConsumer] Error handling message: {str(e)}", exc_info=True)
            await self.send_error(str(e))
    
    # Event handler for group messages
    async def notification(self, event):
        """Handle notification event from channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    async def send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
