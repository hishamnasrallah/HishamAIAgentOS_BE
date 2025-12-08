"""
Views for secrets management API.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .secrets_manager import get_secrets_manager


@extend_schema(
    summary="Store a secret",
    description="Store a secret in HashiCorp Vault or local encrypted storage",
    tags=["Secrets"]
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def store_secret(request):
    """Store a secret."""
    path = request.data.get('path')
    secret = request.data.get('secret', {})
    metadata = request.data.get('metadata')
    
    if not path:
        return Response(
            {'error': 'path is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    manager = get_secrets_manager()
    success = manager.store_secret(path, secret, metadata)
    
    if success:
        return Response({'message': f'Secret stored: {path}'}, status=status.HTTP_201_CREATED)
    else:
        return Response(
            {'error': 'Failed to store secret'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Get a secret",
    description="Retrieve a secret from HashiCorp Vault or local encrypted storage",
    tags=["Secrets"]
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_secret(request, path):
    """Get a secret."""
    manager = get_secrets_manager()
    secret = manager.get_secret(path)
    
    if secret:
        return Response({'path': path, 'secret': secret})
    else:
        return Response(
            {'error': 'Secret not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    summary="Delete a secret",
    description="Delete a secret from HashiCorp Vault or local encrypted storage",
    tags=["Secrets"]
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_secret(request, path):
    """Delete a secret."""
    manager = get_secrets_manager()
    success = manager.delete_secret(path)
    
    if success:
        return Response({'message': f'Secret deleted: {path}'})
    else:
        return Response(
            {'error': 'Failed to delete secret'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Rotate a secret",
    description="Rotate (update) a secret",
    tags=["Secrets"]
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def rotate_secret(request, path):
    """Rotate a secret."""
    new_secret = request.data.get('secret', {})
    
    if not new_secret:
        return Response(
            {'error': 'secret is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    manager = get_secrets_manager()
    success = manager.rotate_secret(path, new_secret)
    
    if success:
        return Response({'message': f'Secret rotated: {path}'})
    else:
        return Response(
            {'error': 'Failed to rotate secret'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="List secrets",
    description="List all secrets with given prefix",
    tags=["Secrets"]
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_secrets(request):
    """List secrets."""
    prefix = request.query_params.get('prefix', '')
    
    manager = get_secrets_manager()
    secrets = manager.list_secrets(prefix)
    
    return Response({'secrets': secrets, 'count': len(secrets)})

