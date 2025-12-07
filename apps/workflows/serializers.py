"""
Workflow API Serializers

Serializers for workflow execution, control, and status.
"""

from rest_framework import serializers
from apps.workflows.models import Workflow, WorkflowExecution


class WorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for workflow lists."""
    
    steps_count = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'slug', 'description', 'version', 'status', 'execution_count', 'steps_count', 'category']
    
    def get_steps_count(self, obj):
        """Extract step count from workflow definition."""
        if obj.definition and isinstance(obj.definition, dict):
            steps = obj.definition.get('steps', [])
            if isinstance(steps, list):
                return len(steps)
        return 0
    
    def get_category(self, obj):
        """Extract category from workflow definition metadata or infer from name."""
        if obj.definition and isinstance(obj.definition, dict):
            metadata = obj.definition.get('metadata', {})
            tags = metadata.get('tags', [])
            if tags:
                # Return first tag as category
                return tags[0].title()
        
        # Infer category from name
        name_lower = obj.name.lower()
        if 'bug' in name_lower or 'issue' in name_lower:
            return 'Bug Management'
        elif 'feature' in name_lower or 'development' in name_lower:
            return 'Development'
        elif 'release' in name_lower or 'deploy' in name_lower:
            return 'Deployment'
        elif 'review' in name_lower or 'audit' in name_lower:
            return 'Code Review'
        elif 'test' in name_lower or 'qa' in name_lower:
            return 'Testing'
        elif 'security' in name_lower:
            return 'Security'
        elif 'database' in name_lower or 'migration' in name_lower:
            return 'Database'
        elif 'onboarding' in name_lower or 'documentation' in name_lower:
            return 'Documentation'
        return 'General'


class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Detailed workflow serializer including definition."""
    
    steps = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    steps_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = '__all__'
    
    def get_steps(self, obj):
        """Extract and format steps from workflow definition."""
        if obj.definition and isinstance(obj.definition, dict):
            steps = obj.definition.get('steps', [])
            if isinstance(steps, list):
                # Format steps for frontend
                formatted_steps = []
                for idx, step in enumerate(steps):
                    formatted_step = {
                        'id': step.get('id', f'step-{idx}'),
                        'name': step.get('name', f'Step {idx + 1}'),
                        'agent_id': step.get('agent', ''),
                        'command_id': step.get('command', step.get('command_id')),
                        'parameters': step.get('inputs', step.get('parameters', {})),
                        'order': idx + 1,
                        'on_success': step.get('on_success'),
                        'on_failure': step.get('on_failure'),
                    }
                    formatted_steps.append(formatted_step)
                return formatted_steps
        return []
    
    def get_steps_count(self, obj):
        """Extract step count from workflow definition."""
        if obj.definition and isinstance(obj.definition, dict):
            steps = obj.definition.get('steps', [])
            if isinstance(steps, list):
                return len(steps)
        return 0
    
    def get_category(self, obj):
        """Extract category from workflow definition metadata or infer from name."""
        if obj.definition and isinstance(obj.definition, dict):
            metadata = obj.definition.get('metadata', {})
            tags = metadata.get('tags', [])
            if tags:
                return tags[0].title()
        
        # Infer category from name
        name_lower = obj.name.lower()
        if 'bug' in name_lower or 'issue' in name_lower:
            return 'Bug Management'
        elif 'feature' in name_lower or 'development' in name_lower:
            return 'Development'
        elif 'release' in name_lower or 'deploy' in name_lower:
            return 'Deployment'
        elif 'review' in name_lower or 'audit' in name_lower:
            return 'Code Review'
        elif 'test' in name_lower or 'qa' in name_lower:
            return 'Testing'
        elif 'security' in name_lower:
            return 'Security'
        elif 'database' in name_lower or 'migration' in name_lower:
            return 'Database'
        elif 'onboarding' in name_lower or 'documentation' in name_lower:
            return 'Documentation'
        return 'General'


class WorkflowExecutionRequestSerializer(serializers.Serializer):
    """Request serializer for workflow execution."""
    
    input_data = serializers.JSONField(
        help_text="Input data for workflow execution"
    )


class WorkflowExecutionStatusSerializer(serializers.ModelSerializer):
    """Serializer for workflow execution status."""
    
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    workflow_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'workflow_detail', 'status', 'current_step',
            'input_data', 'output_data', 'state', 'error_message',
            'retry_count', 'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_workflow_detail(self, obj):
        """Get workflow details if workflow exists."""
        if obj.workflow:
            return {
                'id': str(obj.workflow.id),
                'name': obj.workflow.name,
                'description': obj.workflow.description,
            }
        return None


class WorkflowExecutionResponseSerializer(serializers.Serializer):
    """Response serializer for workflow execution."""
    
    success = serializers.BooleanField()
    execution_id = serializers.UUIDField()
    output = serializers.JSONField(allow_null=True)
    completed_at = serializers.DateTimeField(allow_null=True)
    error = serializers.CharField(allow_null=True, required=False)
