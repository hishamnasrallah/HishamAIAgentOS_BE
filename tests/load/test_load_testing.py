"""
Load testing utilities and tests.
"""
import pytest
import time
import concurrent.futures
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class LoadTestingTests:
    """Load testing for API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create authenticated API client."""
        client = APIClient()
        user = User.objects.create_user(
            email='loadtest@example.com',
            password='testpass123'
        )
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client, user
    
    def test_concurrent_users_100(self, api_client):
        """Test handling 100 concurrent users."""
        client, user = api_client
        
        def make_request():
            response = client.get('/api/v1/monitoring/health/')
            return response.status_code
        
        start_time = time.time()
        
        # Simulate 100 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = time.time() - start_time
        
        # All requests should complete
        assert len(results) == 100, "Not all requests completed"
        
        # Most requests should succeed (allow some failures under load)
        success_rate = sum(1 for r in results if r in [200, 401, 403]) / len(results)
        assert success_rate > 0.9, f"Success rate ({success_rate:.2%}) too low"
        
        # Should complete within reasonable time
        assert elapsed < 10, f"Load test took too long ({elapsed:.2f}s)"
    
    def test_sustained_load(self, api_client):
        """Test sustained load over time."""
        client, user = api_client
        
        def make_request():
            response = client.get('/api/v1/monitoring/health/')
            return response.status_code, time.time()
        
        # Run for 30 seconds
        end_time = time.time() + 30
        request_count = 0
        successful_requests = 0
        
        while time.time() < end_time:
            status, _ = make_request()
            request_count += 1
            if status in [200, 401, 403]:
                successful_requests += 1
            time.sleep(0.1)  # 10 requests per second
        
        # Should handle sustained load
        success_rate = successful_requests / request_count if request_count > 0 else 0
        assert success_rate > 0.95, f"Sustained load success rate ({success_rate:.2%}) too low"
        assert request_count > 100, "Not enough requests made during sustained load test"

