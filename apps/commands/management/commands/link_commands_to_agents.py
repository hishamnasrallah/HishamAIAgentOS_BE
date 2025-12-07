"""
Django management command to link commands to recommended agents based on capabilities.
"""

from django.core.management.base import BaseCommand
from apps.commands.models import CommandTemplate
from apps.agents.models import Agent


class Command(BaseCommand):
    help = 'Link commands to recommended agents based on their required capabilities'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("  LINKING COMMANDS TO RECOMMENDED AGENTS")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # Get all agents
        agents = {}
        agent_name_map = {}  # Map agent names to agent objects for fallback
        for agent in Agent.objects.all():
            agents[agent.agent_id] = agent
            # Also create a name-based lookup (normalized)
            normalized_name = agent.name.lower().replace(' ', '-').replace('/', '-')
            agent_name_map[normalized_name] = agent
            self.stdout.write(f"  Found agent: {agent.name} ({agent.agent_id})")
        
        if not agents:
            self.stdout.write(self.style.WARNING("  ⚠️  No agents found in database. Skipping agent linking."))
            return
        
        self.stdout.write("")
        
        # Get all commands without agents
        commands_without_agents = CommandTemplate.objects.filter(recommended_agent__isnull=True)
        total_unlinked = commands_without_agents.count()
        
        self.stdout.write(f"  Commands without agents: {total_unlinked}")
        self.stdout.write("")
        
        # Capability to agent mapping (using actual agent_ids from database)
        # Based on actual agents found: business-analyst, coding-agent, code-reviewer, 
        # project-manager, documentation-agent, qa-testing-agent, devops-agent, 
        # scrum-master, product-owner, bug-triage-agent, legal-agent, hr-agent, 
        # finance-agent, ux-designer, release-manager
        capability_to_agent = {
            'CODE_GENERATION': ['coding-agent'],
            'CODE_REVIEW': ['code-reviewer'],
            'REQUIREMENTS_ANALYSIS': ['business-analyst'],
            'USER_STORY_GENERATION': ['business-analyst'],
            'PROJECT_MANAGEMENT': ['project-manager', 'scrum-master', 'product-owner'],
            'TESTING': ['qa-testing-agent', 'bug-triage-agent'],
            'DOCUMENTATION': ['documentation-agent'],
            'DEVOPS': ['devops-agent', 'release-manager'],
            'DEPLOYMENT': ['devops-agent', 'release-manager'],
            'LEGAL_REVIEW': ['legal-agent'],
            'UX_DESIGN': ['ux-designer'],
            'RESEARCH': ['business-analyst'],  # Fallback to BA for research
        }
        
        linked_count = 0
        not_found_count = 0
        
        # Link commands to agents
        for command in commands_without_agents:
            matched_agent = None
            
            # First, try to match by capabilities
            if command.required_capabilities:
                for capability in command.required_capabilities:
                    agent_ids = capability_to_agent.get(capability, [])
                    
                    for agent_id in agent_ids:
                        if agent_id in agents:
                            matched_agent = agents[agent_id]
                            break
                    
                    if matched_agent:
                        break
            
            # If no match found, try to match by category
            if not matched_agent:
                category_slug = command.category.slug
                category_to_agent_map = {
                    'requirements-engineering': ['business-analyst'],
                    'code-generation': ['coding-agent'],
                    'code-review': ['code-reviewer'],
                    'testing-qa': ['qa-testing-agent', 'bug-triage-agent'],
                    'devops-deployment': ['devops-agent', 'release-manager'],
                    'documentation': ['documentation-agent'],
                    'project-management': ['project-manager', 'scrum-master', 'product-owner'],
                    'design-architecture': ['coding-agent'],
                    'legal-compliance': ['legal-agent'],
                    'business-analysis': ['business-analyst'],
                    'research-analysis': ['business-analyst'],  # Fallback to BA
                    'ux-ui-design': ['ux-designer'],
                }
                
                agent_ids = category_to_agent_map.get(category_slug, [])
                for agent_id in agent_ids:
                    if agent_id in agents:
                        matched_agent = agents[agent_id]
                        break
            
            if matched_agent:
                command.recommended_agent = matched_agent
                command.save(update_fields=['recommended_agent'])
                linked_count += 1
                self.stdout.write(f"  ✅ Linked '{command.name}' to {matched_agent.name}")
            else:
                not_found_count += 1
                caps_str = ', '.join(command.required_capabilities) if command.required_capabilities else 'None'
                self.stdout.write(self.style.WARNING(f"  ⚠️  No agent found for '{command.name}' (capabilities: {caps_str}, category: {command.category.slug})"))
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] COMPLETE!"))
        self.stdout.write(f"   Commands linked: {linked_count}")
        self.stdout.write(f"   Commands not linked: {not_found_count}")
        self.stdout.write(f"   Total processed: {total_unlinked}")
        self.stdout.write("=" * 70)

