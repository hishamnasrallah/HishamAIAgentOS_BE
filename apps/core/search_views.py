"""
Global search views for searching across all resources.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

from apps.agents.models import Agent
from apps.workflows.models import Workflow
from apps.commands.models import CommandTemplate
from apps.projects.models import Project
from apps.core.services.roles import RoleService

User = get_user_model()


@extend_schema(
    description="Global search across all resources (agents, workflows, commands, projects)",
    parameters=[],
    responses={200: {
        'type': 'object',
        'properties': {
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string', 'format': 'uuid'},
                        'type': {'type': 'string', 'enum': ['agent', 'workflow', 'command', 'project']},
                        'title': {'type': 'string'},
                        'description': {'type': 'string'},
                        'url': {'type': 'string'},
                    }
                }
            },
            'count': {'type': 'integer'}
        }
    }}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    """
    Search across all resources: agents, workflows, commands, and projects.
    Results are filtered based on user permissions.
    """
    query = request.query_params.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response({
            'results': [],
            'count': 0
        })
    
    user = request.user
    results = []
    
    # Search Agents (all authenticated users can view)
    agents = Agent.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ).only('id', 'name', 'description')[:5]
    
    for agent in agents:
        results.append({
            'id': str(agent.id),
            'type': 'agent',
            'title': agent.name,
            'description': agent.description[:200] if agent.description else '',
            'url': f'/agents/{agent.id}',
        })
    
    # Search Workflows (all authenticated users can view)
    workflows = Workflow.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ).only('id', 'name', 'description')[:5]
    
    for workflow in workflows:
        results.append({
            'id': str(workflow.id),
            'type': 'workflow',
            'title': workflow.name,
            'description': workflow.description[:200] if workflow.description else '',
            'url': f'/workflows/{workflow.id}',
        })
    
    # Search Commands (all authenticated users can view active commands)
    # Tags is a JSONField, so we need to handle it differently
    commands = CommandTemplate.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query)
    ).only('id', 'name', 'description', 'tags')[:10]
    
    # Filter by tags if query matches (tags is JSONField, so check if any tag contains query)
    commands_list = list(commands)
    commands_filtered = []
    for cmd in commands_list:
        # Check if query matches name or description (already filtered)
        if query.lower() in cmd.name.lower() or (cmd.description and query.lower() in cmd.description.lower()):
            commands_filtered.append(cmd)
        # Also check tags (JSONField - list of strings)
        elif cmd.tags and isinstance(cmd.tags, list):
            if any(query.lower() in str(tag).lower() for tag in cmd.tags):
                commands_filtered.append(cmd)
        if len(commands_filtered) >= 5:
            break
    
    commands = commands_filtered[:5]
    
    for command in commands:
        results.append({
            'id': str(command.id),
            'type': 'command',
            'title': command.name,
            'description': command.description[:200] if command.description else '',
            'url': f'/commands/{command.id}',
        })
    
    # Search Projects (respect permissions - only projects user owns or is member of)
    if RoleService.is_admin(user):
        # Admins can see all projects
        projects = Project.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).only('id', 'name', 'description')[:5]
    else:
        # Regular users can only see projects they own or are members of
        # Also include projects from user's organizations
        user_orgs = RoleService.get_user_organizations(user)
        if user.organization:
            user_orgs.append(user.organization)
        org_ids = list(set(org.id for org in user_orgs)) if user_orgs else []
        
        project_filter = Q(owner=user) | Q(members__id=user.id)
        if org_ids:
            project_filter |= Q(organization_id__in=org_ids)
        
        projects = Project.objects.filter(project_filter).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct().only('id', 'name', 'description')[:5]
    
    for project in projects:
        results.append({
            'id': str(project.id),
            'type': 'project',
            'title': project.name,
            'description': project.description[:200] if project.description else '',
            'url': f'/projects/{project.id}',
        })
    
    # Limit total results to 10
    results = results[:10]
    
    return Response({
        'results': results,
        'count': len(results)
    })

