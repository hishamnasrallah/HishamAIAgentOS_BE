"""
Django management command to verify command library statistics.
"""

from django.core.management.base import BaseCommand
from apps.commands.models import CommandCategory, CommandTemplate
from apps.agents.models import Agent


class Command(BaseCommand):
    help = 'Verify command library statistics and count'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("  HISHAMOS COMMAND LIBRARY VERIFICATION")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # Get statistics
        total_commands = CommandTemplate.objects.count()
        total_categories = CommandCategory.objects.count()
        total_agents = Agent.objects.count()
        
        # Commands with agents
        commands_with_agents = CommandTemplate.objects.exclude(recommended_agent__isnull=True).count()
        commands_without_agents = CommandTemplate.objects.filter(recommended_agent__isnull=True).count()
        
        # Commands by category
        self.stdout.write("📊 OVERALL STATISTICS")
        self.stdout.write("-" * 70)
        self.stdout.write(f"  Total Commands: {total_commands}/325 ({total_commands/325*100:.1f}%)")
        self.stdout.write(f"  Total Categories: {total_categories}/12")
        self.stdout.write(f"  Total Agents: {total_agents}")
        self.stdout.write(f"  Commands with Agents: {commands_with_agents}")
        self.stdout.write(f"  Commands without Agents: {commands_without_agents}")
        self.stdout.write("")
        
        # Commands by category
        self.stdout.write("📋 COMMANDS BY CATEGORY")
        self.stdout.write("-" * 70)
        
        categories = CommandCategory.objects.all().order_by('order', 'name')
        total_by_category = 0
        
        for category in categories:
            count = category.commands.count()
            total_by_category += count
            percentage = (count / 325) * 100 if 325 > 0 else 0
            status = "✅" if count > 0 else "❌"
            
            self.stdout.write(
                f"  {status} {category.icon} {category.name:30} {count:3} commands ({percentage:.1f}%)"
            )
        
        self.stdout.write("-" * 70)
        self.stdout.write(f"  {'Total':30} {total_by_category:3} commands")
        self.stdout.write("")
        
        # Commands by agent
        if total_agents > 0:
            self.stdout.write("🤖 COMMANDS BY RECOMMENDED AGENT")
            self.stdout.write("-" * 70)
            
            agents = Agent.objects.all().order_by('name')
            for agent in agents:
                count = agent.recommended_commands.count()
                if count > 0:
                    self.stdout.write(f"  {agent.name:30} {count:3} commands")
            
            if commands_without_agents > 0:
                self.stdout.write(f"  {'No Agent Assigned':30} {commands_without_agents:3} commands")
            self.stdout.write("")
        
        # Commands with required capabilities
        self.stdout.write("🔧 COMMANDS BY CAPABILITY")
        self.stdout.write("-" * 70)
        
        capability_counts = {}
        all_commands = CommandTemplate.objects.all()
        
        for command in all_commands:
            for capability in command.required_capabilities:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
        
        for capability, count in sorted(capability_counts.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f"  {capability:30} {count:3} commands")
        self.stdout.write("")
        
        # Recent commands (last 10)
        self.stdout.write("🆕 RECENTLY ADDED COMMANDS (Last 10)")
        self.stdout.write("-" * 70)
        
        recent_commands = CommandTemplate.objects.all().order_by('-created_at')[:10]
        for command in recent_commands:
            created_date = command.created_at.strftime('%Y-%m-%d %H:%M')
            self.stdout.write(f"  {command.name:50} ({created_date})")
        self.stdout.write("")
        
        # Progress to targets
        self.stdout.write("🎯 PROGRESS TO TARGETS")
        self.stdout.write("-" * 70)
        
        targets = [
            (100, "100 commands (30.8%)"),
            (150, "150 commands (46.2%)"),
            (200, "200 commands (61.5%)"),
            (250, "250 commands (76.9%)"),
            (325, "325 commands (100%)")
        ]
        
        for target, label in targets:
            if total_commands >= target:
                status = "✅"
            elif total_commands >= target * 0.8:
                status = "🟡"
            else:
                status = "❌"
            
            progress = (total_commands / target * 100) if target > 0 else 0
            self.stdout.write(f"  {status} {label:30} Current: {total_commands} ({progress:.1f}%)")
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        
        # Recommendations
        if total_commands < 200:
            needed = 200 - total_commands
            self.stdout.write(self.style.WARNING(f"⚠️  Need {needed} more commands to reach 200 (61.5% target)"))
        
        if commands_without_agents > 0 and total_agents > 0:
            self.stdout.write(self.style.WARNING(f"⚠️  {commands_without_agents} commands need agent assignments"))
        
        if total_commands >= 200:
            self.stdout.write(self.style.SUCCESS("✅ Great progress! Over 200 commands loaded."))
        
        self.stdout.write("=" * 70)

