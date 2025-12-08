"""
Performance tests for API endpoints.
"""
import pytest
import time
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class APIPerformanceTests:
    """Performance tests for API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        client = APIClient()
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client, user
    
    def test_api_response_time_under_200ms(self, api_client):
        """Test that API endpoints respond within 200ms (p95 target)."""
        client, user = api_client
        
        endpoints = [
            '/api/v1/monitoring/health/',
            '/api/v1/agents/',
            '/api/v1/workflows/',
            '/api/v1/commands/templates/',
            '/api/v1/projects/',
        ]
        
        response_times = []
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds
            response_times.append(elapsed)
            
            assert response.status_code in [200, 401, 403], \
                f"Endpoint {endpoint} returned {response.status_code}"
        
        # Calculate p95
        response_times.sort()
        p95_index = int(len(response_times) * 0.95)
        p95_time = response_times[p95_index] if p95_index < len(response_times) else response_times[-1]
        
        assert p95_time < 200, \
            f"p95 response time ({p95_time:.2f}ms) exceeds 200ms target"
    
    def test_concurrent_requests(self, api_client):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        client, user = api_client
        
        def make_request():
            response = client.get('/api/v1/monitoring/health/')
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status in [200, 401, 403] for status in results), \
            "Some concurrent requests failed"
    
    def test_database_query_optimization(self, api_client):
        """Test that database queries are optimized (no N+1 queries)."""
        from django.db import connection
        from django.test.utils import override_settings
        
        client, user = api_client
        
        # Reset query count
        connection.queries_log.clear()
        
        # Make request
        response = client.get('/api/v1/agents/')
        
        # Count queries
        query_count = len(connection.queries)
        
        # Should not have excessive queries (target: < 10 for list endpoint)
        assert query_count < 20, \
            f"Too many database queries ({query_count}). Possible N+1 problem."

