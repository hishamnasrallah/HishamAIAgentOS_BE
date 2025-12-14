"""
Management command to populate comprehensive provider documentation and metadata.

This command sets up complete documentation for each AI provider including:
- Architecture details (stateless/stateful, SDK support)
- Identifier information
- Cost optimization notes
- Implementation details
"""

from django.core.management.base import BaseCommand
from apps.integrations.models import AIPlatform
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate comprehensive provider documentation and metadata'

    def handle(self, *args, **options):
        """Configure provider documentation for all platforms."""
        
        self.stdout.write("=" * 80)
        self.stdout.write("CONFIGURING COMPREHENSIVE PROVIDER DOCUMENTATION")
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Comprehensive provider configurations with full documentation
        provider_configs = {
            'openai': {
                'api_stateful': False,
                'sdk_session_support': False,
                'supported_identifiers': [],
                'metadata_fields': ['id', 'object', 'created', 'model', 'usage', 'choices', 'system_fingerprint'],
                'identifier_extraction_paths': {},
                'provider_notes': """
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
""",
                'cost_optimization_notes': """
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
"""
            },
            'anthropic': {
                'api_stateful': False,
                'sdk_session_support': True,  # SDK provides session_id but API is stateless
                'supported_identifiers': [],
                'metadata_fields': ['id', 'type', 'role', 'content', 'model', 'stop_reason', 'stop_sequence', 'usage'],
                'identifier_extraction_paths': {},
                'provider_notes': """
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
""",
                'cost_optimization_notes': """
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
"""
            },
            'google': {
                'api_stateful': None,  # Unknown - needs testing
                'sdk_session_support': None,  # Unknown
                'supported_identifiers': ['conversation_id'],  # Possible but unverified
                'metadata_fields': ['candidates', 'usageMetadata', 'modelVersion'],
                'identifier_extraction_paths': {'conversation_id': 'conversation.conversation_id'},
                'provider_notes': """
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
""",
                'cost_optimization_notes': """
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
"""
            },
            'openrouter': {
                'api_stateful': False,
                'sdk_session_support': False,
                'supported_identifiers': [],
                'metadata_fields': ['id', 'model', 'created', 'usage', 'choices', 'provider'],
                'identifier_extraction_paths': {},
                'provider_notes': """
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
""",
                'cost_optimization_notes': """
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
"""
            },
        }
        
        updated_count = 0
        for platform_name, config in provider_configs.items():
            try:
                platform = AIPlatform.objects.filter(platform_name=platform_name).first()
                if not platform:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  Platform '{platform_name}' not found - skipping")
                    )
                    continue
                
                # Update all fields
                platform.api_stateful = config.get('api_stateful', False)
                platform.sdk_session_support = config.get('sdk_session_support', False)
                platform.supported_identifiers = config.get('supported_identifiers', [])
                platform.metadata_fields = config.get('metadata_fields', [])
                platform.identifier_extraction_paths = config.get('identifier_extraction_paths', {})
                platform.provider_notes = config.get('provider_notes', '').strip()
                platform.cost_optimization_notes = config.get('cost_optimization_notes', '').strip()
                
                platform.save(update_fields=[
                    'api_stateful',
                    'sdk_session_support',
                    'supported_identifiers',
                    'metadata_fields',
                    'identifier_extraction_paths',
                    'provider_notes',
                    'cost_optimization_notes'
                ])
                
                updated_count += 1
                stateful_status = "Stateful" if config.get('api_stateful') else "Stateless"
                sdk_status = "SDK Support" if config.get('sdk_session_support') else "No SDK Support"
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Configured {platform.display_name} ({platform_name}): "
                        f"{stateful_status}, {sdk_status}"
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Failed to configure {platform_name}: {e}")
                )
        
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(
            self.style.SUCCESS(f"✓ Documentation complete: {updated_count} platform(s) updated")
        )
        self.stdout.write("")
        self.stdout.write("Documentation includes:")
        self.stdout.write("- Architecture details (stateless/stateful, SDK support)")
        self.stdout.write("- Identifier information and extraction paths")
        self.stdout.write("- Token cost implications and optimization strategies")
        self.stdout.write("- Implementation details and recommendations")
        self.stdout.write("=" * 80)
