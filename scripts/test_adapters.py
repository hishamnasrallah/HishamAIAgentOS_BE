"""Test AI platform adapters."""
import asyncio
import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.integrations.services import get_registry, FallbackHandler, tracker
from apps.integrations.adapters.base import CompletionRequest
from apps.authentication.models import User


async def test_single_adapter():
    """Test a single adapter."""
    print("=" * 60)
    print("TEST 1: Single Adapter (OpenAI)")
    print("=" * 60)
    
    # Get registry
    registry = await get_registry()
    print(f"✓ Registry initialized with {len(registry.get_adapter_names())} adapters")
    print(f"  Available: {', '.join(registry.get_adapter_names())}\n")
    
    # Get OpenAI adapter
    openai = registry.get_adapter('openai')
    if not openai:
        print("✗ OpenAI adapter not found. Please add OpenAI configuration in admin.")
        return False
    
    # Create test request
    request = CompletionRequest(
        prompt="Say 'Hello from HishamOS!' in exactly 5 words.",
        temperature=0.7,
        max_tokens=50,
        system_prompt="You are a helpful AI assistant."
    )
    
    print("Sending request to OpenAI...")
    try:
        response = await openai.generate_completion(request)
        
        print("\n✓ SUCCESS!")
        print(f"  Platform: {response.platform}")
        print(f"  Model: {response.model}")
        print(f"  Response: {response.content}")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Cost: ${response.cost:.6f}")
        print(f"  Latency: {response.metadata.get('latency_ms')}ms")
        
        # Track usage
        user = await User.objects.afirst()  # Get first user
        await tracker.track_completion(response, 'openai', user)
        print(f"  ✓ Usage tracked to database")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        return False


async def test_fallback():
    """Test fallback mechanism."""
    print("\n" + "=" * 60)
    print("TEST 2: Fallback Mechanism")
    print("=" * 60)
    
    # Create fallback handler
    fallback = FallbackHandler(['openai', 'anthropic', 'google'])
    
    request = CompletionRequest(
        prompt="What is 2+2? Answer in one word.",
        temperature=0,
        max_tokens=10
    )
    
    print("Attempting completion with fallback...")
    try:
        response = await fallback.generate_with_fallback(request)
        
        print("\n✓ SUCCESS!")
        print(f"  Platform used: {response.platform}")
        print(f"  Response: {response.content}")
        print(f"  Fallback attempts: {response.metadata.get('fallback_attempts')}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        return False


async def test_health_checks():
    """Test platform health checks."""
    print("\n" + "=" * 60)
    print("TEST 3: Health Checks")
    print("=" * 60)
    
    registry = await get_registry()
    health_results = await registry.check_all_health()
    
    for platform_name, health in health_results.items():
        status_icon = "✓" if health.get('available') else "✗"
        print(f"{status_icon} {platform_name}: {health.get('status')} "
              f"({health.get('latency_ms', 0)}ms)")
    
    return True


async def test_cost_summary():
    """Test cost tracking summary."""
    print("\n" + "=" * 60)
    print("TEST 4: Cost Summary")
    print("=" * 60)
    
    user = await User.objects.afirst()
    if not user:
        print("No users found")
        return False
    
    summary = await tracker.get_user_cost_summary(user)
    
    print(f"User: {user.email}")
    print(f"  Total requests: {summary['total_requests']}")
    print(f"  Total tokens: {summary['total_tokens']:,}")
    print(f"  Total cost: ${summary['total_cost']:.6f}")
    print(f"  Avg response time: {summary['avg_response_time_seconds']:.2f}s")
    
    return True


async def main():
    """Run all tests."""
    print("\n🧪 HishamOS Phase 3 - AI Platform Integration Tests\n")
    
    results = []
    
    # Run tests
    results.append(await test_single_adapter())
    results.append(await test_fallback())
    results.append(await test_health_checks())
    results.append(await test_cost_summary())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 3 is working perfectly!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check errors above.")
    
    print("\n📊 Check Django Admin for usage logs:")
    print("   http://localhost:8000/admin/integrations/platformusage/")


if __name__ == '__main__':
    asyncio.run(main())
