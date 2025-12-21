"""
Django management command to seed subscription plans, features, and tier mappings.

This command:
1. Creates subscription plans (trial, basic, professional, enterprise)
2. Creates all feature definitions
3. Maps features to tiers based on the feature matrix

Usage:
    python manage.py seed_subscriptions
    python manage.py seed_subscriptions --update  # Update existing data
"""

from django.core.management.base import BaseCommand
from apps.organizations.models import SubscriptionPlan, Feature, TierFeature


class Command(BaseCommand):
    help = 'Seed subscription plans, features, and tier feature mappings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing plans and features instead of skipping them'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding (DANGEROUS - use with caution)'
        )

    def handle(self, *args, **options):
        update = options['update']
        clear = options['clear']

        self.stdout.write("=" * 70)
        self.stdout.write("  SEEDING SUBSCRIPTION PLANS AND FEATURES")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        if clear:
            self.stdout.write(
                self.style.WARNING("⚠️  Clearing existing subscription data...")
            )
            TierFeature.objects.all().delete()
            Feature.objects.all().delete()
            SubscriptionPlan.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✓ Cleared existing data"))

        # Step 1: Create Subscription Plans
        self.stdout.write("📦 Step 1: Creating subscription plans...")
        plans_data = [
            {
                'tier_code': 'trial',
                'tier_name': 'Trial',
                'description': 'Free trial with limited features',
                'monthly_price': 0,
                'annual_price': 0,
                'display_order': 1,
                'is_active': True,
            },
            {
                'tier_code': 'basic',
                'tier_name': 'Basic',
                'description': 'Basic plan for small teams',
                'monthly_price': 29.00,
                'annual_price': 290.00,
                'display_order': 2,
                'is_active': True,
            },
            {
                'tier_code': 'professional',
                'tier_name': 'Professional',
                'description': 'Professional plan for growing teams',
                'monthly_price': 99.00,
                'annual_price': 990.00,
                'display_order': 3,
                'is_active': True,
            },
            {
                'tier_code': 'enterprise',
                'tier_name': 'Enterprise',
                'description': 'Enterprise plan with unlimited features',
                'monthly_price': None,  # Custom pricing
                'annual_price': None,  # Custom pricing
                'display_order': 4,
                'is_active': True,
            },
        ]

        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                tier_code=plan_data['tier_code'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created plan: {plan.tier_name}")
                )
            elif update:
                for key, value in plan_data.items():
                    setattr(plan, key, value)
                plan.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Updated plan: {plan.tier_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⊘ Skipped existing plan: {plan.tier_name}")
                )

        # Step 2: Create Features
        self.stdout.write("")
        self.stdout.write("🔧 Step 2: Creating features...")

        features_data = [
            # User Management Features
            {
                'code': 'users.max_count',
                'name': 'Maximum Users',
                'category': 'users',
                'description': 'Maximum number of users allowed in the organization',
                'feature_type': 'count',
                'default_value': {},
            },
            {
                'code': 'users.invite',
                'name': 'Invite Users',
                'category': 'users',
                'description': 'Ability to invite users to the organization',
                'feature_type': 'boolean',
                'default_value': True,
            },
            {
                'code': 'users.roles',
                'name': 'Custom Roles',
                'category': 'users',
                'description': 'Create and manage custom user roles',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'users.sso',
                'name': 'SSO/SAML',
                'category': 'users',
                'description': 'Single Sign-On with SAML support',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'users.audit_log',
                'name': 'Audit Logs',
                'category': 'users',
                'description': 'User activity audit logs',
                'feature_type': 'boolean',
                'default_value': False,
            },
            # Project Management Features
            {
                'code': 'projects.max_count',
                'name': 'Maximum Projects',
                'category': 'projects',
                'description': 'Maximum number of projects allowed',
                'feature_type': 'count',
                'default_value': {},
            },
            {
                'code': 'projects.create',
                'name': 'Create Projects',
                'category': 'projects',
                'description': 'Ability to create new projects',
                'feature_type': 'boolean',
                'default_value': True,
            },
            {
                'code': 'projects.archive',
                'name': 'Archive Projects',
                'category': 'projects',
                'description': 'Ability to archive projects',
                'feature_type': 'boolean',
                'default_value': True,
            },
            {
                'code': 'projects.templates',
                'name': 'Project Templates',
                'category': 'projects',
                'description': 'Access to project templates',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'projects.custom_fields',
                'name': 'Custom Fields',
                'category': 'projects',
                'description': 'Custom project fields',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'projects.import_export',
                'name': 'Import/Export',
                'category': 'projects',
                'description': 'Import and export project data',
                'feature_type': 'boolean',
                'default_value': False,
            },
            # AI & Automation Features
            {
                'code': 'ai.chat',
                'name': 'AI Chat',
                'category': 'ai',
                'description': 'AI chat messages per month',
                'feature_type': 'usage',
                'default_value': {},
            },
            {
                'code': 'ai.agent_executions',
                'name': 'Agent Executions',
                'category': 'ai',
                'description': 'Agent executions per month',
                'feature_type': 'usage',
                'default_value': {},
            },
            {
                'code': 'ai.workflow_executions',
                'name': 'Workflow Executions',
                'category': 'ai',
                'description': 'Workflow executions per month',
                'feature_type': 'usage',
                'default_value': {},
            },
            {
                'code': 'ai.custom_agents',
                'name': 'Custom Agents',
                'category': 'ai',
                'description': 'Create and manage custom AI agents',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'ai.custom_workflows',
                'name': 'Custom Workflows',
                'category': 'ai',
                'description': 'Create and manage custom workflows',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'ai.batch_processing',
                'name': 'Batch Processing',
                'category': 'ai',
                'description': 'Batch processing capabilities',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'ai.api_access',
                'name': 'API Access',
                'category': 'ai',
                'description': 'API access to AI features',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'ai.command_executions',
                'name': 'Command Executions',
                'category': 'ai',
                'description': 'Command executions per month',
                'feature_type': 'usage',
                'default_value': {},
            },
            # Integration Features
            {
                'code': 'integrations.max_count',
                'name': 'Maximum Integrations',
                'category': 'integrations',
                'description': 'Maximum number of integrations',
                'feature_type': 'count',
                'default_value': {},
            },
            {
                'code': 'integrations.github',
                'name': 'GitHub Integration',
                'category': 'integrations',
                'description': 'GitHub integration',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'integrations.slack',
                'name': 'Slack Integration',
                'category': 'integrations',
                'description': 'Slack integration',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'integrations.jira',
                'name': 'Jira Integration',
                'category': 'integrations',
                'description': 'Jira integration',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'integrations.webhooks',
                'name': 'Webhooks',
                'category': 'integrations',
                'description': 'Webhook integrations',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'integrations.custom',
                'name': 'Custom Integrations',
                'category': 'integrations',
                'description': 'Custom integrations',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'integrations.api_keys',
                'name': 'API Keys',
                'category': 'integrations',
                'description': 'Maximum number of API keys',
                'feature_type': 'count',
                'default_value': {},
            },
            # Analytics Features
            {
                'code': 'analytics.basic',
                'name': 'Basic Analytics',
                'category': 'analytics',
                'description': 'Basic analytics and reporting',
                'feature_type': 'boolean',
                'default_value': True,
            },
            {
                'code': 'analytics.advanced',
                'name': 'Advanced Analytics',
                'category': 'analytics',
                'description': 'Advanced analytics and insights',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'analytics.custom_reports',
                'name': 'Custom Reports',
                'category': 'analytics',
                'description': 'Create custom reports',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'analytics.export',
                'name': 'Export Reports',
                'category': 'analytics',
                'description': 'Export analytics reports',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'analytics.api',
                'name': 'Analytics API',
                'category': 'analytics',
                'description': 'API access to analytics data',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'analytics.realtime',
                'name': 'Real-time Analytics',
                'category': 'analytics',
                'description': 'Real-time analytics dashboard',
                'feature_type': 'boolean',
                'default_value': False,
            },
            # Security Features
            {
                'code': 'security.2fa',
                'name': 'Two-Factor Authentication',
                'category': 'security',
                'description': 'Two-factor authentication',
                'feature_type': 'boolean',
                'default_value': True,
            },
            {
                'code': 'security.sso',
                'name': 'SSO/SAML',
                'category': 'security',
                'description': 'Single Sign-On with SAML',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'security.audit_logs',
                'name': 'Audit Logs',
                'category': 'security',
                'description': 'Security audit logs',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'security.ip_whitelist',
                'name': 'IP Whitelisting',
                'category': 'security',
                'description': 'IP address whitelisting',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'security.data_encryption',
                'name': 'Data Encryption',
                'category': 'security',
                'description': 'Data encryption at rest',
                'feature_type': 'boolean',
                'default_value': True,
            },
            {
                'code': 'security.compliance',
                'name': 'Compliance Reports',
                'category': 'security',
                'description': 'Compliance reporting',
                'feature_type': 'boolean',
                'default_value': False,
            },
            {
                'code': 'security.on_premise',
                'name': 'On-Premise Option',
                'category': 'security',
                'description': 'On-premise deployment option',
                'feature_type': 'boolean',
                'default_value': False,
            },
        ]

        features_dict = {}
        for feature_data in features_data:
            feature, created = Feature.objects.get_or_create(
                code=feature_data['code'],
                defaults=feature_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created feature: {feature.name}")
                )
            elif update:
                for key, value in feature_data.items():
                    setattr(feature, key, value)
                feature.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Updated feature: {feature.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⊘ Skipped existing feature: {feature.name}")
                )
            features_dict[feature.code] = feature

        # Step 3: Map Features to Tiers
        self.stdout.write("")
        self.stdout.write("🔗 Step 3: Mapping features to tiers...")

        # Define tier feature mappings based on feature matrix
        tier_feature_mappings = {
            'trial': {
                'users.max_count': 3,
                'users.invite': True,
                'users.roles': False,
                'users.sso': False,
                'users.audit_log': False,
                'projects.max_count': 1,
                'projects.create': True,
                'projects.archive': True,
                'projects.templates': False,
                'projects.custom_fields': False,
                'projects.import_export': False,
                'ai.chat': 50,
                'ai.agent_executions': 10,
                'ai.workflow_executions': 5,
                'ai.command_executions': 20,  # Command executions per month
                'ai.custom_agents': False,
                'ai.custom_workflows': False,
                'ai.batch_processing': False,
                'ai.api_access': False,
                'integrations.max_count': 0,
                'integrations.github': False,
                'integrations.slack': False,
                'integrations.jira': False,
                'integrations.webhooks': False,
                'integrations.custom': False,
                'integrations.api_keys': 1,
                'analytics.basic': True,
                'analytics.advanced': False,
                'analytics.custom_reports': False,
                'analytics.export': False,
                'analytics.api': False,
                'analytics.realtime': False,
                'security.2fa': True,
                'security.sso': False,
                'security.audit_logs': False,
                'security.ip_whitelist': False,
                'security.data_encryption': True,
                'security.compliance': False,
                'security.on_premise': False,
            },
            'basic': {
                'users.max_count': 10,
                'users.invite': True,
                'users.roles': False,
                'users.sso': False,
                'users.audit_log': False,
                'projects.max_count': 5,
                'projects.create': True,
                'projects.archive': True,
                'projects.templates': True,
                'projects.custom_fields': False,
                'projects.import_export': True,
                'ai.chat': 500,
                'ai.agent_executions': 100,
                'ai.workflow_executions': 50,
                'ai.command_executions': 200,  # Command executions per month
                'ai.custom_agents': False,
                'ai.custom_workflows': False,
                'ai.batch_processing': False,
                'ai.api_access': True,
                'integrations.max_count': 1,
                'integrations.github': False,
                'integrations.slack': True,
                'integrations.jira': True,
                'integrations.webhooks': False,
                'integrations.custom': False,
                'integrations.api_keys': 3,
                'analytics.basic': True,
                'analytics.advanced': False,
                'analytics.custom_reports': False,
                'analytics.export': True,
                'analytics.api': False,
                'analytics.realtime': False,
                'security.2fa': True,
                'security.sso': False,
                'security.audit_logs': False,
                'security.ip_whitelist': False,
                'security.data_encryption': True,
                'security.compliance': False,
                'security.on_premise': False,
            },
            'professional': {
                'users.max_count': 50,
                'users.invite': True,
                'users.roles': True,
                'users.sso': False,
                'users.audit_log': True,
                'projects.max_count': 20,
                'projects.create': True,
                'projects.archive': True,
                'projects.templates': True,
                'projects.custom_fields': True,
                'projects.import_export': True,
                'ai.chat': 5000,
                'ai.agent_executions': 1000,
                'ai.workflow_executions': 500,
                'ai.command_executions': 2000,  # Command executions per month
                'ai.custom_agents': True,
                'ai.custom_workflows': True,
                'ai.batch_processing': False,
                'ai.api_access': True,
                'integrations.max_count': 5,
                'integrations.github': True,
                'integrations.slack': True,
                'integrations.jira': True,
                'integrations.webhooks': True,
                'integrations.custom': False,
                'integrations.api_keys': 10,
                'analytics.basic': True,
                'analytics.advanced': True,
                'analytics.custom_reports': True,
                'analytics.export': True,
                'analytics.api': True,
                'analytics.realtime': False,
                'security.2fa': True,
                'security.sso': False,
                'security.audit_logs': True,
                'security.ip_whitelist': False,
                'security.data_encryption': True,
                'security.compliance': False,
                'security.on_premise': False,
            },
            'enterprise': {
                'users.max_count': None,  # Unlimited
                'users.invite': True,
                'users.roles': True,
                'users.sso': True,
                'users.audit_log': True,
                'projects.max_count': None,  # Unlimited
                'projects.create': True,
                'projects.archive': True,
                'projects.templates': True,
                'projects.custom_fields': True,
                'projects.import_export': True,
                'ai.chat': None,  # Unlimited
                'ai.agent_executions': None,  # Unlimited
                'ai.workflow_executions': None,  # Unlimited
                'ai.command_executions': None,  # Unlimited
                'ai.custom_agents': True,
                'ai.custom_workflows': True,
                'ai.batch_processing': True,
                'ai.api_access': True,
                'integrations.max_count': None,  # Unlimited
                'integrations.github': True,
                'integrations.slack': True,
                'integrations.jira': True,
                'integrations.webhooks': True,
                'integrations.custom': True,
                'integrations.api_keys': None,  # Unlimited
                'analytics.basic': True,
                'analytics.advanced': True,
                'analytics.custom_reports': True,
                'analytics.export': True,
                'analytics.api': True,
                'analytics.realtime': True,
                'security.2fa': True,
                'security.sso': True,
                'security.audit_logs': True,
                'security.ip_whitelist': True,
                'security.data_encryption': True,
                'security.compliance': True,
                'security.on_premise': True,
            },
        }

        total_mappings = 0
        for tier_code, feature_mappings in tier_feature_mappings.items():
            for feature_code, value in feature_mappings.items():
                if feature_code not in features_dict:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Feature {feature_code} not found, skipping..."
                        )
                    )
                    continue

                feature = features_dict[feature_code]
                # Convert None to a JSON-serializable null value
                json_value = value if value is not None else None
                
                tier_feature, created = TierFeature.objects.get_or_create(
                    tier_code=tier_code,
                    feature=feature,
                    defaults={'value': json_value, 'is_enabled': True}
                )
                if created:
                    total_mappings += 1
                elif update:
                    tier_feature.value = json_value
                    tier_feature.is_enabled = True
                    tier_feature.save()
                    total_mappings += 1

        self.stdout.write(
            self.style.SUCCESS(f"✓ Created/updated {total_mappings} tier feature mappings")
        )

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("  ✓ SEEDING COMPLETE"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write(f"Plans: {SubscriptionPlan.objects.count()}")
        self.stdout.write(f"Features: {Feature.objects.count()}")
        self.stdout.write(f"Tier Mappings: {TierFeature.objects.count()}")
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "You can now use FeatureService to check features dynamically!"
            )
        )

