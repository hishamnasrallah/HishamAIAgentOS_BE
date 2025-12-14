"""
Conversational Agent - handles multi-turn conversations with context.
"""

from typing import Dict, Any, List
import logging

from .base_agent import BaseAgent, AgentCapability, AgentContext


logger = logging.getLogger(__name__)


class ConversationalAgent(BaseAgent):
    """
    Agent specialized for conversations.
    
    Conversational agents:
    - Maintain conversation history
    - Provide context-aware responses
    - Support multi-turn dialogues
    - Remember previous messages
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        max_history_messages: int = 10,
        **kwargs
    ):
        """
        Initialize conversational agent.
        
        Args:
            agent_id: Unique identifier
            name: Agent name
            description: Agent description
            system_prompt: System prompt
            max_history_messages: Maximum conversation history to maintain
            **kwargs: Additional base agent parameters
        """
        # Conversational agents always have CONVERSATION capability
        capabilities = kwargs.pop('capabilities', [])
        if AgentCapability.CONVERSATION not in capabilities:
            capabilities.append(AgentCapability.CONVERSATION)
        
        # Default to slightly higher temperature for more natural responses
        temperature = kwargs.pop('temperature', 0.8)
        
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            capabilities=capabilities,
            temperature=temperature,
            **kwargs
        )
        
        self.max_history_messages = max_history_messages
    
    async def prepare_prompt(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """
        Prepare prompt with conversation history using sliding window approach.
        
        To reduce token costs, only sends:
        - Conversation summary (if available) for older context
        - Recent messages (sliding window)
        - Current message
        
        This dramatically reduces tokens compared to sending full history.
        """
        user_message = input_data.get('message', input_data.get('prompt', ''))
        
        # Log initial state for debugging
        total_history = len(context.conversation_history) if context.conversation_history else 0
        logger.info(
            f"[ConversationalAgent] prepare_prompt: history_count={total_history}, "
            f"has_metadata={context.metadata is not None}, "
            f"has_platform_config={'platform_config' in (context.metadata or {})}"
        )
        
        if context.conversation_history:
            logger.info(
                f"[ConversationalAgent] Conversation history sample (first 2, last 2): "
                f"{context.conversation_history[:2] if len(context.conversation_history) >= 2 else context.conversation_history} "
                f"... {context.conversation_history[-2:] if len(context.conversation_history) >= 2 else []}"
            )
        
        # Use ConversationManager to get optimal messages based on provider capabilities
        from apps.integrations.services.conversation_manager import ConversationManager
        
        # Get platform config from metadata (if available) to determine strategy
        platform_config = None
        if context.metadata and 'platform_config' in context.metadata:
            platform_config = context.metadata['platform_config']
            logger.info(f"[ConversationalAgent] Platform config found: {platform_config.get('platform_name') if isinstance(platform_config, dict) else getattr(platform_config, 'platform_name', 'unknown')}")
        
        # Get conversation context from metadata
        conversation_context = context.metadata.get('conversation_context', {}) if context.metadata else {}
        
        # If we have platform config, use ConversationManager for optimal message selection
        if platform_config:
            # Create a mock object for ConversationManager if platform_config is a dict
            # ConversationManager expects platform_config to have attributes, not dict keys
            class PlatformConfigWrapper:
                def __init__(self, config_dict):
                    for key, value in config_dict.items():
                        setattr(self, key, value)
            
            # Wrap dict as object if needed
            if isinstance(platform_config, dict):
                platform_config_obj = PlatformConfigWrapper(platform_config)
            else:
                platform_config_obj = platform_config
            
            # Get model name from context metadata or agent
            model_name = None
            if context.metadata and 'model_name' in context.metadata:
                model_name = context.metadata['model_name']
            elif hasattr(self, 'model_name'):
                model_name = self.model_name
            
            logger.info(
                f"[ConversationalAgent] CALLING ConversationManager.get_optimal_messages_to_send: "
                f"history_count={len(context.conversation_history or [])}, "
                f"conversation_context_keys={list(conversation_context.keys())}, "
                f"has_code_blocks={len(conversation_context.get('code_blocks', []))}, "
                f"model_name={model_name}"
            )
            
            messages_list = ConversationManager.get_optimal_messages_to_send(
                platform_config=platform_config_obj,
                conversation_history=context.conversation_history or [],
                conversation_context=conversation_context,
                current_message=user_message,
                model_name=model_name
            )
            
            strategy = ConversationManager.get_conversation_strategy(platform_config_obj)
            platform_name = platform_config.get('platform_name', 'unknown') if isinstance(platform_config, dict) else getattr(platform_config, 'platform_name', 'unknown')
            logger.info(
                f"[ConversationalAgent] ✅ ConversationManager returned {len(messages_list)} message(s) using strategy '{strategy}' for platform {platform_name}"
            )
            
            # Detailed log of what messages we're sending
            for i, msg in enumerate(messages_list[:5]):  # Log first 5
                logger.info(
                    f"[ConversationalAgent] Message {i+1}/{len(messages_list)}: role={msg.get('role')}, "
                    f"content_length={len(msg.get('content', ''))}, "
                    f"content_preview={msg.get('content', '')[:80]}..."
                )
            
            # Log message details for debugging
            if messages_list:
                logger.info(
                    f"[ConversationalAgent] Messages to send: {[(msg.get('role'), len(msg.get('content', ''))) for msg in messages_list[:3]]} "
                    f"{'...' if len(messages_list) > 3 else ''}"
                )
        else:
            # Fallback: Use sliding window approach (for stateless providers)
            logger.warning("[ConversationalAgent] No platform_config found, using fallback sliding window approach")
            messages_list = []
            total_history_msgs = len(context.conversation_history) if context.conversation_history else 0
            max_recent = conversation_context.get('max_recent_messages', self.max_history_messages)
            
            if context.conversation_history and total_history_msgs > 0:
                recent_history = context.conversation_history[-max_recent:]
                for msg in recent_history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    api_role = 'assistant' if role == 'assistant' else 'user'
                    messages_list.append({
                        'role': api_role,
                        'content': content
                    })
                logger.info(
                    f"[ConversationalAgent] Fallback mode: Sending {len(recent_history)} recent messages "
                    f"(total: {total_history_msgs}, window: {max_recent})"
                )
            else:
                logger.warning(f"[ConversationalAgent] No conversation history available (total_history_msgs={total_history_msgs})")
            
            messages_list.append({
                'role': 'user',
                'content': user_message
            })
        
        # Store messages in metadata for adapter to use
        if context.metadata is None:
            context.metadata = {}
        context.metadata['messages'] = messages_list
        
        logger.info(f"[ConversationalAgent] Final messages_list: {len(messages_list)} messages stored in metadata")
        
        # Return current message as prompt (fallback for non-chat adapters)
        return user_message
    
    async def process_response(
        self,
        response,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Any:
        """
        Process response and update conversation history.
        """
        # Get response content
        content = response.content
        
        # Update conversation history in context
        user_message = input_data.get('message', input_data.get('prompt', ''))
        
        context.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        context.conversation_history.append({
            'role': 'assistant',
            'content': content
        })
        
        # Trim history if too long
        if len(context.conversation_history) > self.max_history_messages * 2:
            # Keep system message + recent messages
            context.conversation_history = context.conversation_history[-(self.max_history_messages * 2):]
        
        return content
    
    def get_conversation_summary(self, context: AgentContext) -> str:
        """
        Get a summary of the conversation so far.
        
        Args:
            context: Agent context with conversation history
            
        Returns:
            Text summary of conversation
        """
        if not context.conversation_history:
            return "No conversation history."
        
        summary_parts = [f"Conversation ({len(context.conversation_history) // 2} exchanges):"]
        
        for msg in context.conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            # Truncate long messages
            if len(content) > 100:
                content = content[:97] + "..."
            summary_parts.append(f"  {role}: {content}")
        
        return "\n".join(summary_parts)
