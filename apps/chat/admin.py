"""
Django admin configuration for chat app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation admin."""
    
    list_display = (
        'title',
        'user',
        'agent',
        'message_count',
        'is_archived_badge',
        'created_at',
        'updated_at'
    )
    list_filter = ('is_archived', 'created_at', 'updated_at', 'agent')
    search_fields = ('title', 'user__email', 'user__username', 'agent__name', 'agent__agent_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'message_count')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'agent', 'title', 'is_archived')
        }),
        ('Statistics', {
            'fields': ('message_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['archive_conversations', 'unarchive_conversations']
    
    def is_archived_badge(self, obj):
        """Display archived status as badge."""
        if obj.is_archived:
            return format_html(
                '<span style="background-color: #6c757d; color: white; '
                'padding: 3px 8px; border-radius: 4px;">Archived</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; '
            'padding: 3px 8px; border-radius: 4px;">Active</span>'
        )
    is_archived_badge.short_description = 'Status'
    is_archived_badge.admin_order_field = 'is_archived'
    
    def message_count(self, obj):
        """Display number of messages."""
        count = obj.messages.count()
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            count
        )
    message_count.short_description = 'Messages'
    
    def archive_conversations(self, request, queryset):
        """Archive selected conversations."""
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} conversation(s) archived.')
    archive_conversations.short_description = 'Archive selected conversations'
    
    def unarchive_conversations(self, request, queryset):
        """Unarchive selected conversations."""
        updated = queryset.update(is_archived=False)
        self.message_user(request, f'{updated} conversation(s) unarchived.')
    unarchive_conversations.short_description = 'Unarchive selected conversations'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin."""
    
    list_display = (
        'conversation',
        'role_badge',
        'content_preview',
        'tokens_used_display',
        'attachments_count',
        'created_at'
    )
    list_filter = ('role', 'created_at', 'conversation__agent')
    search_fields = (
        'content',
        'conversation__title',
        'conversation__user__email',
        'conversation__agent__name'
    )
    readonly_fields = ('id', 'created_at', 'attachments_count')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Message Information', {
            'fields': ('conversation', 'role', 'content')
        }),
        ('Attachments', {
            'fields': ('attachments', 'attachments_count'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('tokens_used',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def role_badge(self, obj):
        """Display role as colored badge."""
        colors = {
            'user': '#007bff',
            'assistant': '#28a745',
            'system': '#6c757d',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
    
    def content_preview(self, obj):
        """Preview message content."""
        preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)
    content_preview.short_description = 'Content'
    
    def tokens_used_display(self, obj):
        """Display tokens used."""
        if obj.tokens_used:
            return format_html(
                '<span style="font-weight: bold; color: #6f42c1;">{}</span>',
                obj.tokens_used
            )
        return '-'
    tokens_used_display.short_description = 'Tokens'
    tokens_used_display.admin_order_field = 'tokens_used'
    
    def attachments_count(self, obj):
        """Display number of attachments."""
        if obj.attachments:
            count = len(obj.attachments) if isinstance(obj.attachments, list) else 0
            if count > 0:
                return format_html(
                    '<span style="font-weight: bold; color: #17a2b8;">{}</span>',
                    count
                )
        return '-'
    attachments_count.short_description = 'Attachments'
