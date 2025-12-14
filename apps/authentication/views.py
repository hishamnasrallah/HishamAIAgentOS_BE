"""
Views for authentication app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import csv
import io
import os
import uuid
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
from .models import APIKey
from .serializers import UserSerializer, UserCreateSerializer, APIKeySerializer
from .permissions import IsAdminUser
from apps.monitoring.mixins import AuditLoggingMixin
from apps.core.services.roles import RoleService
from apps.organizations.services import OrganizationStatusService, SubscriptionService

User = get_user_model()


class UserViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
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
        Filter users based on organization and permissions.
        - Super admins: See all users across all organizations
        - Org admins: See all users in their organization
        - Regular users: Can only see themselves
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return User.objects.none()
        
        # Super admins see all users
        if RoleService.is_super_admin(user):
            return User.objects.all().select_related('organization')
        
        # Org admins see all users in their organization(s), but exclude superusers
        user_orgs = RoleService.get_user_organizations(user)
        if user_orgs:
            org_ids = [org.id for org in user_orgs]
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            if is_org_admin:
                # Org admins see all users in their organization(s), but NOT superusers
                return User.objects.filter(
                    organization_id__in=org_ids,
                    is_superuser=False
                ).select_related('organization')
        
        # Regular users can only see themselves
        return User.objects.filter(id=user.id).select_related('organization')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Override to allow read/update for own profile, but restrict create/delete to admins."""
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'me']:
            return [IsAuthenticated()]
        # Create/delete require admin (super_admin or org_admin) - use our custom IsAdminUser
        return [IsAuthenticated(), IsAdminUser()]
    
    def perform_create(self, serializer):
        """Validate organization limits and set organization for new users."""
        user = self.request.user
        
        # Get organization for the new user
        organization = None
        if RoleService.is_super_admin(user):
            # Super admin can assign to any organization from request data
            organization_id = self.request.data.get('organization')
            if organization_id:
                from apps.organizations.models import Organization
                try:
                    organization = Organization.objects.get(pk=organization_id)
                except Organization.DoesNotExist:
                    pass
        elif RoleService.is_org_admin(user):
            # Org admin can only create users in their organization
            user_orgs = RoleService.get_user_organizations(user)
            if user_orgs:
                organization = user_orgs[0]  # Use first organization
        
        # If no organization found, try to get from serializer validated_data
        if not organization:
            organization = serializer.validated_data.get('organization')
        
        # Validate organization limits if organization is set
        # Super admins can bypass all checks
        if organization and not RoleService.is_super_admin(user):
            # Check if organization is active
            if not organization.is_active():
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f'Cannot create user. Organization "{organization.name}" is {organization.get_status_display()}.')
            
            # Check if organization subscription is active
            if not organization.is_subscription_active():
                from rest_framework.exceptions import ValidationError
                raise ValidationError('Cannot create user. Organization subscription has expired.')
            
            # Check user limit
            if not organization.can_add_user():
                current_count = organization.get_member_count()
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f'Cannot create user. Organization has reached the maximum number of users ({organization.max_users}). Current: {current_count}')
        
        # Save the user (organization will be set in serializer.create() if not already set)
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Update user with organization status and subscription validation.
        Users can update their own profile, but org status/subscription must be valid.
        """
        user = serializer.instance
        request_user = self.request.user
        
        # Get organization from the user being updated
        organization = user.organization if user else None
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=request_user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=request_user)
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete user with organization status and subscription validation.
        """
        user = self.request.user
        
        # Get organization from the user being deleted
        organization = instance.organization if instance else None
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
        
        super().perform_destroy(instance)
    
    # Note: Audit logging is now handled automatically by:
    # 1. Middleware for API requests
    # 2. Signals for model saves
    # No need for explicit logging here
    
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get or update current user profile.
        For updates, validate organization status and subscription.
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            # Update profile
            user = request.user
            organization = user.organization if user else None
            
            # Super admins can bypass checks (handled in service methods)
            if organization:
                try:
                    # Check organization status
                    OrganizationStatusService.require_active_organization(organization, user=user)
                    
                    # Check subscription active
                    OrganizationStatusService.require_subscription_active(organization, user=user)
                except Exception as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user (admin only)."""
        if not RoleService.is_admin(request.user):
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
        if not RoleService.is_admin(request.user):
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
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_activate(self, request):
        """Bulk activate users (admin only)."""
        if not RoleService.is_admin(request.user):
            return Response(
                {'error': 'Only admins can perform bulk operations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {'error': 'user_ids is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        updated_count = users.update(is_active=True)
        
        return Response({
            'message': f'{updated_count} user(s) activated.',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_deactivate(self, request):
        """Bulk deactivate users (admin only)."""
        if not RoleService.is_admin(request.user):
            return Response(
                {'error': 'Only admins can perform bulk operations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {'error': 'user_ids is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deactivating yourself
        if str(request.user.id) in user_ids:
            return Response(
                {'error': 'You cannot deactivate your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        updated_count = users.update(is_active=False)
        
        return Response({
            'message': f'{updated_count} user(s) deactivated.',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_delete(self, request):
        """Bulk delete users (admin only)."""
        if not RoleService.is_admin(request.user):
            return Response(
                {'error': 'Only admins can perform bulk operations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response(
                {'error': 'user_ids is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deleting yourself
        if str(request.user.id) in user_ids:
            return Response(
                {'error': 'You cannot delete your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        deleted_count = users.count()
        users.delete()
        
        return Response({
            'message': f'{deleted_count} user(s) deleted.',
            'deleted_count': deleted_count
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_assign_role(self, request):
        """Bulk assign role to users (admin only)."""
        if not RoleService.is_admin(request.user):
            return Response(
                {'error': 'Only admins can perform bulk operations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_ids = request.data.get('user_ids', [])
        role = request.data.get('role')
        
        if not user_ids:
            return Response(
                {'error': 'user_ids is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not role:
            return Response(
                {'error': 'role is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not RoleService.is_valid_role(role):
            valid_roles = RoleService.get_all_system_roles()
            return Response(
                {'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        updated_count = users.update(role=role)
        
        return Response({
            'message': f'Role "{role}" assigned to {updated_count} user(s).',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export(self, request):
        """Export users to CSV (admin only)."""
        if not RoleService.is_admin(request.user):
            return Response(
                {'error': 'Only admins can export users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Apply filters
        queryset = self.get_queryset()
        role = request.query_params.get('role')
        is_active = request.query_params.get('is_active')
        search = request.query_params.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(username__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Email', 'Username', 'First Name', 'Last Name', 'Role',
            'Is Active', '2FA Enabled', 'Date Joined', 'Last Login'
        ])
        
        for user in queryset:
            writer.writerow([
                user.email,
                user.username,
                user.first_name or '',
                user.last_name or '',
                user.role,
                'Yes' if user.is_active else 'No',
                'Yes' if user.two_factor_enabled else 'No',
                user.date_joined.isoformat() if user.date_joined else '',
                user.last_login.isoformat() if user.last_login else '',
            ])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_export_{timezone.now().date()}.csv"'
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def import_users(self, request):
        """Import users from CSV (admin only)."""
        if not RoleService.is_admin(request.user):
            return Response(
                {'error': 'Only admins can import users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response(
                {'error': 'File must be a CSV file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            decoded_file = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(decoded_file))
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    email = row.get('Email', '').strip()
                    if not email:
                        errors.append(f'Row {row_num}: Email is required')
                        continue
                    
                    username = row.get('Username', '').strip() or email.split('@')[0]
                    first_name = row.get('First Name', '').strip()
                    last_name = row.get('Last Name', '').strip()
                    role = row.get('Role', 'viewer').strip().lower()
                    is_active = row.get('Is Active', 'Yes').strip().lower() in ('yes', 'true', '1')
                    
                    if not RoleService.is_valid_role(role):
                        role = 'viewer'
                    
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': username,
                            'first_name': first_name,
                            'last_name': last_name,
                            'role': role,
                            'is_active': is_active,
                        }
                    )
                    
                    if not created:
                        user.username = username
                        user.first_name = first_name
                        user.last_name = last_name
                        user.role = role
                        user.is_active = is_active
                        user.save()
                        updated_count += 1
                    else:
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
            
            return Response({
                'message': f'Import completed. Created: {created_count}, Updated: {updated_count}',
                'created_count': created_count,
                'updated_count': updated_count,
                'errors': errors[:10],  # Limit errors to first 10
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def activity(self, request, pk=None):
        """Get user activity log (admin only or own user)."""
        user = self.get_object()
        
        # Users can only see their own activity, admins can see anyone's
        if not RoleService.is_admin(request.user) and user.id != request.user.id:
            return Response(
                {'error': 'You can only view your own activity.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Query AuditLog model for user activity
        from apps.monitoring.models import AuditLog
        
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        activities = AuditLog.objects.filter(user=user).order_by('-timestamp')[offset:offset+limit]
        
        activity_data = []
        for activity in activities:
            activity_data.append({
                'id': str(activity.id),
                'action': activity.action,
                'resource_type': activity.resource_type,
                'resource_id': str(activity.resource_id) if activity.resource_id else None,
                'details': activity.description,  # Use description field
                'changes': activity.changes,
                'ip_address': str(activity.ip_address) if activity.ip_address else None,
                'created_at': activity.timestamp.isoformat(),  # Use timestamp field
            })
        
        return Response({
            'user_id': str(user.id),
            'activities': activity_data,
            'total': AuditLog.objects.filter(user=user).count(),
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    def upload_avatar(self, request, pk=None):
        """Upload avatar for user (own profile or admin)."""
        user = self.get_object()
        
        # Check permissions: users can only update their own avatar, admins can update anyone's
        if not RoleService.is_admin(request.user) and user.id != request.user.id:
            return Response(
                {'error': 'You can only update your own avatar.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        avatar_file = request.FILES['avatar']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response(
                {'error': f'Invalid file type. Allowed types: {", ".join(allowed_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'File size exceeds 5MB limit.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if not HAS_PIL:
                return Response(
                    {'error': 'Image processing library (Pillow) is not available.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Process and save image
            image = Image.open(avatar_file)
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Resize to max 512x512 while maintaining aspect ratio
            image.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            # Generate filename
            file_ext = os.path.splitext(avatar_file.name)[1] or '.jpg'
            filename = f'avatars/{user.id}/{uuid.uuid4()}{file_ext}'
            
            # Save to storage
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            # Delete old avatar if exists
            if user.avatar and not user.avatar.startswith('http'):
                try:
                    default_storage.delete(user.avatar)
                except:
                    pass
            
            # Save new avatar
            saved_path = default_storage.save(filename, ContentFile(output.read()))
            user.avatar = saved_path
            user.save(update_fields=['avatar'])
            
            serializer = self.get_serializer(user)
            return Response({
                'message': 'Avatar uploaded successfully.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process avatar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_avatar(self, request, pk=None):
        """Delete avatar for user (own profile or admin)."""
        user = self.get_object()
        
        # Check permissions
        if not RoleService.is_admin(request.user) and user.id != request.user.id:
            return Response(
                {'error': 'You can only delete your own avatar.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not user.avatar:
            return Response(
                {'error': 'No avatar to delete.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete file if it's not a URL
        if not user.avatar.startswith('http'):
            try:
                default_storage.delete(user.avatar)
            except:
                pass
        
        user.avatar = ''
        user.save(update_fields=['avatar'])
        
        serializer = self.get_serializer(user)
        return Response({
            'message': 'Avatar deleted successfully.',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


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
    
    def perform_create(self, serializer):
        """
        Create API key with organization status, subscription, and tier limit validation.
        """
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
            
            # Check API key limit based on tier
            from apps.organizations.services import SubscriptionService
            current_count = APIKey.objects.filter(user=user, is_active=True).count()
            tier = organization.subscription_tier or 'trial'
            max_api_keys = SubscriptionService.get_limit_for_feature(tier, 'max_api_keys')
            
            # Super admins can bypass API key limits
            if not RoleService.is_super_admin(user) and max_api_keys is not None and current_count >= max_api_keys:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    f'You have reached your API key limit ({max_api_keys} for {tier.title()} tier). '
                    f'Current: {current_count}/{max_api_keys}. Please upgrade your subscription or deactivate existing keys.'
                )
        
        serializer.save(user=user, created_by=user)
    
    def perform_update(self, serializer):
        """
        Update API key with organization status and subscription validation.
        """
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
        
        serializer.save(updated_by=user)
    
    def perform_destroy(self, instance):
        """
        Delete API key with organization status and subscription validation.
        """
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
        
        super().perform_destroy(instance)
