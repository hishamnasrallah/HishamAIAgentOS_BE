"""
Django management command to create subscriptions for existing organizations.

This command:
1. Creates Subscription records for all existing organizations
2. Links organizations to their subscriptions
3. Sets appropriate tier codes and dates

Usage:
    python manage.py create_organization_subscriptions
    python manage.py create_organization_subscriptions --update  # Update existing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization, Subscription, SubscriptionPlan


class Command(BaseCommand):
    help = 'Create subscriptions for existing organizations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing subscriptions instead of skipping them'
        )

    def handle(self, *args, **options):
        update = options['update']

        self.stdout.write("=" * 70)
        self.stdout.write("  CREATING SUBSCRIPTIONS FOR EXISTING ORGANIZATIONS")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Get all organizations
        organizations = Organization.objects.all()
        total_orgs = organizations.count()
        
        self.stdout.write(f"Found {total_orgs} organizations to process...")
        self.stdout.write("")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for org in organizations:
            tier_code = org.subscription_tier or 'trial'
            
            # Get the subscription plan for this tier
            try:
                plan = SubscriptionPlan.objects.get(tier_code=tier_code)
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Plan not found for tier '{tier_code}' for org '{org.name}', skipping..."
                    )
                )
                skipped_count += 1
                continue

            # Check if subscription already exists
            # Check both through active_subscription field and through subscriptions reverse relation
            existing_subscription = None
            if hasattr(org, 'active_subscription') and org.active_subscription:
                existing_subscription = org.active_subscription
            else:
                # Also check through reverse relation
                existing_subscription = org.subscriptions.filter(status='active').first()
            
            if existing_subscription:
                if update:
                    # Update existing subscription
                    existing_subscription.plan = plan
                    existing_subscription.tier_code = tier_code
                    existing_subscription.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Updated subscription for: {org.name} ({tier_code})")
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⊘ Skipped existing subscription for: {org.name}")
                    )
                    skipped_count += 1
                continue

            # Determine billing cycle (default to monthly)
            billing_cycle = 'monthly'
            
            # Calculate dates
            now = timezone.now()
            started_at = org.subscription_start_date or org.created_at.date() if hasattr(org.created_at, 'date') else now.date()
            
            # Use subscription_end_date if exists, otherwise set default period
            if org.subscription_end_date:
                period_end = org.subscription_end_date
                # Calculate period start (30 days before end for monthly)
                period_start = period_end - timedelta(days=30)
            else:
                # Default: 30-day period from now
                period_start = now.date()
                period_end = period_start + timedelta(days=30)

            # Create subscription
            subscription = Subscription.objects.create(
                organization=org,
                plan=plan,
                tier_code=tier_code,
                status='active',
                billing_cycle=billing_cycle,
                started_at=started_at,
                current_period_start=period_start,
                current_period_end=period_end,
            )

            # Link organization to subscription
            org.active_subscription = subscription
            org.save(update_fields=['active_subscription'])

            self.stdout.write(
                self.style.SUCCESS(f"✓ Created subscription for: {org.name} ({tier_code})")
            )
            created_count += 1

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("  ✓ PROCESSING COMPLETE"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write(f"Created: {created_count}")
        self.stdout.write(f"Updated: {updated_count}")
        self.stdout.write(f"Skipped: {skipped_count}")
        self.stdout.write(f"Total: {total_orgs}")
        self.stdout.write("")

