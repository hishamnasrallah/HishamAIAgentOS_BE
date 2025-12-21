"""
Management command to check and fix project limit for trial tier.

Usage:
    python manage.py check_project_limit
    python manage.py check_project_limit --fix
    python manage.py check_project_limit --tier trial --value 5
"""

from django.core.management.base import BaseCommand
from apps.organizations.models import TierFeature, Feature
from apps.organizations.services import FeatureService


class Command(BaseCommand):
    help = 'Check and optionally fix project limit for a tier'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tier',
            type=str,
            default='trial',
            help='Tier code to check (default: trial)'
        )
        parser.add_argument(
            '--value',
            type=int,
            help='Value to set (if --fix is used)'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix the value if it doesn\'t match'
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear cache after fixing'
        )

    def handle(self, *args, **options):
        tier_code = options['tier']
        fix = options['fix']
        clear_cache = options['clear_cache']
        target_value = options.get('value')

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Checking project limit for tier: {tier_code}")
        self.stdout.write(f"{'='*60}\n")

        try:
            # Get the feature
            feature = Feature.objects.get(code='projects.max_count')
            self.stdout.write(self.style.SUCCESS(f"✓ Found feature: {feature.code}"))

            # Get tier feature
            try:
                tier_feature = TierFeature.objects.get(
                    tier_code=tier_code,
                    feature=feature
                )
                current_value = tier_feature.value
                self.stdout.write(f"  Current value in database: {current_value}")
                self.stdout.write(f"  Is enabled: {tier_feature.is_enabled}")
            except TierFeature.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"✗ TierFeature not found for tier '{tier_code}'"))
                return

            # Check cached value
            cached_features = FeatureService.get_features_for_tier(tier_code)
            cached_value = cached_features.get('projects.max_count', {}).get('value') if cached_features else None
            self.stdout.write(f"  Cached value: {cached_value}")

            # Check if values match
            if current_value != cached_value:
                self.stdout.write(self.style.WARNING(f"⚠ Warning: Database value ({current_value}) != Cached value ({cached_value})"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Database and cache values match"))

            # Fix if requested
            if fix:
                if target_value is None:
                    self.stdout.write(self.style.ERROR("✗ --value is required when using --fix"))
                    return

                if current_value != target_value:
                    self.stdout.write(f"\nUpdating value from {current_value} to {target_value}...")
                    tier_feature.value = target_value
                    tier_feature.save()
                    self.stdout.write(self.style.SUCCESS(f"✓ Updated database value to {target_value}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"✓ Value already correct ({current_value})"))

                if clear_cache:
                    self.stdout.write("\nClearing cache...")
                    FeatureService.invalidate_cache(tier_code=tier_code)
                    self.stdout.write(self.style.SUCCESS("✓ Cache cleared"))

            # Summary
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write("Summary:")
            self.stdout.write(f"  Tier: {tier_code}")
            self.stdout.write(f"  Database value: {current_value}")
            self.stdout.write(f"  Cached value: {cached_value}")
            if fix and target_value:
                self.stdout.write(f"  Target value: {target_value}")
            self.stdout.write(f"{'='*60}\n")

        except Feature.DoesNotExist:
            self.stdout.write(self.style.ERROR("✗ Feature 'projects.max_count' not found in database"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {str(e)}"))
