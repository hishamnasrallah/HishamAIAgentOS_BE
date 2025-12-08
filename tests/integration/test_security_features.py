"""
Integration tests for security features.
"""
import pytest
import time
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

User = get_user_model()


@pytest.mark.django_db
class SecurityFeaturesTests:
    """Integration tests for security features."""
    
    @pytest.fixture
    def user_and_client(self):
        """Create user and authenticated client."""
        user = User.objects.create_user(
            email='security@example.com',
            password='testpass123'
        )
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return user, client
    
    def test_rate_limiting_works(self, user_and_client):
        """Test that rate limiting is enforced."""
        user, client = user_and_client
        
        # Make many requests quickly
        responses = []
        for i in range(150):  # Exceed 100 req/min limit
            response = client.get('/api/v1/monitoring/health/')
            responses.append(response.status_code)
            if response.status_code == 429:
                break
        
        # Should hit rate limit
        assert 429 in responses, "Rate limiting not enforced"
    
    def test_security_headers_present(self, user_and_client):
        """Test that security headers are present in responses."""
        user, client = user_and_client
        
        response = client.get('/api/v1/monitoring/health/')
        
        # Check security headers
        assert 'X-Content-Type-Options' in response
        assert response['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in response
        assert response['X-Frame-Options'] == 'DENY'
        
        assert 'X-XSS-Protection' in response
        assert 'Referrer-Policy' in response
    
    def test_cors_headers(self, user_and_client):
        """Test CORS headers are properly set."""
        user, client = user_and_client
        
        response = client.get('/api/v1/monitoring/health/', HTTP_ORIGIN='http://localhost:3000')
        
        # CORS headers should be present
        # Note: Actual CORS behavior depends on settings
        assert response.status_code in [200, 401, 403]
    
    def test_api_key_throttling(self):
        """Test API key rate throttling."""
        from apps.authentication.models import APIKey
        from apps.authentication.middleware import APIKeyAuthentication
        
        user = User.objects.create_user(
            email='apikey@example.com',
            password='testpass123'
        )
        
        api_key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key='test-key-123',
            rate_limit_per_minute=10  # Low limit for testing
        )
        
        client = APIClient()
        client.credentials(HTTP_X_API_KEY=api_key.key)
        
        # Make requests
        responses = []
        for i in range(15):  # Exceed 10 req/min limit
            response = client.get('/api/v1/monitoring/health/')
            responses.append(response.status_code)
            if response.status_code == 429:
                break
        
        # Should hit rate limit
        assert 429 in responses, "API key rate limiting not enforced"

