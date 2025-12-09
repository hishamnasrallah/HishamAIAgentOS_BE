"""
Status Change Approval Serializer
"""

from rest_framework import serializers
from apps.projects.models import StatusChangeApproval


class StatusChangeApprovalSerializer(serializers.ModelSerializer):
    """Serializer for StatusChangeApproval model."""
    
    requested_by_email = serializers.EmailField(source='requested_by.email', read_only=True)
    requested_by_name = serializers.SerializerMethodField()
    approver_email = serializers.EmailField(source='approver.email', read_only=True, allow_null=True)
    approver_name = serializers.SerializerMethodField()
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True, allow_null=True)
    approved_by_name = serializers.SerializerMethodField()
    work_item_type = serializers.CharField(source='content_type.model', read_only=True)
    work_item_title = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = StatusChangeApproval
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'approved_by', 'approved_at',
            'requested_by', 'content_type', 'object_id', 'project'
        ]
        extra_kwargs = {
            'approver': {'required': False, 'allow_null': True},
            'rejection_reason': {'required': False, 'allow_blank': True},
        }
    
    def get_requested_by_name(self, obj):
        """Get full name of user who requested the approval."""
        if obj.requested_by:
            if obj.requested_by.first_name and obj.requested_by.last_name:
                return f"{obj.requested_by.first_name} {obj.requested_by.last_name}"
            return obj.requested_by.email
        return None
    
    def get_approver_name(self, obj):
        """Get full name of approver."""
        if obj.approver:
            if obj.approver.first_name and obj.approver.last_name:
                return f"{obj.approver.first_name} {obj.approver.last_name}"
            return obj.approver.email
        return None
    
    def get_approved_by_name(self, obj):
        """Get full name of user who approved/rejected."""
        if obj.approved_by:
            if obj.approved_by.first_name and obj.approved_by.last_name:
                return f"{obj.approved_by.first_name} {obj.approved_by.last_name}"
            return obj.approved_by.email
        return None
    
    def get_work_item_title(self, obj):
        """Get title of the work item."""
        try:
            work_item = obj.work_item
            if hasattr(work_item, 'title'):
                return work_item.title
            elif hasattr(work_item, 'name'):
                return work_item.name
            return str(work_item)
        except:
            return None
    
    def validate(self, attrs):
        """Validate approval request."""
        if self.instance and self.instance.status != 'pending':
            raise serializers.ValidationError("Can only modify pending approval requests.")
        return attrs

