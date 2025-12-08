"""
Chat API views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    SendMessageSerializer
)


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
        
        # Create user message
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=serializer.validated_data['content'],
            attachments=serializer.validated_data.get('attachments', [])
        )
        
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
