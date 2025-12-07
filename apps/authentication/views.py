"""
Views for authentication app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from django.contrib.auth import get_user_model
from .models import APIKey
from .serializers import UserSerializer, UserCreateSerializer, APIKeySerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    User viewset.
    
    Access Control:
    - Users can view their own profile and update it
    - Admins can view and manage all users
    - Only admins can create/delete users
    """
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'email']
    
    def get_queryset(self):
        """
        Filter users to only show the current user.
        Admins can see all users.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return User.objects.none()
        
        # Admins can see all users
        if user.role == 'admin':
            return User.objects.all()
        
        # Regular users can only see themselves
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Override to allow read/update for own profile, but restrict create/delete to admins."""
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'me']:
            return [IsAuthenticated()]
        # Create/delete require admin
        return [IsAuthenticated(), permissions.IsAdminUser()]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user (admin only)."""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can activate users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active'])
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user (admin only)."""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can deactivate users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        # Prevent deactivating yourself
        if user.id == request.user.id:
            return Response(
                {'error': 'You cannot deactivate your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save(update_fields=['is_active'])
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class APIKeyViewSet(viewsets.ModelViewSet):
    """API Key viewset."""
    
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'user']
    search_fields = ['name']
    ordering_fields = ['created_at', 'expires_at']
    
    def get_queryset(self):
        """Filter to current user's API keys."""
        if self.request.user.is_superuser:
            return APIKey.objects.all()
        return APIKey.objects.filter(user=self.request.user)
