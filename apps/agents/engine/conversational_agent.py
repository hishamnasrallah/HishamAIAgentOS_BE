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
        Prepare prompt with conversation history.
        
        Includes relevant conversation history for context.
        """
        user_message = input_data.get('message', input_data.get('prompt', ''))
        
        # Build prompt with conversation history
        prompt_parts = []
        
        # Add conversation history if available
        if context.conversation_history:
            # Limit history to max_history_messages
            history = context.conversation_history[-self.max_history_messages:]
            
            if history:
                prompt_parts.append("Previous conversation:")
                for msg in history:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    prompt_parts.append(f"{role.capitalize()}: {content}")
                
                prompt_parts.append("")  # Empty line separator
        
        # Add current message
        prompt_parts.append(f"User: {user_message}")
        
        return "\n".join(prompt_parts)
    
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
