"""
Views for external integrations.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import (
    GitHubIntegration,
    SlackIntegration,
    JiraIntegration,
    EmailNotificationSettings,
    WebhookEndpoint,
    WebhookDelivery
)
from .serializers import (
    GitHubIntegrationSerializer,
    SlackIntegrationSerializer,
    JiraIntegrationSerializer,
    EmailNotificationSettingsSerializer,
    WebhookEndpointSerializer,
    WebhookDeliverySerializer
)
from .services import (
    GitHubService,
    SlackService,
    JiraService,
    EmailService,
    WebhookService
)
from apps.core.services.roles import RoleService
from apps.organizations.services import FeatureService


class GitHubIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for GitHub integrations."""
    serializer_class = GitHubIntegrationSerializer
    permission_classes = [IsAuthenticated]
    queryset = GitHubIntegration.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Get GitHub integrations for the current user."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return GitHubIntegration.objects.none()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return GitHubIntegration.objects.none()
        
        return GitHubIntegration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a GitHub integration with integration limit and feature checks."""
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if organization:
            # Check if GitHub integration feature is available
            FeatureService.is_feature_available(
                organization, 
                'integrations.github', 
                user=user, 
                raise_exception=True
            )
            
            # Check integration limit
            max_integrations = FeatureService.get_feature_value(organization, 'integrations.max_count', default=0)
            
            if max_integrations is not None and max_integrations > 0:
                # Count all integrations for organization members
                from apps.organizations.models import OrganizationMember
                org_member_ids = OrganizationMember.objects.filter(
                    organization=organization
                ).values_list('user_id', flat=True)
                
                # Count all integrations across all types for organization
                github_count = GitHubIntegration.objects.filter(user_id__in=org_member_ids).count()
                slack_count = SlackIntegration.objects.filter(user_id__in=org_member_ids).count()
                jira_count = JiraIntegration.objects.filter(user_id__in=org_member_ids).count()
                webhook_count = WebhookEndpoint.objects.filter(user_id__in=org_member_ids).count()
                current_count = github_count + slack_count + jira_count + webhook_count
                
                if current_count >= max_integrations:
                    tier_display = organization.subscription_tier.title()
                    raise ValidationError(
                        f'Integration limit reached ({current_count}/{max_integrations} for {tier_display} tier). '
                        f'Please upgrade your subscription or remove existing integrations.'
                    )
        
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify GitHub connection."""
        integration = self.get_object()
        service = GitHubService(integration)
        is_valid = service.verify_connection()
        
        return Response({
            'verified': is_valid,
            'message': 'Connection verified' if is_valid else 'Connection failed'
        })
    
    @action(detail=True, methods=['post'])
    def sync_prs(self, request, pk=None):
        """Sync pull requests from GitHub."""
        integration = self.get_object()
        service = GitHubService(integration)
        prs = service.sync_pull_requests()
        
        return Response({
            'synced': len(prs),
            'pull_requests': prs
        })


class SlackIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Slack integrations."""
    serializer_class = SlackIntegrationSerializer
    permission_classes = [IsAuthenticated]
    queryset = SlackIntegration.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Get Slack integrations for the current user."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return SlackIntegration.objects.none()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return SlackIntegration.objects.none()
        
        return SlackIntegration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a Slack integration with integration limit and feature checks."""
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if organization:
            # Check if Slack integration feature is available
            FeatureService.is_feature_available(
                organization, 
                'integrations.slack', 
                user=user, 
                raise_exception=True
            )
            
            # Check integration limit
            max_integrations = FeatureService.get_feature_value(organization, 'integrations.max_count', default=0)
            
            if max_integrations is not None and max_integrations > 0:
                # Count all integrations for organization members
                from apps.organizations.models import OrganizationMember
                org_member_ids = OrganizationMember.objects.filter(
                    organization=organization
                ).values_list('user_id', flat=True)
                
                # Count all integrations across all types for organization
                github_count = GitHubIntegration.objects.filter(user_id__in=org_member_ids).count()
                slack_count = SlackIntegration.objects.filter(user_id__in=org_member_ids).count()
                jira_count = JiraIntegration.objects.filter(user_id__in=org_member_ids).count()
                webhook_count = WebhookEndpoint.objects.filter(user_id__in=org_member_ids).count()
                current_count = github_count + slack_count + jira_count + webhook_count
                
                if current_count >= max_integrations:
                    tier_display = organization.subscription_tier.title()
                    raise ValidationError(
                        f'Integration limit reached ({current_count}/{max_integrations} for {tier_display} tier). '
                        f'Please upgrade your subscription or remove existing integrations.'
                    )
        
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify Slack connection."""
        integration = self.get_object()
        service = SlackService(integration)
        is_valid = service.verify_connection()
        
        return Response({
            'verified': is_valid,
            'message': 'Connection verified' if is_valid else 'Connection failed'
        })
    
    @action(detail=True, methods=['post'])
    def test_message(self, request, pk=None):
        """Send a test message to Slack."""
        integration = self.get_object()
        service = SlackService(integration)
        success = service.send_message("Test message from HishamOS")
        
        return Response({
            'sent': success,
            'message': 'Test message sent' if success else 'Failed to send message'
        })


class JiraIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Jira integrations."""
    serializer_class = JiraIntegrationSerializer
    permission_classes = [IsAuthenticated]
    queryset = JiraIntegration.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Get Jira integrations for the current user."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return JiraIntegration.objects.none()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return JiraIntegration.objects.none()
        
        return JiraIntegration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a Jira integration with integration limit and feature checks."""
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if organization:
            # Check if Jira integration feature is available
            FeatureService.is_feature_available(
                organization, 
                'integrations.jira', 
                user=user, 
                raise_exception=True
            )
            
            # Check integration limit
            max_integrations = FeatureService.get_feature_value(organization, 'integrations.max_count', default=0)
            
            if max_integrations is not None and max_integrations > 0:
                # Count all integrations for organization members
                from apps.organizations.models import OrganizationMember
                org_member_ids = OrganizationMember.objects.filter(
                    organization=organization
                ).values_list('user_id', flat=True)
                
                # Count all integrations across all types for organization
                github_count = GitHubIntegration.objects.filter(user_id__in=org_member_ids).count()
                slack_count = SlackIntegration.objects.filter(user_id__in=org_member_ids).count()
                jira_count = JiraIntegration.objects.filter(user_id__in=org_member_ids).count()
                webhook_count = WebhookEndpoint.objects.filter(user_id__in=org_member_ids).count()
                current_count = github_count + slack_count + jira_count + webhook_count
                
                if current_count >= max_integrations:
                    tier_display = organization.subscription_tier.title()
                    raise ValidationError(
                        f'Integration limit reached ({current_count}/{max_integrations} for {tier_display} tier). '
                        f'Please upgrade your subscription or remove existing integrations.'
                    )
        
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify Jira connection."""
        integration = self.get_object()
        service = JiraService(integration)
        is_valid = service.verify_connection()
        
        return Response({
            'verified': is_valid,
            'message': 'Connection verified' if is_valid else 'Connection failed'
        })
    
    @action(detail=True, methods=['post'])
    def create_issue(self, request, pk=None):
        """Create a Jira issue."""
        integration = self.get_object()
        service = JiraService(integration)
        
        summary = request.data.get('summary', '')
        description = request.data.get('description', '')
        issue_type = request.data.get('issue_type')
        priority = request.data.get('priority')
        
        issue = service.create_issue(summary, description, issue_type, priority)
        
        if issue:
            return Response({
                'created': True,
                'issue_key': issue.get('key'),
                'issue_id': issue.get('id'),
                'issue': issue
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'created': False,
                'message': 'Failed to create Jira issue'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def get_project(self, request, pk=None):
        """Get Jira project information."""
        integration = self.get_object()
        service = JiraService(integration)
        project = service.get_project()
        
        if project:
            return Response(project)
        else:
            return Response({
                'error': 'Failed to fetch project information'
            }, status=status.HTTP_400_BAD_REQUEST)


class EmailNotificationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for email notification settings."""
    serializer_class = EmailNotificationSettingsSerializer
    permission_classes = [IsAuthenticated]
    queryset = EmailNotificationSettings.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Get email settings for the current user."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return EmailNotificationSettings.objects.none()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return EmailNotificationSettings.objects.none()
        
        return EmailNotificationSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create email settings for the current user."""
        obj, created = EmailNotificationSettings.objects.get_or_create(
            user=self.request.user,
            defaults={'email_address': self.request.user.email}
        )
        return obj
    
    def perform_create(self, serializer):
        """Create email notification settings."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def test_email(self, request):
        """Send a test email."""
        settings_obj = self.get_object()
        service = EmailService(settings_obj)
        success = service.send_email(
            subject="Test Email from HishamOS",
            message="This is a test email to verify your email notification settings."
        )
        
        return Response({
            'sent': success,
            'message': 'Test email sent' if success else 'Failed to send email'
        })


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """ViewSet for webhook endpoints."""
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsAuthenticated]
    queryset = WebhookEndpoint.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Get webhook endpoints for the current user."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return WebhookEndpoint.objects.none()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return WebhookEndpoint.objects.none()
        
        return WebhookEndpoint.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a webhook endpoint with integration limit and feature checks."""
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if organization:
            # Check if webhooks feature is available
            FeatureService.is_feature_available(
                organization, 
                'integrations.webhooks', 
                user=user, 
                raise_exception=True
            )
            
            # Check integration limit
            max_integrations = FeatureService.get_feature_value(organization, 'integrations.max_count', default=0)
            
            if max_integrations is not None and max_integrations > 0:
                # Count all integrations for organization members
                from apps.organizations.models import OrganizationMember
                org_member_ids = OrganizationMember.objects.filter(
                    organization=organization
                ).values_list('user_id', flat=True)
                
                # Count all integrations across all types for organization
                github_count = GitHubIntegration.objects.filter(user_id__in=org_member_ids).count()
                slack_count = SlackIntegration.objects.filter(user_id__in=org_member_ids).count()
                jira_count = JiraIntegration.objects.filter(user_id__in=org_member_ids).count()
                webhook_count = WebhookEndpoint.objects.filter(user_id__in=org_member_ids).count()
                current_count = github_count + slack_count + jira_count + webhook_count
                
                if current_count >= max_integrations:
                    tier_display = organization.subscription_tier.title()
                    raise ValidationError(
                        f'Integration limit reached ({current_count}/{max_integrations} for {tier_display} tier). '
                        f'Please upgrade your subscription or remove existing integrations.'
                    )
        
        serializer.save(user=user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test webhook endpoint."""
        endpoint = self.get_object()
        service = WebhookService(endpoint)
        delivery = service.deliver('test', {'message': 'Test webhook from HishamOS'})
        
        return Response({
            'status': delivery.status,
            'response_status': delivery.response_status,
            'message': 'Webhook test completed'
        })
    
    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get webhook delivery history."""
        endpoint = self.get_object()
        deliveries = endpoint.deliveries.all()[:50]  # Last 50 deliveries
        serializer = WebhookDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for webhook deliveries (read-only)."""
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAuthenticated]
    queryset = WebhookDelivery.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Get webhook deliveries for the current user's endpoints."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return WebhookDelivery.objects.none()
        
        if not self.request.user or not self.request.user.is_authenticated:
            return WebhookDelivery.objects.none()
        
        return WebhookDelivery.objects.filter(
            endpoint__user=self.request.user
        ).select_related('endpoint')

