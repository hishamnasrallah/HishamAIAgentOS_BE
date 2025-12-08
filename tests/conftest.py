"""
Pytest configuration and fixtures for HishamOS tests.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123',
        role='developer'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin test user."""
    return User.objects.create_user(
        email='admin@example.com',
        username='admin',
        password='adminpass123',
        role='admin'
    )


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create an authenticated admin API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def django_client():
    """Create a Django test client."""
    return Client()


