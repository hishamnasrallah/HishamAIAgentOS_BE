"""
Django management command to set up Anthropic Claude platform and agents.

This command:
1. Creates or updates the Anthropic Claude AI platform configuration
2. Creates agents configured to use Claude (Opus, Sonnet, Haiku)
3. Sets up comprehensive conversation management configuration

Usage:
    python manage.py setup_anthropic --api-key YOUR_ANTHROPIC_API_KEY
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up Anthropic Claude platform and agents (Opus, Sonnet, Haiku)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='Anthropic API key (required)',
            required=True
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing Anthropic platform if it exists'
        )
        parser.add_argument(
            '--create-agents',
            action='store_true',
            default=True,
            help='Create default agents (default: True)'
        )

    def handle(self, *args, **options):
        api_key = options['api_key']
        update = options['update']
        create_agents = options['create_agents']

        self.stdout.write("=" * 70)
        self.stdout.write("  SETTING UP ANTHROPIC CLAUDE PLATFORM")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Get or create admin user
        admin_user = User.objects.filter(email='admin@hishamos.com').first()
        if not admin_user:
            self.stdout.write(
                self.style.WARNING("⚠️  Admin user not found. Creating one...")
            )
            admin_user = User.objects.create_superuser(
                email='admin@hishamos.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created admin user: {admin_user.email}")
            )

        # Step 1: Create or update Anthropic platform
        self.stdout.write("📦 Step 1: Setting up Anthropic Claude AI Platform...")
        
        platform, created = AIPlatform.objects.get_or_create(
            platform_name='anthropic',
            defaults={
                'display_name': 'Anthropic Claude',
                'api_url': 'https://api.anthropic.com',
                'api_type': 'anthropic',
                'default_model': 'claude-3-sonnet',
                'timeout': 60,
                'max_tokens': 4096,
                'supports_vision': False,
                'supports_json_mode': False,
                'supports_image_generation': False,
                'rate_limit_per_minute': 50,
                'rate_limit_per_day': 5000,
                'status': 'active',
                'is_enabled': True,
                'is_default': False,
                'priority': 8,
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )

        if not created and not update:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Anthropic platform already exists. Use --update to update it."
                )
            )
            return

        if not created:
            platform.display_name = 'Anthropic Claude'
            platform.api_url = 'https://api.anthropic.com'
            platform.api_type = 'anthropic'
            platform.default_model = 'claude-3-sonnet'
            platform.timeout = 60
            platform.max_tokens = 4096
            platform.status = 'active'
            platform.is_enabled = True
            platform.updated_by = admin_user
            self.stdout.write("  ↻ Updating existing platform...")

        # Set comprehensive conversation management configuration
        platform.conversation_strategy = 'stateless'
        platform.conversation_id_field = None
        platform.returns_conversation_id = False
        platform.conversation_id_path = None
        platform.api_stateful = False
        platform.sdk_session_support = True  # SDK provides session_id wrapper (but API is stateless)
        platform.supported_identifiers = []
        platform.metadata_fields = ['id', 'type', 'role', 'content', 'model', 'stop_reason', 'stop_sequence', 'usage']
        platform.identifier_extraction_paths = {}
        platform.provider_notes = """
=== Anthropic Claude Messages API ===

ARCHITECTURE:
- API-Level: Stateless (no conversation ID support)
- SDK-Level: SDK provides session_id wrapper (client-side convenience)
- Identifiers: None at API level

HOW IT WORKS:
- Messages API is completely stateless
- Each request must include full message history
- SDK (anthropic.AsyncAnthropic) provides session_id wrapper:
  * SDK stores history client-side (in memory/cache)
  * When you pass session_id, SDK prepends stored history
  * SDK still sends full history to API (API is stateless)
  * More convenient API but NO token savings

IDENTIFIERS:
- API: None available (stateless)
- SDK: session_id (client-side wrapper only)
- Response includes: id, model, type, role, content, usage, stop_reason

TOKEN COSTS:
- Full history sent each time (~5,000 tokens for 20 messages)
- SDK session_id provides convenience but NO token savings
- API is stateless regardless of SDK features

SDK INFORMATION:
- SDK: anthropic.AsyncAnthropic
- SDK provides session_id for convenience wrapper
- SDK manages history client-side (not server-side)
- State lost if SDK instance/process dies
- Our database approach is more robust

