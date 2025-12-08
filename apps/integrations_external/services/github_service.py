"""
GitHub integration service.
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from django.utils import timezone
from ..models import GitHubIntegration

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, integration: GitHubIntegration):
        """Initialize with a GitHub integration."""
        self.integration = integration
        self.access_token = integration.access_token
        self.headers = {
            'Authorization': f'token {self.access_token}',
            'Accept': 'application/vnd.github.v3+json',
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make a request to GitHub API."""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            return None
    
    def get_repository(self) -> Optional[Dict]:
        """Get repository information."""
        endpoint = f"/repos/{self.integration.repository_owner}/{self.integration.repository_name}"
        return self._make_request('GET', endpoint)
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[Dict]:
        """Create a GitHub issue."""
        endpoint = f"/repos/{self.integration.repository_owner}/{self.integration.repository_name}/issues"
        data = {
            'title': title,
            'body': body,
        }
        if labels:
            data['labels'] = labels
        
        result = self._make_request('POST', endpoint, json=data)
        if result:
            logger.info(f"Created GitHub issue: {result.get('number')}")
        return result
    
    def get_pull_requests(self, state: str = 'open') -> List[Dict]:
        """Get pull requests for the repository."""
        endpoint = f"/repos/{self.integration.repository_owner}/{self.integration.repository_name}/pulls"
        params = {'state': state}
        result = self._make_request('GET', endpoint, params=params)
        return result if result else []
    
    def create_webhook(self, url: str, events: List[str] = None) -> Optional[Dict]:
        """Create a webhook for the repository."""
        endpoint = f"/repos/{self.integration.repository_owner}/{self.integration.repository_name}/hooks"
        data = {
            'name': 'web',
            'active': True,
            'events': events or ['push', 'pull_request', 'issues'],
            'config': {
                'url': url,
                'content_type': 'json',
                'secret': self.integration.webhook_secret or '',
            }
        }
        return self._make_request('POST', endpoint, json=data)
    
    def sync_pull_requests(self) -> List[Dict]:
        """Sync pull requests from GitHub."""
        if not self.integration.auto_sync_prs:
            return []
        
        prs = self.get_pull_requests()
        self.integration.last_sync_at = timezone.now()
        self.integration.save(update_fields=['last_sync_at'])
        
        return prs
    
    def create_issue_from_story(self, story_title: str, story_description: str) -> Optional[Dict]:
        """Create a GitHub issue from a user story."""
        if not self.integration.auto_create_issues:
            return None
        
        return self.create_issue(
            title=story_title,
            body=story_description,
            labels=['user-story', 'hishamos']
        )
    
    def verify_connection(self) -> bool:
        """Verify the GitHub connection is working."""
        repo = self.get_repository()
        return repo is not None

