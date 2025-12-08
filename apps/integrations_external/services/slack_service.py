"""
Slack integration service.
"""
import requests
import logging
from typing import Dict, Optional, List
from django.utils import timezone
from ..models import SlackIntegration

logger = logging.getLogger(__name__)


class SlackService:
    """Service for interacting with Slack API."""
    
    BASE_URL = "https://slack.com/api"
    
    def __init__(self, integration: SlackIntegration):
        """Initialize with a Slack integration."""
        self.integration = integration
        self.bot_token = integration.bot_token
        self.headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make a request to Slack API."""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('ok'):
                logger.error(f"Slack API error: {data.get('error')}")
                return None
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Slack API request failed: {e}")
            return None
    
    def send_message(self, text: str, blocks: List[Dict] = None) -> bool:
        """Send a message to the configured Slack channel."""
        endpoint = "/chat.postMessage"
        data = {
            'channel': self.integration.channel_id,
            'text': text,
        }
        if blocks:
            data['blocks'] = blocks
        
        result = self._make_request('POST', endpoint, json=data)
        
        if result:
            self.integration.last_used_at = timezone.now()
            self.integration.save(update_fields=['last_used_at'])
            return True
        
        return False
    
    def send_workflow_notification(self, workflow_name: str, status: str, execution_id: str) -> bool:
        """Send a workflow completion notification."""
        if not self.integration.notify_workflow_completion:
            return False
        
        emoji = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
        text = f"{emoji} Workflow *{workflow_name}* {status}\nExecution ID: `{execution_id}`"
        
        return self.send_message(text)
    
    def send_command_notification(self, command_name: str, status: str, result_summary: str = None) -> bool:
        """Send a command execution notification."""
        if not self.integration.notify_command_execution:
            return False
        
        emoji = "✅" if status == "success" else "❌"
        text = f"{emoji} Command *{command_name}* executed: {status}"
        if result_summary:
            text += f"\n{result_summary}"
        
        return self.send_message(text)
    
    def send_system_alert(self, alert_type: str, message: str) -> bool:
        """Send a system alert."""
        if not self.integration.notify_system_alerts:
            return False
        
        text = f"🚨 *System Alert: {alert_type}*\n{message}"
        return self.send_message(text)
    
    def send_project_update(self, project_name: str, update_message: str) -> bool:
        """Send a project update notification."""
        if not self.integration.notify_project_updates:
            return False
        
        text = f"📋 *Project Update: {project_name}*\n{update_message}"
        return self.send_message(text)
    
    def verify_connection(self) -> bool:
        """Verify the Slack connection is working."""
        endpoint = "/auth.test"
        result = self._make_request('POST', endpoint)
        return result is not None and result.get('ok', False)

