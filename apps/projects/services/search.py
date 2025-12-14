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
        # Updated pattern to handle values that might contain special characters like @ in emails and - in UUIDs
        # Pattern: word characters for field, then :, then any characters until whitespace, quote, or end of string
        # We need to allow hyphens for UUIDs, @ for emails, etc.
        # Use a more permissive pattern: field:value where value can contain alphanumeric, @, ., -, and _
        field_pattern = r'(\w+):([^\s"\'()]+)'
        field_matches = re.findall(field_pattern, query_without_phrases)
        for field, value in field_matches:
            if field not in result['field_queries']:
                result['field_queries'][field] = []
            # Clean up the value (remove any trailing punctuation that might have been captured)
            # But preserve @, ., and - for email addresses and UUIDs
            value = value.rstrip('.,;:!?')
            if value:  # Only add non-empty values
                result['field_queries'][field].append(value)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        if result['field_queries']:
            logger.debug(f"Parsed field queries: {result['field_queries']}")
        
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
        # Start with a Q object that matches nothing (we'll build it up)
        # Using Q() and then combining with &= means we need at least one condition
        q_objects = None
        
        # Validate fields exist on model if model_class provided
        valid_fields = model_fields
        if model_class:
            valid_fields = [f for f in model_fields if hasattr(model_class, f)]
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Building Q objects: parsed_query={parsed_query}, valid_fields={valid_fields}, model={model_class.__name__ if model_class else 'None'}")
        
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
                            # Use icontains for case-insensitive partial matching
                            term_q |= Q(**{f'{field}__icontains': term})
                    except Exception as e:
                        # Skip fields that cause errors
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug(f"Skipping field {field} for term {term}: {e}")
                        continue
                if term_q.children:  # Only add if we have valid conditions
                    text_q &= term_q  # All terms must match (AND between terms)
            if text_q.children:
                if q_objects is None:
                    q_objects = text_q
                else:
                    q_objects &= text_q  # Combine with other conditions using AND
        
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
                if q_objects is None:
                    q_objects = phrase_q
                else:
                    q_objects &= phrase_q
        
        # Field-specific queries
        # Special handling: if both 'assigned_to' and 'owner' are specified with the same values,
        # combine them with OR logic (since different models use different field names)
        user_fields = ['assigned_to', 'owner', 'assignee', 'reporter']
        user_field_values = {}
        other_field_queries = {}
        
        for field, values in parsed_query['field_queries'].items():
            if field in user_fields:
                # Collect user field queries to handle OR logic
                if field not in user_field_values:
                    user_field_values[field] = []
                user_field_values[field].extend(values)
            else:
                other_field_queries[field] = values
        
        # Process user fields with OR logic if both assigned_to and owner are present
        if 'assigned_to' in user_field_values or 'owner' in user_field_values or 'assignee' in user_field_values or 'reporter' in user_field_values:
            user_field_q = Q()
            all_user_values = set()
            if 'assigned_to' in user_field_values:
                all_user_values.update(user_field_values['assigned_to'])
            if 'owner' in user_field_values:
                all_user_values.update(user_field_values['owner'])
            if 'assignee' in user_field_values:
                all_user_values.update(user_field_values['assignee'])
            if 'reporter' in user_field_values:
                all_user_values.update(user_field_values['reporter'])
            
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Processing user fields: {user_field_values}, all_user_values: {all_user_values}, model: {model_class.__name__ if model_class else 'None'}")
            
            for value in all_user_values:
                value_q = Q()
                from apps.authentication.models import User
                user_found = False
                user = None
                
                # Try to find user by UUID first
                try:
                    user = User.objects.get(id=value)
                    user_found = True
                except (User.DoesNotExist, ValueError):
                    # Try to find by email (case-insensitive)
                    try:
                        user = User.objects.get(email__iexact=value)
                        user_found = True
                    except User.DoesNotExist:
                        pass
                
                if user_found and user:
                    # User found - use direct user object matching (most efficient)
                    if model_class:
                        if hasattr(model_class, 'assigned_to'):
                            value_q |= Q(**{'assigned_to': user})
                        if hasattr(model_class, 'owner'):
                            value_q |= Q(**{'owner': user})
                        if hasattr(model_class, 'assignee'):
                            value_q |= Q(**{'assignee': user})
                        if hasattr(model_class, 'reporter'):
                            value_q |= Q(**{'reporter': user})
                    else:
                        # If no model_class, try all fields
                        value_q |= Q(**{'assigned_to': user}) | Q(**{'owner': user})
                else:
                    # User not found by UUID or email - try name-based matching
                    if model_class:
                        if hasattr(model_class, 'assigned_to'):
                            value_q |= (
                                Q(**{'assigned_to__first_name__icontains': value}) |
                                Q(**{'assigned_to__last_name__icontains': value}) |
                                Q(**{'assigned_to__username__icontains': value}) |
                                Q(**{'assigned_to__email__icontains': value})
                            )
                        if hasattr(model_class, 'owner'):
                            value_q |= (
                                Q(**{'owner__first_name__icontains': value}) |
                                Q(**{'owner__last_name__icontains': value}) |
                                Q(**{'owner__username__icontains': value}) |
                                Q(**{'owner__email__icontains': value})
                            )
                    else:
                        value_q |= (
                            Q(**{'assigned_to__first_name__icontains': value}) |
                            Q(**{'assigned_to__last_name__icontains': value}) |
                            Q(**{'assigned_to__username__icontains': value}) |
                            Q(**{'assigned_to__email__icontains': value}) |
                            Q(**{'owner__first_name__icontains': value}) |
                            Q(**{'owner__last_name__icontains': value}) |
                            Q(**{'owner__username__icontains': value}) |
                            Q(**{'owner__email__icontains': value})
                        )
                
                if value_q.children:
                    user_field_q |= value_q
                    logger.debug(f"Added user field condition for value '{value}': {value_q}, user_found={user_found}, user={user.email if user else 'None'}")
                else:
                    # Log if no conditions were added for debugging
                    logger.warning(f"No conditions added for user field value: '{value}', model: {model_class.__name__ if model_class else 'None'}, user_found={user_found}")
            
            if user_field_q.children:
                logger.debug(f"User field Q object has conditions: {user_field_q}")
                if q_objects is None:
                    q_objects = user_field_q
                else:
                    q_objects &= user_field_q
            else:
                logger.warning(f"User field Q object is empty for values: {all_user_values}, model: {model_class.__name__ if model_class else 'None'}")
        
        # Process other field queries
        for field, values in other_field_queries.items():
            # Map 'owner' to 'assigned_to' for models that don't have 'owner' field
            # Epic and Project have 'owner', but UserStory, Task, Bug, Issue have 'assigned_to'
            actual_field = field
            if model_class:
                if field == 'owner' and not hasattr(model_class, 'owner') and hasattr(model_class, 'assigned_to'):
                    actual_field = 'assigned_to'
                elif field == 'assigned_to' and not hasattr(model_class, 'assigned_to') and hasattr(model_class, 'owner'):
                    actual_field = 'owner'
            
            # Check if field is in valid_fields or is a special field
            # Also check if the field exists on the model (for fields like 'owner', 'assigned_to')
            special_fields = ['status', 'priority', 'title', 'description', 'acceptance_criteria']
            field_exists = False
            if model_class:
                # Check if field exists on the model (using actual_field)
                field_exists = hasattr(model_class, actual_field)
            
            if field in valid_fields or field in special_fields or field_exists:
                field_q = Q()
                for value in values:
                    try:
                        if actual_field in ['status', 'priority']:
                            field_q |= Q(**{f'{actual_field}__iexact': value})
                        else:
                            # For text fields, use icontains for case-insensitive partial matching
                            field_q |= Q(**{f'{actual_field}__icontains': value})
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug(f"Error building field query for {field}={value} (actual_field={actual_field}): {e}")
                        continue
                if field_q.children:
                    if q_objects is None:
                        q_objects = field_q
                    else:
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
                if q_objects is None:
                    q_objects = ~exclude_q
                else:
                    q_objects &= ~exclude_q  # NOT
        
        # If no conditions were added, return an empty Q object (matches nothing)
        if q_objects is None:
            q_objects = Q()
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        # Check if Q object has children - it might be a Q() with no children (empty) or Q() with children
        has_children = bool(q_objects.children) if q_objects else False
        logger.debug(
            f"Built Q object: has_children={has_children}, "
            f"parsed_query={parsed_query}, valid_fields={valid_fields}, "
            f"q_objects={q_objects}, type={type(q_objects)}"
        )
        
        # If we have an empty Q object but field_queries exist, log a warning
        if not has_children and parsed_query.get('field_queries'):
            logger.warning(f"Q object is empty but field_queries exist: {parsed_query.get('field_queries')}")
        
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
            from apps.core.services.roles import RoleService
            if RoleService.is_admin(user):
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
                elif hasattr(model_class, 'story') and hasattr(model_class.story, 'project'):
                    # For Task model, filter through story
                    queryset = queryset.filter(story__project=project)
            elif accessible_projects:
                # Filter to accessible projects
                if hasattr(model_class, 'project'):
                    queryset = queryset.filter(project_id__in=accessible_projects)
                elif hasattr(model_class, 'story') and hasattr(model_class.story, 'project'):
                    queryset = queryset.filter(story__project_id__in=accessible_projects)
            
            # Debug: Log queryset count before search filter
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Base queryset for {content_type} (project={project.id if project else 'all'}): {queryset.count()} items")
            
            # Apply additional filters
            for filter_key, filter_value in filters.items():
                if hasattr(model_class, filter_key):
                    if isinstance(filter_value, list):
                        queryset = queryset.filter(**{f'{filter_key}__in': filter_value})
                    else:
                        queryset = queryset.filter(**{filter_key: filter_value})
            
            # Apply search query
            if query and query.strip():
                try:
                    search_q = SearchService.build_q_objects(parsed_query, search_fields, model_class)
                    if search_q.children:  # Only filter if we have valid conditions
                        queryset_before = queryset.count()
                        queryset = queryset.filter(search_q)
                        queryset_after = queryset.count()
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.debug(
                            f"Applied search filter for {content_type}: "
                            f"{queryset_before} -> {queryset_after} items, "
                            f"Q object: {search_q}"
                        )
                    else:
                        # If query exists but no valid conditions were built, return empty results
                        # This means the query couldn't be matched to any searchable fields
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Search query '{query}' resulted in empty Q object for {content_type}. Parsed: {parsed_query}")
                        results[content_type] = []
                        continue
                except Exception as e:
                    # If search query building fails, log error but don't fail completely
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Search query failed for {content_type}: {str(e)}", exc_info=True)
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
                result_list = list(queryset.values('id', 'title', 'created_at'))
                results[content_type] = result_list
                
                # Debug: Log final result count
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Final results for {content_type}: {len(result_list)} items")
                if len(result_list) > 0:
                    logger.debug(f"Sample result: {result_list[0]}")
        
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

