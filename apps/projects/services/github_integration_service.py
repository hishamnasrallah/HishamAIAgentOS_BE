"""
GitHub Integration Service.
Handles integration with GitHub repositories for linking issues, commits, and PRs.
"""

import requests
from typing import Dict, List, Optional
from django.conf import settings


class GitHubIntegrationService:
    """Service for GitHub integration."""
    
    BASE_URL = "https://api.github.com"
    
    @staticmethod
    def get_headers(token: str) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        return {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ProjectManagementApp/1.0'
        }
    
    @staticmethod
    def verify_connection(token: str, repo_owner: str, repo_name: str) -> Dict:
        """
        Verify GitHub connection and repository access.
        
        Returns:
            Dict with connection status
        """
        try:
            url = f"{GitHubIntegrationService.BASE_URL}/repos/{repo_owner}/{repo_name}"
            response = requests.get(
                url,
                headers=GitHubIntegrationService.get_headers(token),
                timeout=10
            )
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'success': True,
                    'repository': {
                        'name': repo_data.get('name'),
                        'full_name': repo_data.get('full_name'),
                        'description': repo_data.get('description'),
                        'url': repo_data.get('html_url'),
                        'private': repo_data.get('private'),
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'message': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_issues(token: str, repo_owner: str, repo_name: str, state: str = 'open', limit: int = 50) -> List[Dict]:
        """
        Get issues from GitHub repository.
        
        Args:
            token: GitHub access token
            repo_owner: Repository owner
            repo_name: Repository name
            state: Issue state (open, closed, all)
            limit: Maximum number of issues to return
        
        Returns:
            List of issue dictionaries
        """
        try:
            url = f"{GitHubIntegrationService.BASE_URL}/repos/{repo_owner}/{repo_name}/issues"
            params = {
                'state': state,
                'per_page': min(limit, 100),
                'page': 1
            }
            
            response = requests.get(
                url,
                headers=GitHubIntegrationService.get_headers(token),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                issues = response.json()
                # Filter out pull requests (they appear as issues in GitHub API)
                issues = [issue for issue in issues if 'pull_request' not in issue]
                
                return [{
                    'id': issue.get('id'),
                    'number': issue.get('number'),
                    'title': issue.get('title'),
                    'body': issue.get('body'),
                    'state': issue.get('state'),
                    'url': issue.get('html_url'),
                    'created_at': issue.get('created_at'),
                    'updated_at': issue.get('updated_at'),
                    'labels': [label.get('name') for label in issue.get('labels', [])],
                    'assignee': issue.get('assignee', {}).get('login') if issue.get('assignee') else None,
                } for issue in issues[:limit]]
            else:
                return []
        except Exception as e:
            return []
    
    @staticmethod
    def create_issue(token: str, repo_owner: str, repo_name: str, title: str, body: str = '', labels: List[str] = None) -> Dict:
        """
        Create an issue in GitHub repository.
        
        Returns:
            Dict with created issue info
        """
        try:
            url = f"{GitHubIntegrationService.BASE_URL}/repos/{repo_owner}/{repo_name}/issues"
            data = {
                'title': title,
                'body': body,
            }
            if labels:
                data['labels'] = labels
            
            response = requests.post(
                url,
                headers=GitHubIntegrationService.get_headers(token),
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                issue = response.json()
                return {
                    'success': True,
                    'issue': {
                        'id': issue.get('id'),
                        'number': issue.get('number'),
                        'title': issue.get('title'),
                        'url': issue.get('html_url'),
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'GitHub API error: {response.status_code}',
                    'message': response.json().get('message', 'Unknown error')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_commits(token: str, repo_owner: str, repo_name: str, branch: str = 'main', limit: int = 50) -> List[Dict]:
        """
        Get commits from GitHub repository.
        
        Returns:
            List of commit dictionaries
        """
        try:
            url = f"{GitHubIntegrationService.BASE_URL}/repos/{repo_owner}/{repo_name}/commits"
            params = {
                'sha': branch,
                'per_page': min(limit, 100),
                'page': 1
            }
            
            response = requests.get(
                url,
                headers=GitHubIntegrationService.get_headers(token),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                commits = response.json()
                return [{
                    'sha': commit.get('sha'),
                    'message': commit.get('commit', {}).get('message'),
                    'author': commit.get('commit', {}).get('author', {}).get('name'),
                    'date': commit.get('commit', {}).get('author', {}).get('date'),
                    'url': commit.get('html_url'),
                } for commit in commits[:limit]]
            else:
                return []
        except Exception as e:
            return []
    
    @staticmethod
    def get_pull_requests(token: str, repo_owner: str, repo_name: str, state: str = 'open', limit: int = 50) -> List[Dict]:
        """
        Get pull requests from GitHub repository.
        
        Returns:
            List of PR dictionaries
        """
        try:
            url = f"{GitHubIntegrationService.BASE_URL}/repos/{repo_owner}/{repo_name}/pulls"
            params = {
                'state': state,
                'per_page': min(limit, 100),
                'page': 1
            }
            
            response = requests.get(
                url,
                headers=GitHubIntegrationService.get_headers(token),
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                prs = response.json()
                return [{
                    'id': pr.get('id'),
                    'number': pr.get('number'),
                    'title': pr.get('title'),
                    'body': pr.get('body'),
                    'state': pr.get('state'),
                    'url': pr.get('html_url'),
                    'created_at': pr.get('created_at'),
                    'merged_at': pr.get('merged_at'),
                    'author': pr.get('user', {}).get('login'),
                } for pr in prs[:limit]]
            else:
                return []
        except Exception as e:
            return []

