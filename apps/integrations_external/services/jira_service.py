"""
Jira integration service.
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from ..models import JiraIntegration

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with Jira API."""
    
    def __init__(self, integration: JiraIntegration):
        """Initialize with a Jira integration."""
        self.integration = integration
        self.base_url = integration.jira_url.rstrip('/')
        self.username = integration.username
        self.api_token = integration.api_token
        self.project_key = integration.project_key
        
        # Use HTTP Basic Auth with API token
        self.auth = HTTPBasicAuth(self.username, self.api_token)
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make a request to Jira API."""
        url = f"{self.base_url}/rest/api/3{endpoint}"
        
        try:
            response = requests.request(
                method,
                url,
                auth=self.auth,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Jira API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Jira API error response: {e.response.text}")
            return None
    
    def verify_connection(self) -> bool:
        """Verify the Jira connection is working."""
        try:
            result = self._make_request('GET', '/myself')
            return result is not None and 'accountId' in result
        except Exception as e:
            logger.error(f"Jira connection verification failed: {e}")
            return False
    
    def get_project(self) -> Optional[Dict]:
        """Get Jira project information."""
        endpoint = f"/project/{self.project_key}"
        return self._make_request('GET', endpoint)
    
    def create_issue(self, summary: str, description: str = '', issue_type: str = None, priority: str = None) -> Optional[Dict]:
        """Create a Jira issue."""
        issue_type = issue_type or self.integration.issue_type
        
        # Map priority if provided
        priority_id = None
        if priority:
            priority_mapping = self.integration.priority_mapping or {}
            priority_id = priority_mapping.get(priority)
        
        data = {
            'fields': {
                'project': {'key': self.project_key},
                'summary': summary,
                'description': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'paragraph',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': description or ''
                                }
                            ]
                        }
                    ]
                },
                'issuetype': {'name': issue_type}
            }
        }
        
        if priority_id:
            data['fields']['priority'] = {'id': priority_id}
        
        result = self._make_request('POST', '/issue', json=data)
        if result:
            logger.info(f"Created Jira issue: {result.get('key')}")
        return result
    
    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """Get a Jira issue by key."""
        endpoint = f"/issue/{issue_key}"
        return self._make_request('GET', endpoint)
    
    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Optional[Dict]:
        """Update a Jira issue."""
        endpoint = f"/issue/{issue_key}"
        data = {'fields': fields}
        return self._make_request('PUT', endpoint, json=data)
    
    def add_comment(self, issue_key: str, comment: str) -> Optional[Dict]:
        """Add a comment to a Jira issue."""
        endpoint = f"/issue/{issue_key}/comment"
        data = {
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [
                            {
                                'type': 'text',
                                'text': comment
                            }
                        ]
                    }
                ]
            }
        }
        return self._make_request('POST', endpoint, json=data)
    
    def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """Transition a Jira issue to a different status."""
        endpoint = f"/issue/{issue_key}/transitions"
        data = {'transition': {'id': transition_id}}
        result = self._make_request('POST', endpoint, json=data)
        return result is not None
    
    def get_transitions(self, issue_key: str) -> List[Dict]:
        """Get available transitions for an issue."""
        endpoint = f"/issue/{issue_key}/transitions"
        result = self._make_request('GET', endpoint)
        return result.get('transitions', []) if result else []
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search for issues using JQL."""
        endpoint = "/search"
        params = {
            'jql': jql,
            'maxResults': max_results
        }
        result = self._make_request('GET', endpoint, params=params)
        return result.get('issues', []) if result else []
    
    def create_issue_from_story(self, story_title: str, story_description: str, priority: str = None) -> Optional[Dict]:
        """Create a Jira issue from a user story."""
        if not self.integration.auto_create_issues:
            return None
        
        return self.create_issue(
            summary=story_title,
            description=story_description,
            priority=priority
        )
    
    def sync_issue_status(self, issue_key: str, target_status: str) -> bool:
        """Sync issue status by finding and applying the appropriate transition."""
        transitions = self.get_transitions(issue_key)
        
        # Find transition that matches target status
        for transition in transitions:
            if transition.get('to', {}).get('name', '').lower() == target_status.lower():
                return self.transition_issue(issue_key, transition['id'])
        
        logger.warning(f"No transition found for status: {target_status}")
        return False

