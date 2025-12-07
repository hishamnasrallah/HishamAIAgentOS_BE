"""
Authentication views for login, registration, password reset, etc.
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from drf_spectacular.utils import extend_schema

from .auth_serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer
)
from .serializers import UserSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with extra user data."""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @extend_schema(
        summary="Register new user",
        description="Create a new user account with email and password",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "user": UserSerializer(user).data,
            "message": "User created successfully. Please login to get access tokens."
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information",
    tags=["Authentication"],
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer}
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile."""
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = UserProfileSerializer(request.user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(
    summary="Change password",
    description="Change the authenticated user's password",
    tags=["Authentication"],
    request=ChangePasswordSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"old_password": {"type": "string"}}}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password."""
    
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    
    # Check old password
    if not user.check_password(serializer.validated_data['old_password']):
        return Response(
            {"old_password": "Wrong password."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    return Response({
        "message": "Password updated successfully."
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Request password reset",
    description="Request a password reset email with reset token",
    tags=["Authentication"],
    request=PasswordResetRequestSerializer,
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset."""
    
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # TODO: Send email with reset link
        # For now, just return the token (in production, send via email)
        reset_link = f"http://localhost:3000/reset-password?uid={uid}&token={token}"
        
        return Response({
            "message": "Password reset instructions sent to email.",
            "reset_link": reset_link  # Remove this in production
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # Don't reveal if user exists or not
        return Response({
            "message": "If an account with that email exists, password reset instructions have been sent."
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Confirm password reset",
    description="Reset password using the token received via email",
    tags=["Authentication"],
    request=PasswordResetConfirmSerializer,
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with token."""
    
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # In a real implementation, uid would come from URL parameter
    # For simplicity, we'll include it in the request data
    uid = request.data.get('uid')
    token = serializer.validated_data['token']
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        
        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                "message": "Password has been reset successfully."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Invalid or expired token."
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            "error": "Invalid reset link."
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Logout",
    description="Logout user (client should discard tokens)",
    tags=["Authentication"],
    request=None,
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user."""
    
    # In JWT, logout is typically handled client-side by removing tokens
    # For additional security, you could implement token blacklisting
    
    return Response({
        "message": "Logged out successfully."
    }, status=status.HTTP_200_OK)
