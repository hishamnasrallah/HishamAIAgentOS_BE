"""
URLs for external integrations.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GitHubIntegrationViewSet,
    SlackIntegrationViewSet,
    JiraIntegrationViewSet,
    EmailNotificationSettingsViewSet,
    WebhookEndpointViewSet,
    WebhookDeliveryViewSet
)

router = DefaultRouter()
router.register(r'github', GitHubIntegrationViewSet, basename='github-integration')
router.register(r'slack', SlackIntegrationViewSet, basename='slack-integration')
router.register(r'jira', JiraIntegrationViewSet, basename='jira-integration')
router.register(r'email', EmailNotificationSettingsViewSet, basename='email-settings')
router.register(r'webhooks', WebhookEndpointViewSet, basename='webhook-endpoint')
router.register(r'webhook-deliveries', WebhookDeliveryViewSet, basename='webhook-delivery')

app_name = 'integrations_external'

urlpatterns = [
    path('', include(router.urls)),
]

