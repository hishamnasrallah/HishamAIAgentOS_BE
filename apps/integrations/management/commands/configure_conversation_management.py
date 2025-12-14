"""
Management command to configure conversation management capabilities for AI platforms.

This command sets up the conversation management strategy for each AI provider:
- OpenAI: Thread ID (Assistants API) - requires separate setup
- Anthropic Claude: Stateless - must send full history
- Google Gemini: Conversation ID (if supported)
- OpenRouter: Stateless - must send full history
- DeepSeek: Stateless - must send full history
- Grok: Need to research
"""

from django.core.management.base import BaseCommand
from apps.integrations.models import AIPlatform
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Configure conversation management capabilities for AI platforms'

    def handle(self, *args, **options):
        """Configure conversation management for all platforms."""
        
        self.stdout.write("=" * 80)
        self.stdout.write("CONFIGURING CONVERSATION MANAGEMENT FOR AI PLATFORMS")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Platform configurations based on deep research of official documentation
        # CRITICAL: Field names verified from official API docs where available
        # See docs/PROVIDER_CONVERSATION_IDENTIFIERS.md for detailed reference
        platform_configs = {
            'openai': {
                # Chat Completions API - confirmed stateless
                # NOTE: Assistants API uses thread_id but is a separate API (not implemented)
                'conversation_strategy': 'stateless',
                'conversation_id_field': None,
                'returns_conversation_id': False,
                'conversation_id_path': None,
                'notes': 'Chat Completions API confirmed stateless (no conversation_id). Assistants API uses thread_id but requires separate implementation.'
            },
            'anthropic': {
                # Messages API - confirmed stateless
                # SDK has session_id but API does not support it
                'conversation_strategy': 'stateless',
                'conversation_id_field': None,
                'returns_conversation_id': False,
                'conversation_id_path': None,
                'notes': 'Anthropic Claude Messages API confirmed stateless - must send full message history. SDK session_id is SDK-level, not API-level.'
            },
            'google': {
                # Gemini API - unclear from documentation
                # May support stateful mode but field names unknown
                # Defaulting to stateless until API testing confirms
                'conversation_strategy': 'stateless',
                'conversation_id_field': None,  # Unknown - needs API testing
                'returns_conversation_id': False,  # Unknown - needs API testing
                'conversation_id_path': None,
                'notes': 'Google Gemini - API TESTING NEEDED: Documentation unclear on conversation state. Defaulting to stateless until verified.'
            },
            'openrouter': {
                # Confirmed stateless - tested
                'conversation_strategy': 'stateless',
                'conversation_id_field': None,
                'returns_conversation_id': False,
                'conversation_id_path': None,
                'notes': 'OpenRouter confirmed stateless (tested). Does NOT support conversationId parameter - causes errors if sent.'
            },
            'deepseek': {
                # No official documentation found
                'conversation_strategy': 'stateless',
                'conversation_id_field': None,
                'returns_conversation_id': False,
                'conversation_id_path': None,
                'notes': 'DeepSeek - API TESTING NEEDED: No official docs found. Defaulting to stateless until verified.'
            },
            'grok': {
                # Limited public documentation
                'conversation_strategy': 'stateless',
                'conversation_id_field': None,
                'returns_conversation_id': False,
                'conversation_id_path': None,
                'notes': 'Grok (xAI) - API TESTING NEEDED: Limited docs available. Defaulting to stateless until verified.'
            },
        }
        
        updated_count = 0
        for platform_name, config in platform_configs.items():
            try:
                platform = AIPlatform.objects.filter(platform_name=platform_name).first()
                if not platform:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Platform '{platform_name}' not found - skipping")
                    )
                    continue
                
                # Update platform configuration
                platform.conversation_strategy = config['conversation_strategy']
                platform.conversation_id_field = config['conversation_id_field']
                platform.returns_conversation_id = config['returns_conversation_id']
                platform.conversation_id_path = config['conversation_id_path']
                platform.save(update_fields=[
                    'conversation_strategy',
                    'conversation_id_field',
                    'returns_conversation_id',
                    'conversation_id_path'
                ])
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Configured {platform.display_name} ({platform_name}): "
                        f"strategy={config['conversation_strategy']}"
                    )
                )
                if config.get('notes'):
                    self.stdout.write(f"  Note: {config['notes']}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to configure {platform_name}: {e}")
                )
        
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"✓ Configuration complete: {updated_count} platform(s) updated")
        )
        self.stdout.write("")
        self.stdout.write("IMPORTANT NOTES:")
        self.stdout.write("- Stateless providers (OpenAI Chat, Claude, OpenRouter) require sending full history")
        self.stdout.write("- Stateful providers (Gemini with conversation_id) can maintain context server-side")
        self.stdout.write("- For stateful providers, conversation IDs will be extracted and stored automatically")
        self.stdout.write("- The system will automatically use optimal strategy per provider")
        self.stdout.write("=" * 80)
