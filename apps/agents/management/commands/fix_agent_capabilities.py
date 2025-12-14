"""
Management command to fix agent capabilities.

Usage:
    python manage.py fix_agent_capabilities
    python manage.py fix_agent_capabilities --agent-id mistral-7b-assistant
"""

from django.core.management.base import BaseCommand
from apps.agents.models import Agent


class Command(BaseCommand):
    help = 'Fix agent capabilities - add CONVERSATION to chat agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--agent-id',
            type=str,
            help='Specific agent ID to fix'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fix all agents (adds CONVERSATION to all)'
        )

    def handle(self, *args, **options):
        agent_id = options.get('agent_id')
        fix_all = options.get('all', False)
        
        if agent_id:
            try:
                agents = [Agent.objects.get(agent_id=agent_id)]
            except Agent.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Agent {agent_id} not found'))
                return
        elif fix_all:
            # Fix ALL agents
            agents = Agent.objects.all()
            self.stdout.write(f"Fixing all {agents.count()} agents...\n")
        else:
            # Find all agents that are likely chat/conversation agents
            # This includes agents with "assistant" in name or used for chat
            agents = Agent.objects.filter(
                agent_id__icontains='assistant'
            ) | Agent.objects.filter(
                name__icontains='assistant'
            ) | Agent.objects.filter(
                name__icontains='chat'
            )
            
            # Also check for common AI model agents (mistral, gpt, claude, etc.)
            agents = agents | Agent.objects.filter(
                agent_id__icontains='mistral'
            ) | Agent.objects.filter(
                agent_id__icontains='gpt'
            ) | Agent.objects.filter(
                agent_id__icontains='claude'
            ) | Agent.objects.filter(
                agent_id__icontains='gemini'
            )
            
            agents = agents.distinct()
            self.stdout.write(f"Found {agents.count()} likely conversational agent(s) to check...\n")

        updated_count = 0
        skipped_count = 0
        
        for agent in agents:
            capabilities = agent.capabilities or []
            
            # Add CONVERSATION if not present
            if 'CONVERSATION' not in capabilities:
                capabilities.append('CONVERSATION')
                agent.capabilities = capabilities
                agent.save(update_fields=['capabilities'])
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Updated {agent.name} ({agent.agent_id}): Added CONVERSATION capability'
                    )
                )
                updated_count += 1
            else:
                self.stdout.write(
                    f'ℹ️  {agent.name} ({agent.agent_id}): Already has CONVERSATION capability'
                )
                skipped_count += 1

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            self.style.SUCCESS(f"✅ Summary:")
        )
        self.stdout.write(f"   Updated: {updated_count} agent(s)")
        self.stdout.write(f"   Already had CONVERSATION: {skipped_count} agent(s)")
        self.stdout.write(f"   Total checked: {updated_count + skipped_count} agent(s)")
        self.stdout.write("=" * 70)
        
        if updated_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  IMPORTANT: Restart your Django server for changes to take effect!"
                )
            )

