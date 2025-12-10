"""
Jira Integration Service.
Handles integration with Jira for syncing issues and work items.
"""

import requests
from typing import Dict, List, Optional
from django.conf import settings
import base64


class JiraIntegrationService:
    """Service for Jira integration."""
    
    @staticmethod
    def get_headers(email: str, api_token: str) -> Dict[str, str]:
        """Get headers for Jira API requests."""
        credentials = f"{email}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    @staticmethod
    def verify_connection(base_url: str, email: str, api_token: str) -> Dict:
        """
        Verify Jira connection.
        
        Returns:
            Dict with connection status
        """
        try:
            url = f"{base_url}/rest/api/3/myself"
            response = requests.get(
                url,
                headers=JiraIntegrationService.get_headers(email, api_token),
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user': {
                        'account_id': user_data.get('accountId'),
                        'display_name': user_data.get('displayName'),
                        'email': user_data.get('emailAddress'),
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Jira API error: {response.status_code}',
                    'message': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_issues(base_url: str, email: str, api_token: str, project_key: str, jql: str = None, limit: int = 50) -> List[Dict]:
        """
        Get issues from Jira project.
        
        Args:
            base_url: Jira base URL
            email: Jira email
            api_token: Jira API token
            project_key: Jira project key
            jql: JQL query string (optional)
            limit: Maximum number of issues to return
        
        Returns:
            List of issue dictionaries
        """
        try:
            if jql:
                url = f"{base_url}/rest/api/3/search"
                params = {
                    'jql': jql,
                    'maxResults': min(limit, 100),
                    'fields': 'summary,description,status,priority,assignee,created,updated'
                }
            else:
                url = f"{base_url}/rest/api/3/search"
                params = {
                    'jql': f'project = {project_key}',
                    'maxResults': min(limit, 100),
                    'fields': 'summary,description,status,priority,assignee,created,updated'
                }
            
            response = requests.get(
                url,
                headers=JiraIntegrationService.get_headers(email, api_token),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                
                return [{
                    'key': issue.get('key'),
                    'id': issue.get('id'),
                    'summary': issue.get('fields', {}).get('summary'),
                    'description': issue.get('fields', {}).get('description'),
                    'status': issue.get('fields', {}).get('status', {}).get('name'),
                    'priority': issue.get('fields', {}).get('priority', {}).get('name'),
                    'assignee': issue.get('fields', {}).get('assignee', {}).get('displayName') if issue.get('fields', {}).get('assignee') else None,
                    'created': issue.get('fields', {}).get('created'),
                    'updated': issue.get('fields', {}).get('updated'),
                    'url': f"{base_url}/browse/{issue.get('key')}",
                } for issue in issues]
            else:
                return []
        except Exception as e:
            return []
    
    @staticmethod
    def create_issue(base_url: str, email: str, api_token: str, project_key: str, issue_type: str, summary: str, description: str = '') -> Dict:
        """
        Create an issue in Jira.
        
        Returns:
            Dict with created issue info
        """
        try:
            url = f"{base_url}/rest/api/3/issue"
            data = {
                'fields': {
                    'project': {
                        'key': project_key
                    },
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
                                        'text': description
                                    }
                                ]
                            }
                        ]
                    },
                    'issuetype': {
                        'name': issue_type
                    }
                }
            }
            
            response = requests.post(
                url,
                headers=JiraIntegrationService.get_headers(email, api_token),
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                issue = response.json()
                return {
                    'success': True,
                    'issue': {
                        'key': issue.get('key'),
                        'id': issue.get('id'),
                        'url': f"{base_url}/browse/{issue.get('key')}",
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Jira API error: {response.status_code}',
                    'message': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def update_issue(base_url: str, email: str, api_token: str, issue_key: str, fields: Dict) -> Dict:
        """
        Update an issue in Jira.
        
        Returns:
            Dict with update result
        """
        try:
            url = f"{base_url}/rest/api/3/issue/{issue_key}"
            data = {
                'fields': fields
            }
            
            response = requests.put(
                url,
                headers=JiraIntegrationService.get_headers(email, api_token),
                json=data,
                timeout=10
            )
            
            if response.status_code == 204:
                return {
                    'success': True,
                    'message': 'Issue updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': f'Jira API error: {response.status_code}',
                    'message': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

