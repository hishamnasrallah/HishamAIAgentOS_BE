"""
GDPR compliance API endpoints.
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .gdpr import GDPRCompliance
from .models import User

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    """
    Export all user data (GDPR Article 15 - Right of access).
    
    GET /api/v1/auth/gdpr/export/
    """
    try:
        user = request.user
        data = GDPRCompliance.export_user_data(user)
        
        # Log the data export
        from apps.monitoring.audit import audit_logger
        audit_logger.log_data_access(
            resource_type='user_data',
            resource_id=str(user.id),
            user=user,
            request=request
        )
        
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error exporting user data: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to export user data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_user_data_json_file(request):
    """
    Export user data as downloadable JSON file.
    
    GET /api/v1/auth/gdpr/export-file/
    """
    try:
        user = request.user
        json_data = GDPRCompliance.export_user_data_json(user)
        
        # Log the data export
        from apps.monitoring.audit import audit_logger
        audit_logger.log_data_access(
            resource_type='user_data',
            resource_id=str(user.id),
            user=user,
            request=request
        )
        
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="user_data_{user.id}_{user.email}.json"'
        return response
    except Exception as e:
        logger.error(f"Error exporting user data file: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to export user data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_user_data(request):
    """
    Delete all user data (GDPR Article 17 - Right to erasure).
    
    POST /api/v1/auth/gdpr/delete/
    Body: {"reason": "Optional reason for deletion"}
    
    WARNING: This is a destructive operation!
    """
    try:
        user = request.user
        reason = request.data.get('reason', 'GDPR Right to be Forgotten')
        
        # Require confirmation
        confirm = request.data.get('confirm', False)
        if not confirm:
            return Response(
                {'error': 'Deletion requires explicit confirmation. Set "confirm": true in request body.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform deletion
        deletion_summary = GDPRCompliance.delete_user_data(user, reason=reason)
        
        return Response(
            {
                'message': 'User data deletion initiated',
                'summary': deletion_summary
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error deleting user data: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to delete user data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def data_retention_policy(request):
    """
    Get data retention policy information (GDPR Article 13).
    
    GET /api/v1/auth/gdpr/retention-policy/
    """
    try:
        policy = GDPRCompliance.get_data_retention_policy()
        return Response(policy, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting retention policy: {e}", exc_info=True)
        return Response(
            {'error': 'Failed to get retention policy'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

