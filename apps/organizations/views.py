"""
Views for organizations app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from django.db import models
from django.db.models import Q
from django.http import Http404 as DjangoHttp404

from .models import (
    Organization, 
    OrganizationMember,
    SubscriptionPlan,
    Feature,
    TierFeature,
    Subscription,
    BillingRecord,
    OrganizationUsage
)
from .serializers import (
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrganizationMemberSerializer,
    OrganizationMemberAddSerializer,
    OrganizationMemberUpdateSerializer,
    SubscriptionPlanSerializer,
    FeatureSerializer,
    TierFeatureSerializer,
    SubscriptionSerializer,
    BillingRecordSerializer,
    OrganizationUsageSerializer,
    FeatureAvailabilitySerializer,
    TierFeaturesListSerializer,
)
from apps.core.services.roles import RoleService
from apps.monitoring.mixins import AuditLoggingMixin
from apps.organizations.services import OrganizationStatusService, SubscriptionService
from apps.organizations.payment_service import PaymentService


class OrganizationViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoints for managing organizations.
    
    - Super admins: Can access all organizations
    - Org admins: Can access and manage their own organization
    - Regular users: Can only view their own organization
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    
    def get_queryset(self):
        """Filter organizations based on user permissions."""
        user = self.request.user
        
        # Super admins see all organizations
        if RoleService.is_super_admin(user):
            return Organization.objects.all().select_related('owner', 'created_by').prefetch_related('members', 'projects')
        
        # Get organizations user is a member of (via OrganizationMember)
        from apps.organizations.models import OrganizationMember
        member_org_ids = OrganizationMember.objects.filter(user=user).values_list('organization_id', flat=True)
        
        # Get organizations where user is the owner
        owner_org_ids = Organization.objects.filter(owner=user).values_list('id', flat=True)
        
        # Get organizations where user is org_admin (via OrganizationMember with org_admin role)
        org_admin_org_ids = OrganizationMember.objects.filter(
            user=user, 
            role='org_admin'
        ).values_list('organization_id', flat=True)
        
        # Also include user's primary organization if set
        org_ids = list(member_org_ids) + list(owner_org_ids) + list(org_admin_org_ids)
        if user.organization_id:
            org_ids.append(user.organization_id)
        
        # Remove duplicates
        org_ids = list(set(org_ids))
        
        if not org_ids:
            return Organization.objects.none()
        
        return Organization.objects.filter(id__in=org_ids).select_related('owner', 'created_by').prefetch_related('members', 'projects')
    
    def get_serializer_class(self):
        """Use create serializer for creation."""
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def perform_create(self, serializer):
        """Create organization and set creator as owner."""
        # Owner is set in serializer.create()
        serializer.save()
    
    def perform_update(self, serializer):
        """Update organization - only org admin or super admin can update."""
        organization = self.get_object()
        user = self.request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only organization administrators can update organization settings.")
        
        # Org admins cannot update when organization is suspended (only super_admin can reactivate)
        if not RoleService.is_super_admin(user) and organization:
            # Allow update if org is active or trial, but block if suspended or cancelled
            if organization.status in ['suspended', 'cancelled']:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(f"Cannot update organization. Organization is {organization.get_status_display()}. Please contact support.")
            
            # Check subscription active
            if not organization.is_subscription_active():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Cannot update organization. Organization subscription has expired.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete organization - only super admin can delete."""
        user = self.request.user
        
        if not RoleService.is_super_admin(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only super administrators can delete organizations.")
        
        instance.delete()
    
    def get_object(self):
        """Override to ensure org_admin can access their organization even if not in queryset."""
        # First try to get from queryset (normal flow)
        try:
            obj = super().get_object()
            return obj
        except (NotFound, DjangoHttp404, Organization.DoesNotExist) as e:
            # DRF raises NotFound when object is not in queryset
            # Django raises Http404, and models raise DoesNotExist
            # Check if user is org_admin for this organization
            pk = self.kwargs.get('pk')
            if not pk:
                raise NotFound("Organization not found.")
            
            try:
                organization = Organization.objects.get(pk=pk)
            except Organization.DoesNotExist:
                raise NotFound("Organization not found.")
            
            user = self.request.user
            
            # If user is super admin, they can access any organization
            if RoleService.is_super_admin(user):
                return organization
            
            # If user is org_admin for this organization, allow access
            if RoleService.is_org_admin(user, organization):
                return organization
            
            # Otherwise, raise 404
            raise NotFound("You do not have access to this organization.")
    
    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        """Get all members of the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can view members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        members = OrganizationMember.objects.filter(organization=organization).select_related('user', 'invited_by')
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Add a member to the organization",
        request=OrganizationMemberAddSerializer,
        responses={201: OrganizationMemberSerializer}
    )
    @action(detail=True, methods=['post'], url_path='members/add')
    def add_member(self, request, pk=None):
        """Add a user to the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can add members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate organization status and subscription (super admins bypass in service)
        try:
            OrganizationStatusService.require_active_organization(organization, user=user)
            OrganizationStatusService.require_subscription_active(organization, user=user)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check users.invite feature availability
        from apps.organizations.services import FeatureService
        try:
            FeatureService.is_feature_available(organization, 'users.invite', user=user, raise_exception=True)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate user limit (super admins can bypass)
        if not RoleService.is_super_admin(user) and not organization.can_add_user():
            from apps.organizations.services import FeatureService
            current_count = organization.get_member_count()
            max_users = FeatureService.get_feature_value(organization, 'users.max_count', default=0)
            return Response(
                {'error': f'Cannot add member. Organization has reached the maximum number of users ({max_users}). Current: {current_count}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrganizationMemberAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data.get('role', 'org_member')
        
        # Check if user is already a member
        if OrganizationMember.objects.filter(organization=organization, user_id=user_id).exists():
            return Response(
                {'error': 'User is already a member of this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create member
        member = OrganizationMember.objects.create(
            organization=organization,
            user_id=user_id,
            role=role,
            invited_by=user
        )
        
        # Update user's primary organization if not set
        from apps.authentication.models import User
        try:
            member_user = User.objects.get(id=user_id)
            if not member_user.organization:
                member_user.organization = organization
                member_user.save(update_fields=['organization'])
        except User.DoesNotExist:
            pass
        
        return Response(OrganizationMemberSerializer(member).data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Remove a member from the organization",
        request={'type': 'object', 'properties': {'user_id': {'type': 'string'}}},
        responses={204: None}
    )
    @action(detail=True, methods=['post'], url_path='members/remove')
    def remove_member(self, request, pk=None):
        """Remove a user from the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can remove members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate organization status and subscription (super admins bypass in service)
        if organization:
            try:
                OrganizationStatusService.require_active_organization(organization, user=user)
                OrganizationStatusService.require_subscription_active(organization, user=user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            member = OrganizationMember.objects.get(organization=organization, user_id=user_id)
            # Don't allow removing the organization owner
            if organization.owner_id == user_id:
                return Response(
                    {'error': 'Cannot remove the organization owner.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        description="Update a member's role in the organization",
        request=OrganizationMemberUpdateSerializer,
        responses={200: OrganizationMemberSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='members/(?P<member_id>[^/.]+)/update-role')
    def update_member_role(self, request, pk=None, member_id=None):
        """Update a member's role in the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can update member roles.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate organization status and subscription (super admins bypass in service)
        if organization:
            try:
                OrganizationStatusService.require_active_organization(organization, user=user)
                OrganizationStatusService.require_subscription_active(organization, user=user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            member = OrganizationMember.objects.get(organization=organization, id=member_id)
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'Member not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = OrganizationMemberUpdateSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(OrganizationMemberSerializer(member).data)


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing organization members.
    """
    serializer_class = OrganizationMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter members based on user permissions."""
        organization_id = self.kwargs.get('organization_pk')
        user = self.request.user
        
        if not organization_id:
            return OrganizationMember.objects.none()
        
        try:
            organization = Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist:
            return OrganizationMember.objects.none()
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return OrganizationMember.objects.none()
        
        return OrganizationMember.objects.filter(organization=organization).select_related('user', 'organization', 'invited_by')


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing subscription plans.
    
    - All authenticated users: Can view available plans
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionPlanSerializer
    
    def get_queryset(self):
        """Get active subscription plans."""
        return SubscriptionPlan.objects.filter(is_active=True).order_by('display_order', 'tier_code')


class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing features.
    
    - All authenticated users: Can view available features
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FeatureSerializer
    
    def get_queryset(self):
        """Get active, non-deprecated features."""
        queryset = Feature.objects.filter(is_active=True, is_deprecated=False)
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('category', 'code')


class TierFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing tier-to-feature mappings.
    
    - All authenticated users: Can view tier features
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TierFeatureSerializer
    
    def get_queryset(self):
        """Get tier features filtered by tier_code if provided."""
        queryset = TierFeature.objects.filter(is_enabled=True).select_related('feature').filter(
            feature__is_active=True,
            feature__is_deprecated=False
        )
        
        tier_code = self.request.query_params.get('tier_code')
        if tier_code:
            queryset = queryset.filter(tier_code=tier_code)
        
        return queryset.order_by('tier_code', 'feature__category', 'feature__code')


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing subscriptions.
    
    - Super admins: Can view and manage all subscriptions
    - Org admins: Can view and manage subscriptions for their organization
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        """Filter subscriptions based on user permissions."""
        user = self.request.user
        
        # Super admins see all subscriptions
        if RoleService.is_super_admin(user):
            return Subscription.objects.all().select_related('organization', 'plan').order_by('-created_at')
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if not organization:
            return Subscription.objects.none()
        
        # Check if user is org_admin
        if not RoleService.is_org_admin(user, organization):
            return Subscription.objects.none()
        
        # Return subscriptions for user's organization
        return Subscription.objects.filter(organization=organization).select_related('organization', 'plan').order_by('-created_at')
    
    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """Get current active subscription for user's organization."""
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        if not organization:
            return Response(
                {'error': 'User is not associated with an organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can view subscription details.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get active subscription
        subscription = organization.get_active_subscription()
        
        if not subscription:
            return Response(
                {'error': 'No active subscription found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='features')
    def features(self, request):
        """Get all features available for current organization's tier."""
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        if not organization:
            return Response(
                {'error': 'User is not associated with an organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from apps.organizations.services import FeatureService
        import logging
        logger = logging.getLogger(__name__)
        
        tier_code = organization.subscription_tier or 'trial'
        
        # Check if cache should be cleared (for debugging)
        clear_cache = request.query_params.get('clear_cache', 'false').lower() == 'true'
        # Also clear cache if _t parameter is present (cache busting from frontend)
        force_refresh = '_t' in request.query_params
        
        if clear_cache or force_refresh:
            FeatureService.invalidate_cache(tier_code=tier_code)
            logger.info(f"[Features Endpoint] Cache cleared for tier: {tier_code} (clear_cache={clear_cache}, force_refresh={force_refresh})")
        
        # Log for debugging
        logger.info(f"[Features Endpoint] Organization {organization.id}: subscription_tier={tier_code}, clear_cache={clear_cache}, force_refresh={force_refresh}")
        
        features = FeatureService.get_features_for_tier(tier_code)
        
        # Log the projects.max_count value for debugging
        if 'projects.max_count' in features:
            logger.info(f"[Features Endpoint] projects.max_count for tier {tier_code}: {features['projects.max_count']['value']}")
        else:
            logger.warning(f"[Features Endpoint] projects.max_count not found for tier {tier_code}")
        
        return Response({
            'tier_code': tier_code,
            'features': features
        })
    
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """Create a checkout session for subscription."""
        from apps.organizations.payment_service import PaymentService
        from rest_framework.exceptions import ValidationError
        
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        if not organization:
            return Response(
                {'error': 'User is not associated with an organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can create checkout sessions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plan_id = request.data.get('plan_id')
        billing_cycle = request.data.get('billing_cycle', 'monthly')
        
        if not plan_id:
            raise ValidationError({'plan_id': 'This field is required.'})
        
        if billing_cycle not in ['monthly', 'annual']:
            raise ValidationError({'billing_cycle': 'Must be either "monthly" or "annual".'})
        
        try:
            session = PaymentService.create_checkout_session(organization, plan_id, billing_cycle)
            return Response(session, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='checkout/success')
    def checkout_success(self, request):
        """
        Complete checkout and update subscription.
        
        TODO: Payment Integration
        In production, this should:
        1. Verify payment was successful via payment provider API (Stripe, PayPal, etc.)
        2. Verify the session_id corresponds to a completed payment
        3. Only then update the subscription
        4. Handle payment webhooks for async verification
        For now, this directly updates the subscription without payment verification.
        """
        from apps.organizations.payment_service import PaymentService
        from rest_framework.exceptions import ValidationError
        
        try:
            user = request.user
            organization = RoleService.get_user_organization(user)
            
            if not organization:
                return Response(
                    {'error': 'User is not associated with an organization.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check permissions
            if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
                return Response(
                    {'error': 'Only organization administrators can complete checkout.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            session_id = request.data.get('session_id')
            if not session_id:
                raise ValidationError({'session_id': 'This field is required.'})
            
            # Try to get plan_id and billing_cycle from request first (for mock payment fallback)
            plan_id_from_request = request.data.get('plan_id')
            billing_cycle_from_request = request.data.get('billing_cycle', 'monthly')
            
            # TODO: Payment Integration
            # In production, verify payment was successful:
            # 1. Verify session_id with payment provider (Stripe, PayPal, etc.)
            # 2. Check payment status (paid, completed, etc.)
            # 3. Only proceed if payment is confirmed
            # For now, we allow direct plan changes without payment verification
            
            # Try to verify the checkout session (for backward compatibility)
            result = None
            session_verified = False
            import logging
            logger = logging.getLogger(__name__)
            
            # Check if this is a direct plan change (bypassing payment)
            is_direct_change = session_id.startswith('direct_plan_change_')
            
            if is_direct_change:
                # Direct plan change - skip payment verification
                logger.info(f"Direct plan change detected: {session_id}")
                if not plan_id_from_request:
                    return Response(
                        {'error': 'Plan ID is required for direct plan changes.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                result = {
                    'plan_id': str(plan_id_from_request),
                    'billing_cycle': billing_cycle_from_request,
                }
            else:
                # Try to verify the checkout session (for payment-based changes)
                try:
                    result = PaymentService.verify_checkout_session(session_id)
                    session_verified = True
                    logger.info(f"Checkout session verified successfully: {session_id}")
                except ValidationError as ve:
                    # Session not found or expired - use plan_id from request as fallback
                    logger.warning(f"Checkout session not found, using fallback: {session_id}, error: {ve}, plan_id_from_request: {plan_id_from_request}")
                    
                    if not plan_id_from_request:
                        # Extract error message properly
                        error_msg = str(ve)
                        if hasattr(ve, 'detail'):
                            if isinstance(ve.detail, list):
                                error_msg = '; '.join(str(msg) for msg in ve.detail)
                            elif isinstance(ve.detail, str):
                                error_msg = ve.detail
                            elif isinstance(ve.detail, dict):
                                error_msg = '; '.join(f"{k}: {v}" for k, v in ve.detail.items())
                        
                        return Response(
                            {'error': f'Checkout session expired or invalid ({error_msg}), and plan_id not provided. Please try selecting the plan again.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Use plan_id from request if session is expired
                    result = {
                        'plan_id': str(plan_id_from_request),
                        'billing_cycle': billing_cycle_from_request,
                    }
                    logger.info(f"Using fallback plan_id: {plan_id_from_request}, billing_cycle: {billing_cycle_from_request}")
            
            # TODO: Payment Integration
            # In production, this should:
            # 1. Verify payment was successful via payment provider API
            # 2. Create or update subscription based on verified payment
            # 3. Handle payment webhooks for async verification
            # For now, we directly create/update subscription without payment verification
            
            # Create or update subscription based on checkout session
            from apps.organizations.models import SubscriptionPlan
            from django.utils import timezone
            from datetime import timedelta
            
            # Get plan from session result (should always have plan_id now due to fallback)
            plan_id = result.get('plan_id') if result else None
            billing_cycle = result.get('billing_cycle', 'monthly') if result else 'monthly'
            
            # Final fallback to request data if still not found
            if not plan_id:
                plan_id = plan_id_from_request
            if not billing_cycle or billing_cycle not in ['monthly', 'annual']:
                billing_cycle = billing_cycle_from_request
            
            if not plan_id:
                return Response(
                    {'error': 'Plan ID not found in checkout session or request. Please try selecting the plan again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Ensure plan_id is a string
            plan_id = str(plan_id)
            
            try:
                plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
            except SubscriptionPlan.DoesNotExist:
                return Response(
                    {'error': 'Subscription plan not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Cancel any existing active subscriptions for this organization
            Subscription.objects.filter(
                organization=organization,
                status='active'
            ).update(status='cancelled', cancelled_at=timezone.now())
            
            # Create new subscription
            now = timezone.now()
            if billing_cycle == 'annual':
                period_end = now + timedelta(days=365)
            else:
                period_end = now + timedelta(days=30)
            
            subscription = Subscription.objects.create(
                organization=organization,
                plan=plan,
                tier_code=plan.tier_code,
                status='active',
                billing_cycle=billing_cycle,
                started_at=now,
                current_period_start=now,
                current_period_end=period_end,
                cancel_at_period_end=False,
            )
            
            # Update organization subscription tier
            organization.subscription_tier = plan.tier_code
            organization.status = 'active'
            organization.active_subscription = subscription
            organization.subscription_start_date = now.date()
            organization.subscription_end_date = period_end.date()
            
            # Update max_users and max_projects from tier features
            # Use the refresh method to ensure consistency
            organization.refresh_limits_from_features()
            
            # Invalidate feature cache for the new tier to ensure fresh data
            from apps.organizations.services import FeatureService
            FeatureService.invalidate_cache(tier_code=plan.tier_code)
            
            # Save organization with all updates
            organization.save()
            
            # Create billing record for this subscription
            from apps.organizations.models import BillingRecord
            amount = plan.monthly_price if billing_cycle == 'monthly' else plan.annual_price
            if amount:
                BillingRecord.objects.create(
                    organization=organization,
                    subscription=subscription,
                    amount=str(amount),
                    currency='usd',
                    status='paid',
                    billing_type='subscription',
                    paid_at=now,
                    metadata={
                        'session_id': session_id,
                        'payment_method': 'mock',
                        'transaction_id': f"mock_txn_{session_id}",
                    }
                )
            
            serializer = self.get_serializer(subscription)
            return Response({
                'subscription': serializer.data,
                'message': 'Subscription activated successfully.'
            }, status=status.HTTP_200_OK)
        
        except ValidationError as ve:
            # Handle ValidationError with proper formatting
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ValidationError in checkout_success: {ve}")
            
            # Check if it's a dict (field-specific errors)
            if isinstance(ve.detail, dict):
                # Format dict errors properly
                error_messages = []
                for field, messages in ve.detail.items():
                    if isinstance(messages, list):
                        error_messages.extend([f"{field}: {msg}" for msg in messages])
                    else:
                        error_messages.append(f"{field}: {messages}")
                return Response(
                    {'error': '; '.join(error_messages) if error_messages else str(ve)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Check if it has detail attribute
            elif hasattr(ve, 'detail'):
                if isinstance(ve.detail, str):
                    return Response({'error': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
                elif isinstance(ve.detail, list):
                    # Handle list of error messages
                    error_message = '; '.join(str(msg) for msg in ve.detail) if ve.detail else str(ve)
                    return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
                return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
            # Fallback to string representation
            return Response(
                {'error': str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Error completing checkout: {str(e)}")
            
            # Handle ValidationError that might have been re-raised or not caught
            if isinstance(e, ValidationError):
                error_msg = str(e)
                if hasattr(e, 'detail'):
                    if isinstance(e.detail, list):
                        error_msg = '; '.join(str(msg) for msg in e.detail) if e.detail else str(e)
                    elif isinstance(e.detail, str):
                        error_msg = e.detail
                    elif isinstance(e.detail, dict):
                        error_msg = '; '.join(f"{k}: {v}" for k, v in e.detail.items())
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'error': f'An error occurred while processing your subscription: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='cancel')
    def cancel(self, request):
        """Cancel subscription."""
        from django.utils import timezone
        from rest_framework.exceptions import ValidationError
        
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        if not organization:
            return Response(
                {'error': 'User is not associated with an organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can cancel subscriptions.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        immediately = request.data.get('immediately', False)
        
        subscription = organization.get_active_subscription()
        if not subscription:
            return Response(
                {'error': 'No active subscription found to cancel.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if immediately:
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
        else:
            subscription.cancel_at_period_end = True
        
        subscription.save()
        
        serializer = self.get_serializer(subscription)
        return Response({
            'subscription': serializer.data,
            'message': 'Subscription cancelled successfully.' if immediately else 'Subscription will be cancelled at the end of the billing period.'
        }, status=status.HTTP_200_OK)


class BillingRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing billing records.
    
    - Super admins: Can view all billing records
    - Org admins: Can view billing records for their organization
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BillingRecordSerializer
    
    def get_queryset(self):
        """Filter billing records based on user permissions."""
        user = self.request.user
        
        # Super admins see all billing records
        if RoleService.is_super_admin(user):
            return BillingRecord.objects.all().select_related('subscription', 'organization').order_by('-created_at')
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if not organization:
            return BillingRecord.objects.none()
        
        # Check if user is org_admin
        if not RoleService.is_org_admin(user, organization):
            return BillingRecord.objects.none()
        
        # Return billing records for user's organization
        return BillingRecord.objects.filter(organization=organization).select_related(
            'subscription', 'organization'
        ).order_by('-created_at')


class OrganizationUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing organization usage.
    
    - Super admins: Can view all usage records
    - Org admins: Can view usage records for their organization
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationUsageSerializer
    
    def get_queryset(self):
        """Filter usage records based on user permissions."""
        user = self.request.user
        
        # Super admins see all usage records
        if RoleService.is_super_admin(user):
            queryset = OrganizationUsage.objects.all().select_related('organization')
        else:
            # Get user's organization
            organization = RoleService.get_user_organization(user)
            if not organization:
                return OrganizationUsage.objects.none()
            
            # Check if user is org_admin
            if not RoleService.is_org_admin(user, organization):
                return OrganizationUsage.objects.none()
            
            # Return usage records for user's organization
            queryset = OrganizationUsage.objects.filter(organization=organization).select_related('organization')
        
        # Filter by usage_type if provided
        usage_type = self.request.query_params.get('usage_type')
        if usage_type:
            queryset = queryset.filter(usage_type=usage_type)
        
        # Filter by month/year if provided
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(month=int(month))
        
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=int(year))
        
        return queryset.order_by('-year', '-month', 'usage_type')
    
    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        """Get current month usage for user's organization."""
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        if not organization:
            return Response(
                {'error': 'User is not associated with an organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can view usage details.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.utils import timezone
        now = timezone.now()
        month = now.month
        year = now.year
        
        usage_records = OrganizationUsage.objects.filter(
            organization=organization,
            month=month,
            year=year
        )
        
        serializer = self.get_serializer(usage_records, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='feature/(?P<feature_code>[^/.]+)')
    def feature(self, request, feature_code=None):
        """Check feature availability and usage for current organization."""
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        if not organization:
            return Response(
                {'error': 'User is not associated with an organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from apps.organizations.services import FeatureService, SubscriptionService
        
        tier_code = organization.subscription_tier or 'trial'
        is_available = FeatureService.is_feature_available(organization, feature_code)
        limit = FeatureService.get_feature_limit(organization, feature_code)
        
        # Map feature_code to usage_type if it's a usage feature
        # This mapping is used for API responses to show current usage
        # The feature codes must match actual feature codes in the database
        usage_type_mapping = {
            'users.max_count': 'max_users',  # For display purposes (count feature, not usage)
            'projects.max_count': 'max_projects',  # For display purposes (count feature, not usage)
            'ai.agent_executions': 'agent_executions',  # Fixed: matches actual feature code
            'ai.workflow_executions': 'workflow_executions',  # Fixed: matches actual feature code
            'ai.chat': 'chat_messages',  # Fixed: matches actual feature code
            'ai.command_executions': 'command_executions',  # Fixed: matches actual feature code
        }
        
        usage_type = None
        current_usage = None
        
        # Try to get current usage if it's a usage-based feature
        for key, value in usage_type_mapping.items():
            if feature_code == key:
                usage_type = value
                from django.utils import timezone
                now = timezone.now()
                current_usage = SubscriptionService.get_usage_count(organization, usage_type, now.month, now.year)
                break
        
        # Get feature name
        features = FeatureService.get_features_for_tier(tier_code)
        feature_name = features.get(feature_code, {}).get('name') if feature_code in features else None
        
        serializer = FeatureAvailabilitySerializer({
            'feature_code': feature_code,
            'is_available': is_available,
            'limit': limit,
            'current_usage': current_usage,
            'tier_code': tier_code,
            'feature_name': feature_name,
        })
        
        return Response(serializer.data)

