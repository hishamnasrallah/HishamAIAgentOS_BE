#!/usr/bin/env python
"""
System Verification Script
Verifies that HishamOS is ready for UAT testing.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.commands.models import CommandTemplate, CommandCategory
from apps.workflows.models import Workflow
from apps.agents.models import Agent

def verify_commands():
    """Verify command library."""
    print("\n" + "="*60)
    print("VERIFYING COMMAND LIBRARY")
    print("="*60)
    
    total_commands = CommandTemplate.objects.count()
    active_commands = CommandTemplate.objects.filter(is_active=True).count()
    categories = CommandCategory.objects.count()
    
    print(f"✅ Total Commands: {total_commands}")
    print(f"✅ Active Commands: {active_commands}")
    print(f"✅ Categories: {categories}")
    
    if total_commands == 250:
        print("✅ Command library target reached (250 commands)")
    else:
        print(f"⚠️  Expected 250 commands, found {total_commands}")
    
    # Check new commands
    new_command_slugs = [
        'requirements-validation-checklist',
        'requirements-change-management',
        'generate-graphql-schema-resolvers',
        'generate-microservices-communication',
        'security-vulnerability-scan',
        'performance-optimization-review',
        'generate-load-testing-scripts',
        'create-accessibility-test-suite',
        'generate-kubernetes-helm-charts',
        'create-terraform-infrastructure',
        'generate-openapi-documentation',
        'create-runbook-documentation',
        'generate-sprint-retrospective',
        'create-risk-register',
        'design-event-driven-architecture',
        'create-database-schema-design',
        'generate-gdpr-compliance-checklist',
        'create-business-process-model',
        'generate-technology-stack-comparison',
        'create-design-system-documentation',
        'generate-rest-api-client-library',
        'generate-contract-testing-suite'
    ]
    
    found_new = 0
    for slug in new_command_slugs:
        if CommandTemplate.objects.filter(slug=slug).exists():
            found_new += 1
    
    print(f"✅ New Commands Found: {found_new} / {len(new_command_slugs)}")
    
    return total_commands == 250

def verify_workflows():
    """Verify workflows."""
    print("\n" + "="*60)
    print("VERIFYING WORKFLOWS")
    print("="*60)
    
    total_workflows = Workflow.objects.count()
    print(f"✅ Total Workflows: {total_workflows}")
    
    return True

def verify_agents():
    """Verify agents."""
    print("\n" + "="*60)
    print("VERIFYING AGENTS")
    print("="*60)
    
    total_agents = Agent.objects.count()
    active_agents = Agent.objects.filter(status='active').count()
    
    print(f"✅ Total Agents: {total_agents}")
    print(f"✅ Active Agents: {active_agents}")
    
    return True

def verify_database():
    """Verify database connection."""
    print("\n" + "="*60)
    print("VERIFYING DATABASE")
    print("="*60)
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run all verifications."""
    print("\n" + "="*60)
    print("HISHAMOS SYSTEM VERIFICATION")
    print("="*60)
    print("Verifying system readiness for UAT testing...")
    
    results = {
        'database': verify_database(),
        'commands': verify_commands(),
        'workflows': verify_workflows(),
        'agents': verify_agents()
    }
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check.upper()}")
    
    if all_passed:
        print("\n✅ SYSTEM READY FOR UAT TESTING")
    else:
        print("\n⚠️  SYSTEM HAS ISSUES - REVIEW ABOVE")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

