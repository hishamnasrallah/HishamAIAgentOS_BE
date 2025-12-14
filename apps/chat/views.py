"""
Chat API views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Conversation, Message, MemberConversation, MemberMessage
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    SendMessageSerializer,
    MemberConversationListSerializer,
    MemberConversationDetailSerializer,
    MemberConversationCreateSerializer,
    MemberMessageSerializer,
    SendMemberMessageSerializer
)
from apps.core.services.roles import RoleService
from apps.organizations.services import OrganizationStatusService, SubscriptionService


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    list: Get all user's conversations
    create: Create a new conversation
    retrieve: Get conversation with all messages
    destroy: Archive a conversation
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter conversations by current user."""
        queryset = Conversation.objects.filter(user=self.request.user)
        
        # Filter by agent if provided
        agent_id = self.request.query_params.get('agent_id')
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        
        # Filter archived/active
        is_archived = self.request.query_params.get('is_archived')
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')
        
        return queryset.select_related('agent', 'user').prefetch_related('messages')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return ConversationCreateSerializer
        return ConversationDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Archive conversation instead of deleting."""
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message in this conversation.
        
        POST /api/v1/chat/conversations/{id}/send_message/
        Body: {"content": "Hello", "attachments": []}
        """
        conversation = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's organization and validate
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (but we still track usage if they have an org)
        if organization:
            try:
                # Check organization status
                OrganizationStatusService.require_active_organization(organization, user=user)
                
                # Check subscription active
                OrganizationStatusService.require_subscription_active(organization, user=user)
                
                # Check tier-based usage limit
                SubscriptionService.check_usage_limit(organization, 'chat_messages', user=user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Create user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=serializer.validated_data['content'],
            attachments=serializer.validated_data.get('attachments', [])
        )
        
        # Increment usage count after message creation (only if organization exists)
        if organization:
            try:
                SubscriptionService.increment_usage(organization, 'chat_messages')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to increment usage count: {e}")
        
        # Trigger agent response asynchronously
        # Use Celery if available, otherwise use asyncio
        try:
            from apps.agents.tasks import execute_agent_task_sync
            if execute_agent_task_sync:
                # Trigger async agent response via Celery
                execute_agent_task_sync.delay(
                    agent_id=str(conversation.agent.agent_id),
                    input_data={'prompt': serializer.validated_data['content'], 'message': serializer.validated_data['content']},
                    user_id=request.user.id,
                    context={'conversation_id': str(conversation.id), 'message_id': str(user_message.id)}
                )
        except (ImportError, AttributeError):
            # Fallback: Trigger agent response in background thread
            import threading
            from apps.agents.services import execution_engine
            import asyncio
            
            def trigger_agent_response():
                """Trigger agent response in background."""
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        execution_engine.execute_agent(
                            agent=conversation.agent,
                            input_data={'prompt': serializer.validated_data['content'], 'message': serializer.validated_data['content']},
                            user=request.user,
                            context={'conversation_id': str(conversation.id), 'message_id': str(user_message.id)}
                        )
                    )
                    loop.close()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to trigger agent response: {str(e)}", exc_info=True)
            
            # Start background thread
            thread = threading.Thread(target=trigger_agent_response, daemon=True)
            thread.start()
        
        return Response(
            MessageSerializer(user_message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages in a conversation with pagination.
        
        GET /api/v1/chat/conversations/{id}/messages/
        """
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Simple pagination
        page_size = 50
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_messages = messages[start:end]
        serializer = MessageSerializer(paginated_messages, many=True)
        
        return Response({
            'count': messages.count(),
            'page': page,
            'page_size': page_size,
                'results': serializer.data
            })
    
    @action(detail=True, methods=['patch'])
    def update_title(self, request, pk=None):
        """
        Update conversation title.
        
        PATCH /api/v1/chat/conversations/{id}/update_title/
        Body: {"title": "New Title"}
        """
        conversation = self.get_object()
        title = request.data.get('title', '').strip()
        
        if not title:
            return Response(
                {'error': 'Title cannot be empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(title) > 200:
            return Response(
                {'error': 'Title cannot exceed 200 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.title = title
        conversation.save(update_fields=['title', 'updated_at'])
        
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)


class MemberConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing member-to-member conversations.
    
    list: Get all user's member conversations
    create: Create a new member conversation (or get existing)
    retrieve: Get conversation with all messages
    update: Update conversation (e.g., title)
    destroy: Archive a conversation
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter conversations where current user is a participant."""
        user = self.request.user
        queryset = MemberConversation.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        )
        
        # Filter archived/active
        is_archived = self.request.query_params.get('is_archived')
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')
        
        return queryset.select_related('participant1', 'participant2', 'organization').prefetch_related('messages')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return MemberConversationListSerializer
        elif self.action == 'create':
            return MemberConversationCreateSerializer
        return MemberConversationDetailSerializer
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def destroy(self, request, *args, **kwargs):
        """Archive conversation instead of deleting."""
        conversation = self.get_object()
        conversation.is_archived = True
        conversation.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message in this member conversation.
        
        POST /api/v1/chat/member-conversations/{id}/send_message/
        Body: {"content": "Hello", "attachments": []}
        """
        conversation = self.get_object()
        
        # Verify user is a participant
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SendMemberMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create message
        member_message = MemberMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            role='user',
            content=serializer.validated_data['content'],
            attachments=serializer.validated_data.get('attachments', [])
        )
        
        # Update conversation updated_at and last_message_at
        from django.utils import timezone
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['updated_at'])
        
        # Send notifications to the other participant (only if conversation is not open)
        other_participant = conversation.get_other_participant(request.user)
        if other_participant:
            # Check if conversation is currently open for the recipient
            from apps.chat.consumers import MemberChatConsumer
            conversation_is_open = MemberChatConsumer.is_conversation_open(
                str(conversation.id),
                str(other_participant.id)
            )
            
            # Only send notifications if conversation is not open
            if not conversation_is_open:
                try:
                    from apps.projects.models import Notification
                    Notification.objects.create(
                        recipient=other_participant,
                        notification_type='mention',  # Using mention as closest type, could be extended
                        title=f'New message from {request.user.username or request.user.email}',
                        message=serializer.validated_data['content'][:200],  # Truncate for notification
                        metadata={
                            'type': 'member_message',
                            'conversation_id': str(conversation.id),
                            'message_id': str(member_message.id),
                            'sender_id': str(request.user.id),
                            'sender_email': request.user.email,
                        }
                    )
                    
                    # Send WebSocket notification
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    channel_layer = get_channel_layer()
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f'user_{other_participant.id}_notifications',
                            {
                                'type': 'notification',
                                'notification': {
                                    'type': 'member_message',
                                    'conversation_id': str(conversation.id),
                                    'message_id': str(member_message.id),
                                    'sender': request.user.username or request.user.email,
                                    'content': serializer.validated_data['content'][:100],
                                    'title': f'New message from {request.user.username or request.user.email}',
                                }
                            }
                        )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send notification for member message: {e}", exc_info=True)
        
        # Broadcast to member conversation WebSocket group
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'member_chat_{conversation.id}',
                    {
                        'type': 'member_message',
                        'message': MemberMessageSerializer(member_message).data,
                    }
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to broadcast member message to WebSocket: {e}", exc_info=True)
        
        return Response(
            MemberMessageSerializer(member_message).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def update_title(self, request, pk=None):
        """
        Update conversation title.
        
        PATCH /api/v1/chat/member-conversations/{id}/update_title/
        Body: {"title": "New Title"}
        """
        conversation = self.get_object()
        
        # Verify user is a participant
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        title = request.data.get('title', '').strip()
        
        if len(title) > 200:
            return Response(
                {'error': 'Title cannot exceed 200 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.title = title
        conversation.save(update_fields=['title', 'updated_at'])
        
        serializer = MemberConversationDetailSerializer(conversation, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark all messages in conversation as read for current user.
        
        POST /api/v1/chat/member-conversations/{id}/mark_read/
        """
        conversation = self.get_object()
        
        # Verify user is a participant
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response(
                {'error': 'You are not a participant in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark all unread messages from other participant as read
        from django.utils import timezone
        updated = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'marked_read': updated
        })
