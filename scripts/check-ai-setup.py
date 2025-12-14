#!/usr/bin/env python
"""
Quick script to check AI platform and agent setup.
Run this to verify your OpenRouter configuration.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

print("=" * 70)
print("AI PLATFORM & AGENT SETUP CHECK")
print("=" * 70)
print()

# Check OpenRouter platform
print("1. Checking OpenRouter Platform...")
openrouter = AIPlatform.objects.filter(platform_name='openrouter').first()
if openrouter:
    print(f"   ✓ OpenRouter platform found")
    print(f"   - Status: {openrouter.status}")
    print(f"   - Enabled: {openrouter.is_enabled}")
    print(f"   - API URL: {openrouter.api_url}")
    print(f"   - Default Model: {openrouter.default_model}")
    
    # Check if API key is set
    try:
        api_key = openrouter.get_api_key()
        if api_key:
            print(f"   - API Key: {'*' * 20}...{api_key[-4:]}")
        else:
            print(f"   ⚠ API Key: NOT SET")
    except Exception as e:
        print(f"   ⚠ API Key: Error retrieving - {e}")
else:
    print("   ✗ OpenRouter platform NOT FOUND")
    print("   → Run: python manage.py setup_openrouter --api-key YOUR_KEY")

print()

# Check Mistral agent
print("2. Checking Mistral 7B Assistant Agent...")
mistral_agent = Agent.objects.filter(agent_id='mistral-7b-assistant').first()
if mistral_agent:
    print(f"   ✓ Mistral agent found")
    print(f"   - Name: {mistral_agent.name}")
    print(f"   - Preferred Platform: {mistral_agent.preferred_platform}")
    print(f"   - Model: {mistral_agent.model_name}")
    print(f"   - Status: {mistral_agent.status}")
    
    if mistral_agent.preferred_platform != 'openrouter':
        print(f"   ⚠ WARNING: Preferred platform is '{mistral_agent.preferred_platform}', not 'openrouter'")
else:
    print("   ✗ Mistral agent NOT FOUND")
    print("   → Run: python manage.py setup_openrouter --api-key YOUR_KEY")

print()

# Check all agents
print("3. All Available Agents:")
agents = Agent.objects.filter(status='active').order_by('name')
if agents:
    for agent in agents:
        print(f"   - {agent.name} ({agent.agent_id})")
        print(f"     Platform: {agent.preferred_platform}, Model: {agent.model_name}")
else:
    print("   No active agents found")

print()

# Check all platforms
print("4. All Enabled AI Platforms:")
platforms = AIPlatform.objects.filter(is_enabled=True, status='active')
if platforms:
    for platform in platforms:
        print(f"   - {platform.display_name} ({platform.platform_name})")
        print(f"     Model: {platform.default_model}")
else:
    print("   No enabled platforms found (only mock will be available)")

print()
print("=" * 70)
print("RECOMMENDATIONS:")
print("=" * 70)

if not openrouter:
    print("→ Run the setup command:")
    print("  python manage.py setup_openrouter --api-key YOUR_OPENROUTER_API_KEY")
elif openrouter and not openrouter.is_enabled:
    print("→ Enable OpenRouter platform in the database")
elif openrouter and not mistral_agent:
    print("→ Run the setup command to create the agent:")
    print("  python manage.py setup_openrouter --api-key YOUR_OPENROUTER_API_KEY --update")
elif mistral_agent and mistral_agent.preferred_platform != 'openrouter':
    print("→ Update agent's preferred platform to 'openrouter'")
else:
    print("✓ Setup looks good!")
    print("→ Make sure to RESTART Django server after setup")
    print("→ Use 'Mistral 7B Assistant' agent in chat conversations")

print()

