"""
Agent API Caller Service

Allows agents to make authenticated API calls to HishamOS services.
"""

from typing import Dict, Any, Optional
import httpx
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Raised when API call fails."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AgentAPICaller:
    """
    Service for agents to call HishamOS APIs directly.
    
    Provides:
    - Authenticated API requests
    - Endpoint discovery
    - Error handling and retries
    - Response formatting for agents
    """
    
    def __init__(self, user: User):
        """
        Initialize API caller with user context.
        
        Args:
            user: User making the API call (for auth/permissions)
        """
        self.user = user
        # Get backend URL from settings
        self.base_url = settings.BACKEND_URL.rstrip('/')
        self.token = self._get_auth_token()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    def _get_auth_token(self) -> str:
        """Generate JWT token for API authentication."""
        token = AccessToken.for_user(self.user)
        return str(token)
    
    async def call(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API call.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/api/v1/projects/')
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If API call fails
        """
        try:
            # Ensure endpoint starts with /
            if not endpoint.startswith('/'):
                endpoint = f'/{endpoint}'
            
            # Ensure endpoint includes /api/v1/ prefix
            if not endpoint.startswith('/api/v1/'):
                endpoint = f'/api/v1{endpoint}'
            
            response = await self.client.request(
                method=method.upper(),
                url=endpoint,
                json=data,
                params=params
            )
            
            response.raise_for_status()
            
            # Return empty dict if no content
            if not response.content:
                return {}
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            error_msg = f"API call failed: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and 'detail' in error_data:
                    error_msg = f"{error_msg} - {error_data['detail']}"
                elif isinstance(error_data, dict) and 'message' in error_data:
                    error_msg = f"{error_msg} - {error_data['message']}"
            except:
                error_msg = f"{error_msg} - {e.response.text[:200]}"
            
            logger.error(f"API call failed: {endpoint} - {error_msg}")
            raise APIError(error_msg, status_code=e.response.status_code)
            
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(f"API request error: {endpoint} - {error_msg}")
            raise APIError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected API error: {endpoint} - {error_msg}", exc_info=True)
            raise APIError(error_msg)
    
    async def create_story(
        self,
        project_id: str,
        title: str,
        description: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a user story via API.
        
        Args:
            project_id: Project UUID
            title: Story title
            description: Story description
            **kwargs: Additional story fields
            
        Returns:
            Created story data
        """
        data = {
            'project': project_id,
            'title': title,
            'description': description,
            **kwargs
        }
        return await self.call('POST', f'/projects/{project_id}/stories/', data=data)
    
    async def update_story_status(
        self,
        story_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update story status via API.
        
        Args:
            story_id: Story UUID
            status: New status
            
        Returns:
            Updated story data
        """
        return await self.call(
            'PATCH',
            f'/stories/{story_id}/',
            data={'status': status}
        )
    
    async def create_sprint(
        self,
        project_id: str,
        name: str,
        start_date: str,
        end_date: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a sprint via API.
        
        Args:
            project_id: Project UUID
            name: Sprint name
            start_date: Sprint start date (ISO format)
            end_date: Sprint end date (ISO format)
            **kwargs: Additional sprint fields
            
        Returns:
            Created sprint data
        """
        data = {
            'project': project_id,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            **kwargs
        }
        return await self.call('POST', f'/projects/{project_id}/sprints/', data=data)
    
    async def update_sprint(
        self,
        sprint_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a sprint via API.
        
        Args:
            sprint_id: Sprint UUID
            **kwargs: Fields to update
            
        Returns:
            Updated sprint data
        """
        return await self.call('PATCH', f'/sprints/{sprint_id}/', data=kwargs)
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        Get project details via API.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Project data
        """
        return await self.call('GET', f'/projects/{project_id}/')
    
    async def list_stories(
        self,
        project_id: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List stories for a project via API.
        
        Args:
            project_id: Project UUID
            params: Query parameters (status, assigned_to, etc.)
            
        Returns:
            Stories data (paginated)
        """
        return await self.call('GET', f'/projects/{project_id}/stories/', params=params)
    
    async def list_sprints(
        self,
        project_id: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List sprints for a project via API.
        
        Args:
            project_id: Project UUID
            params: Query parameters
            
        Returns:
            Sprints data (paginated)
        """
        return await self.call('GET', f'/projects/{project_id}/sprints/', params=params)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

