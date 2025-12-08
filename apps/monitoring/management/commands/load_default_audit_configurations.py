"""
Management command to load default audit configurations.

These configurations cover 90% of common audit scenarios.
"""

from django.core.management.base import BaseCommand
from apps.monitoring.models import AuditConfiguration


class Command(BaseCommand):
    help = 'Load default audit configurations for common scenarios'

    def handle(self, *args, **options):
        """Load default configurations."""
        self.stdout.write('Loading default audit configurations...')
        
        configurations = [
            {
                'name': 'Default - Audit Everything',
                'description': 'Comprehensive audit logging for all actions and resources. Recommended for most scenarios.',
                'configuration_type': 'default',
                'is_active': True,
                'is_default': True,
                'priority': 0,
                'audit_actions': [],  # Empty = all actions
                'audit_resource_types': [],  # Empty = all resources
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'GDPR Compliance',
                'description': 'Audit all data access, export, and deletion activities for GDPR compliance.',
                'configuration_type': 'gdpr',
                'is_active': True,
                'is_default': False,
                'priority': 10,
                'audit_actions': ['read', 'delete', 'execute'],
                'audit_resource_types': ['user', 'authentication', 'gdpr'],
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'Security & Access Control',
                'description': 'Audit all security-related actions: authentication, authorization, and access control changes.',
                'configuration_type': 'security',
                'is_active': True,
                'is_default': False,
                'priority': 20,
                'audit_actions': ['login', 'logout', 'create', 'update', 'delete'],
                'audit_resource_types': ['authentication', 'user', 'api_key', 'permission', 'role'],
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'User Management',
                'description': 'Audit all user management activities: creation, updates, role changes, and deletions.',
                'configuration_type': 'user_management',
                'is_active': True,
                'is_default': False,
                'priority': 15,
                'audit_actions': ['create', 'update', 'delete'],
                'audit_resource_types': ['user', 'role', 'permission'],
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'System Configuration Changes',
                'description': 'Audit all system configuration and settings changes.',
                'configuration_type': 'system_changes',
                'is_active': True,
                'is_default': False,
                'priority': 25,
                'audit_actions': ['create', 'update', 'delete'],
                'audit_resource_types': ['system_setting', 'feature_flag', 'audit_configuration'],
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'Financial Transactions',
                'description': 'Audit all financial and cost-related activities.',
                'configuration_type': 'financial',
                'is_active': True,
                'is_default': False,
                'priority': 30,
                'audit_actions': ['create', 'update', 'delete', 'execute'],
                'audit_resource_types': ['payment', 'billing', 'subscription', 'cost'],
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'Data Access Only',
                'description': 'Audit only data access activities (read operations). Lightweight configuration.',
                'configuration_type': 'data_access',
                'is_active': False,  # Not active by default
                'is_default': False,
                'priority': 5,
                'audit_actions': ['read'],
                'audit_resource_types': [],  # All resources
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': False,  # Don't need changes for read operations
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'Minimal Audit - Critical Actions Only',
                'description': 'Audit only critical actions: deletions, authentication, and system changes. Minimal logging.',
                'configuration_type': 'custom',
                'is_active': False,  # Not active by default
                'is_default': False,
                'priority': 40,
                'audit_actions': ['delete', 'login', 'logout'],
                'audit_resource_types': [],  # All resources
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': False,  # Minimal data
            },
            {
                'name': 'API Operations Only',
                'description': 'Audit only API operations (execute actions). Useful for API monitoring.',
                'configuration_type': 'custom',
                'is_active': False,  # Not active by default
                'is_default': False,
                'priority': 35,
                'audit_actions': ['execute'],
                'audit_resource_types': ['api', 'agent', 'workflow', 'command'],
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': True,
                'include_changes': False,
                'include_ip_address': True,
                'include_user_agent': True,
            },
            {
                'name': 'External Access Only',
                'description': 'Audit only actions from external IP addresses. Excludes internal/localhost IPs.',
                'configuration_type': 'security',
                'is_active': False,  # Not active by default
                'is_default': False,
                'priority': 45,
                'audit_actions': [],  # All actions
                'audit_resource_types': [],  # All resources
                'exclude_actions': [],
                'exclude_resource_types': [],
                'audit_all_users': True,
                'audit_all_ips': False,
                'audit_ips': [],  # Will be set programmatically or manually
                'exclude_ips': ['127.0.0.1', 'localhost', '::1'],
                'include_changes': True,
                'include_ip_address': True,
                'include_user_agent': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for config_data in configurations:
            name = config_data.pop('name')
            config, created = AuditConfiguration.objects.update_or_create(
                name=name,
                defaults=config_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully loaded {len(configurations)} audit configurations:'
            f'\n  - Created: {created_count}'
            f'\n  - Updated: {updated_count}'
        ))
        
        # Show active configurations
        active_configs = AuditConfiguration.objects.filter(is_active=True).order_by('-priority', 'name')
        if active_configs.exists():
            self.stdout.write(f'\nActive configurations ({active_configs.count()}):')
            for config in active_configs:
                default_marker = ' [DEFAULT]' if config.is_default else ''
                self.stdout.write(f'  - {config.name} (Priority: {config.priority}){default_marker}')


