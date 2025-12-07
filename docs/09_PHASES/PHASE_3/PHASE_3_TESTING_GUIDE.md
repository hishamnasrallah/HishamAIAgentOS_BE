---
title: "Phase 3 Testing Guide"
description: "Before testing, you need API keys for at least one platform:"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Testing
    - QA
  secondary:
    - Development

tags:
  - phase-3
  - testing
  - test
  - phase
  - core
  - guide

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Phase 3 Testing Guide

## Prerequisites

Before testing, you need API keys for at least one platform:
- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic:** https://console.anthropic.com/settings/keys  
- **Google Gemini:** https://makersuite.google.com/app/apikey

---

## Step 1: Start Django Server

```bash
python manage.py runserver
```

Keep this terminal running.

---

## Step 2: Access Django Admin

1. Open browser: http://localhost:8000/admin/
2. Login with:
   - Username: `admin`
   - Password: `Amman123`

---

## Step 3: Add AI Platform Configuration

### Navigate to AI Platforms
1. Click **"AI Platforms"** in the left sidebar
2. Click **"Add AI Platform"** button

### Configure OpenAI (Example)
Fill in the form:

**Basic Information:**
- Display name: `OpenAI GPT-4`
- Name: Select `openai`
- Status: `Active`
- Is default: ✓ (checked)
- Priority: `1`

**API Configuration:**
- API key: `sk-...` (your OpenAI API key)
- API URL: (leave blank - uses default)
- Organization ID: (optional)

**Rate Limiting:**
- Rate limit per minute: `60`
- Rate limit per day: `10000`

Click **Save**

### Repeat for Other Platforms (Optional)
- Anthropic: name = `anthropic`
- Google: name = `google`

---

## Step 4: Create Test Script

Create `test_adapters.py` in project root:

```python
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
```

---

## Step 5: Run Tests

```bash
python test_adapters.py
```

**Expected Output:**
```
🧪 HishamOS Phase 3 - AI Platform Integration Tests

============================================================
TEST 1: Single Adapter (OpenAI)
============================================================
✓ Registry initialized with 1 adapters
  Available: openai

Sending request to OpenAI...

✓ SUCCESS!
  Platform: openai
  Model: gpt-3.5-turbo
  Response: Hello from HishamOS system here!
  Tokens: 15
  Cost: $0.000015
  Latency: 847ms
  ✓ Usage tracked to database

============================================================
TEST 2: Fallback Mechanism
============================================================
Attempting completion with fallback...

✓ SUCCESS!
  Platform used: openai
  Response: Four
  Fallback attempts: [{'platform': 'openai', 'status': 'success', ...}]

============================================================
TEST 3: Health Checks
============================================================
✓ openai: healthy (892ms)

============================================================
TEST 4: Cost Summary
============================================================
User: admin@hishamos.com
  Total requests: 2
  Total tokens: 25
  Total cost: $0.000025
  Avg response time: 0.85s

============================================================
TEST SUMMARY
============================================================
Passed: 4/4

🎉 All tests passed! Phase 3 is working perfectly!

📊 Check Django Admin for usage logs:
   http://localhost:8000/admin/integrations/platformusage/
```

---

## Step 6: Verify in Admin

1. Go to: http://localhost:8000/admin/integrations/platformusage/
2. You should see 2 usage records
3. Click on one to see full details:
   - Platform, User, Model
   - Tokens used, Cost
   - Success status, Response time

---

## Step 7: Check Platform Statistics

1. Go to: http://localhost:8000/admin/integrations/aiplatform/
2. Click on your OpenAI platform
3. Verify statistics updated:
   - Total requests: 2
   - Total tokens: ~25
   - Total cost: ~$0.000025

---

## Troubleshooting

### "Adapter not found"
- Make sure you created AIPlatform in admin
- Name must be exactly: `openai`, `anthropic`, or `google`
- Status must be `Active`

### "API Error" 
- Check your API key is correct
- Check you have credits/quota
- Check API key has correct permissions

### "Module not found"
- Make sure you're in project root
- Virtual environment activated
- Run from: `c:\Users\hisha\PycharmProjects\hishamAiAgentOS\`

---

## Success Criteria

✅ Test script runs without errors
✅ At least 1 adapter responds successfully  
✅ Usage tracked in database
✅ Admin shows usage logs
✅ Platform statistics updated
✅ Health checks pass

**Once all criteria met, Phase 3 testing is COMPLETE!**
