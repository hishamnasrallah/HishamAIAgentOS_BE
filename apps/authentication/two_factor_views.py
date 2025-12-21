"""
Two-Factor Authentication API views.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from apps.organizations.services import FeatureService
from apps.core.services.roles import RoleService

from .two_factor import (
    setup_two_factor,
    enable_two_factor,
    disable_two_factor,
    verify_two_factor,
    get_backup_codes,
    verify_totp_token
)
from .two_factor_serializers import (
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
    TwoFactorEnableSerializer,
    TwoFactorDisableSerializer
)

User = get_user_model()


@extend_schema(
    summary="Setup 2FA",
    description="Generate QR code and backup codes for 2FA setup. Does not enable 2FA yet.",
    tags=["Two-Factor Authentication"],
    responses={
        200: TwoFactorSetupSerializer,
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_setup(request):
    """
    Set up 2FA for the current user.
    
    Returns QR code and backup codes. User must verify with a token before enabling.
    """
    user = request.user
    
    # Check if 2FA feature is available (typically always available, but check for consistency)
    organization = RoleService.get_user_organization(user)
    if organization:
        FeatureService.is_feature_available(
            organization, 
            'security.2fa', 
            user=user, 
            raise_exception=True
        )
    
    if user.two_factor_enabled:
        return Response(
            {"error": "2FA is already enabled. Disable it first to set up again."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate secret, QR code, and backup codes
    secret, qr_code, backup_codes = setup_two_factor(user)
    
    # Store secret temporarily (we'll save it after verification)
    # For now, we'll return it and the client will send it back with verification
    return Response({
        "secret": secret,  # Client needs this for verification
        "qr_code": qr_code,
        "backup_codes": backup_codes,
        "message": "Scan QR code with authenticator app, then verify with a token to enable 2FA."
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Verify 2FA token",
    description="Verify a TOTP token during setup to enable 2FA",
    tags=["Two-Factor Authentication"],
    request=TwoFactorVerifySerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_verify(request):
    """
    Verify a TOTP token during 2FA setup.
    
    This is used to verify the token before enabling 2FA.
    """
    serializer = TwoFactorVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    secret = serializer.validated_data['secret']
    token = serializer.validated_data['token']
    backup_codes = serializer.validated_data.get('backup_codes', [])
    
    # Verify the token
    if not verify_totp_token(secret, token):
        return Response(
            {"error": "Invalid token. Please try again."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Token is valid - enable 2FA
    enable_two_factor(user, secret, backup_codes)
    
    return Response({
        "message": "2FA enabled successfully.",
        "backup_codes": backup_codes
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Enable 2FA",
    description="Enable 2FA with verified secret and backup codes",
    tags=["Two-Factor Authentication"],
    request=TwoFactorEnableSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_enable(request):
    """
    Enable 2FA for the current user.
    
    This endpoint combines setup and verification in one step.
    """
    serializer = TwoFactorEnableSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    
    if user.two_factor_enabled:
        return Response(
            {"error": "2FA is already enabled."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    secret = serializer.validated_data['secret']
    token = serializer.validated_data['token']
    backup_codes = serializer.validated_data.get('backup_codes', [])
    
    # Verify token before enabling
    if not verify_totp_token(secret, token):
        return Response(
            {"error": "Invalid token. Please verify with your authenticator app."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Enable 2FA
    enable_two_factor(user, secret, backup_codes)
    
    return Response({
        "message": "2FA enabled successfully.",
        "backup_codes": backup_codes
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Disable 2FA",
    description="Disable 2FA for the current user",
    tags=["Two-Factor Authentication"],
    request=TwoFactorDisableSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def two_factor_disable(request):
    """
    Disable 2FA for the current user.
    
    Requires password confirmation for security.
    """
    serializer = TwoFactorDisableSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    
    if not user.two_factor_enabled:
        return Response(
            {"error": "2FA is not enabled."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify password
    password = serializer.validated_data['password']
    if not user.check_password(password):
        return Response(
            {"error": "Invalid password."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Disable 2FA
    disable_two_factor(user)
    
    return Response({
        "message": "2FA disabled successfully."
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get backup codes",
    description="Get remaining backup codes for 2FA",
    tags=["Two-Factor Authentication"],
    responses={
        200: {"type": "object", "properties": {"backup_codes": {"type": "array", "items": {"type": "string"}}}},
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def two_factor_backup_codes(request):
    """
    Get remaining backup codes for the current user.
    """
    user = request.user
    
    if not user.two_factor_enabled:
        return Response(
            {"error": "2FA is not enabled."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    backup_codes = get_backup_codes(user)
    
    return Response({
        "backup_codes": backup_codes,
        "count": len(backup_codes)
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Verify 2FA during login",
    description="Verify 2FA token during login process",
    tags=["Two-Factor Authentication"],
    request={"type": "object", "properties": {"token": {"type": "string"}}},
    responses={
        200: {"type": "object", "properties": {"valid": {"type": "boolean"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}}
    }
)
@api_view(['POST'])
@permission_classes([])  # No authentication required - this is for login
def two_factor_verify_login(request):
    """
    Verify 2FA token during login.
    
    This is called after initial login when user has 2FA enabled.
    The user_id should be in the session or request data from the login step.
    """
    token = request.data.get('token')
    user_id = request.data.get('user_id')
    
    if not token or not user_id:
        return Response(
            {"error": "Token and user_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid user."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.two_factor_enabled:
        return Response(
            {"error": "2FA is not enabled for this user."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify token
    if verify_two_factor(user, token):
        return Response({
            "valid": True,
            "message": "2FA token verified successfully."
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "Invalid 2FA token."},
            status=status.HTTP_400_BAD_REQUEST
        )

