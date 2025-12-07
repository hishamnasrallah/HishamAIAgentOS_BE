"""
Django admin configuration for results app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Result, ResultFeedback


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    """Result admin."""
    
    list_display = (
        'title',
        'result_type',
        'format',
        'user',
        'quality_score_display',
        'confidence_score_display',
        'version',
        'created_at',
        'updated_at'
    )
    list_filter = (
        'result_type',
        'format',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'title',
        'content',
        'user__email',
        'tags'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'feedback_count'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    filter_horizontal = ()
    
    fieldsets = (
        ('Source Information', {
            'fields': (
                'result_type',
                'agent_execution',
                'workflow_execution',
                'user'
            )
        }),
        ('Content', {
            'fields': (
                'title',
                'content',
                'format',
                'metadata'
            )
        }),
        ('Analysis', {
            'fields': (
                'critique',
                'action_items'
            ),
            'classes': ('collapse',)
        }),
        ('Quality Metrics', {
            'fields': (
                'quality_score',
                'confidence_score'
            )
        }),
        ('Versioning', {
            'fields': (
                'version',
                'parent_result'
            ),
            'classes': ('collapse',)
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Feedback', {
            'fields': ('feedback_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quality_score_display(self, obj):
        """Display quality score with color coding."""
        if obj.quality_score is None:
            return '-'
        
        score = float(obj.quality_score)
        if score >= 80:
            color = '#28a745'
        elif score >= 60:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        # Format the number first, then pass to format_html
        score_str = f"{score:.1f}/100"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            score_str
        )
    quality_score_display.short_description = 'Quality'
    quality_score_display.admin_order_field = 'quality_score'
    
    def confidence_score_display(self, obj):
        """Display confidence score with color coding."""
        if obj.confidence_score is None:
            return '-'
        
        score = float(obj.confidence_score)
        if score >= 80:
            color = '#28a745'
        elif score >= 60:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        # Format the number first, then pass to format_html
        score_str = f"{score:.1f}/100"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            score_str
        )
    confidence_score_display.short_description = 'Confidence'
    confidence_score_display.admin_order_field = 'confidence_score'
    
    def feedback_count(self, obj):
        """Display number of feedback entries."""
        count = obj.feedback.count()
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            count
        )
    feedback_count.short_description = 'Feedback Count'
    
    actions = ['export_results', 'reset_quality_scores']
    
    def export_results(self, request, queryset):
        """Export selected results (placeholder for future implementation)."""
        self.message_user(request, f'Export functionality for {queryset.count()} result(s) - to be implemented.')
    export_results.short_description = 'Export selected results'
    
    def reset_quality_scores(self, request, queryset):
        """Reset quality and confidence scores."""
        updated = queryset.update(quality_score=None, confidence_score=None)
        self.message_user(request, f'Quality scores reset for {updated} result(s).')
    reset_quality_scores.short_description = 'Reset quality scores'


@admin.register(ResultFeedback)
class ResultFeedbackAdmin(admin.ModelAdmin):
    """Result Feedback admin."""
    
    list_display = (
        'result',
        'user',
        'rating_display',
        'is_accurate_display',
        'is_helpful_display',
        'is_complete_display',
        'created_at'
    )
    list_filter = (
        'rating',
        'is_accurate',
        'is_helpful',
        'is_complete',
        'created_at'
    )
    search_fields = (
        'result__title',
        'user__email',
        'comment'
    )
    readonly_fields = ('id', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Feedback Information', {
            'fields': (
                'result',
                'user',
                'rating',
                'comment'
            )
        }),
        ('Specific Feedback', {
            'fields': (
                'is_accurate',
                'is_helpful',
                'is_complete'
            )
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """Display rating with stars."""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        colors = {
            5: '#28a745',
            4: '#28a745',
            3: '#ffc107',
            2: '#ffc107',
            1: '#dc3545',
        }
        color = colors.get(obj.rating, '#6c757d')
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span>',
            color,
            stars
        )
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'rating'
    
    def is_accurate_display(self, obj):
        """Display accuracy status."""
        if obj.is_accurate is None:
            return '-'
        if obj.is_accurate:
            return format_html('<span style="color: #28a745;">✓ Yes</span>')
        return format_html('<span style="color: #dc3545;">✗ No</span>')
    is_accurate_display.short_description = 'Accurate'
    is_accurate_display.admin_order_field = 'is_accurate'
    
    def is_helpful_display(self, obj):
        """Display helpfulness status."""
        if obj.is_helpful is None:
            return '-'
        if obj.is_helpful:
            return format_html('<span style="color: #28a745;">✓ Yes</span>')
        return format_html('<span style="color: #dc3545;">✗ No</span>')
    is_helpful_display.short_description = 'Helpful'
    is_helpful_display.admin_order_field = 'is_helpful'
    
    def is_complete_display(self, obj):
        """Display completeness status."""
        if obj.is_complete is None:
            return '-'
        if obj.is_complete:
            return format_html('<span style="color: #28a745;">✓ Yes</span>')
        return format_html('<span style="color: #dc3545;">✗ No</span>')
    is_complete_display.short_description = 'Complete'
    is_complete_display.admin_order_field = 'is_complete'
