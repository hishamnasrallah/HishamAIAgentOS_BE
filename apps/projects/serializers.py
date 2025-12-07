"""
Project Management API Serializers

Serializers for AI Project Management endpoints.
"""

from rest_framework import serializers
from apps.projects.models import Project, Sprint, Story, Epic, Task


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer."""
    
    # Make slug optional - will auto-generate from name
    slug = serializers.SlugField(required=False)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Auto-generate slug from name if not provided
        if 'slug' not in validated_data:
            from django.utils.text import slugify
            validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class SprintSerializer(serializers.ModelSerializer):
    """Sprint serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Sprint
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class StoryGenerationRequestSerializer(serializers.Serializer):
    """Request serializer for story generation."""
    
    product_vision = serializers.CharField(
        help_text="High-level product vision or feature description"
    )
    context = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional context (target users, constraints, etc.)"
    )
    epic_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Optional epic to associate stories with"
    )


class StorySerializer(serializers.ModelSerializer):
    """Story serializer."""
    
    epic_name = serializers.CharField(source='epic.title', read_only=True, allow_null=True)
    sprint_name = serializers.CharField(source='sprint.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Story
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'generated_by_ai', 'generation_workflow', 'created_by']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'acceptance_criteria': {'required': False},
            'story_points': {'required': False, 'allow_null': True},
            'status': {'required': False},
            'priority': {'required': False},
            'epic': {'required': False, 'allow_null': True},
            'sprint': {'required': False, 'allow_null': True},
            'assigned_to': {'required': False, 'allow_null': True},
        }
    
    def update(self, instance, validated_data):
        """Override update to ensure all fields are saved, including null values."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StorySerializer] Updating story {instance.id}")
        logger.info(f"[StorySerializer] Validated data: {validated_data}")
        
        # Get raw request data to check for explicitly null fields
        request = self.context.get('request')
        raw_data = {}
        if request:
            raw_data = dict(request.data)  # Convert to dict to ensure we can iterate
            logger.info(f"[StorySerializer] Raw request data: {raw_data}")
        
        # Fields that can be null and need explicit handling
        nullable_fields = ['story_points', 'epic', 'sprint', 'assigned_to']
        all_fields = ['title', 'description', 'acceptance_criteria', 'priority', 'status'] + nullable_fields
        
        # Update all fields - prioritize validated_data, then check raw_data
        for field in all_fields:
            if field in validated_data:
                # Field has a value (including None if explicitly set)
                setattr(instance, field, validated_data[field])
                logger.info(f"[StorySerializer] Set {field} = {validated_data[field]} (from validated_data)")
            elif field in raw_data:
                # Field was in request but not in validated_data - check if it's null
                raw_value = raw_data[field]
                if raw_value is None or raw_value == '' or raw_value == 'null' or (isinstance(raw_value, str) and raw_value.lower() == 'null'):
                    if field in nullable_fields:
                        setattr(instance, field, None)
                        logger.info(f"[StorySerializer] Explicitly set {field} = None (from raw_data, was: {raw_value})")
                else:
                    # Field has a value in raw_data but wasn't validated - try to use it
                    # This can happen if the value is valid but serializer didn't include it
                    if field in nullable_fields:
                        # For foreign keys, the value should be a UUID string
                        try:
                            setattr(instance, field, raw_value)
                            logger.info(f"[StorySerializer] Set {field} = {raw_value} (from raw_data, not in validated_data)")
                        except Exception as e:
                            logger.warning(f"[StorySerializer] Could not set {field} = {raw_value}: {e}")
        
        instance.save()
        logger.info(f"[StorySerializer] Story saved. Story points: {instance.story_points}, Assigned to: {instance.assigned_to}, Epic: {instance.epic}, Sprint: {instance.sprint}")
        return instance
    
    def create(self, validated_data):
        """Override create to ensure all fields are saved."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StorySerializer] Creating story")
        logger.info(f"[StorySerializer] Validated data: {validated_data}")
        
        # Get raw request data to ensure all fields are included
        request = self.context.get('request')
        if request:
            raw_data = dict(request.data)
            logger.info(f"[StorySerializer] Raw request data: {raw_data}")
            
            # Ensure nullable fields are included even if they're null
            nullable_fields = ['story_points', 'epic', 'sprint', 'assigned_to']
            for field in nullable_fields:
                if field in raw_data and field not in validated_data:
                    # Field was in request but not validated - add it
                    validated_data[field] = raw_data[field] if raw_data[field] not in [None, '', 'null'] else None
                    logger.info(f"[StorySerializer] Added {field} = {validated_data[field]} to validated_data")
        
        instance = super().create(validated_data)
        logger.info(f"[StorySerializer] Story created. Story points: {instance.story_points}, Assigned to: {instance.assigned_to}, Epic: {instance.epic}, Sprint: {instance.sprint}")
        return instance


class SprintPlanningRequestSerializer(serializers.Serializer):
    """Request serializer for sprint planning."""
    
    team_velocity = serializers.IntegerField(
        min_value=1,
        help_text="Team's average velocity in story points"
    )
    backlog_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific backlog story IDs to consider (optional)"
    )
    constraints = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Optional planning constraints"
    )


class EstimationRequestSerializer(serializers.Serializer):
    """Request serializer for story estimation."""
    
    use_historical = serializers.BooleanField(
        default=True,
        help_text="Whether to use historical data for estimation"
    )


class EstimationResponseSerializer(serializers.Serializer):
    """Response serializer for estimation."""
    
    estimated_points = serializers.IntegerField()
    confidence = serializers.FloatField()
    rationale = serializers.CharField()
    complexity_factors = serializers.ListField(child=serializers.CharField())
    risks = serializers.ListField(child=serializers.CharField(), required=False)


class EpicSerializer(serializers.ModelSerializer):
    """Epic serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Epic
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer."""
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']