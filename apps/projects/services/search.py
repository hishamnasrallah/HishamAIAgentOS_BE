"""
Advanced search service for project management system.
Supports full-text search with operators, filters, and multi-model searching.
"""

from django.db.models import Q, TextField
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from apps.projects.models import (
    Project, UserStory, Task, Bug, Issue, Epic, StoryComment, StoryAttachment
)
from typing import List, Dict, Any, Optional
import re


class SearchService:
    """Service for advanced search functionality."""
    
    # Search operators
    OPERATORS = {
        'AND': 'AND',
        'OR': 'OR',
        'NOT': 'NOT',
        'QUOTE': '"',  # Exact phrase
        'FIELD': ':',  # Field-specific search (e.g., title:bug)
    }
    
    # Fields that can be searched for each model
    SEARCHABLE_FIELDS = {
        'userstory': ['title', 'description', 'acceptance_criteria', 'tags'],
        'task': ['title', 'description', 'tags'],
        'bug': ['title', 'description', 'reproduction_steps', 'expected_behavior', 'actual_behavior', 'tags'],
        'issue': ['title', 'description', 'tags'],
        'epic': ['title', 'description', 'tags'],
        'project': ['name', 'description', 'tags'],
        'comment': ['content'],
        'attachment': ['file_name', 'description'],
    }
    
    @staticmethod
    def parse_query(query: str) -> Dict[str, Any]:
        """
        Parse a search query string into components.
        
        Supports:
        - Simple text: "bug fix"
        - Quoted phrases: "critical bug"
        - Field-specific: title:bug, status:open
        - Operators: AND, OR, NOT
        - Negation: -status:closed
        
        Returns:
            dict with parsed components
        """
        result = {
            'text_terms': [],
            'field_queries': {},
            'phrases': [],
            'excluded_terms': [],
        }
        
        if not query:
            return result
        
        # Extract quoted phrases
        phrase_pattern = r'"([^"]+)"'
        phrases = re.findall(phrase_pattern, query)
        result['phrases'] = phrases
        
        # Remove quoted phrases from query for further processing
        query_without_phrases = re.sub(phrase_pattern, '', query)
        
        # Extract field-specific queries (field:value)
        field_pattern = r'(\w+):([^\s]+)'
        field_matches = re.findall(field_pattern, query_without_phrases)
        for field, value in field_matches:
            if field not in result['field_queries']:
                result['field_queries'][field] = []
            result['field_queries'][field].append(value)
        
        # Remove field queries from query
        query_without_fields = re.sub(field_pattern, '', query_without_phrases)
        
        # Extract excluded terms (prefixed with -)
        excluded_pattern = r'-(\S+)'
        excluded = re.findall(excluded_pattern, query_without_fields)
        result['excluded_terms'] = excluded
        
        # Remove excluded terms
        query_clean = re.sub(excluded_pattern, '', query_without_fields)
        
        # Split remaining text into terms
        terms = [t.strip() for t in query_clean.split() if t.strip() and t.strip() not in ['AND', 'OR', 'NOT']]
        result['text_terms'] = terms
        
        return result
    
    @staticmethod
    def build_q_objects(parsed_query: Dict[str, Any], model_fields: List[str], model_class=None) -> Q:
        """
        Build Django Q objects from parsed query for a specific model.
        
        Args:
            parsed_query: Parsed query dictionary
            model_fields: List of field names to search in
            model_class: Optional model class to validate fields exist
        
        Returns:
            Q object for filtering
        """
        q_objects = Q()
        
        # Validate fields exist on model if model_class provided
        valid_fields = model_fields
        if model_class:
            valid_fields = [f for f in model_fields if hasattr(model_class, f)]
        
        # Text terms - search across all fields
        if parsed_query['text_terms'] and valid_fields:
            text_q = Q()
            for term in parsed_query['text_terms']:
                term_q = Q()
                for field in valid_fields:
                    try:
                        if field == 'tags':
                            # Tags are stored as JSON array - use JSONField lookup
                            term_q |= Q(**{f'{field}__icontains': term})
                        else:
                            term_q |= Q(**{f'{field}__icontains': term})
                    except Exception:
                        # Skip fields that cause errors
                        continue
                if term_q.children:  # Only add if we have valid conditions
                    text_q &= term_q  # All terms must match (AND)
            if text_q.children:
                q_objects &= text_q
        
        # Quoted phrases - exact phrase matching
        if parsed_query['phrases'] and valid_fields:
            phrase_q = Q()
            for phrase in parsed_query['phrases']:
                phrase_term_q = Q()
                for field in valid_fields:
                    try:
                        if field == 'tags':
                            phrase_term_q |= Q(**{f'{field}__icontains': phrase})
                        else:
                            phrase_term_q |= Q(**{f'{field}__icontains': phrase})
                    except Exception:
                        continue
                if phrase_term_q.children:
                    phrase_q |= phrase_term_q
            if phrase_q.children:
                q_objects &= phrase_q
        
        # Field-specific queries
        for field, values in parsed_query['field_queries'].items():
            if field in valid_fields or field in ['status', 'priority', 'assignee', 'reporter']:
                field_q = Q()
                for value in values:
                    try:
                        if field in ['status', 'priority']:
                            field_q |= Q(**{f'{field}__iexact': value})
                        elif field in ['assignee', 'reporter']:
                            # Handle UUID or email
                            field_q |= Q(**{f'{field}__id': value}) | Q(**{f'{field}__email__icontains': value})
                        else:
                            field_q |= Q(**{f'{field}__icontains': value})
                    except Exception:
                        continue
                if field_q.children:
                    q_objects &= field_q
        
        # Excluded terms
        if parsed_query['excluded_terms'] and valid_fields:
            exclude_q = Q()
            for term in parsed_query['excluded_terms']:
                for field in valid_fields:
                    try:
                        exclude_q |= Q(**{f'{field}__icontains': term})
                    except Exception:
                        continue
            if exclude_q.children:
                q_objects &= ~exclude_q  # NOT
        
        return q_objects
    
    @staticmethod
    def search(
        query: str,
        content_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        project: Optional[Project] = None,
        user=None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced search across multiple models.
        
        Args:
            query: Search query string
            content_types: List of content types to search (e.g., ['userstory', 'task'])
            filters: Additional filters (e.g., {'status': 'open', 'assignee': user_id})
            project: Optional project to limit search to
            user: User performing the search (for permission filtering)
            limit: Optional limit on results per model
        
        Returns:
            dict with search results organized by content type
        """
        if content_types is None:
            content_types = ['userstory', 'task', 'bug', 'issue', 'epic']
        
        if filters is None:
            filters = {}
        
        # Parse the query
        parsed_query = SearchService.parse_query(query)
        
        # Get accessible projects for user
        accessible_projects = []
        if user and not user.is_anonymous:
            if user.role == 'admin':
                accessible_projects = list(Project.objects.all().values_list('id', flat=True))
            else:
                accessible_projects = list(Project.objects.filter(
                    Q(owner=user) | Q(members__id=user.id)
                ).values_list('id', flat=True))
        
        results = {}
        
        # Search each content type
        for content_type in content_types:
            model_class = None
            search_fields = []
            
            if content_type == 'userstory':
                model_class = UserStory
                search_fields = SearchService.SEARCHABLE_FIELDS['userstory']
            elif content_type == 'task':
                model_class = Task
                search_fields = SearchService.SEARCHABLE_FIELDS['task']
            elif content_type == 'bug':
                model_class = Bug
                search_fields = SearchService.SEARCHABLE_FIELDS['bug']
            elif content_type == 'issue':
                model_class = Issue
                search_fields = SearchService.SEARCHABLE_FIELDS['issue']
            elif content_type == 'epic':
                model_class = Epic
                search_fields = SearchService.SEARCHABLE_FIELDS['epic']
            elif content_type == 'project':
                model_class = Project
                search_fields = SearchService.SEARCHABLE_FIELDS['project']
            
            if not model_class:
                continue
            
            # Build base queryset
            queryset = model_class.objects.all()
            
            # Apply project filter
            if project:
                if hasattr(model_class, 'project'):
                    queryset = queryset.filter(project=project)
            elif accessible_projects:
                # Filter to accessible projects
                if hasattr(model_class, 'project'):
                    queryset = queryset.filter(project_id__in=accessible_projects)
                elif hasattr(model_class, 'story') and hasattr(model_class.story, 'project'):
                    queryset = queryset.filter(story__project_id__in=accessible_projects)
            
            # Apply additional filters
            for filter_key, filter_value in filters.items():
                if hasattr(model_class, filter_key):
                    if isinstance(filter_value, list):
                        queryset = queryset.filter(**{f'{filter_key}__in': filter_value})
                    else:
                        queryset = queryset.filter(**{filter_key: filter_value})
            
            # Apply search query
            if query:
                try:
                    search_q = SearchService.build_q_objects(parsed_query, search_fields, model_class)
                    if search_q.children:  # Only filter if we have valid conditions
                        queryset = queryset.filter(search_q)
                except Exception as e:
                    # If search query building fails, return empty results for this content type
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Search query failed for {content_type}: {str(e)}")
                    results[content_type] = []
                    continue
            
            # Apply limit
            if limit:
                queryset = queryset[:limit]
            
            # Get appropriate fields based on model
            if content_type == 'project':
                # Project uses 'name' instead of 'title'
                results[content_type] = [
                    {
                        'id': item['id'],
                        'title': item.get('name', ''),
                        'created_at': item.get('created_at')
                    }
                    for item in queryset.values('id', 'name', 'created_at')
                ]
            else:
                # All other models use 'title'
                results[content_type] = list(queryset.values('id', 'title', 'created_at'))
        
        return results
    
    @staticmethod
    def search_unified(
        query: str,
        content_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        project: Optional[Project] = None,
        user=None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform unified search across all models and return a single sorted list.
        
        Returns:
            List of results with content_type and object data
        """
        results = SearchService.search(
            query=query,
            content_types=content_types,
            filters=filters,
            project=project,
            user=user,
            limit=limit
        )
        
        unified_results = []
        for content_type, items in results.items():
            for item in items:
                unified_results.append({
                    'content_type': content_type,
                    'id': str(item['id']),
                    'title': item.get('title', ''),
                    'created_at': item.get('created_at'),
                })
        
        # Sort by created_at (newest first)
        unified_results.sort(key=lambda x: x.get('created_at') or '', reverse=True)
        
        return unified_results


# Convenience function
def search(*args, **kwargs):
    """Convenience function to perform search."""
    return SearchService.search(*args, **kwargs)

