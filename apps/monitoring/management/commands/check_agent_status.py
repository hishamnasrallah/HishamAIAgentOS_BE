"""
Django management command to check agent statuses and executions.
"""

from django.core.management.base import BaseCommand
from apps.agents.models import Agent, AgentExecution
from django.db.models import Count, Max, Q
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check agent statuses and their execution history'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('AGENT STATUS REPORT')
        self.stdout.write('=' * 60)
        self.stdout.write()
        
        agents = Agent.objects.all().order_by('name')
        
        self.stdout.write(f'Total Agents: {agents.count()}')
        self.stdout.write()
        
        for agent in agents:
            self.stdout.write(f'Agent: {agent.name}')
            self.stdout.write(f'  - ID: {agent.id}')
            self.stdout.write(f'  - Model Status: {agent.status}')
            self.stdout.write(f'  - Agent ID: {agent.agent_id}')
            
            # Get execution statistics
            total_executions = agent.executions.count()
            running_executions = agent.executions.filter(status='running').count()
            completed_executions = agent.executions.filter(status='completed').count()
            recent_executions = agent.executions.filter(
                started_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            self.stdout.write(f'  - Total Executions: {total_executions}')
            self.stdout.write(f'  - Running Executions: {running_executions}')
            self.stdout.write(f'  - Completed Executions: {completed_executions}')
            self.stdout.write(f'  - Executions (last 24h): {recent_executions}')
            
            # Get last execution
            last_execution = agent.executions.order_by('-started_at').first()
            if last_execution:
                self.stdout.write(f'  - Last Execution Status: {last_execution.status}')
                self.stdout.write(f'  - Last Execution Started: {last_execution.started_at}')
                self.stdout.write(f'  - Last Execution Completed: {last_execution.completed_at}')
                
                # Calculate dashboard status based on updated dashboard_views.py logic
                is_agent_available = agent.status == 'active'
                if last_execution.status == 'running':
                    dashboard_status = 'busy'
                elif is_agent_available:
                    dashboard_status = 'active'
                else:
                    dashboard_status = 'idle'
            else:
                self.stdout.write(f'  - Last Execution: None')
                # Agent is available but hasn't been used yet
                dashboard_status = 'active' if agent.status == 'active' else 'idle'
            
            self.stdout.write(f'  - Dashboard Status: {dashboard_status}')
            self.stdout.write()
        
        self.stdout.write('=' * 60)
        self.stdout.write('SUMMARY')
        self.stdout.write('=' * 60)
        
        # Count by dashboard status
        active_count = 0
        busy_count = 0
        idle_count = 0
        
        for agent in agents:
            last_execution = agent.executions.order_by('-started_at').first()
            is_agent_available = agent.status == 'active'
            
            if last_execution:
                if last_execution.status == 'running':
                    busy_count += 1
                elif is_agent_available:
                    active_count += 1
                else:
                    idle_count += 1
            else:
                # Agent is available but hasn't been used yet
                if is_agent_available:
                    active_count += 1
                else:
                    idle_count += 1
        
        self.stdout.write(f'Active Agents: {active_count}')
        self.stdout.write(f'Busy Agents: {busy_count}')
        self.stdout.write(f'Idle Agents: {idle_count}')
        self.stdout.write()

