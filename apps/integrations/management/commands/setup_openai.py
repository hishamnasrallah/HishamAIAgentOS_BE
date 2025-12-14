"""
Django management command to set up OpenAI platform and agents.

This command:
1. Creates or updates the OpenAI AI platform configuration
2. Creates agents configured to use OpenAI (GPT-4, GPT-3.5)
3. Sets up comprehensive conversation management configuration

Usage:
    python manage.py setup_openai --api-key YOUR_OPENAI_API_KEY
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up OpenAI platform and agents (GPT-4, GPT-3.5)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='OpenAI API key (required)',
            required=True
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing OpenAI platform if it exists'
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
        self.stdout.write("  SETTING UP OPENAI PLATFORM")
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

        # Step 1: Create or update OpenAI platform
        self.stdout.write("📦 Step 1: Setting up OpenAI AI Platform...")
        
        platform, created = AIPlatform.objects.get_or_create(
            platform_name='openai',
            defaults={
                'display_name': 'OpenAI GPT-4',
                'api_url': 'https://api.openai.com/v1',
                'api_type': 'openai',
                'default_model': 'gpt-3.5-turbo',
                'timeout': 60,
                'max_tokens': 16384,
                'supports_vision': False,
                'supports_json_mode': True,
                'supports_image_generation': False,
                'rate_limit_per_minute': 60,
                'rate_limit_per_day': 10000,
                'status': 'active',
                'is_enabled': True,
                'is_default': False,
                'priority': 5,
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )

        if not created and not update:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  OpenAI platform already exists. Use --update to update it."
                )
            )
            return

        if not created:
            # Update existing platform
            platform.display_name = 'OpenAI GPT-4'
            platform.api_url = 'https://api.openai.com/v1'
            platform.api_type = 'openai'
            platform.default_model = 'gpt-3.5-turbo'
            platform.timeout = 60
            platform.max_tokens = 16384
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
        platform.sdk_session_support = False
        platform.supported_identifiers = []
        platform.metadata_fields = ['id', 'object', 'created', 'model', 'usage', 'choices', 'system_fingerprint']
        platform.identifier_extraction_paths = {}
        platform.provider_notes = """
=== OpenAI Chat Completions API ===

ARCHITECTURE:
- API-Level: Stateless (no conversation ID support)
- SDK-Level: No built-in session management
- Identifiers: None available in Chat Completions API

HOW IT WORKS:
- Each request must include full conversation history in messages array
- No server-side conversation state
- Context maintained client-side only
- Uses openai.AsyncOpenAI SDK for API calls

IDENTIFIERS:
- None available in Chat Completions API
- Response includes: id, model, created, usage, choices
- No thread_id, conversation_id, or session_id

TOKEN COSTS:
- Full history sent each time (~5,000 tokens for 20 messages)
- No token savings possible with Chat Completions API
- Recommendation: Use sliding window approach (last 20 messages)
- Consider summarizing old messages for very long conversations

SDK INFORMATION:
- SDK: openai.AsyncOpenAI
- No conversation management features in SDK
- Must manage history manually
- SDK only provides API wrapper

OPTIMIZATION STRATEGIES:
1. Use sliding window (last N messages) - IMPLEMENTED
2. Summarize old conversation parts for very long threads
3. Monitor token usage per conversation
4. Consider OpenAI Assistants API for stateful conversations (different API)

NOTE: OpenAI Assistants API (v2) uses thread_id and is stateful, but it's a 
separate API requiring different implementation (assistant_id + thread_id pattern).
""".strip()
        platform.cost_optimization_notes = """
STATELESS COST IMPLICATIONS:
- Each message requires sending full conversation history
- For 20-message conversation: ~5,000 input tokens per request
- No server-side context = no token savings
- Sliding window reduces but doesn't eliminate token usage

OPTIMIZATION RECOMMENDATIONS:
1. Limit sliding window to 20 messages (current default)
2. Implement conversation summarization for old messages
3. Monitor and alert on high token usage conversations
4. Consider switching to Assistants API for stateful needs (different API)
5. Use cheaper models (gpt-3.5-turbo) when possible

COST COMPARISON:
- Stateless (20 messages): ~5,000 tokens/request
- Stateful (if using Assistants API): ~50 tokens/request (95% savings)
""".strip()

        # Set API key (encrypted)
        platform.set_api_key(api_key)
        platform.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created OpenAI platform: {platform.display_name}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated OpenAI platform: {platform.display_name}")
            )
        self.stdout.write(f"  - API URL: {platform.api_url}")
        self.stdout.write(f"  - Default Model: {platform.default_model}")
        self.stdout.write("")

        # Step 2: Create agents
        if create_agents:
            self.stdout.write("🤖 Step 2: Creating agents...")
            
            agents_config = [
                {
                    'agent_id': 'gpt-4-assistant',
                    'name': 'GPT-4 Assistant',
                    'description': 'Advanced AI assistant powered by OpenAI GPT-4 Turbo. Best for complex tasks, analysis, and high-quality responses.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by OpenAI GPT-4 Turbo. You provide clear, accurate, and detailed responses.',
                    'model_name': 'gpt-4-turbo',
                    'temperature': 0.7,
                    'max_tokens': 4000,
                },
                {
                    'agent_id': 'gpt-35-assistant',
                    'name': 'GPT-3.5 Assistant',
                    'description': 'Fast and efficient AI assistant powered by OpenAI GPT-3.5 Turbo. Great for general tasks and faster responses.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by OpenAI GPT-3.5 Turbo. You provide clear and helpful responses.',
                    'model_name': 'gpt-3.5-turbo',
                    'temperature': 0.7,
                    'max_tokens': 4000,
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
                        'preferred_platform': 'openai',
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
                    agent.preferred_platform = 'openai'
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
        self.stdout.write(f"  • OpenAI Platform: {platform.display_name}")
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
