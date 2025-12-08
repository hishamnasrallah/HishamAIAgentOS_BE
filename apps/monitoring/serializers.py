"""
Serializers for monitoring app.
"""

from rest_framework import serializers
from .models import SystemMetric, HealthCheck, AuditLog, AuditConfiguration


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


class AuditConfigurationSerializer(serializers.ModelSerializer):
    """Audit configuration serializer."""
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True, allow_null=True)
    rules_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditConfiguration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_rules_summary(self, obj):
        """Get summary of rules."""
        parts = []
        if obj.audit_actions:
            parts.append(f"{len(obj.audit_actions)} actions")
        if obj.audit_resource_types:
            parts.append(f"{len(obj.audit_resource_types)} resource types")
        if obj.exclude_actions or obj.exclude_resource_types:
            parts.append("with exclusions")
        if not obj.audit_all_users:
            parts.append(f"{len(obj.audit_users)} users")
        return ", ".join(parts) if parts else "All actions & resources"
