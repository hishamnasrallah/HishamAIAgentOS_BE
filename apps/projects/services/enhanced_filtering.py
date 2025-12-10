"""
Enhanced filtering service for stories, tasks, bugs, and issues.
Supports filtering by tags, mentions, dependencies, date ranges, and custom fields.
"""

from django.db.models import Q, Prefetch
from django.utils import timezone
from datetime import timedelta, datetime
from typing import List, Dict, Any, Optional
from apps.projects.models import UserStory, Task, Bug, Issue, Mention, StoryDependency


class EnhancedFilteringService:
    """Service for advanced filtering of work items."""
    
    @staticmethod
    def filter_by_tags(queryset, tags: List[str], operator: str = 'contains'):
        """Filter by tags (multi-select)."""
        if not tags:
            return queryset
        
        if operator == 'contains':
            # Items that have any of the specified tags
            q = Q()
            for tag in tags:
                q |= Q(tags__icontains=tag)
            return queryset.filter(q).distinct()
        elif operator == 'not_contains':
            # Items that don't have any of the specified tags
            q = Q()
            for tag in tags:
                q |= Q(tags__icontains=tag)
            return queryset.exclude(q).distinct()
        elif operator == 'is_empty':
            return queryset.filter(Q(tags__isnull=True) | Q(tags=[]))
        
        return queryset
    
    @staticmethod
    def filter_by_mentions(queryset, user_ids: List[str], operator: str = 'contains'):
        """Filter by mentions."""
        if not user_ids:
            return queryset
        
        if operator == 'contains':
            # Items where the user is mentioned
            return queryset.filter(
                mentions__mentioned_user_id__in=user_ids
            ).distinct()
        elif operator == 'not_contains':
            # Items where the user is not mentioned
            return queryset.exclude(
                mentions__mentioned_user_id__in=user_ids
            ).distinct()
        elif operator == 'is_empty':
            return queryset.filter(mentions__isnull=True).distinct()
        
        return queryset
    
    @staticmethod
    def filter_by_dependencies(queryset, story_ids: List[str], dependency_type: str = 'has_dependencies'):
        """Filter by dependencies."""
        if not story_ids:
            return queryset
        
        if dependency_type == 'has_dependencies':
            # Items that have dependencies
            return queryset.filter(outgoing_dependencies__isnull=False).distinct()
        elif dependency_type == 'is_dependency':
            # Items that are dependencies of other items
            return queryset.filter(incoming_dependencies__isnull=False).distinct()
        elif dependency_type == 'blocks':
            # Items that block the specified stories
            return queryset.filter(
                outgoing_dependencies__target_story_id__in=story_ids,
                outgoing_dependencies__dependency_type='blocks'
            ).distinct()
        elif dependency_type == 'blocked_by':
            # Items that are blocked by the specified stories
            return queryset.filter(
                incoming_dependencies__source_story_id__in=story_ids,
                incoming_dependencies__dependency_type='blocks'
            ).distinct()
        elif dependency_type == 'no_dependencies':
            return queryset.filter(
                outgoing_dependencies__isnull=True,
                incoming_dependencies__isnull=True
            ).distinct()
        
        return queryset
    
    @staticmethod
    def filter_by_date_range(queryset, field: str, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None, preset: Optional[str] = None):
        """Filter by date range."""
        if preset:
            now = timezone.now()
            if preset == 'last_7_days':
                start_date = now - timedelta(days=7)
                end_date = now
            elif preset == 'last_30_days':
                start_date = now - timedelta(days=30)
                end_date = now
            elif preset == 'this_week':
                start_date = now - timedelta(days=now.weekday())
                end_date = now
            elif preset == 'this_month':
                start_date = now.replace(day=1)
                end_date = now
            elif preset == 'this_quarter':
                quarter = (now.month - 1) // 3
                start_date = now.replace(month=quarter * 3 + 1, day=1)
                end_date = now
        
        if start_date and end_date:
            return queryset.filter(**{
                f'{field}__gte': start_date,
                f'{field}__lte': end_date
            })
        elif start_date:
            return queryset.filter(**{f'{field}__gte': start_date})
        elif end_date:
            return queryset.filter(**{f'{field}__lte': end_date})
        
        return queryset
    
    @staticmethod
    def filter_by_custom_field(queryset, field_name: str, value: Any, operator: str = 'equals'):
        """Filter by custom field."""
        # Custom fields are stored in JSONField
        if operator == 'equals':
            return queryset.filter(**{f'custom_fields__{field_name}': value})
        elif operator == 'not_equals':
            return queryset.exclude(**{f'custom_fields__{field_name}': value})
        elif operator == 'contains':
            return queryset.filter(**{f'custom_fields__{field_name}__icontains': value})
        elif operator == 'not_contains':
            return queryset.exclude(**{f'custom_fields__{field_name}__icontains': value})
        
        return queryset
    
    @staticmethod
    def apply_filters(queryset, filters: List[Dict[str, Any]]):
        """Apply multiple filters to a queryset."""
        for filter_rule in filters:
            field = filter_rule.get('field')
            operator = filter_rule.get('operator')
            value = filter_rule.get('value')
            
            if field == 'tags':
                queryset = EnhancedFilteringService.filter_by_tags(queryset, value if isinstance(value, list) else [value], operator)
            elif field == 'mentions':
                queryset = EnhancedFilteringService.filter_by_mentions(queryset, value if isinstance(value, list) else [value], operator)
            elif field == 'dependencies':
                queryset = EnhancedFilteringService.filter_by_dependencies(queryset, value if isinstance(value, list) else [value], operator)
            elif field == 'date_range':
                queryset = EnhancedFilteringService.filter_by_date_range(queryset, 'created_at', preset=value)
            elif field == 'custom_field':
                field_name = filter_rule.get('custom_field_name')
                queryset = EnhancedFilteringService.filter_by_custom_field(queryset, field_name, value, operator)
        
        return queryset

