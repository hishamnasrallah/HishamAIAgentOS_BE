"""
Services for external integrations.
"""
from .github_service import GitHubService
from .slack_service import SlackService
from .email_service import EmailService
from .webhook_service import WebhookService

__all__ = [
    'GitHubService',
    'SlackService',
    'EmailService',
    'WebhookService',
]

