"""
Token Budget Manager Service.

Manages intelligent token allocation across different context components,
similar to how Cursor IDE allocates tokens for optimal context distribution.
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TokenBudgetManager:
    """
    Manages token budget allocation across conversation context components.
    
    Similar to Cursor IDE's intelligent token distribution strategy.
    """
    
    # Default allocation percentages
    DEFAULT_ALLOCATION = {
        'with_summary': {
            'summary': 0.10,           # 10% for conversation summary
            'code_blocks': 0.30,       # 30% for code blocks
            'recent_messages': 0.40,   # 40% for recent messages
            'system_prompt': 0.20,     # 20% for system prompt
        },
        'without_summary': {
            'code_blocks': 0.35,       # 35% for code blocks
            'recent_messages': 0.45,   # 45% for recent messages
            'system_prompt': 0.20,     # 20% for system prompt
        }
    }
    
    @staticmethod
    def calculate_token_budget(
        total_limit: int,
        has_summary: bool = False,
        has_code_blocks: bool = False,
        custom_allocation: Optional[Dict[str, float]] = None
    ) -> Dict[str, int]:
        """
        Calculate token budget allocation across context components.
        
        Args:
            total_limit: Total token limit (e.g., 8192 for GPT-3.5)
            has_summary: Whether conversation has a summary
            has_code_blocks: Whether conversation has code blocks
            custom_allocation: Optional custom allocation percentages
            
        Returns:
            Dict mapping component names to token budgets
        """
        # Use custom allocation if provided, otherwise use defaults
        if custom_allocation:
            allocation = custom_allocation
        elif has_summary:
            allocation = TokenBudgetManager.DEFAULT_ALLOCATION['with_summary'].copy()
        else:
            allocation = TokenBudgetManager.DEFAULT_ALLOCATION['without_summary'].copy()
        
        # If no code blocks, redistribute that budget to messages
        if not has_code_blocks and 'code_blocks' in allocation:
            code_budget = allocation.pop('code_blocks', 0)
            allocation['recent_messages'] = allocation.get('recent_messages', 0) + code_budget
        
        # Calculate actual token budgets
        budget = {}
        for component, percentage in allocation.items():
            budget[component] = int(total_limit * percentage)
        
        # Ensure we don't exceed total limit
        total_allocated = sum(budget.values())
        if total_allocated > total_limit:
            # Proportionally reduce
            scale = total_limit / total_allocated
            budget = {k: int(v * scale) for k, v in budget.items()}
        
        logger.debug(
            f"[TokenBudgetManager] Calculated budget for {total_limit} tokens: "
            f"{budget} (has_summary={has_summary}, has_code={has_code_blocks})"
        )
        
        return budget
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text (approximation).
        
        Uses heuristic: ~4 characters per token on average.
        More accurate would require actual tokenizer, but this is faster.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Rough approximation: 4 chars per token (conservative)
        # Actual varies by language, but this is a good average
        char_count = len(text)
        return max(1, char_count // 4)
    
    @staticmethod
    def estimate_message_tokens(message: Dict[str, str]) -> int:
        """
        Estimate tokens for a message dict.
        
        Args:
            message: Message dict with 'role' and 'content' keys
            
        Returns:
            Estimated token count
        """
        role = message.get('role', '')
        content = message.get('content', '')
        
        # Role adds ~2 tokens, content is estimated
        return 2 + TokenBudgetManager.estimate_tokens(content)
    
    @staticmethod
    def prioritize_context_items(
        items: List[Dict[str, Any]],
        budget: int,
        priority_key: str = 'priority',
        token_key: str = 'tokens'
    ) -> List[Dict[str, Any]]:
        """
        Prioritize and select items within token budget.
        
        Args:
            items: List of items, each with priority and token count
            budget: Maximum tokens to allocate
            priority_key: Key name for priority value (higher = more important)
            token_key: Key name for token count
            
        Returns:
            Filtered list of items that fit within budget
        """
        # Sort by priority (descending)
        sorted_items = sorted(
            items,
            key=lambda x: x.get(priority_key, 0),
            reverse=True
        )
        
        selected = []
        token_count = 0
        
        for item in sorted_items:
            item_tokens = item.get(token_key, 0)
            if token_count + item_tokens <= budget:
                selected.append(item)
                token_count += item_tokens
            else:
                # If this item alone exceeds budget, skip it
                if item_tokens > budget:
                    logger.debug(
                        f"[TokenBudgetManager] Item exceeds budget: {item_tokens} > {budget}"
                    )
                break
        
        logger.debug(
            f"[TokenBudgetManager] Selected {len(selected)}/{len(items)} items "
            f"using {token_count}/{budget} tokens"
        )
        
        return selected
    
    @staticmethod
    def fit_messages_in_budget(
        messages: List[Dict[str, str]],
        budget: int
    ) -> List[Dict[str, str]]:
        """
        Fit messages into token budget, prioritizing recent messages.
        
        Args:
            messages: List of message dicts
            budget: Maximum tokens to allocate
            
        Returns:
            Filtered list of messages that fit within budget
        """
        # Recent messages have higher priority
        items = []
        for idx, msg in enumerate(reversed(messages)):  # Reverse to prioritize recent
            priority = 1.0 / (idx + 1)  # Higher priority for more recent
            tokens = TokenBudgetManager.estimate_message_tokens(msg)
            items.append({
                'item': msg,
                'priority': priority,
                'tokens': tokens,
                'index': len(messages) - idx - 1  # Original index
            })
        
        selected_items = TokenBudgetManager.prioritize_context_items(items, budget)
        
        # Sort back by original order
        selected_items.sort(key=lambda x: x['index'])
        
        return [item['item'] for item in selected_items]
    
    @staticmethod
    def fit_code_blocks_in_budget(
        code_blocks: List[Dict[str, Any]],
        budget: int
    ) -> List[Dict[str, Any]]:
        """
        Fit code blocks into token budget, prioritizing recent and larger blocks.
        
        Args:
            code_blocks: List of code block dicts
            budget: Maximum tokens to allocate
            
        Returns:
            Filtered list of code blocks that fit within budget
        """
        items = []
        for idx, block in enumerate(reversed(code_blocks)):  # Reverse for recency
            # Priority based on recency and size
            recency_priority = 1.0 / (idx + 1)
            size_priority = min(1.0, block.get('tokens', 0) / 500)  # Larger blocks preferred
            priority = (recency_priority * 0.6) + (size_priority * 0.4)
            
            tokens = block.get('tokens', TokenBudgetManager.estimate_tokens(block.get('content', '')))
            items.append({
                'item': block,
                'priority': priority,
                'tokens': tokens
            })
        
        selected_items = TokenBudgetManager.prioritize_context_items(items, budget)
        
        return [item['item'] for item in selected_items]
    
    @staticmethod
    def get_model_token_limit(model_name: str) -> int:
        """
        Get token limit for a given model.
        
        Args:
            model_name: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4', 'mistralai/mistral-7b-instruct:free')
            
        Returns:
            Token limit for the model, or default 8192
        """
        if not model_name:
            return 8192
        
        # Common model limits
        limits = {
            'gpt-4-turbo': 128000,
            'gpt-4-1106-preview': 128000,
            'gpt-4': 8192,
            'gpt-3.5-turbo': 16385,
            'gpt-3.5-turbo-16k': 16385,
            'claude-3-opus': 200000,
            'claude-3-sonnet': 200000,
            'claude-3-haiku': 200000,
            'gemini-pro': 32760,
            'gemini-1.5-pro': 1000000,
            # Mistral models (common on OpenRouter)
            'mistral-7b': 8192,
            'mistral-7b-instruct': 8192,
            'mistral-8x7b': 32768,
            'mistral-large': 32768,
            # Llama models
            'llama-2': 4096,
            'llama-3': 8192,
            'llama-3-70b': 8192,
        }
        
        # Normalize model name (handle OpenRouter format: mistralai/mistral-7b-instruct:free)
        model_normalized = model_name.lower()
        # Remove provider prefix (e.g., "mistralai/", "openai/")
        if '/' in model_normalized:
            model_normalized = model_normalized.split('/')[-1]
        # Remove tag suffix (e.g., ":free", ":latest")
        if ':' in model_normalized:
            model_normalized = model_normalized.split(':')[0]
        
        # Check exact match first
        if model_name in limits:
            return limits[model_name]
        
        # Check normalized match
        if model_normalized in limits:
            return limits[model_normalized]
        
        # Check partial match against normalized name
        for model, limit in limits.items():
            if model in model_normalized or model_normalized in model:
                logger.debug(f"[TokenBudgetManager] Matched '{model_name}' to '{model}' (limit: {limit})")
                return limit
        
        # Default to 8192 for unknown models (more generous than 4096)
        logger.debug(f"[TokenBudgetManager] Unknown model '{model_name}', using default limit: 8192")
        return 8192