OPTIMIZATION STRATEGIES:
1. Use sliding window (last N messages) - IMPLEMENTED
2. SDK session_id is optional convenience (doesn't save tokens)
3. Our database-backed history is more persistent
4. Monitor token usage per conversation
""".strip()
        platform.cost_optimization_notes = """
STATELESS COST IMPLICATIONS:
- Each message requires sending full conversation history
- SDK session_id doesn't change this (still stateless API)
- For 20-message conversation: ~5,000 input tokens per request
- No server-side context = no token savings

OPTIMIZATION RECOMMENDATIONS:
1. Limit sliding window to 20 messages (current default)
2. SDK session_id is for convenience only (use our DB approach instead)
3. Implement conversation summarization for old messages
4. Monitor and alert on high token usage conversations
5. Use Claude Haiku for lower costs when possible

NOTE: SDK session_id is a client-side convenience wrapper. It makes the API 
easier to use but provides NO token savings since the underlying API is stateless.
""".strip()

        # Set API key (encrypted)
        platform.set_api_key(api_key)
        platform.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created Anthropic platform: {platform.display_name}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated Anthropic platform: {platform.display_name}")
            )
        self.stdout.write(f"  - API URL: {platform.api_url}")
        self.stdout.write(f"  - Default Model: {platform.default_model}")
        self.stdout.write("")

        # Step 2: Create agents
        if create_agents:
            self.stdout.write("🤖 Step 2: Creating agents...")
            
            agents_config = [
                {
                    'agent_id': 'claude-opus-assistant',
                    'name': 'Claude Opus Assistant',
                    'description': 'Most powerful Claude model. Best for complex analysis, research, and high-quality responses.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by Anthropic Claude Opus. You provide detailed, thoughtful, and accurate responses.',
                    'model_name': 'claude-3-opus',
                    'temperature': 0.7,
                    'max_tokens': 4096,
                },
                {
                    'agent_id': 'claude-sonnet-assistant',
                    'name': 'Claude Sonnet Assistant',
                    'description': 'Balanced Claude model. Great for general tasks, analysis, and quality responses.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by Anthropic Claude Sonnet. You provide clear, accurate, and helpful responses.',
                    'model_name': 'claude-3-sonnet',
                    'temperature': 0.7,
                    'max_tokens': 4096,
                },
                {
                    'agent_id': 'claude-haiku-assistant',
                    'name': 'Claude Haiku Assistant',
                    'description': 'Fast and efficient Claude model. Perfect for quick responses and lower cost tasks.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by Anthropic Claude Haiku. You provide fast, clear, and helpful responses.',
                    'model_name': 'claude-3-haiku',
                    'temperature': 0.7,
                    'max_tokens': 4096,
                },
            ]

            for agent_config in agents_config:
                agent, agent_created = Agent.objects.get_or_create(
                    agent_id=agent_config['agent_id'],
                    defaults={
                        'name': agent_config['name'],
                        'description': agent_config['description'],
                        'capabilities': agent_config['capabilities'],
                        'system_prompt': agent_config['system_prompt'],
                        'preferred_platform': 'anthropic',
                        'fallback_platforms': [],
                        'model_name': agent_config['model_name'],
                        'temperature': agent_config['temperature'],
                        'max_tokens': agent_config['max_tokens'],
                        'status': 'active',
                        'version': '1.0.0',
                        'created_by': admin_user,
                        'updated_by': admin_user,
                    }
                )

                if not agent_created and update:
                    agent.name = agent_config['name']
                    agent.description = agent_config['description']
                    agent.model_name = agent_config['model_name']
                    agent.preferred_platform = 'anthropic'
                    agent.updated_by = admin_user
                    agent.save()

                if agent_created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Created agent: {agent.name} ({agent.agent_id})")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Updated agent: {agent.name} ({agent.agent_id})")
                    )
                self.stdout.write(f"  - Model: {agent.model_name}")

        # Step 3: Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("✓ SETUP COMPLETE"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("📋 Summary:")
        self.stdout.write(f"  • Anthropic Platform: {platform.display_name}")
        if create_agents:
            self.stdout.write(f"  • Agents created: {len(agents_config)}")
        self.stdout.write("")
        self.stdout.write("🚀 Next Steps:")
        self.stdout.write("  1. Test the agents in the chat interface")
        self.stdout.write("  2. Use the agents in workflows")
        self.stdout.write("  3. The system will automatically manage conversation context")
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "⚠️  Note: Make sure to restart your Django server and Celery workers "
                "for the adapter registry to pick up the new platform."
            )
        )
        self.stdout.write("")
