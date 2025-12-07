"""
URL configuration for authentication app - updated with auth endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, APIKeyViewSet
from .auth_views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    user_profile,
    change_password,
    password_reset_request,
    password_reset_confirm,
    logout
)
from .two_factor_views import (
    two_factor_setup,
    two_factor_verify,
    two_factor_enable,
    two_factor_disable,
    two_factor_backup_codes,
    two_factor_verify_login
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'api-keys', APIKeyViewSet, basename='apikey')

urlpatterns = [
    # JWT Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('logout/', logout, name='logout'),
    
    # User Profile
    path('profile/', user_profile, name='user_profile'),
    path('me/', user_profile, name='user_me'),  # Alias for frontend compatibility
    path('change-password/', change_password, name='change_password'),
    
    # Password Reset
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
    
    # Two-Factor Authentication
    path('2fa/setup/', two_factor_setup, name='two_factor_setup'),
    path('2fa/verify/', two_factor_verify, name='two_factor_verify'),
    path('2fa/enable/', two_factor_enable, name='two_factor_enable'),
    path('2fa/disable/', two_factor_disable, name='two_factor_disable'),
    path('2fa/backup-codes/', two_factor_backup_codes, name='two_factor_backup_codes'),
    path('2fa/verify-login/', two_factor_verify_login, name='two_factor_verify_login'),
    
    # User and APIKey management
    path('', include(router.urls)),
]
