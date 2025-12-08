"""
Django admin configuration for commands app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import CommandCategory, CommandTemplate


@admin.register(CommandCategory)
class CommandCategoryAdmin(admin.ModelAdmin):
    """Command Category admin."""
    
    list_display = ('name', 'slug', 'order', 'command_count', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
        ('Display', {'fields': ('icon', 'order')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def command_count(self, obj):
        """Display number of commands in this category."""
        count = obj.commands.count()
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            count
        )
    command_count.short_description = 'Commands'
    command_count.admin_order_field = 'commands__count'


@admin.register(CommandTemplate)
class CommandTemplateAdmin(admin.ModelAdmin):
    """Command Template admin."""
    
    list_display = (
        'name',
        'category',
        'recommended_agent',
        'is_active',
        'usage_count',
        'success_rate_display',
        'estimated_cost_display',
        'avg_execution_time_display',
        'created_at',
        'updated_at'
    )
    list_filter = (
        'category',
        'is_active',
        'recommended_agent',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'name',
        'slug',
        'description',
        'category__name',
        'tags'
    )
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ()
    readonly_fields = (
        'usage_count',
        'total_successes_display',
        'total_failures_display',
        'success_rate_display',
        'estimated_cost',
        'avg_execution_time_display',
        'created_at',
        'updated_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'category',
                'name',
                'slug',
                'description',
                'version',
                'is_active'
            )
        }),
        ('Template Content', {
            'fields': ('template', 'parameters', 'example_usage')
        }),
        ('Agent Integration', {
            'fields': (
                'recommended_agent',
                'required_capabilities'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'usage_count',
                'total_successes_display',
                'total_failures_display',
                'success_rate_display',
                'estimated_cost',
                'avg_execution_time_display'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_commands', 'deactivate_commands', 'reset_metrics']
    
    def total_successes_display(self, obj):
        """Display total successful executions."""
        count = obj.executions.filter(status='completed').count()
        return count
    total_successes_display.short_description = 'Total Successes'
    
    def total_failures_display(self, obj):
        """Display total failed executions."""
        count = obj.executions.filter(status='failed').count()
        return count
    total_failures_display.short_description = 'Total Failures'
    
    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        total = obj.executions.count()
        if total == 0:
            rate = 0.0
        else:
            successful = obj.executions.filter(status='completed').count()
            rate = (successful / total) * 100
        
        if rate >= 90:
            color = '#28a745'
        elif rate >= 70:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        # Format the number first, then pass to format_html
        rate_str = f"{rate:.1f}%"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            rate_str
        )
    success_rate_display.short_description = 'Success Rate'
    
    def estimated_cost_display(self, obj):
        """Display estimated cost formatted."""
        cost = float(obj.estimated_cost) if obj.estimated_cost else 0.0
        # Return plain formatted string - no HTML needed
        return f"${cost:.6f}"
    estimated_cost_display.short_description = 'Est. Cost'
    estimated_cost_display.admin_order_field = 'estimated_cost'
    
    def avg_execution_time_display(self, obj):
        """Display average execution time formatted."""
        from django.db.models import Avg
        
        executions = obj.executions.filter(status='completed', execution_time_ms__gt=0)
        if executions.exists():
            avg_ms = executions.aggregate(avg=Avg('execution_time_ms'))['avg'] or 0
            avg_seconds = avg_ms / 1000.0
            return f"{avg_seconds:.2f}s"
        return "0.00s"
    avg_execution_time_display.short_description = 'Avg Time'
    
    def activate_commands(self, request, queryset):
        """Activate selected commands."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} command(s) activated.')
    activate_commands.short_description = 'Activate selected commands'
    
    def deactivate_commands(self, request, queryset):
        """Deactivate selected commands."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} command(s) deactivated.')
    deactivate_commands.short_description = 'Deactivate selected commands'
    
    def reset_metrics(self, request, queryset):
        """Reset metrics for selected commands."""
        for command in queryset:
            command.usage_count = 0
            command.estimated_cost = 0.0
            command.estimated_duration = 0
            command.save()
            # Delete execution records (optional - comment out if you want to keep history)
            # command.executions.all().delete()
        self.message_user(request, f'Metrics reset for {queryset.count()} command(s).')
    reset_metrics.short_description = 'Reset metrics for selected commands'
