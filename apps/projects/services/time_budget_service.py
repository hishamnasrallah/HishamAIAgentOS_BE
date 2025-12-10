"""
Time Budget Service for managing time budgets and overtime tracking.
"""

from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Optional
from apps.projects.models import TimeBudget, OvertimeRecord, TimeLog, Project, Sprint, UserStory, Task


class TimeBudgetService:
    """Service for managing time budgets and tracking overtime."""
    
    @staticmethod
    def check_budgets(project_id: Optional[str] = None, sprint_id: Optional[str] = None) -> List[Dict]:
        """
        Check all active budgets and create overtime records if exceeded.
        
        Returns:
            List of budgets that exceeded their limits
        """
        from apps.projects.models import TimeBudget
        
        queryset = TimeBudget.objects.filter(is_active=True)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if sprint_id:
            queryset = queryset.filter(sprint_id=sprint_id)
        
        exceeded_budgets = []
        
        for budget in queryset:
            if budget.is_over_budget:
                # Check if overtime record already exists for this period
                period_start, period_end = TimeBudgetService._get_period_dates(budget)
                
                existing_record = OvertimeRecord.objects.filter(
                    time_budget=budget,
                    period_start=period_start,
                    period_end=period_end
                ).first()
                
                if not existing_record:
                    overtime_hours = budget.spent_hours - float(budget.budget_hours)
                    overtime_percentage = ((budget.spent_hours / float(budget.budget_hours)) - 1) * 100
                    
                    overtime_record = OvertimeRecord.objects.create(
                        time_budget=budget,
                        overtime_hours=overtime_hours,
                        overtime_percentage=round(overtime_percentage, 2),
                        period_start=period_start,
                        period_end=period_end
                    )
                    
                    exceeded_budgets.append({
                        'budget': budget,
                        'overtime_record': overtime_record,
                        'spent_hours': budget.spent_hours,
                        'budget_hours': float(budget.budget_hours),
                        'overtime_hours': overtime_hours,
                    })
                    
                    # Send alert if enabled
                    if budget.auto_alert:
                        TimeBudgetService._send_overtime_alert(budget, overtime_record)
        
        return exceeded_budgets
    
    @staticmethod
    def _get_period_dates(budget: TimeBudget) -> tuple:
        """Get start and end dates for budget period."""
        from django.utils import timezone
        
        if budget.period == 'custom' and budget.period_start and budget.period_end:
            return budget.period_start, budget.period_end
        elif budget.period == 'sprint' and budget.sprint:
            return budget.sprint.start_date, budget.sprint.end_date
        elif budget.period == 'project' and budget.project:
            return budget.project.start_date, budget.project.end_date
        elif budget.period == 'daily':
            today = timezone.now().date()
            return today, today
        elif budget.period == 'weekly':
            today = timezone.now().date()
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        elif budget.period == 'monthly':
            today = timezone.now().date()
            start = today.replace(day=1)
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            return start, end
        
        # Default to current date
        today = timezone.now().date()
        return today, today
    
    @staticmethod
    def _send_overtime_alert(budget: TimeBudget, overtime_record: OvertimeRecord):
        """Send overtime alert notification."""
        from apps.projects.services.notifications import get_notification_service
        
        try:
            notification_service = get_notification_service()
            
            # Determine recipients
            recipients = []
            if budget.user:
                recipients.append(budget.user)
            elif budget.project:
                recipients.extend([budget.project.owner] + list(budget.project.members.all()))
            
            for recipient in recipients:
                notification_service.create_notification(
                    recipient=recipient,
                    notification_type='overtime_alert',
                    title=f'Time Budget Exceeded: {budget}',
                    message=f'Budget exceeded by {overtime_record.overtime_hours} hours ({overtime_record.overtime_percentage}%)',
                    project=budget.project,
                    metadata={
                        'budget_id': str(budget.id),
                        'overtime_hours': float(overtime_record.overtime_hours),
                        'overtime_percentage': float(overtime_record.overtime_percentage),
                    }
                )
            
            overtime_record.alert_sent = True
            overtime_record.alert_sent_at = timezone.now()
            overtime_record.save(update_fields=['alert_sent', 'alert_sent_at'])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error sending overtime alert: {e}")
    
    @staticmethod
    def get_budget_summary(project_id: Optional[str] = None, sprint_id: Optional[str] = None) -> Dict:
        """Get summary of all budgets for a project or sprint."""
        from apps.projects.models import TimeBudget
        
        queryset = TimeBudget.objects.filter(is_active=True)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if sprint_id:
            queryset = queryset.filter(sprint_id=sprint_id)
        
        budgets = list(queryset)
        
        total_budget = sum(float(b.budget_hours) for b in budgets)
        total_spent = sum(b.spent_hours for b in budgets)
        total_remaining = sum(b.remaining_hours for b in budgets)
        over_budget_count = sum(1 for b in budgets if b.is_over_budget)
        warning_count = sum(1 for b in budgets if b.is_warning_threshold_reached and not b.is_over_budget)
        
        return {
            'total_budgets': len(budgets),
            'total_budget_hours': round(total_budget, 2),
            'total_spent_hours': round(total_spent, 2),
            'total_remaining_hours': round(total_remaining, 2),
            'over_budget_count': over_budget_count,
            'warning_count': warning_count,
            'budgets': [
                {
                    'id': str(b.id),
                    'scope': b.scope,
                    'budget_hours': float(b.budget_hours),
                    'spent_hours': b.spent_hours,
                    'remaining_hours': b.remaining_hours,
                    'utilization_percentage': b.utilization_percentage,
                    'is_over_budget': b.is_over_budget,
                    'is_warning': b.is_warning_threshold_reached,
                }
                for b in budgets
            ]
        }
    
    @staticmethod
    def get_overtime_history(
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get overtime history."""
        queryset = OvertimeRecord.objects.all()
        
        if project_id:
            queryset = queryset.filter(time_budget__project_id=project_id)
        if user_id:
            queryset = queryset.filter(time_budget__user_id=user_id)
        
        records = queryset.select_related('time_budget').order_by('-created_at')[:limit]
        
        return [
            {
                'id': str(r.id),
                'budget_id': str(r.time_budget.id),
                'budget_scope': r.time_budget.get_scope_display(),
                'overtime_hours': float(r.overtime_hours),
                'overtime_percentage': float(r.overtime_percentage),
                'period_start': r.period_start,
                'period_end': r.period_end,
                'alert_sent': r.alert_sent,
                'created_at': r.created_at,
            }
            for r in records
        ]


