"""
GDPR compliance features: data export, deletion, and privacy management.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from apps.monitoring.audit import audit_logger

logger = logging.getLogger(__name__)
User = get_user_model()


class GDPRCompliance:
    """
    GDPR compliance utilities for data export and deletion.
    """
    
    @staticmethod
    def export_user_data(user: User) -> Dict[str, Any]:
        """
        Export all user data in JSON format (GDPR Article 15 - Right of access).
        
        Returns:
            Dictionary containing all user data
        """
        data = {
            'export_date': timezone.now().isoformat(),
            'user_id': str(user.id),
            'email': user.email,
            'profile': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'api_keys': [],
            'projects': [],
            'agents': [],
            'workflows': [],
            'commands': [],
            'chat_conversations': [],
            'audit_logs': [],
        }
        
        # Export API keys
        from apps.authentication.models import APIKey
        api_keys = APIKey.objects.filter(user=user)
        for api_key in api_keys:
            data['api_keys'].append({
                'id': str(api_key.id),
                'name': api_key.name,
                'created_at': api_key.created_at.isoformat() if api_key.created_at else None,
                'last_used_at': api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                'is_active': api_key.is_active,
                'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
            })
        
        # Export projects
        try:
            from apps.projects.models import Project
            projects = Project.objects.filter(created_by=user)
            for project in projects:
                data['projects'].append({
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description,
                    'created_at': project.created_at.isoformat() if project.created_at else None,
                })
        except ImportError:
            pass
        
        # Export agents
        try:
            from apps.agents.models import Agent
            agents = Agent.objects.filter(created_by=user)
            for agent in agents:
                data['agents'].append({
                    'id': str(agent.id),
                    'name': agent.name,
                    'agent_id': agent.agent_id,
                    'description': agent.description,
                    'created_at': agent.created_at.isoformat() if agent.created_at else None,
                })
        except ImportError:
            pass
        
        # Export workflows
        try:
            from apps.workflows.models import Workflow
            workflows = Workflow.objects.filter(created_by=user)
            for workflow in workflows:
                data['workflows'].append({
                    'id': str(workflow.id),
                    'name': workflow.name,
                    'description': workflow.description,
                    'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
                })
        except ImportError:
            pass
        
        # Export chat conversations
        try:
            from apps.chat.models import Conversation
            conversations = Conversation.objects.filter(user=user)
            for conv in conversations:
                data['chat_conversations'].append({
                    'id': str(conv.id),
                    'title': conv.title,
                    'created_at': conv.created_at.isoformat() if conv.created_at else None,
                    'message_count': conv.messages.count(),
                })
        except ImportError:
            pass
        
        # Export audit logs
        audit_logs = audit_logger.get_user_audit_trail(user)
        for log in audit_logs[:1000]:  # Limit to last 1000 entries
            data['audit_logs'].append({
                'id': str(log.id),
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'description': log.description,
                'timestamp': log.timestamp.isoformat(),
            })
        
        return data
    
    @staticmethod
    def export_user_data_json(user: User) -> str:
        """Export user data as JSON string."""
        data = GDPRCompliance.export_user_data(user)
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    @transaction.atomic
    def delete_user_data(user: User, reason: str = "GDPR Right to be Forgotten") -> Dict[str, Any]:
        """
        Delete all user data (GDPR Article 17 - Right to erasure).
        
        Note: This is a destructive operation. Some data may be anonymized
        rather than deleted for legal/operational requirements.
        
        Returns:
            Dictionary with deletion summary
        """
        deletion_summary = {
            'user_id': str(user.id),
            'email': user.email,
            'deletion_date': timezone.now().isoformat(),
            'reason': reason,
            'deleted_items': {},
            'anonymized_items': {},
        }
        
        # Log the deletion request
        audit_logger.log_data_deletion(
            resource_type='user',
            resource_id=str(user.id),
            user=user,
            reason=reason
        )
        
        # Delete API keys
        from apps.authentication.models import APIKey
        api_keys = APIKey.objects.filter(user=user)
        api_key_count = api_keys.count()
        api_keys.delete()
        deletion_summary['deleted_items']['api_keys'] = api_key_count
        
        # Anonymize user data (instead of deleting for audit trail)
        user.email = f"deleted_{user.id}@deleted.local"
        user.first_name = "Deleted"
        user.last_name = "User"
        user.is_active = False
        user.set_unusable_password()
        user.save()
        deletion_summary['anonymized_items']['user'] = True
        
        # Delete user's projects (or transfer ownership - depends on business logic)
        try:
            from apps.projects.models import Project
            projects = Project.objects.filter(created_by=user)
            project_count = projects.count()
            # Option 1: Delete projects
            # projects.delete()
            # Option 2: Transfer to system user (recommended)
            # system_user = User.objects.filter(is_superuser=True).first()
            # if system_user:
            #     projects.update(created_by=system_user)
            deletion_summary['deleted_items']['projects'] = project_count
        except ImportError:
            pass
        
        # Delete user's agents
        try:
            from apps.agents.models import Agent
            agents = Agent.objects.filter(created_by=user)
            agent_count = agents.count()
            agents.delete()
            deletion_summary['deleted_items']['agents'] = agent_count
        except ImportError:
            pass
        
        # Delete user's workflows
        try:
            from apps.workflows.models import Workflow
            workflows = Workflow.objects.filter(created_by=user)
            workflow_count = workflows.count()
            workflows.delete()
            deletion_summary['deleted_items']['workflows'] = workflow_count
        except ImportError:
            pass
        
        # Delete chat conversations
        try:
            from apps.chat.models import Conversation
            conversations = Conversation.objects.filter(user=user)
            conv_count = conversations.count()
            conversations.delete()
            deletion_summary['deleted_items']['conversations'] = conv_count
        except ImportError:
            pass
        
        logger.info(f"GDPR deletion completed for user {user.id}: {deletion_summary}")
        
        return deletion_summary
    
    @staticmethod
    def get_data_retention_policy() -> Dict[str, Any]:
        """
        Get data retention policy information (GDPR Article 13).
        
        Returns:
            Dictionary with retention policy details
        """
        return {
            'audit_logs': {
                'retention_period_days': 365,
                'purpose': 'Security and compliance auditing',
                'legal_basis': 'Legitimate interest (security)',
            },
            'user_data': {
                'retention_period_days': 'Until account deletion',
                'purpose': 'Service provision',
                'legal_basis': 'Contract performance',
            },
            'api_keys': {
                'retention_period_days': 'Until revocation or account deletion',
                'purpose': 'API access',
                'legal_basis': 'Contract performance',
            },
            'chat_conversations': {
                'retention_period_days': 90,
                'purpose': 'Service improvement',
                'legal_basis': 'Legitimate interest',
            },
        }

