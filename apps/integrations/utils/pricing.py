"""AI platform pricing data and calculators."""


class OpenAIPricing:
    """OpenAI pricing per 1M tokens (USD)."""
    
    PRICES = {
        'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
        'gpt-4-1106-preview': {'input': 0.01, 'output': 0.03},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'gpt-3.5-turbo-1106': {'input': 0.001, 'output': 0.002},
    }
    
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        prices = self.PRICES.get(model, self.PRICES['gpt-3.5-turbo'])
        input_cost = (input_tokens / 1_000_000) * prices['input']
        output_cost = (output_tokens / 1_000_000) * prices['output']
        return round(input_cost + output_cost, 6)


class AnthropicPricing:
    """Anthropic Claude pricing per 1M tokens (USD)."""
    
    PRICES = {
        'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
        'claude-2.1': {'input': 0.008, 'output': 0.024},
        'claude-2.0': {'input': 0.008, 'output': 0.024},
    }
    
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        prices = self.PRICES.get(model, self.PRICES['claude-3-sonnet-20240229'])
        input_cost = (input_tokens / 1_000_000) * prices['input']
        output_cost = (output_tokens / 1_000_000) * prices['output']
        return round(input_cost + output_cost, 6)


class GeminiPricing:
    """Google Gemini pricing per 1M tokens (USD)."""
    
    PRICES = {
        'gemini-pro': {'input': 0.00025, 'output': 0.0005},
        'gemini-pro-vision': {'input': 0.00025, 'output': 0.0005},
        'gemini-1.5-pro': {'input': 0.00125, 'output': 0.005},
    }
    
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        prices = self.PRICES.get(model, self.PRICES['gemini-pro'])
        input_cost = (input_tokens / 1_000_000) * prices['input']
        output_cost = (output_tokens / 1_000_000) * prices['output']
        return round(input_cost + output_cost, 6)
