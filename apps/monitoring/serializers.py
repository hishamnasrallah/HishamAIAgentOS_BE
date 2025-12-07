"""
Serializers for monitoring app.
"""

from rest_framework import serializers
from .models import SystemMetric, HealthCheck, AuditLog


class SystemMetricSerializer(serializers.ModelSerializer):
    """System metric serializer."""
    
    class Meta:
        model = SystemMetric
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class HealthCheckSerializer(serializers.ModelSerializer):
    """Health check serializer."""
    
    class Meta:
        model = HealthCheck
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    ip_address = serializers.CharField(read_only=True, allow_null=True)  # Explicitly define for DRF compatibility
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']

