"""
Export/Import Service.
Handles exporting and importing stories, tasks, and other work items.
"""

import csv
import json
from io import StringIO, BytesIO
from typing import Dict, List, Optional
from django.http import HttpResponse
from apps.projects.models import UserStory, Task, Bug, Issue, Project


class ExportImportService:
    """Service for exporting and importing data."""
    
    @staticmethod
    def export_stories_to_csv(project_id: str, story_ids: Optional[List[str]] = None) -> HttpResponse:
        """
        Export stories to CSV.
        
        Returns:
            HttpResponse with CSV file
        """
        queryset = UserStory.objects.filter(project_id=project_id)
        
        if story_ids:
            queryset = queryset.filter(id__in=story_ids)
        
        stories = queryset.select_related('assigned_to', 'epic', 'sprint').order_by('created_at')
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Description', 'Status', 'Priority', 'Story Points',
            'Story Type', 'Component', 'Assigned To', 'Epic', 'Sprint',
            'Due Date', 'Tags', 'Labels', 'Created At', 'Updated At'
        ])
        
        # Write data
        for story in stories:
            writer.writerow([
                str(story.id),
                story.title,
                story.description,
                story.status,
                story.priority,
                story.story_points or '',
                story.story_type,
                story.component or '',
                story.assigned_to.email if story.assigned_to else '',
                story.epic.title if story.epic else '',
                story.sprint.name if story.sprint else '',
                story.due_date.isoformat() if story.due_date else '',
                ','.join(story.tags) if story.tags else '',
                ','.join(str(l) for l in story.labels) if story.labels else '',
                story.created_at.isoformat(),
                story.updated_at.isoformat(),
            ])
        
        # Create response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="stories_export_{project_id}.csv"'
        
        return response
    
    @staticmethod
    def export_stories_to_excel(project_id: str, story_ids: Optional[List[str]] = None) -> HttpResponse:
        """
        Export stories to Excel.
        
        Returns:
            HttpResponse with Excel file
        """
        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment
        except ImportError:
            # Fallback to CSV if openpyxl not available
            return ExportImportService.export_stories_to_csv(project_id, story_ids)
        
        queryset = UserStory.objects.filter(project_id=project_id)
        
        if story_ids:
            queryset = queryset.filter(id__in=story_ids)
        
        stories = queryset.select_related('assigned_to', 'epic', 'sprint').order_by('created_at')
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Stories"
        
        # Write header
        headers = [
            'ID', 'Title', 'Description', 'Status', 'Priority', 'Story Points',
            'Story Type', 'Component', 'Assigned To', 'Epic', 'Sprint',
            'Due Date', 'Tags', 'Labels', 'Created At', 'Updated At'
        ]
        ws.append(headers)
        
        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Write data
        for story in stories:
            ws.append([
                str(story.id),
                story.title,
                story.description,
                story.status,
                story.priority,
                story.story_points or '',
                story.story_type,
                story.component or '',
                story.assigned_to.email if story.assigned_to else '',
                story.epic.title if story.epic else '',
                story.sprint.name if story.sprint else '',
                story.due_date.isoformat() if story.due_date else '',
                ','.join(story.tags) if story.tags else '',
                ','.join(str(l) for l in story.labels) if story.labels else '',
                story.created_at.isoformat(),
                story.updated_at.isoformat(),
            ])
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Create response
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="stories_export_{project_id}.xlsx"'
        
        return response
    
    @staticmethod
    def import_stories_from_csv(project_id: str, csv_file) -> Dict:
        """
        Import stories from CSV file.
        
        Returns:
            Dict with import results
        """
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return {'error': 'Project not found'}
        
        # Read CSV
        decoded_file = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(decoded_file))
        
        imported = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Create story
                story = UserStory.objects.create(
                    project=project,
                    title=row.get('Title', ''),
                    description=row.get('Description', ''),
                    status=row.get('Status', 'backlog'),
                    priority=row.get('Priority', 'medium'),
                    story_points=int(row['Story Points']) if row.get('Story Points') else None,
                    story_type=row.get('Story Type', 'feature'),
                    component=row.get('Component', ''),
                )
                
                # Parse tags
                if row.get('Tags'):
                    story.tags = [tag.strip() for tag in row['Tags'].split(',') if tag.strip()]
                
                story.save()
                
                imported.append({
                    'row': row_num,
                    'story_id': str(story.id),
                    'title': story.title,
                })
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'error': str(e),
                })
        
        return {
            'imported_count': len(imported),
            'error_count': len(errors),
            'imported': imported,
            'errors': errors,
        }

