"""
Views for API documentation generation.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.http import HttpResponse, JsonResponse
from .api_documentation import (
    get_postman_generator, get_python_sdk_generator, get_js_sdk_generator
)
import json
import os


@extend_schema(
    summary="Export Postman collection",
    description="Generate and export Postman collection from OpenAPI schema",
    tags=["API Documentation"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_postman_collection(request):
    """Export Postman collection."""
    base_url = request.query_params.get('base_url', 'http://localhost:8000')
    collection_name = request.query_params.get('name', 'HishamOS API')
    
    generator = get_postman_generator()
    collection = generator.generate_collection(base_url, collection_name)
    
    response = JsonResponse(collection, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = 'attachment; filename="hishamos-api.postman_collection.json"'
    response['Content-Type'] = 'application/json'
    
    return response


@extend_schema(
    summary="Generate Python SDK",
    description="Generate Python SDK package",
    tags=["API Documentation"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_python_sdk(request):
    """Generate Python SDK."""
    output_dir = request.data.get('output_dir', 'sdk/python')
    package_name = request.data.get('package_name', 'hishamos_sdk')
    
    generator = get_python_sdk_generator()
    sdk_path = generator.generate_sdk(output_dir, package_name)
    
    return Response({
        'message': 'Python SDK generated successfully',
        'path': sdk_path,
        'package_name': package_name
    })


@extend_schema(
    summary="Generate JavaScript SDK",
    description="Generate JavaScript/TypeScript SDK package",
    tags=["API Documentation"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_javascript_sdk(request):
    """Generate JavaScript SDK."""
    output_dir = request.data.get('output_dir', 'sdk/javascript')
    package_name = request.data.get('package_name', '@hishamos/sdk')
    
    generator = get_js_sdk_generator()
    sdk_path = generator.generate_sdk(output_dir, package_name)
    
    return Response({
        'message': 'JavaScript SDK generated successfully',
        'path': sdk_path,
        'package_name': package_name
    })

