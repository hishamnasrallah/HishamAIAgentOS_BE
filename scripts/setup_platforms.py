"""
Setup script to create sample AI platform configurations.
Run this once to populate your database with test platforms.
"""
import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.integrations.models import AIPlatform


def create_platforms():
    """Create sample AI platform configurations."""
    
    print("\n" + "=" * 70)
    print("  HishamOS - AI Platform Setup")
    print("=" * 70)
    print("\nThis script will create AI platform configurations.")
    print("You'll need to provide at least one API key.\n")
    
    # Check existing platforms
    existing = AIPlatform.objects.count()
    if existing > 0:
        print(f"⚠️  Found {existing} existing platform(s).")
        response = input("Delete and recreate? (y/n): ").strip().lower()
        if response == 'y':
            AIPlatform.objects.all().delete()
            print("✓ Deleted existing platforms\n")
        else:
            print("Keeping existing platforms\n")
    
    platforms_created = []
    
    # OpenAI
    print("-" * 70)
    print("1️⃣  OpenAI Configuration")
    print("-" * 70)
    response = input("Do you want to add OpenAI? (y/n): ").strip().lower()
    
    if response == 'y':
        api_key = input("Enter your OpenAI API key (or 'skip'): ").strip()
        
        if api_key and api_key.lower() != 'skip':
            platform = AIPlatform.objects.create(
                platform_name='openai',
                display_name='OpenAI GPT-4',
                api_type='openai',
                default_model='gpt-3.5-turbo',
                api_key=api_key,
                api_url='',
                organization_id='',
                timeout=30,
                max_tokens=4096,
                supports_json_mode=True,
                rate_limit_per_minute=60,
                rate_limit_per_day=10000,
                status='active',
                is_enabled=True,
                is_default=True,
                priority=1
            )
            platforms_created.append(platform)
            print(f"✓ Created OpenAI platform (ID: {platform.id})\n")
        else:
            print("⊘ Skipped OpenAI\n")
    
    # Anthropic
    print("-" * 70)
    print("2️⃣  Anthropic Claude Configuration")
    print("-" * 70)
    response = input("Do you want to add Anthropic? (y/n): ").strip().lower()
    
    if response == 'y':
        api_key = input("Enter your Anthropic API key (or 'skip'): ").strip()
        
        if api_key and api_key.lower() != 'skip':
            platform = AIPlatform.objects.create(
                platform_name='anthropic',
                display_name='Anthropic Claude',
                api_type='anthropic',
                default_model='claude-3-sonnet-20240229',
                api_key=api_key,
                api_url='',
                organization_id='',
                timeout=30,
                max_tokens=200000,
                supports_vision=True,
                rate_limit_per_minute=50,
                rate_limit_per_day=5000,
                status='active',
                is_enabled=True,
                is_default=False,
                priority=2
            )
            platforms_created.append(platform)
            print(f"✓ Created Anthropic platform (ID: {platform.id})\n")
        else:
            print("⊘ Skipped Anthropic\n")
    
    # Google Gemini
    print("-" * 70)
    print("3️⃣  Google Gemini Configuration")
    print("-" * 70)
    response = input("Do you want to add Google Gemini? (y/n): ").strip().lower()
    
    if response == 'y':
        api_key = input("Enter your Google API key (or 'skip'): ").strip()
        
        if api_key and api_key.lower() != 'skip':
            platform = AIPlatform.objects.create(
                platform_name='google',
                display_name='Google Gemini',
                api_type='google',
                default_model='gemini-pro',
                api_key=api_key,
                api_url='',
                organization_id='',
                timeout=30,
                max_tokens=32760,
                supports_vision=True,
                rate_limit_per_minute=60,
                rate_limit_per_day=15000,
                status='active',
                is_enabled=True,
                is_default=False,
                priority=3
            )
            platforms_created.append(platform)
            print(f"✓ Created Google Gemini platform (ID: {platform.id})\n")
        else:
            print("⊘ Skipped Google Gemini\n")
    
    # Summary
    print("=" * 70)
    print("  Setup Complete!")
    print("=" * 70)
    
    if platforms_created:
        print(f"\n✓ Created {len(platforms_created)} platform(s):")
        for p in platforms_created:
            print(f"  • {p.display_name} ({p.platform_name})")
        
        print("\n📝 Next Steps:")
        print("  1. Run: python test_phase3_interactive.py")
        print("  2. Or view in admin: http://localhost:8000/admin/integrations/aiplatform/")
    else:
        print("\n⚠️  No platforms created.")
        print("You can run this script again or add platforms manually in admin.")
    
    print("")


def create_demo_platforms_with_placeholders():
    """Create demo platforms with placeholder keys (for testing without real keys)."""
    
    print("\n" + "=" * 70)
    print("  Creating DEMO platforms (placeholder keys)")
    print("=" * 70)
    print("\n⚠️  These won't work for real API calls!")
    print("They're just for viewing the admin interface.\n")
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Delete existing
    AIPlatform.objects.all().delete()
    
    # Create demo platforms
    platforms = [
        {
            'name': 'openai',
            'display_name': 'OpenAI GPT-4',
            'api_key': 'sk-demo-key-replace-with-real-key',
            'priority': 1,
            'rate_limit_per_minute': 60,
        },
        {
            'name': 'anthropic',
            'display_name': 'Anthropic Claude',
            'api_key': 'sk-ant-demo-key-replace-with-real-key',
            'priority': 2,
            'rate_limit_per_minute': 50,
        },
        {
            'name': 'google',
            'display_name': 'Google Gemini',
            'api_key': 'AIza-demo-key-replace-with-real-key',
            'priority': 3,
            'rate_limit_per_minute': 60,
        }
    ]
    
    created = []
    for p in platforms:
        platform = AIPlatform.objects.create(
            name=p['name'],
            display_name=p['display_name'],
            api_key=p['api_key'],
            api_url='',
            organization_id='',
            rate_limit_per_minute=p['rate_limit_per_minute'],
            rate_limit_per_day=10000,
            status='active',
            is_default=(p['priority'] == 1),
            priority=p['priority']
        )
        created.append(platform)
        print(f"✓ Created {platform.display_name}")
    
    print(f"\n✓ Created {len(created)} demo platforms")
    print("\n📝 To use them:")
    print("  1. Go to: http://localhost:8000/admin/integrations/aiplatform/")
    print("  2. Click on each platform and replace the API key with a real one")
    print("  3. Save")
    print("  4. Run: python test_phase3_interactive.py")
    print("")


if __name__ == '__main__':
    print("\nChoose setup mode:")
    print("  1. Interactive setup (enter your API keys)")
    print("  2. Create demo platforms (placeholder keys)")
    print("  3. Exit")
    
    choice = input("\nYour choice (1/2/3): ").strip()
    
    if choice == '1':
        create_platforms()
    elif choice == '2':
        create_demo_platforms_with_placeholders()
    else:
        print("\nExiting. No changes made.")
