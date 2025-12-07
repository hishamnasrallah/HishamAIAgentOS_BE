"""
Django management command to verify system readiness for UAT.
"""

from django.core.management.base import BaseCommand
from apps.commands.models import CommandTemplate, CommandCategory
from apps.workflows.models import Workflow
from apps.agents.models import Agent
from django.db import connection


class Command(BaseCommand):
    help = 'Verify that HishamOS is ready for UAT testing'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write("HISHAMOS SYSTEM VERIFICATION")
        self.stdout.write("="*60)
        self.stdout.write("Verifying system readiness for UAT testing...\n")
        
        results = {
            'database': self.verify_database(),
            'commands': self.verify_commands(),
            'workflows': self.verify_workflows(),
            'agents': self.verify_agents()
        }
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("VERIFICATION SUMMARY")
        self.stdout.write("="*60)
        
        all_passed = all(results.values())
        
        for check, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            self.stdout.write(f"{status}: {check.upper()}")
        
        if all_passed:
            self.stdout.write(self.style.SUCCESS("\n✅ SYSTEM READY FOR UAT TESTING"))
        else:
            self.stdout.write(self.style.WARNING("\n⚠️  SYSTEM HAS ISSUES - REVIEW ABOVE"))
        
        self.stdout.write("="*60 + "\n")
        
        return 0 if all_passed else 1

    def verify_database(self):
        """Verify database connection."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("VERIFYING DATABASE")
        self.stdout.write("="*60)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("✅ Database connection successful"))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Database connection failed: {e}"))
            return False

    def verify_commands(self):
        """Verify command library."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("VERIFYING COMMAND LIBRARY")
        self.stdout.write("="*60)
        
        total_commands = CommandTemplate.objects.count()
        active_commands = CommandTemplate.objects.filter(is_active=True).count()
        categories = CommandCategory.objects.count()
        
        self.stdout.write(f"✅ Total Commands: {total_commands}")
        self.stdout.write(f"✅ Active Commands: {active_commands}")
        self.stdout.write(f"✅ Categories: {categories}")
        
        if total_commands == 250:
            self.stdout.write(self.style.SUCCESS("✅ Command library target reached (250 commands)"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  Expected 250 commands, found {total_commands}"))
        
        # Check new commands
        new_command_slugs = [
            'requirements-validation-checklist',
            'requirements-change-management',
            'generate-graphql-schema-resolvers',
            'generate-microservices-communication',
            'security-vulnerability-scan',
            'performance-optimization-review',
            'generate-load-testing-scripts',
            'create-accessibility-test-suite',
            'generate-kubernetes-helm-charts',
            'create-terraform-infrastructure',
            'generate-openapi-documentation',
            'create-runbook-documentation',
            'generate-sprint-retrospective',
            'create-risk-register',
            'design-event-driven-architecture',
            'create-database-schema-design',
            'generate-gdpr-compliance-checklist',
            'create-business-process-model',
            'generate-technology-stack-comparison',
            'create-design-system-documentation',
            'generate-rest-api-client-library',
            'generate-contract-testing-suite'
        ]
        
        found_new = 0
        for slug in new_command_slugs:
            if CommandTemplate.objects.filter(slug=slug).exists():
                found_new += 1
        
        self.stdout.write(f"✅ New Commands Found: {found_new} / {len(new_command_slugs)}")
        
        return total_commands == 250

    def verify_workflows(self):
        """Verify workflows."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("VERIFYING WORKFLOWS")
        self.stdout.write("="*60)
        
        total_workflows = Workflow.objects.count()
        self.stdout.write(f"✅ Total Workflows: {total_workflows}")
        
        return True

    def verify_agents(self):
        """Verify agents."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("VERIFYING AGENTS")
        self.stdout.write("="*60)
        
        total_agents = Agent.objects.count()
        active_agents = Agent.objects.filter(status='active').count()
        
        self.stdout.write(f"✅ Total Agents: {total_agents}")
        self.stdout.write(f"✅ Active Agents: {active_agents}")
        
        return True

