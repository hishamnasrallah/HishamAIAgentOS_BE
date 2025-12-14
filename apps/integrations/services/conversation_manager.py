"""
Conversation Manager - Unified abstraction for managing AI provider conversations.

Provides a unified interface for handling conversation context across different AI providers.
Each provider has different capabilities:
- OpenAI: Thread ID (Assistants API)
- Anthropic: Stateless (must send full history)
- Gemini: Conversation ID (can maintain state)
- OpenRouter: Stateless (must send full history)
- DeepSeek: Stateless (must send full history)
- Grok: Need to research

This manager handles:
1. Extracting conversation IDs from provider responses
2. Storing provider-specific conversation metadata
3. Determining optimal message sending strategy per provider
4. Reducing token costs by leveraging provider-side context when available
"""

from typing import Dict, Any, Optional, List
import logging
from django.db import models

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Unified conversation context manager for all AI providers.
    
    Handles provider-specific conversation management strategies:
    - Thread ID based (OpenAI Assistants API)
    - Conversation ID based (Gemini)
    - Session ID based (some providers)
    - Stateless (must send history - Claude, OpenRouter, etc.)
    """
    
    @staticmethod
    def get_conversation_strategy(platform_config) -> str:
        """Get conversation management strategy for a platform."""
        if platform_config is None:
            return 'stateless'
        
        # Handle dict (from serialized platform_config)
        if isinstance(platform_config, dict):
            return platform_config.get('conversation_strategy', 'stateless')
        
        # Handle object with attributes
        if hasattr(platform_config, 'conversation_strategy'):
            return platform_config.conversation_strategy
        return 'stateless'  # Default to stateless
    
    @staticmethod
    def extract_all_identifiers(
        platform_config,
        response: Any,
        response_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Extract ALL possible identifiers from provider response.
        
        Checks for: thread_id, session_id, conversation_id, run_id, assistant_id, etc.
        
        Args:
            platform_config: AIPlatform model instance
            response: API response object (can be dict, object, or raw response)
            response_metadata: Optional metadata from CompletionResponse
            
        Returns:
            Dictionary of all found identifiers: {identifier_type: identifier_value}
        """
        identifiers = {}
        
        # Get supported identifier types from config (handle both dict and object)
        if platform_config is None:
            supported_types = []
            identifier_paths = {}
        elif isinstance(platform_config, dict):
            supported_types = platform_config.get('supported_identifiers', []) or []
            identifier_paths = platform_config.get('identifier_extraction_paths', {}) or {}
        else:
            supported_types = getattr(platform_config, 'supported_identifiers', None) or []
            identifier_paths = getattr(platform_config, 'identifier_extraction_paths', None) or {}
        
        # Convert response to dict for easier access
        response_dict = None
        if isinstance(response, dict):
            response_dict = response
        elif hasattr(response, '__dict__'):
            response_dict = response.__dict__
        elif hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        elif hasattr(response, 'dict'):
            response_dict = response.dict()
        
        # Check metadata first (most reliable source)
        if response_metadata:
            for identifier_type in supported_types:
                # Try configured path
                if identifier_type in identifier_paths:
                    path = identifier_paths[identifier_type]
                    value = ConversationManager._extract_from_path(response_metadata, path)
                    if value:
                        identifiers[identifier_type] = str(value)
                        continue
                
                # Try direct metadata access
                if identifier_type in response_metadata:
                    identifiers[identifier_type] = str(response_metadata[identifier_type])
        
        # Check response object/dict for identifiers
        if response_dict:
            # Try all common identifier field names
            common_fields = [
                'thread_id', 'session_id', 'conversation_id', 'conversationId',
                'run_id', 'runId', 'assistant_id', 'assistantId',
                'message_id', 'messageId', 'request_id', 'requestId',
                'id'  # Generic ID field
            ]
            
            for field in common_fields:
                # Check direct access
                if field in response_dict:
                    # Map to standard identifier type
                    identifier_type = field.replace('Id', '_id').replace('_id', '_id')
                    if identifier_type not in identifiers:  # Don't overwrite if already found
                        identifiers[identifier_type] = str(response_dict[field])
                
                # Check nested structures (common patterns)
                for nested_key in ['metadata', 'data', 'response', 'result', 'thread', 'session', 'conversation']:
                    if nested_key in response_dict and isinstance(response_dict[nested_key], dict):
                        if field in response_dict[nested_key]:
                            identifier_type = field.replace('Id', '_id').replace('_id', '_id')
                            if identifier_type not in identifiers:
                                identifiers[identifier_type] = str(response_dict[nested_key][field])
        
        # Try object attribute access (for response objects)
        if hasattr(response, '__class__'):
            common_attrs = [
                'thread_id', 'session_id', 'conversation_id', 'run_id',
                'assistant_id', 'message_id', 'request_id', 'id'
            ]
            for attr in common_attrs:
                if hasattr(response, attr):
                    value = getattr(response, attr, None)
                    if value:
                        identifier_type = attr
                        if identifier_type not in identifiers:
                            identifiers[identifier_type] = str(value)
        
        # Use configured extraction paths from metadata
        if response_metadata and identifier_paths:
            for identifier_type, path in identifier_paths.items():
                if identifier_type not in identifiers:  # Don't overwrite
                    value = ConversationManager._extract_from_path(response_metadata, path)
                    if value:
                        identifiers[identifier_type] = str(value)
        
        return identifiers
    
    @staticmethod
    def extract_conversation_id(
        platform_config,
        response: Dict[str, Any],
        response_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Extract primary conversation/thread ID from provider response (backwards compatibility).
        
        Args:
            platform_config: AIPlatform model instance
            response: API response object
            response_metadata: Optional metadata from CompletionResponse
            
        Returns:
            Primary conversation/thread ID if found, None otherwise
        """
        # Use comprehensive extraction and return primary identifier
        all_ids = ConversationManager.extract_all_identifiers(
            platform_config, response, response_metadata
        )
        
        # Get conversation_id_field (handle both dict and object)
        if platform_config is None:
            conversation_id_field = 'conversation_id'
        elif isinstance(platform_config, dict):
            conversation_id_field = platform_config.get('conversation_id_field') or 'conversation_id'
        else:
            conversation_id_field = getattr(platform_config, 'conversation_id_field', None) or 'conversation_id'
        
        # Priority order for primary ID
        priority_order = [
            conversation_id_field,
            'thread_id',
            'conversation_id',
            'session_id',
            'run_id'
        ]
        
        for identifier_type in priority_order:
            if identifier_type in all_ids:
                return all_ids[identifier_type]
        
        # Return first available identifier if any found
        if all_ids:
            return list(all_ids.values())[0]
        
        return None
    
    @staticmethod
    def _extract_from_path(data: Dict[str, Any], path: str) -> Optional[Any]:
        """Extract value from nested dict using dot-notation path."""
        if not path:
            return None
        
        parts = path.split('.')
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
            if current is None:
                return None
        return current
    
    @staticmethod
    def should_send_full_history(
        platform_config,
        conversation_context: Dict[str, Any]
    ) -> bool:
        """
        Determine if we should send full message history based on provider capabilities.
        
        Returns True if provider is stateless or conversation ID is not available.
        Returns False if provider maintains context and we have a valid conversation ID.
        """
        strategy = ConversationManager.get_conversation_strategy(platform_config)
        
        # Stateless providers always need full history
        if strategy == 'stateless':
            return True
        
        # For providers with conversation management, check if we have a valid ID
        # Get conversation_id_field (handle both dict and object)
        if platform_config is None:
            conversation_id_field = 'conversation_id'
        elif isinstance(platform_config, dict):
            conversation_id_field = platform_config.get('conversation_id_field') or 'conversation_id'
        else:
            conversation_id_field = getattr(platform_config, 'conversation_id_field', None) or 'conversation_id'
        
        provider_context = conversation_context.get('ai_provider_context', {})
        provider_id = provider_context.get(conversation_id_field)
        
        # If we have a valid ID, provider maintains context - don't send full history
        if provider_id:
            return False
        
        # No ID available - fallback to sending history
        return True
    
    @staticmethod
    def get_optimal_messages_to_send(
        platform_config,
        conversation_history: List[Dict[str, str]],
        conversation_context: Dict[str, Any],
        current_message: str,
        model_name: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get optimal messages to send based on provider capabilities.
        
        For stateless providers: Send sliding window of recent messages + code context + summary
        For stateful providers with ID: Send only new message (provider maintains context)
        For stateful providers without ID: Send recent messages until ID is obtained
        
        Args:
            platform_config: Platform configuration
            conversation_history: List of previous messages
            conversation_context: Conversation context dict (includes summary, code context)
            current_message: Current user message
            model_name: Optional model name for token limit calculation
            
        Returns:
            List of message dicts to send to provider
        """
        strategy = ConversationManager.get_conversation_strategy(platform_config)
        max_recent = conversation_context.get('max_recent_messages', 20)
        
        # Get provider-specific conversation ID field (handle both dict and object)
        if platform_config is None:
            conversation_id_field = 'conversation_id'
        elif isinstance(platform_config, dict):
            conversation_id_field = platform_config.get('conversation_id_field') or 'conversation_id'
        else:
            conversation_id_field = getattr(platform_config, 'conversation_id_field', None) or 'conversation_id'
        
        provider_context = conversation_context.get('ai_provider_context', {})
        provider_id = provider_context.get(conversation_id_field)
        
        logger.info(
            f"[ConversationManager] get_optimal_messages_to_send: "
            f"strategy={strategy}, history_count={len(conversation_history) if conversation_history else 0}, "
            f"max_recent={max_recent}, provider_id={provider_id is not None}"
        )
        
        # Stateless providers: always send recent history with smart token allocation
        if strategy == 'stateless':
            return ConversationManager._build_enriched_context_for_stateless(
                conversation_history=conversation_history,
                conversation_context=conversation_context,
                current_message=current_message,
                max_recent=max_recent,
                model_name=model_name
            )
        
        # Stateful providers with conversation ID: send only new message
        if provider_id:
            logger.info(f"[ConversationManager] Stateful with ID: returning only current message")
            return [{'role': 'user', 'content': current_message}]
        
        # Stateful providers without ID yet: send recent history until we get ID
        messages = []
        if conversation_history:
            recent = conversation_history[-max_recent:]
            for msg in recent:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                api_role = 'assistant' if role == 'assistant' else 'user'
                messages.append({
                    'role': api_role,
                    'content': content
                })
        messages.append({'role': 'user', 'content': current_message})
        logger.info(f"[ConversationManager] Stateful without ID: returning {len(messages)} messages")
        return messages
    
    @staticmethod
    def _build_enriched_context_for_stateless(
        conversation_history: List[Dict[str, str]],
        conversation_context: Dict[str, Any],
        current_message: str,
        max_recent: int,
        model_name: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build enriched context for stateless providers with code blocks and smart token allocation.
        
        Similar to Cursor IDE's context building approach.
        
        Args:
            conversation_history: List of previous messages
            conversation_context: Conversation context with summary and code context
            current_message: Current user message
            max_recent: Maximum recent messages to include
            model_name: Optional model name for token limit
            
        Returns:
            List of message dicts optimized for token budget
        """
        from apps.chat.services.token_budget_manager import TokenBudgetManager
        
        messages = []
        
        # Get token limit for model (default to 8192 if unknown)
        token_limit = 8192
        if model_name:
            token_limit = TokenBudgetManager.get_model_token_limit(model_name)
        
        # Get code context
        code_blocks = conversation_context.get('code_blocks', [])
        referenced_files = conversation_context.get('referenced_files', [])
        conversation_summary = conversation_context.get('conversation_summary')
        
        has_code = len(code_blocks) > 0
        has_summary = bool(conversation_summary)
        
        logger.info(
            f"[ConversationManager] Building enriched context: "
            f"history_count={len(conversation_history)}, code_blocks={len(code_blocks)}, "
            f"has_summary={has_summary}, token_limit={token_limit}"
        )
        
        # Calculate token budget
        budget = TokenBudgetManager.calculate_token_budget(
            total_limit=token_limit,
            has_summary=has_summary,
            has_code_blocks=has_code
        )
        
        logger.info(
            f"[ConversationManager] Token budget calculated: {budget} "
            f"(total_limit={token_limit}, has_summary={has_summary}, has_code={has_code})"
        )
        
        # Build system messages with summary and file references
        system_parts = []
        
        if conversation_summary and budget.get('summary', 0) > 0:
            summary_text = (
                "Previous conversation summary:\n"
                f"{conversation_summary}\n\n"
                "Below are the recent messages continuing from this summary."
            )
            system_parts.append(summary_text)
            logger.info("[ConversationManager] Including conversation summary")
        
        # Add referenced files if available (useful context)
        if referenced_files and len(referenced_files) > 0:
            files_text = f"Referenced files in this conversation: {', '.join(referenced_files[:10])}"  # Limit to 10 files
            system_parts.append(files_text)
            logger.info(f"[ConversationManager] Including {len(referenced_files)} referenced files")
        
        if system_parts:
            messages.append({
                'role': 'system',
                'content': '\n\n'.join(system_parts)
            })
        
        # Add code blocks if available
        if code_blocks and budget.get('code_blocks', 0) > 0:
            selected_blocks = TokenBudgetManager.fit_code_blocks_in_budget(
                code_blocks,
                budget['code_blocks']
            )
            
            if selected_blocks:
                code_context_text = "Code blocks referenced in this conversation:\n\n"
                for idx, block in enumerate(selected_blocks, 1):
                    language = block.get('language', 'text')
                    content = block.get('content', '')
                    code_context_text += f"```{language}\n{content}\n```\n\n"
                
                messages.append({
                    'role': 'system',
                    'content': code_context_text
                })
                logger.info(f"[ConversationManager] Including {len(selected_blocks)}/{len(code_blocks)} code blocks")
        
        # Add recent messages (within budget)
        if conversation_history and budget.get('recent_messages', 0) > 0:
            recent = conversation_history[-max_recent:]
            logger.info(
                f"[ConversationManager] Processing {len(recent)} recent messages from history "
                f"(total history: {len(conversation_history)}, max_recent: {max_recent})"
            )
            # Convert to proper format
            formatted_messages = []
            for msg in recent:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                api_role = 'assistant' if role == 'assistant' else 'user'
                formatted_messages.append({
                    'role': api_role,
                    'content': content
                })
            
            # Log token estimates for debugging
            total_estimated_tokens = sum(
                TokenBudgetManager.estimate_message_tokens(msg) for msg in formatted_messages
            )
            logger.debug(
                f"[ConversationManager] Estimated tokens for {len(formatted_messages)} messages: "
                f"{total_estimated_tokens} (budget: {budget['recent_messages']})"
            )
            
            # Fit within token budget
            selected_messages = TokenBudgetManager.fit_messages_in_budget(
                formatted_messages,
                budget['recent_messages']
            )
            
            messages.extend(selected_messages)
            logger.info(
                f"[ConversationManager] Including {len(selected_messages)}/{len(formatted_messages)} recent messages "
                f"(budget: {budget['recent_messages']} tokens, "
                f"estimated: {sum(TokenBudgetManager.estimate_message_tokens(m) for m in selected_messages)} tokens)"
            )
        elif conversation_history:
            logger.warning(
                f"[ConversationManager] Conversation history exists ({len(conversation_history)} messages) "
                f"but recent_messages budget is {budget.get('recent_messages', 0)}. Skipping history. "
                f"Full budget: {budget}"
            )
        else:
            logger.debug("[ConversationManager] No conversation history to include")
        
        # Add current message
        messages.append({'role': 'user', 'content': current_message})
        
        logger.info(
            f"[ConversationManager] Stateless enriched context: "
            f"{len(messages)} messages total (summary={'yes' if has_summary else 'no'}, "
            f"code_blocks={len(code_blocks) if code_blocks else 0}, "
            f"files={len(referenced_files) if referenced_files else 0})"
        )
        
        return messages
    
    @staticmethod
    def update_conversation_context(
        platform_config,
        conversation_context: Dict[str, Any],
        extracted_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Update conversation context with extracted conversation ID from provider.
        
        Args:
            platform_config: AIPlatform model instance
            conversation_context: Current conversation context dict
            extracted_id: Conversation/thread ID extracted from provider response
            
        Returns:
            Updated conversation context
        """
        if not extracted_id:
            return conversation_context
        
        # Get conversation_id_field (handle both dict and object)
        if platform_config is None:
            conversation_id_field = 'conversation_id'
            platform_name = 'unknown'
        elif isinstance(platform_config, dict):
            conversation_id_field = platform_config.get('conversation_id_field') or 'conversation_id'
            platform_name = platform_config.get('platform_name', 'unknown')
        else:
            conversation_id_field = getattr(platform_config, 'conversation_id_field', None) or 'conversation_id'
            platform_name = getattr(platform_config, 'platform_name', 'unknown')
        
        # Ensure ai_provider_context exists
        if 'ai_provider_context' not in conversation_context:
            conversation_context['ai_provider_context'] = {}
        
        # Store the provider-specific conversation ID
        conversation_context['ai_provider_context'][conversation_id_field] = extracted_id
        
        # Also store platform name for reference
        conversation_context['ai_provider_context']['platform'] = platform_name
        
        logger.info(
            f"[ConversationManager] Stored {conversation_id_field}={extracted_id} "
            f"for platform {platform_config.platform_name}"
        )
        
        return conversation_context
