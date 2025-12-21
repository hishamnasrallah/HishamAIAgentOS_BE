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
        description="Create a new user account with email and password. Automatically creates an organization and trial subscription.",
        tags=["Authentication"]
    )
    def post(self, request, *args, **kwargs):
        from rest_framework_simplejwt.tokens import RefreshToken
        from .serializers import UserSerializer
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for automatic login
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # Get organization ID from serializer if available
        organization_id = getattr(serializer, 'organization_id', None)
        if not organization_id and user.organization:
            organization_id = str(user.organization.id)
        
        response_data = {
            "user": UserSerializer(user).data,
            "access": str(access),
            "refresh": str(refresh),
            "message": "User and organization created successfully. You are now logged in."
        }
        
        # Include organization ID in response for frontend to set as current
        if organization_id:
            response_data["organization_id"] = organization_id
        
        return Response(response_data, status=status.HTTP_201_CREATED)


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
        
        # Build reset link
        from django.conf import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"
        
        # Send email with reset link
        try:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            
            subject = 'Password Reset Request - HishamOS'
            
            # Create email content
            html_message = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {user.get_full_name() or user.email},</p>
                <p>You requested to reset your password for your HishamOS account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{reset_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <p>Best regards,<br>The HishamOS Team</p>
            </body>
            </html>
            """
            
            plain_message = f"""
            Password Reset Request
            
            Hello {user.get_full_name() or user.email},
            
            You requested to reset your password for your HishamOS account.
            
            Click the link below to reset your password:
            {reset_link}
            
            This link will expire in 24 hours.
            
            If you didn't request this password reset, please ignore this email.
            
            Best regards,
            The HishamOS Team
            """
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hishamos.com')
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=from_email,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            return Response({
                "message": "Password reset instructions have been sent to your email."
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log error but don't expose it to user (security best practice)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send password reset email: {str(e)}")
            
            # In development, return the link for debugging
            if settings.DEBUG:
                return Response({
                    "message": "Password reset email failed to send. (Debug mode - link provided)",
                    "reset_link": reset_link
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "message": "Password reset instructions have been sent to your email."
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
    
    # Audit logout before processing
    try:
        from apps.monitoring.audit import audit_logger
        audit_logger.log_authentication(
            action='logout',
            user=request.user if request.user.is_authenticated else None,
            request=request,
            success=True,
        )
    except Exception as e:
        # Don't break logout if audit logging fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to audit logout: {e}", exc_info=True)
    
    # Remove user from online presence
    try:
        from apps.core.presence_views import _online_users
        user_id = str(request.user.id)
        if user_id in _online_users:
            del _online_users[user_id]
    except Exception as e:
        # Don't break logout if presence removal fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to remove user presence on logout: {e}", exc_info=True)
    
    # In JWT, logout is typically handled client-side by removing tokens
    # For additional security, you could implement token blacklisting
    
    return Response({
        "message": "Logged out successfully."
    }, status=status.HTTP_200_OK)
