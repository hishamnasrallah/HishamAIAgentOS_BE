"""
User presence views for tracking online users.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from apps.core.services.roles import RoleService

User = get_user_model()

# In-memory store for online users (in production, use Redis)
# Format: {user_id: {'last_seen': datetime, 'current_page': str}}
_online_users = {}


@extend_schema(
    description="Get list of online users",
    responses={200: {
        'type': 'object',
        'properties': {
            'users': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string', 'format': 'uuid'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'status': {'type': 'string', 'enum': ['online', 'away', 'busy']},
                        'current_page': {'type': 'string'},
                    }
                }
            },
            'count': {'type': 'integer'}
        }
    }}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def online_users(request):
    """
    Get list of currently online users.
    Users are considered online if they've been active in the last 5 minutes.
    Only admins can see current_page information.
    """
    now = timezone.now()
    active_threshold = now - timedelta(minutes=5)
    user = request.user
    is_admin = RoleService.is_admin(user)
    
    # Clean up stale entries
    global _online_users
    _online_users = {
        user_id: data 
        for user_id, data in _online_users.items() 
        if data['last_seen'] > active_threshold
    }
    
    # Get user IDs that are online
    online_user_ids = list(_online_users.keys())
    
    if not online_user_ids:
        return Response({
            'users': [],
            'count': 0
        })
    
    # Filter by organization for non-super-admins
    if not RoleService.is_super_admin(user):
        user_orgs = RoleService.get_user_organizations(user)
        if user_orgs:
            org_ids = [org.id for org in user_orgs]
            # Filter users by organization
            users = User.objects.filter(
                id__in=online_user_ids,
                organization_id__in=org_ids
            ).only('id', 'email', 'first_name', 'last_name', 'role', 'organization')
        else:
            # User has no organization, only show themselves
            users = User.objects.filter(id=user.id).only('id', 'email', 'first_name', 'last_name', 'role', 'organization')
    else:
        # Super admins see all online users
        users = User.objects.filter(id__in=online_user_ids).only(
            'id', 'email', 'first_name', 'last_name', 'role', 'organization'
        )
    
    online_users_list = []
    for user_obj in users:
        presence_data = _online_users.get(str(user_obj.id), {})
        # Use get_full_name method or construct from first_name/last_name
        full_name = user_obj.get_full_name() if hasattr(user_obj, 'get_full_name') else (
            f"{user_obj.first_name} {user_obj.last_name}".strip() if user_obj.first_name or user_obj.last_name else None
        )
        user_data = {
            'id': str(user_obj.id),
            'name': full_name or user_obj.email.split('@')[0],
            'email': user_obj.email,
            'status': presence_data.get('status', 'online'),
        }
        
        # Only admins can see current_page (always include it for admins, even if None)
        if is_admin:
            current_page = presence_data.get('current_page')
            user_data['current_page'] = current_page if current_page else None
        
        online_users_list.append(user_data)
    
    return Response({
        'users': online_users_list,
        'count': len(online_users_list)
    })


@extend_schema(
    description="Update user presence (heartbeat)",
    request={
        'type': 'object',
        'properties': {
            'current_page': {'type': 'string'},
            'status': {'type': 'string', 'enum': ['online', 'away', 'busy']},
        }
    },
    responses={200: {'type': 'object'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_presence(request):
    """
    Update user presence (heartbeat).
    Call this periodically (every 30-60 seconds) to keep user online.
    """
    user = request.user
    user_id = str(user.id)
    
    global _online_users
    _online_users[user_id] = {
        'last_seen': timezone.now(),
        'current_page': request.data.get('current_page', request.path),
        'status': request.data.get('status', 'online'),
    }
    
    return Response({
        'status': 'updated',
        'user_id': user_id
    })


@extend_schema(
    description="Remove user presence (called on logout)",
    responses={200: {'type': 'object'}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_presence(request):
    """
    Remove user from online users list (called on logout).
    """
    user = request.user
    user_id = str(user.id)
    
    global _online_users
    if user_id in _online_users:
        del _online_users[user_id]
    
    return Response({
        'status': 'removed',
        'user_id': user_id
    })

