"""
Django management command to set up Google Gemini platform and agents.

This command:
1. Creates or updates the Google Gemini AI platform configuration
2. Creates agents configured to use Gemini models
3. Sets up comprehensive conversation management configuration

Usage:
    python manage.py setup_gemini --api-key YOUR_GEMINI_API_KEY
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up Google Gemini platform and agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='Google Gemini API key (required)',
            required=True
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing Gemini platform if it exists'
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
        self.stdout.write("  SETTING UP GOOGLE GEMINI PLATFORM")
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

        # Step 1: Create or update Gemini platform
        self.stdout.write("📦 Step 1: Setting up Google Gemini AI Platform...")
        
        platform, created = AIPlatform.objects.get_or_create(
            platform_name='google',
            defaults={
                'display_name': 'Google Gemini',
                'api_url': 'https://generativelanguage.googleapis.com',
                'api_type': 'gemini',
                'default_model': 'gemini-pro',
                'timeout': 60,
                'max_tokens': 8192,
                'supports_vision': True,
                'supports_json_mode': False,
                'supports_image_generation': False,
                'rate_limit_per_minute': 60,
                'rate_limit_per_day': 1500,
                'status': 'active',
                'is_enabled': True,
                'is_default': False,
                'priority': 7,
                'created_by': admin_user,
                'updated_by': admin_user,
            }
        )

        if not created and not update:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Gemini platform already exists. Use --update to update it."
                )
            )
            return

        if not created:
            platform.display_name = 'Google Gemini'
            platform.api_url = 'https://generativelanguage.googleapis.com'
            platform.api_type = 'gemini'
            platform.default_model = 'gemini-pro'
            platform.timeout = 60
            platform.max_tokens = 8192
            platform.status = 'active'
            platform.is_enabled = True
            platform.updated_by = admin_user
            self.stdout.write("  ↻ Updating existing platform...")

        # Set comprehensive conversation management configuration
        # NOTE: Gemini conversation state support needs API testing
        platform.conversation_strategy = 'stateless'  # Default to stateless until verified
        platform.conversation_id_field = None  # Unknown - needs testing
        platform.returns_conversation_id = False  # Unknown - needs testing
        platform.conversation_id_path = None
        platform.api_stateful = None  # Unknown - needs testing
        platform.sdk_session_support = None  # Unknown - needs verification
        platform.supported_identifiers = ['conversation_id']  # Possible but unverified
        platform.metadata_fields = ['candidates', 'usageMetadata', 'modelVersion']
        platform.identifier_extraction_paths = {'conversation_id': 'conversation.conversation_id'}
        platform.provider_notes = """
=== Google Gemini API ===

ARCHITECTURE:
- API-Level: UNKNOWN - Needs API testing
- SDK-Level: UNKNOWN - Needs verification
- Identifiers: Possibly conversation_id (unverified)

HOW IT WORKS:
- Documentation unclear on conversation state support
- Some sources mention "stateful mode" but API details unclear
- May support conversation_id parameter (needs testing)
- Conversational Analytics API may have different capabilities

IDENTIFIERS:
- Possible: conversation_id (needs API testing to verify)
- Response structure needs verification
- Check: conversation.conversation_id path

TOKEN COSTS:
- If stateless: Full history required (~5,000 tokens for 20 messages)
- If stateful: Only new message needed (~50 tokens) - 95% savings potential
- Current: Defaulting to stateless until verified

SDK INFORMATION:
- SDK: google-generativeai (needs verification)
- Conversation management features unclear
- Needs testing to determine capabilities

OPTIMIZATION STRATEGIES:
- CURRENT: Using stateless approach (sliding window)
- TODO: Test API for conversation_id support
- TODO: Verify stateful mode availability
- TODO: Test identifier extraction

TESTING REQUIRED:
1. Test if conversation_id parameter is accepted
2. Test if responses include conversation identifiers
3. Verify if context is maintained server-side
4. Check SDK for conversation management features
""".strip()
        platform.cost_optimization_notes = """
COST IMPLICATIONS (Pending Verification):
- If stateless: ~5,000 tokens/request (20 messages)
- If stateful: ~50 tokens/request (95% potential savings)

CURRENT STATUS:
- Defaulting to stateless (safe approach)
- Testing needed to verify stateful capabilities
- Will update configuration once verified

RECOMMENDATIONS:
1. Test API for conversation state support
2. If stateful: Extract and use conversation_id
3. If stateless: Continue with sliding window
4. Monitor documentation for updates
""".strip()

        # Set API key (encrypted)
        platform.set_api_key(api_key)
        platform.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Created Gemini platform: {platform.display_name}")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated Gemini platform: {platform.display_name}")
            )
        self.stdout.write(f"  - API URL: {platform.api_url}")
        self.stdout.write(f"  - Default Model: {platform.default_model}")
        self.stdout.write(
            self.style.WARNING(
                "  ⚠️  Note: Conversation state support needs API testing"
            )
        )
        self.stdout.write("")

        # Step 2: Create agents
        if create_agents:
            self.stdout.write("🤖 Step 2: Creating agents...")
            
            agents_config = [
                {
                    'agent_id': 'gemini-pro-assistant',
                    'name': 'Gemini Pro Assistant',
                    'description': 'Google Gemini Pro model. Good for general tasks and analysis.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by Google Gemini Pro. You provide clear and helpful responses.',
                    'model_name': 'gemini-pro',
                    'temperature': 0.7,
                    'max_tokens': 2048,
                },
                {
                    'agent_id': 'gemini-vision-assistant',
                    'name': 'Gemini Vision Assistant',
                    'description': 'Google Gemini Pro Vision model. Supports image analysis and vision tasks.',
                    'capabilities': ['CODE_GENERATION', 'CODE_REVIEW', 'REQUIREMENTS_ANALYSIS', 'DOCUMENTATION', 'RESEARCH'],
                    'system_prompt': 'You are a helpful AI assistant powered by Google Gemini Pro Vision. You can analyze images and provide detailed responses.',
                    'model_name': 'gemini-pro-vision',
                    'temperature': 0.7,
                    'max_tokens': 2048,
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
                        'preferred_platform': 'google',
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
                    agent.preferred_platform = 'google'
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
        self.stdout.write(f"  • Gemini Platform: {platform.display_name}")
        if create_agents:
            self.stdout.write(f"  • Agents created: {len(agents_config)}")
        self.stdout.write("")
        self.stdout.write("🚀 Next Steps:")
        self.stdout.write("  1. Test the agents in the chat interface")
        self.stdout.write("  2. Test conversation state support (if applicable)")
        self.stdout.write("  3. Use the agents in workflows")
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "⚠️  Note: Make sure to restart your Django server and Celery workers "
                "for the adapter registry to pick up the new platform."
            )
        )
        self.stdout.write("")
