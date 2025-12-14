#!/usr/bin/env python
"""
Test script to verify OpenRouter adapter is working.
This will help diagnose why mock responses are being used.
"""
import os
import sys
import django
import asyncio
import logging

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

# Configure logging to see all messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from apps.integrations.services import get_registry
from apps.agents.models import Agent
from asgiref.sync import sync_to_async

async def test_adapter():
    """Test if OpenRouter adapter can be initialized and used."""
    print("=" * 70)
    print("TESTING OPENROUTER ADAPTER")
    print("=" * 70)
    print()
    
    # Step 1: Get registry and initialize
    print("Step 1: Initializing adapter registry...")
    try:
        registry = await get_registry()
        print(f"✓ Registry initialized")
        print(f"  Adapters available: {list(registry.get_all_adapters().keys())}")
    except Exception as e:
        print(f"✗ Failed to initialize registry: {e}")
        import traceback
        traceback.print_exc()
        return
    print()
    
    # Step 2: Check if OpenRouter adapter exists
    print("Step 2: Checking OpenRouter adapter...")
    openrouter_adapter = registry.get_adapter('openrouter')
    if openrouter_adapter:
        print(f"✓ OpenRouter adapter found")
        print(f"  Platform: {openrouter_adapter.platform_name}")
        print(f"  Default Model: {openrouter_adapter.default_model}")
    else:
        print(f"✗ OpenRouter adapter NOT found in registry")
        print(f"  Available adapters: {list(registry.get_all_adapters().keys())}")
        return
    print()
    
    # Step 3: Get Mistral agent
    print("Step 3: Getting Mistral 7B Assistant agent...")
    try:
        get_agent = sync_to_async(lambda: Agent.objects.get(agent_id='mistral-7b-assistant'))
        agent = await get_agent()
        print(f"✓ Agent found: {agent.name}")
        print(f"  Preferred Platform: {agent.preferred_platform}")
        print(f"  Model: {agent.model_name}")
    except Agent.DoesNotExist:
        print(f"✗ Mistral agent not found")
        return
    print()
    
    # Step 4: Test adapter with a simple request
    print("Step 4: Testing adapter with a simple request...")
    try:
        from apps.integrations.adapters.base import CompletionRequest
        
        request = CompletionRequest(
            prompt="Hello, this is a test. Please respond with just 'OK'.",
            system_prompt="You are a helpful assistant.",
            temperature=0.7,
            max_tokens=50
        )
        
        print("  Sending request to OpenRouter...")
        response = await openrouter_adapter.generate_completion(request, agent.model_name)
        print(f"✓ Response received!")
        print(f"  Content: {response.content[:200]}...")
        print(f"  Platform used: {response.platform}")
        print(f"  Model used: {response.model}")
        print(f"  Tokens: {response.tokens_used}")
    except Exception as e:
        print(f"✗ Request failed: {e}")
        import traceback
        traceback.print_exc()
        return
    print()
    
    print("=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print()
    print("If you're still seeing mock responses, check:")
    print("1. Django server logs for adapter initialization messages")
    print("2. Make sure you're using the 'Mistral 7B Assistant' agent in chat")
    print("3. Check that the agent's preferred_platform is 'openrouter'")

if __name__ == '__main__':
    asyncio.run(test_adapter())

