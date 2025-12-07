"""
Django management command to create command library.
"""

from django.core.management.base import BaseCommand
from apps.commands.models import CommandCategory, CommandTemplate
from apps.agents.models import Agent


class Command(BaseCommand):
    help = 'Create command categories and command templates'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("  HISHAMOS COMMAND LIBRARY SETUP")
        self.stdout.write("=" * 60)
        self.stdout.write("")
        
        # Create categories
        self.stdout.write("Step 1: Creating command categories...")
        categories = self.create_categories()
        
        # Create commands
        self.stdout.write("\nStep 2: Creating command templates...")
        total_created, total_updated = self.create_commands(categories)
        
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] COMPLETE!"))
        self.stdout.write(f"   Commands: {total_created} created, {total_updated} updated")
        self.stdout.write(f"   Categories: {categories.count()} total")
        self.stdout.write("=" * 60)

    def create_categories(self):
        """Create all 12 command categories."""
        categories_data = [
            {'name': 'Requirements Engineering', 'slug': 'requirements-engineering', 'description': 'Transform ideas into detailed requirements, user stories, and specifications', 'icon': '📋', 'order': 1},
            {'name': 'Code Generation', 'slug': 'code-generation', 'description': 'Generate high-quality production code across multiple languages and frameworks', 'icon': '💻', 'order': 2},
            {'name': 'Code Review', 'slug': 'code-review', 'description': 'Comprehensive code review and quality analysis', 'icon': '🔍', 'order': 3},
            {'name': 'Testing & QA', 'slug': 'testing-qa', 'description': 'Test generation, quality assurance, and validation', 'icon': '✅', 'order': 4},
            {'name': 'DevOps & Deployment', 'slug': 'devops-deployment', 'description': 'CI/CD, infrastructure, and deployment automation', 'icon': '🚀', 'order': 5},
            {'name': 'Documentation', 'slug': 'documentation', 'description': 'Technical writing, API docs, and user guides', 'icon': '📚', 'order': 6},
            {'name': 'Project Management', 'slug': 'project-management', 'description': 'Sprint planning, task breakdown, and project tracking', 'icon': '📊', 'order': 7},
            {'name': 'Design & Architecture', 'slug': 'design-architecture', 'description': 'System design, architecture decisions, and technical planning', 'icon': '🏗️', 'order': 8},
            {'name': 'Legal & Compliance', 'slug': 'legal-compliance', 'description': 'Contracts, policies, and regulatory compliance', 'icon': '⚖️', 'order': 9},
            {'name': 'Business Analysis', 'slug': 'business-analysis', 'description': 'Market research, ROI analysis, and business strategy', 'icon': '💼', 'order': 10},
            {'name': 'UX/UI Design', 'slug': 'ux-ui-design', 'description': 'User experience, interface design, and usability', 'icon': '🎨', 'order': 11},
            {'name': 'Research & Analysis', 'slug': 'research-analysis', 'description': 'Technology research, competitive analysis, and insights', 'icon': '🔬', 'order': 12}
        ]
        
        created = 0
        updated = 0
        
        for cat_data in categories_data:
            category, created_flag = CommandCategory.objects.update_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created_flag:
                created += 1
                self.stdout.write(f"  [+] Created category: {category.name}")
            else:
                updated += 1
                self.stdout.write(f"  [*] Updated category: {category.name}")
        
        self.stdout.write(f"\n[CATEGORIES] {created} created, {updated} updated")
        return CommandCategory.objects.all()

    def create_commands(self, categories):
        """Create command templates."""
        cat_map = {cat.slug: cat for cat in categories}
        total_created = 0
        total_updated = 0
        
        # Get agents (use None if agent doesn't exist)
        agents = {}
        agent_ids = {
            'business-analyst': 'ba_agent',
            'coding-agent': 'coding_agent',
            'code-reviewer': 'reviewer_agent',
            'qa-testing-agent': 'qa_agent',  # Updated agent_id
            'devops-agent': 'devops_agent',
            'documentation-agent': 'doc_agent',
            'project-manager': 'pm_agent',
            'legal-agent': 'legal_agent',
            'research-agent': 'research_agent'
        }
        
        for agent_id, var_name in agent_ids.items():
            try:
                agents[var_name] = Agent.objects.get(agent_id=agent_id)
            except Agent.DoesNotExist:
                agents[var_name] = None
                self.stdout.write(self.style.WARNING(f"  [!] Agent '{agent_id}' not found, commands will be created without agent"))
        
        # Import templates
        from apps.commands.command_templates import (
            get_requirements_commands,
            get_code_generation_commands,
            get_code_review_commands,
            get_testing_commands,
            get_devops_commands,
            get_documentation_commands,
            get_project_management_commands,
            get_design_architecture_commands,
            get_legal_compliance_commands,
            get_business_analysis_commands,
            get_research_analysis_commands,
            get_ux_ui_design_commands
        )
        
        # Collect all commands
        commands_data = []
        commands_data.extend(get_requirements_commands(cat_map['requirements-engineering'], agents['ba_agent']))
        commands_data.extend(get_code_generation_commands(cat_map['code-generation'], agents['coding_agent']))
        commands_data.extend(get_code_review_commands(cat_map['code-review'], agents['reviewer_agent']))
        commands_data.extend(get_testing_commands(cat_map['testing-qa'], agents['qa_agent']))
        commands_data.extend(get_devops_commands(cat_map['devops-deployment'], agents['devops_agent']))
        commands_data.extend(get_documentation_commands(cat_map['documentation'], agents['doc_agent']))
        commands_data.extend(get_project_management_commands(cat_map['project-management'], agents['pm_agent']))
        commands_data.extend(get_design_architecture_commands(cat_map['design-architecture'], agents['coding_agent']))
        commands_data.extend(get_legal_compliance_commands(cat_map['legal-compliance'], agents['legal_agent']))
        commands_data.extend(get_business_analysis_commands(cat_map['business-analysis'], agents['ba_agent']))
        commands_data.extend(get_research_analysis_commands(cat_map['research-analysis'], agents['research_agent']))
        commands_data.extend(get_ux_ui_design_commands(cat_map['ux-ui-design'], agents['coding_agent']))
        
        # Create/update commands
        for cmd_data in commands_data:
            command, created = CommandTemplate.objects.update_or_create(
                slug=cmd_data['slug'],
                defaults=cmd_data
            )
            if created:
                total_created += 1
                self.stdout.write(f"  [+] {command.name}")
            else:
                total_updated += 1
                self.stdout.write(f"  [*] {command.name}")
        
        return total_created, total_updated
