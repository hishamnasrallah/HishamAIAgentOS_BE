"""
Django management command to set up OpenRouter platform and test agent.

This command:
1. Creates or updates the OpenRouter AI platform configuration
2. Creates a test agent configured to use OpenRouter with Mistral 7B Instruct (free)
3. Sets up the agent for use in workflows and chat

Usage:
    python manage.py setup_openrouter --api-key YOUR_OPENROUTER_API_KEY
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up OpenRouter platform and test agent with Mistral 7B Instruct (free)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='OpenRouter API key (required)',
            required=True
        )
        parser.add_argument(
            '--site-url',
            type=str,
            default='http://localhost:3000',
            help='Your site URL for OpenRouter rankings (default: http://localhost:3000)'
        )
        parser.add_argument(
            '--site-name',
            type=str,
            default='HishamOS',
            help='Your site name for OpenRouter rankings (default: HishamOS)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing OpenRouter platform if it exists'
        )

    def handle(self, *args, **options):
        api_key = options['api_key']
        site_url = options['site_url']
        site_name = options['site_name']
        update = options['update']

        self.stdout.write("=" * 70)
        self.stdout.write("  SETTING UP OPENROUTER PLATFORM")
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

        # Step 1: Create or update OpenRouter platform
        self.stdout.write("📦 Step 1: Setting up OpenRouter AI Platform...")
        
        platform, created = AIPlatform.objects.get_or_create(
            platform_name='openrouter',
            defaults={
                'display_name': 'OpenRouter',
                'api_url': 'https://openrouter.ai/api/v1',
                'api_type': 'openai',  # OpenRouter uses OpenAI-compatible API
                'default_model': 'mistralai/mistral-7b-instruct:free',
                'timeout': 60,
                'max_tokens': 32768,  # Mistral 7B supports 32k context
                'supports_vision': False,
                'supports_json_mode': False,
                'supports_image_generation': False,
                'rate_limit_per_minute': 60,
                'rate_limit_per_day': 10000,
                'status': 'active',
                'is_enabled': True,
                'is_default': False,
                'priority': 10,  # Higher priority than mock
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )

        if not created and not update:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  OpenRouter platform already exists. Use --update to update it."
                )
            )
            return

        if not created:
            # Update existing platform
            platform.display_name = 'OpenRouter'
            platform.api_url = 'https://openrouter.ai/api/v1'
            platform.api_type = 'openai'
            platform.default_model = 'mistralai/mistral-7b-instruct:free'
            platform.timeout = 60
            platform.max_tokens = 32768
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
        platform.metadata_fields = ['id', 'model', 'created', 'usage', 'choices', 'provider']
        platform.identifier_extraction_paths = {}
        platform.provider_notes = """
=== OpenRouter API ===

ARCHITECTURE:
- API-Level: Stateless (confirmed via testing)
- SDK-Level: No session management
- Identifiers: None available

HOW IT WORKS:
- Uses OpenAI-compatible API format
- Completely stateless (confirmed)
- Does NOT support conversationId parameter (tested - causes errors)
- Each request must include full message history
- Provides access to multiple AI models through unified interface

IDENTIFIERS:
- None available (confirmed stateless)
- Response includes: id, model, usage, choices (OpenAI-compatible format)
- No conversation/thread/session IDs

TOKEN COSTS:
- Full history sent each time (~5,000 tokens for 20 messages)
- No token savings possible (confirmed stateless)
- Cost varies by model (some models are free like Mistral 7B)

SDK INFORMATION:
- Uses openai.AsyncOpenAI SDK with custom base_url
- No conversation management features
- Must manage history manually

OPTIMIZATION STRATEGIES:
1. Use sliding window (last N messages) - IMPLEMENTED
2. Choose free models when possible (e.g., mistral-7b-instruct:free)
3. Monitor token usage per conversation
4. Consider model pricing when selecting

NOTE: conversationId parameter tested and confirmed to cause API errors.
OpenRouter explicitly does not support conversation state management.
""".strip()
        platform.cost_optimization_notes = """
