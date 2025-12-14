"""
Django admin configuration for chat app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, MemberConversation, MemberMessage


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
    readonly_fields = ('id', 'created_at', 'updated_at', 'message_count',
                      'ai_provider_context', 'extracted_identifiers', 
                      'provider_metadata', 'token_usage_history', 'cost_tracking',
                      'conversation_summary', 'summary_metadata',
                      'referenced_files', 'referenced_code_blocks', 'code_context_metadata')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'agent', 'title', 'is_archived')
        }),
        ('AI Provider Context', {
            'fields': ('ai_provider_context', 'extracted_identifiers', 'max_recent_messages'),
            'classes': ('collapse',),
            'description': 'Provider-specific conversation context and identifiers for maintaining conversation state'
        }),
        ('Conversation Summarization', {
            'fields': ('conversation_summary', 'summary_metadata', 'summarize_at_message_count', 'summarize_at_token_count'),
            'classes': ('collapse',),
            'description': 'AI-generated conversation summary for long conversations and summarization thresholds'
        }),
        ('Code Context Tracking', {
            'fields': ('referenced_files', 'referenced_code_blocks', 'code_context_metadata'),
            'classes': ('collapse',),
            'description': 'Code blocks and file references extracted from messages (Cursor-style context management)'
        }),
        ('Metadata & Tracking', {
            'fields': ('provider_metadata', 'token_usage_history', 'cost_tracking'),
            'classes': ('collapse',),
            'description': 'Complete provider response metadata, token usage history, and cost tracking'
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


@admin.register(MemberConversation)
class MemberConversationAdmin(admin.ModelAdmin):
    """Member conversation admin."""
    
    list_display = (
        'title',
        'participant1',
        'participant2',
        'organization',
        'message_count_display',
        'unread_count_display',
        'is_archived_badge',
        'created_at',
        'updated_at'
    )
    list_filter = ('is_archived', 'organization', 'created_at', 'updated_at')
    search_fields = (
        'title',
        'participant1__email',
        'participant1__username',
        'participant2__email',
        'participant2__username',
        'organization__name'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'message_count_display', 'unread_count_display')
    date_hierarchy = 'created_at'
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('participant1', 'participant2', 'organization', 'title', 'is_archived')
        }),
        ('Statistics', {
            'fields': ('message_count_display', 'unread_count_display'),
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
    
    def message_count_display(self, obj):
        """Display number of messages."""
        count = obj.messages.count()
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            count
        )
    message_count_display.short_description = 'Messages'
    
    def unread_count_display(self, obj):
        """Display unread message count."""
        # Count total unread messages in the conversation
        unread = obj.messages.filter(is_read=False).count()
        
        if unread > 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
                unread
            )
        return format_html(
            '<span style="color: #6c757d;">0</span>'
        )
    unread_count_display.short_description = 'Unread'
    
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


@admin.register(MemberMessage)
class MemberMessageAdmin(admin.ModelAdmin):
    """Member message admin."""
    
    list_display = (
        'conversation',
        'sender',
        'role_badge',
        'content_preview',
        'is_read_badge',
        'attachments_count',
        'read_at',
        'created_at'
    )
    list_filter = ('role', 'is_read', 'created_at', 'conversation__organization')
    search_fields = (
        'content',
        'sender__email',
        'sender__username',
        'conversation__title',
        'conversation__participant1__email',
        'conversation__participant2__email'
    )
    readonly_fields = ('id', 'created_at', 'read_at', 'attachments_count')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Message Information', {
            'fields': ('conversation', 'sender', 'role', 'content')
        }),
        ('Attachments', {
            'fields': ('attachments', 'attachments_count'),
            'classes': ('collapse',)
        }),
        ('Read Status', {
            'fields': ('is_read', 'read_at'),
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
    
    def is_read_badge(self, obj):
        """Display read status as badge."""
        if obj.is_read:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 4px;">Read</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: #212529; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">Unread</span>'
        )
    is_read_badge.short_description = 'Read Status'
    is_read_badge.admin_order_field = 'is_read'
    
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
