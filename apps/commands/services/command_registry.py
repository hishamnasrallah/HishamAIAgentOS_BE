"""
Command Registry - Central repository for command templates.

Provides search, filter, and recommendation capabilities.
"""

from typing import List, Optional, Dict, Any
import logging
from django.db.models import Q
from asgiref.sync import sync_to_async

from apps.commands.models import CommandTemplate, CommandCategory
from apps.agents.models import Agent

logger = logging.getLogger(__name__)


class CommandRegistry:
    """Central registry for managing and discovering command templates."""
    
    async def search(
        self,
        query: str = '',
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        agent_capabilities: Optional[List[str]] = None,
        is_active: bool = True
    ) -> List[CommandTemplate]:
        """
        Search for commands with multiple filters.
        
        Args:
            query: Text search across name, description, tags
            category: Filter by category slug
            tags: Filter commands that have ALL specified tags
            agent_capabilities: Filter by required capabilities
            is_active: Only return active commands
            
        Returns:
            List of matching CommandTemplate instances
        """
        # Start with base queryset
        queryset = CommandTemplate.objects.all()
        
        # Filter by active status
        if is_active:
            queryset = queryset.filter(is_active=True)
        
        # Category filter
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Text search
        if query:
            search_query = Q(name__icontains=query) | Q(description__icontains=query)
            queryset = queryset.filter(search_query)
        
        # Tags filter (must have ALL tags)
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
        
        # Capabilities filter
        if agent_capabilities:
            # Find commands that require subset of available capabilities
            for capability in agent_capabilities:
                queryset = queryset.filter(
                    Q(required_capabilities__contains=[capability]) |
                    Q(required_capabilities=[])  # Or no specific requirements
                )
        
        # Order by success rate and usage count
        queryset = queryset.order_by('-success_rate', '-usage_count')
        
        # Execute query
        return await sync_to_async(list)(
            queryset.select_related('category', 'recommended_agent')
        )
    
    async def recommend(
        self,
        task_description: str,
        available_agents: Optional[List[Agent]] = None
    ) -> List[CommandTemplate]:
        """
        Recommend commands for a given task.
        
        Uses simple keyword matching. Can be enhanced with ML/embeddings later.
        
        Args:
            task_description: Description of what user wants to do
            available_agents: Optional list of available agents
            
        Returns:
            List of recommended commands
        """
        description_lower = task_description.lower()
        
        # Extract keywords from task description
        keywords = self._extract_keywords(description_lower)
        
        # Search by keywords
        commands = []
        for keyword in keywords:
            keyword_commands = await self.search(query=keyword)
            commands.extend(keyword_commands)
        
        # Remove duplicates and sort by relevance (usage + success)
        seen = set()
        unique_commands = []
        for cmd in commands:
            if cmd.id not in seen:
                seen.add(cmd.id)
                unique_commands.append(cmd)
        
        # Sort by combined score: success_rate * usage_count
        unique_commands.sort(
            key=lambda c: (c.success_rate / 100) * c.usage_count,
            reverse=True
        )
        
        # Limit to top 10
        return unique_commands[:10]
    
    async def get_popular(
        self,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[CommandTemplate]:
        """
        Get most popular commands.
        
        Popularity = success_rate * usage_count
        
        Args:
            category: Optional category filter
            limit: Maximum number of commands to return
            
        Returns:
            List of popular commands
        """
        queryset = CommandTemplate.objects.filter(is_active=True)
        
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Order by usage and success
        queryset = queryset.order_by('-usage_count', '-success_rate')[:limit]
        
        return await sync_to_async(list)(
            queryset.select_related('category', 'recommended_agent')
        )
    
    async def get_by_slug(self, slug: str) -> Optional[CommandTemplate]:
        """Get command by slug."""
        try:
            return await CommandTemplate.objects.select_related(
                'category', 'recommended_agent'
            ).aget(slug=slug)
        except CommandTemplate.DoesNotExist:
            return None
    
    async def get_by_id(self, command_id: str) -> Optional[CommandTemplate]:
        """Get command by ID."""
        try:
            return await CommandTemplate.objects.select_related(
                'category', 'recommended_agent'
            ).aget(id=command_id)
        except CommandTemplate.DoesNotExist:
            return None
    
    async def get_categories(self) -> List[CommandCategory]:
        """Get all command categories."""
        return await sync_to_async(list)(
            CommandCategory.objects.all().order_by('order', 'name')
        )
    
    async def get_by_category(self, category_slug: str) -> List[CommandTemplate]:
        """Get all commands in a category."""
        return await sync_to_async(list)(
            CommandTemplate.objects.filter(
                category__slug=category_slug,
                is_active=True
            ).select_related('category', 'recommended_agent').order_by('-usage_count')
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from text.
        
        Simple implementation - can be enhanced with NLP later.
        """
        # Common task-related keywords
        keyword_map = {
            # Code related
            'code': ['code', 'coding', 'programming', 'develop', 'implement'],
            'review': ['review', 'audit', 'check', 'analyze'],
            'test': ['test', 'testing', 'qa', 'quality'],
            'debug': ['debug', 'fix', 'bug', 'error'],
            'refactor': ['refactor', 'improve', 'optimize'],
            
            # Documentation
            'document': ['document', 'documentation', 'readme', 'guide'],
            'api': ['api', 'endpoint', 'rest', 'graphql'],
            
            # Legal
            'contract': ['contract', 'agreement', 'legal'],
            'policy': ['policy', 'terms', 'privacy'],
            
            # Business
            'requirements': ['requirements', 'specification', 'spec'],
            'story': ['story', 'stories', 'user story'],
            'plan': ['plan', 'planning', 'strategy'],
            
            # DevOps
            'deploy': ['deploy', 'deployment', 'release'],
            'ci': ['ci', 'cd', 'pipeline', 'build'],
            'docker': ['docker', 'container', 'kubernetes'],
        }
        
        keywords = []
        for key, variations in keyword_map.items():
            if any(var in text for var in variations):
                keywords.append(key)
        
        return keywords
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_commands = await CommandTemplate.objects.acount()
        active_commands = await CommandTemplate.objects.filter(is_active=True).acount()
        
        categories = await sync_to_async(list)(
            CommandCategory.objects.all()
        )
        
        category_stats = []
        for category in categories:
            count = await CommandTemplate.objects.filter(
                category=category,
                is_active=True
            ).acount()
            category_stats.append({
                'name': category.name,
                'slug': category.slug,
                'count': count
            })
        
        return {
            'total_commands': total_commands,
            'active_commands': active_commands,
            'categories': category_stats
        }


# Global registry instance
command_registry = CommandRegistry()