STATELESS COST IMPLICATIONS:
- Each message requires sending full conversation history
- For 20-message conversation: ~5,000 input tokens per request
- No server-side context = no token savings

COST VARIANCE BY MODEL:
- Free models (mistral-7b-instruct:free): $0.00
- Paid models: Varies by provider and model
- Check OpenRouter pricing for specific models

OPTIMIZATION RECOMMENDATIONS:
1. Use sliding window (20 messages default)
2. Choose free models when possible
3. Monitor token usage per conversation
4. Consider model costs when selecting provider
5. Implement conversation summarization for long threads

NOTE: OpenRouter is confirmed stateless. No conversation state management 
available regardless of model selected.
""".strip()

        # Set API key (encrypted)
        platform.set_api_key(api_key)
        
        # Store site URL in organization_id field (used as HTTP-Referer header)
        platform.organization_id = site_url
        
        platform.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created OpenRouter platform: {platform.display_name}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated OpenRouter platform: {platform.display_name}")
            )
        self.stdout.write(f"  - API URL: {platform.api_url}")
        self.stdout.write(f"  - Default Model: {platform.default_model}")
        self.stdout.write(f"  - Site URL: {site_url}")
        self.stdout.write("")

        # Step 2: Create test agent
        self.stdout.write("🤖 Step 2: Creating test agent...")
        
        agent_id = 'mistral-7b-assistant'
        agent_name = 'Mistral 7B Assistant'
        
        agent, agent_created = Agent.objects.get_or_create(
            agent_id=agent_id,
            defaults={
                'name': agent_name,
                'description': (
                    'AI assistant powered by Mistral 7B Instruct (free) via OpenRouter. '
                    'This agent can help with general tasks, coding, analysis, and more.'
                ),
                'capabilities': [
                    'CODE_GENERATION',
                    'CODE_REVIEW',
                    'REQUIREMENTS_ANALYSIS',
                    'DOCUMENTATION',
                    'RESEARCH',
                ],
                'system_prompt': (
                    'You are a helpful AI assistant powered by Mistral 7B Instruct. '
                    'You provide clear, accurate, and helpful responses to user queries. '
                    'You can help with coding, analysis, documentation, research, and general tasks.'
                ),
                'preferred_platform': 'openrouter',
                'fallback_platforms': [],
                'model_name': 'mistralai/mistral-7b-instruct:free',
                'temperature': 0.7,
                'max_tokens': 4000,
                'status': 'active',
                'version': '1.0.0',
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )

        if not agent_created:
            # Update existing agent
            agent.name = agent_name
            agent.preferred_platform = 'openrouter'
            agent.model_name = 'mistralai/mistral-7b-instruct:free'
            agent.updated_by = admin_user
            agent.save()
            self.stdout.write("  ↻ Updating existing agent...")

        if agent_created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created agent: {agent.name} ({agent.agent_id})")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated agent: {agent.name} ({agent.agent_id})")
            )
        self.stdout.write(f"  - Platform: {agent.preferred_platform}")
        self.stdout.write(f"  - Model: {agent.model_name}")
        self.stdout.write(f"  - Temperature: {agent.temperature}")
        self.stdout.write("")

        # Step 3: Summary
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("✓ SETUP COMPLETE"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("📋 Summary:")
        self.stdout.write(f"  • OpenRouter Platform: {platform.display_name}")
        self.stdout.write(f"  • Test Agent: {agent.name} ({agent.agent_id})")
        self.stdout.write("")
        self.stdout.write("🚀 Next Steps:")
        self.stdout.write("  1. Test the agent in the chat interface")
        self.stdout.write("  2. Use the agent in workflows")
        self.stdout.write("  3. The agent will use real AI (not mock responses)")
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "⚠️  Note: Make sure to restart your Django server and Celery workers "
                "for the adapter registry to pick up the new platform."
            )
        )
        self.stdout.write("")



