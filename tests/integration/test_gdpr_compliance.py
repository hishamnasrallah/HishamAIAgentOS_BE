"""
Integration tests for GDPR compliance features.
"""
import pytest
import json
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.gdpr import GDPRCompliance
from apps.monitoring.models import AuditLog

User = get_user_model()


@pytest.mark.django_db
class GDPRComplianceTests:
    """Integration tests for GDPR compliance."""
    
    @pytest.fixture
    def user_and_client(self):
        """Create user and authenticated client."""
        user = User.objects.create_user(
            email='gdpr@example.com',
            password='testpass123',
            first_name='GDPR',
            last_name='Test'
        )
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return user, client
    
    def test_export_user_data(self, user_and_client):
        """Test GDPR data export."""
        user, client = user_and_client
        
        # Export data
        data = GDPRCompliance.export_user_data(user)
        
        # Verify structure
        assert 'user_id' in data
        assert 'email' in data
        assert 'profile' in data
        assert 'api_keys' in data
        assert 'audit_logs' in data
        
        # Verify user data
        assert data['email'] == user.email
        assert data['user_id'] == str(user.id)
    
    def test_export_user_data_api(self, user_and_client):
        """Test GDPR data export API endpoint."""
        user, client = user_and_client
        
        response = client.get('/api/v1/auth/gdpr/export/')
        
        assert response.status_code == 200
        data = response.json()
        assert 'user_id' in data
        assert 'email' in data
    
    def test_export_user_data_file(self, user_and_client):
        """Test GDPR data export as file."""
        user, client = user_and_client
        
        response = client.get('/api/v1/auth/gdpr/export-file/')
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        assert 'attachment' in response['Content-Disposition']
        
        # Verify JSON is valid
        data = json.loads(response.content)
        assert 'user_id' in data
    
    def test_data_retention_policy(self, user_and_client):
        """Test data retention policy endpoint."""
        user, client = user_and_client
        
        response = client.get('/api/v1/auth/gdpr/retention-policy/')
        
        assert response.status_code == 200
        data = response.json()
        assert 'audit_logs' in data
        assert 'user_data' in data
    
    def test_delete_user_data_requires_confirmation(self, user_and_client):
        """Test that data deletion requires confirmation."""
        user, client = user_and_client
        
        # Try without confirmation
        response = client.post('/api/v1/auth/gdpr/delete/', {})
        
        assert response.status_code == 400
        assert 'confirmation' in response.json()['error'].lower()
    
    def test_delete_user_data_with_confirmation(self, user_and_client):
        """Test data deletion with confirmation."""
        user, client = user_and_client
        
        # Delete with confirmation
        response = client.post('/api/v1/auth/gdpr/delete/', {
            'confirm': True,
            'reason': 'Test deletion'
        })
        
        assert response.status_code == 200
        data = response.json()
        assert 'summary' in data
        assert 'deletion_date' in data['summary']
        
        # Verify user is anonymized
        user.refresh_from_db()
        assert 'deleted' in user.email.lower()
        assert not user.is_active
    
    def test_audit_log_created_on_export(self, user_and_client):
        """Test that audit log is created on data export."""
        user, client = user_and_client
        
        initial_count = AuditLog.objects.filter(user=user).count()
        
        # Export data
        client.get('/api/v1/auth/gdpr/export/')
        
        # Verify audit log created
        final_count = AuditLog.objects.filter(user=user).count()
        assert final_count > initial_count
        
        # Verify log entry
        log = AuditLog.objects.filter(user=user, action='read').first()
        assert log is not None
        assert 'user_data' in log.resource_type

