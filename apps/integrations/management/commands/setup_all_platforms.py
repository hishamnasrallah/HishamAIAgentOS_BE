"""
Django management command to set up all AI platforms at once.

This command helps you set up multiple AI platforms quickly by prompting for API keys.

Usage:
    python manage.py setup_all_platforms
    
Or with API keys:
    python manage.py setup_all_platforms --openai-key KEY --anthropic-key KEY --gemini-key KEY --openrouter-key KEY
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import sys


class Command(BaseCommand):
    help = 'Set up all AI platforms (OpenAI, Anthropic, Gemini, OpenRouter)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--openai-key',
            type=str,
            help='OpenAI API key'
        )
        parser.add_argument(
            '--anthropic-key',
            type=str,
            help='Anthropic API key'
        )
        parser.add_argument(
            '--gemini-key',
            type=str,
            help='Google Gemini API key'
        )
        parser.add_argument(
            '--openrouter-key',
            type=str,
            help='OpenRouter API key'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip platforms that already exist'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing platforms'
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("  SETTING UP ALL AI PLATFORMS")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        platforms = []
        
        # OpenAI
        if options.get('openai_key'):
            platforms.append(('OpenAI', 'setup_openai', {'api_key': options['openai_key']}))
        elif not options['skip_existing']:
            openai_key = input("Enter OpenAI API key (or press Enter to skip): ").strip()
            if openai_key:
                platforms.append(('OpenAI', 'setup_openai', {'api_key': openai_key}))
        
        # Anthropic
        if options.get('anthropic_key'):
            platforms.append(('Anthropic', 'setup_anthropic', {'api_key': options['anthropic_key']}))
        elif not options['skip_existing']:
            anthropic_key = input("Enter Anthropic API key (or press Enter to skip): ").strip()
            if anthropic_key:
                platforms.append(('Anthropic', 'setup_anthropic', {'api_key': anthropic_key}))
        
        # Gemini
        if options.get('gemini_key'):
            platforms.append(('Gemini', 'setup_gemini', {'api_key': options['gemini_key']}))
        elif not options['skip_existing']:
            gemini_key = input("Enter Google Gemini API key (or press Enter to skip): ").strip()
            if gemini_key:
                platforms.append(('Gemini', 'setup_gemini', {'api_key': gemini_key}))
        
        # OpenRouter
        if options.get('openrouter_key'):
            platforms.append(('OpenRouter', 'setup_openrouter', {'api_key': options['openrouter_key']}))
        elif not options['skip_existing']:
            openrouter_key = input("Enter OpenRouter API key (or press Enter to skip): ").strip()
            if openrouter_key:
                platforms.append(('OpenRouter', 'setup_openrouter', {'api_key': openrouter_key}))

        if not platforms:
            self.stdout.write(
                self.style.WARNING("⚠️  No platforms to set up. Provide API keys or use interactive mode.")
            )
            return

        self.stdout.write(f"\n📦 Setting up {len(platforms)} platform(s)...\n")

        for platform_name, command_name, kwargs in platforms:
            try:
                self.stdout.write(f"\n{'='*70}")
                self.stdout.write(f"  Setting up {platform_name}")
                self.stdout.write(f"{'='*70}\n")
                
                if options['update']:
                    kwargs['update'] = True
                
                call_command(command_name, **kwargs)
                
                self.stdout.write(
                    self.style.SUCCESS(f"\n✓ {platform_name} setup complete!\n")
                )
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING(f"\n⚠️  Setup interrupted. Skipping {platform_name}...")
                )
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"\n✗ Error setting up {platform_name}: {e}")
                )
                continue

        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✓ ALL PLATFORMS SETUP COMPLETE"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("🚀 Next Steps:")
        self.stdout.write("  1. Run: python manage.py configure_conversation_management")
        self.stdout.write("  2. Run: python manage.py configure_provider_documentation")
        self.stdout.write("  3. Restart Django server and Celery workers")
        self.stdout.write("  4. Test agents in the chat interface")
        self.stdout.write("")
