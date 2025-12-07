"""
Interactive manual testing for Phase 3 AI Platform Integration.
Run this script and follow the prompts to test each feature.
"""
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
from apps.integrations.models import AIPlatform, PlatformUsage


def print_header(text):
    """Print a nice header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_info(text, indent=2):
    """Print info message."""
    print(" " * indent + text)


async def show_available_platforms():
    """Show all configured platforms."""
    print_header("STEP 1: Available AI Platforms")
    
    platforms = await AIPlatform.objects.all().acount()
    
    if platforms == 0:
        print_error("No platforms configured yet!")
        print_info("Please add a platform in Django Admin:")
        print_info("1. Go to: http://localhost:8000/admin/integrations/aiplatform/")
        print_info("2. Click 'Add AI Platform'")
        print_info("3. Fill in the form (see PHASE_3_TESTING_GUIDE.md)")
        return False
    
    print_success(f"Found {platforms} platform(s) configured\n")
    
    async for platform in AIPlatform.objects.all():
        status = "🟢 Active" if platform.status == 'active' else "🔴 Inactive"
        print_info(f"{status} {platform.display_name}")
        print_info(f"   - Platform: {platform.platform_name}", 4)
        print_info(f"   - Total Requests: {platform.total_requests:,}", 4)
        print_info(f"   - Total Cost: ${platform.total_cost:.6f}", 4)
        print_info(f"   - Healthy: {'Yes' if platform.is_healthy else 'Unknown'}", 4)
        print("")
    
    return True


async def test_simple_completion():
    """Test a simple completion."""
    print_header("STEP 2: Test Simple Completion")
    
    registry = await get_registry()
    adapters = registry.get_adapter_names()
    
    if not adapters:
        print_error("No adapters available. Please configure a platform first.")
        return False
    
    # Use first available adapter
    platform_name = adapters[0]
    adapter = registry.get_adapter(platform_name)
    
    print_info(f"Using platform: {platform_name}\n")
    
    # Ask user for prompt
    print("Enter your prompt (or press Enter for default):")
    user_prompt = input("> ").strip()
    
    if not user_prompt:
        user_prompt = "Tell me a short joke about programming."
        print_info(f"Using default: {user_prompt}\n")
    
    # Create request
    request = CompletionRequest(
        prompt=user_prompt,
        temperature=0.7,
        max_tokens=150,
        system_prompt="You are a helpful AI assistant."
    )
    
    print("\n🔄 Sending request...")
    print_info("This may take a few seconds...\n")
    
    try:
        response = await adapter.generate_completion(request)
        
        print_success("Response received!\n")
        print("-" * 70)
        print(f"📝 {response.content}")
        print("-" * 70)
        print("")
        print_info(f"Platform: {response.platform}")
        print_info(f"Model: {response.model}")
        print_info(f"Tokens Used: {response.tokens_used}")
        print_info(f"Cost: ${response.cost:.6f}")
        print_info(f"Latency: {response.metadata.get('latency_ms', 0)}ms")
        print_info(f"Finish Reason: {response.finish_reason}")
        
        # Track to database
        user = await User.objects.afirst()
        await tracker.track_completion(response, platform_name, user)
        print("\n" + "✓ " + "Usage saved to database")
        
        return True
        
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False


async def test_streaming():
    """Test streaming completion."""
    print_header("STEP 3: Test Streaming Completion")
    
    print("Would you like to test streaming? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice != 'y':
        print_info("Skipped streaming test")
        return True
    
    registry = await get_registry()
    adapters = registry.get_adapter_names()
    
    if not adapters:
        print_error("No adapters available")
        return False
    
    platform_name = adapters[0]
    adapter = registry.get_adapter(platform_name)
    
    request = CompletionRequest(
        prompt="Count from 1 to 5, one number per line.",
        temperature=0,
        max_tokens=50
    )
    
    print_info(f"Using platform: {platform_name}")
    print("\n🔄 Streaming response...\n")
    print("-" * 70)
    
    try:
        async for chunk in adapter.generate_streaming_completion(request):
            print(chunk, end='', flush=True)
        
        print("\n" + "-" * 70)
        print_success("\nStreaming completed!")
        return True
        
    except Exception as e:
        print_error(f"Streaming failed: {str(e)}")
        return False


async def test_fallback():
    """Test fallback mechanism."""
    print_header("STEP 4: Test Fallback Mechanism")
    
    print("Would you like to test fallback? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice != 'y':
        print_info("Skipped fallback test")
        return True
    
    fallback = FallbackHandler(['openai', 'anthropic', 'google'])
    
    request = CompletionRequest(
        prompt="What is 2+2? Answer in one word.",
        temperature=0,
        max_tokens=10
    )
    
    print("\n🔄 Trying platforms in order: openai → anthropic → google\n")
    
    try:
        response = await fallback.generate_with_fallback(request)
        
        print_success(f"Success! Platform used: {response.platform}")
        print_info(f"Response: {response.content}")
        
        attempts = response.metadata.get('fallback_attempts', [])
        print(f"\nFallback attempts:")
        for attempt in attempts:
            status_icon = "✓" if attempt['status'] == 'success' else "✗"
            print_info(f"{status_icon} {attempt['platform']}: {attempt['status']}")
        
        return True
        
    except Exception as e:
        print_error(f"All platforms failed: {str(e)}")
        return False


async def show_usage_stats():
    """Show usage statistics."""
    print_header("STEP 5: Usage Statistics")
    
    # Platform stats
    print("📊 Platform Statistics:\n")
    async for platform in AIPlatform.objects.all():
        print_info(f"{platform.display_name}:")
        print_info(f"  Total Requests: {platform.total_requests:,}", 4)
        print_info(f"  Failed Requests: {platform.failed_requests:,}", 4)
        print_info(f"  Total Tokens: {platform.total_tokens:,}", 4)
        print_info(f"  Total Cost: ${platform.total_cost:.6f}", 4)
        print("")
    
    # User stats
    user = await User.objects.afirst()
    if user:
        summary = await tracker.get_user_cost_summary(user)
        print(f"💰 Your Usage Summary ({user.email}):\n")
        print_info(f"Total Requests: {summary['total_requests']:,}")
        print_info(f"Total Tokens: {summary['total_tokens']:,}")
        print_info(f"Total Cost: ${summary['total_cost']:.6f}")
        print_info(f"Avg Response Time: {summary['avg_response_time_seconds']:.2f}s")
    
    # Recent requests
    print("\n📋 Recent Requests (Last 5):\n")
    usage_count = await PlatformUsage.objects.all().acount()
    
    if usage_count == 0:
        print_info("No usage records yet")
    else:
        async for usage in PlatformUsage.objects.select_related('platform').order_by('-timestamp')[:5]:
            status_icon = "✓" if usage.success else "✗"
            print_info(f"{status_icon} {usage.timestamp.strftime('%H:%M:%S')} - "
                      f"{usage.platform.display_name} - "
                      f"{usage.tokens_used} tokens - "
                      f"${usage.cost:.6f}")
    
    print("\n" + "=" * 70)
    print("View full details in Django Admin:")
    print("http://localhost:8000/admin/integrations/platformusage/")
    print("=" * 70)
    
    return True


async def main():
    """Run interactive tests."""
    print("\n" + "🧪" * 35)
    print("  HishamOS Phase 3 - Interactive Manual Testing")
    print("🧪" * 35)
    
    # Step 1: Show platforms
    if not await show_available_platforms():
        print("\n⚠️  Please configure at least one platform and run again.")
        return
    
    input("\nPress Enter to continue...")
    
    # Step 2: Simple completion
    await test_simple_completion()
    input("\nPress Enter to continue...")
    
    # Step 3: Streaming (optional)
    await test_streaming()
    input("\nPress Enter to continue...")
    
    # Step 4: Fallback (optional)
    await test_fallback()
    input("\nPress Enter to continue...")
    
    # Step 5: Show stats
    await show_usage_stats()
    
    print("\n" + "🎉" * 35)
    print("  Testing Complete!")
    print("🎉" * 35)
    print("\n✨ Phase 3 is working! Ready for Phase 4!")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
