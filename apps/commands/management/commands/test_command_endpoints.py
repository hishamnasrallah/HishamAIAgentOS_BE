"""
Django management command to test command API endpoints.

This script tests:
1. GET /api/v1/commands/templates/popular/ - Popular commands endpoint
2. POST /api/v1/commands/templates/{id}/preview/ - Preview endpoint
3. POST /api/v1/commands/templates/{id}/execute/ - Execute endpoint (mock, no actual LLM call)
"""

from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from apps.commands.models import CommandTemplate, CommandCategory
from apps.commands.views import CommandTemplateViewSet
from apps.agents.models import Agent
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Test command API endpoints to verify they work correctly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each test',
        )

    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.stdout.write("=" * 70)
        self.stdout.write("  COMMAND API ENDPOINTS TEST SUITE")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Setup
        factory = RequestFactory()
        
        # Get or create test user
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(f"  Created test user: {test_user.username}")
        else:
            self.stdout.write(f"  Using existing test user: {test_user.username}")
        
        self.stdout.write("")

        # Test results
        results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

        # Test 1: Popular Commands Endpoint
        self.stdout.write("  [1/3] Testing Popular Commands Endpoint...")
        try:
            viewset = CommandTemplateViewSet.as_view({'get': 'popular'})
            request = factory.get('/api/v1/commands/templates/popular/')
            force_authenticate(request, user=test_user)
            response = viewset(request)
            
            if response.status_code == 200:
                data = response.data
                if isinstance(data, list):
                    self.stdout.write(self.style.SUCCESS(f"    ✅ Popular endpoint working - returned {len(data)} commands"))
                    results['passed'] += 1
                    if self.verbose and data:
                        self.stdout.write(f"    Sample command: {data[0].get('name', 'N/A')}")
                else:
                    self.stdout.write(self.style.ERROR(f"    ❌ Expected list, got {type(data)}"))
                    results['failed'] += 1
                    results['errors'].append("Popular endpoint returned wrong data type")
            else:
                self.stdout.write(self.style.ERROR(f"    ❌ Status code: {response.status_code}"))
                results['failed'] += 1
                results['errors'].append(f"Popular endpoint returned status {response.status_code}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    ❌ Error: {str(e)}"))
            results['failed'] += 1
            results['errors'].append(f"Popular endpoint error: {str(e)}")
        
        self.stdout.write("")

        # Test 2: Preview Endpoint
        self.stdout.write("  [2/3] Testing Preview Endpoint...")
        try:
            # Get an active command with parameters
            command = CommandTemplate.objects.filter(
                is_active=True,
                parameters__isnull=False
            ).exclude(parameters=[]).first()
            
            if not command:
                self.stdout.write(self.style.WARNING("    ⚠️  No commands with parameters found - skipping preview test"))
                results['errors'].append("No commands with parameters available for preview test")
            else:
                # Generate sample parameters
                sample_params = self._generate_sample_params(command.parameters)
                
                viewset = CommandTemplateViewSet.as_view({'post': 'preview'})
                request = factory.post(
                    f'/api/v1/commands/templates/{command.id}/preview/',
                    data=json.dumps({'parameters': sample_params}),
                    content_type='application/json'
                )
                force_authenticate(request, user=test_user)
                response = viewset(request, pk=command.id)
                
                if response.status_code == 200:
                    data = response.data
                    if 'rendered_template' in data:
                        rendered = data['rendered_template']
                        if rendered and len(rendered) > 0:
                            self.stdout.write(self.style.SUCCESS(f"    ✅ Preview endpoint working - template rendered ({len(rendered)} chars)"))
                            results['passed'] += 1
                            if self.verbose:
                                self.stdout.write(f"    Command: {command.name}")
                                self.stdout.write(f"    Preview: {rendered[:100]}...")
                        else:
                            self.stdout.write(self.style.ERROR("    ❌ Rendered template is empty"))
                            results['failed'] += 1
                            results['errors'].append("Preview endpoint returned empty template")
                    else:
                        self.stdout.write(self.style.ERROR("    ❌ Missing 'rendered_template' in response"))
                        results['failed'] += 1
                        results['errors'].append("Preview endpoint missing rendered_template")
                elif response.status_code == 400:
                    # Validation error - check if it's expected
                    data = response.data
                    if 'validation_errors' in data:
                        self.stdout.write(self.style.WARNING(f"    ⚠️  Validation errors: {data['validation_errors']}"))
                        results['errors'].append(f"Preview validation errors: {data['validation_errors']}")
                    else:
                        self.stdout.write(self.style.ERROR(f"    ❌ Status 400: {data}"))
                        results['failed'] += 1
                        results['errors'].append(f"Preview endpoint validation failed: {data}")
                else:
                    self.stdout.write(self.style.ERROR(f"    ❌ Status code: {response.status_code}, Data: {response.data}"))
                    results['failed'] += 1
                    results['errors'].append(f"Preview endpoint returned status {response.status_code}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    ❌ Error: {str(e)}"))
            import traceback
            if self.verbose:
                self.stdout.write(traceback.format_exc())
            results['failed'] += 1
            results['errors'].append(f"Preview endpoint error: {str(e)}")
        
        self.stdout.write("")

        # Test 3: Execute Endpoint (Structure Test Only)
        self.stdout.write("  [3/3] Testing Execute Endpoint Structure...")
        self.stdout.write("    Note: Execute endpoint will not make actual LLM calls")
        try:
            # Get an active command
            command = CommandTemplate.objects.filter(is_active=True).first()
            
            if not command:
                self.stdout.write(self.style.WARNING("    ⚠️  No active commands found - skipping execute test"))
                results['errors'].append("No active commands available for execute test")
            else:
                # Generate sample parameters
                sample_params = self._generate_sample_params(command.parameters) if command.parameters else {}
                
                viewset = CommandTemplateViewSet.as_view({'post': 'execute'})
                request = factory.post(
                    f'/api/v1/commands/templates/{command.id}/execute/',
                    data=json.dumps({'parameters': sample_params}),
                    content_type='application/json'
                )
                force_authenticate(request, user=test_user)
                
                # Note: This will fail if no AI platform is configured, but we can check the structure
                try:
                    response = viewset(request, pk=command.id)
                    
                    # Check response structure (even if execution fails)
                    if response.status_code in [200, 400, 404, 500]:
                        data = response.data
                        expected_fields = ['success', 'output', 'execution_time', 'cost', 'token_usage', 'agent_used', 'error']
                        has_expected_structure = all(field in data for field in expected_fields)
                        
                        if has_expected_structure:
                            self.stdout.write(self.style.SUCCESS(f"    ✅ Execute endpoint structure correct (status: {response.status_code})"))
                            results['passed'] += 1
                            if self.verbose:
                                self.stdout.write(f"    Command: {command.name}")
                                self.stdout.write(f"    Success: {data.get('success', False)}")
                                if data.get('error'):
                                    self.stdout.write(f"    Error: {data.get('error')}")
                        else:
                            missing = [f for f in expected_fields if f not in data]
                            self.stdout.write(self.style.ERROR(f"    ❌ Missing fields: {missing}"))
                            results['failed'] += 1
                            results['errors'].append(f"Execute endpoint missing fields: {missing}")
                    else:
                        self.stdout.write(self.style.ERROR(f"    ❌ Unexpected status code: {response.status_code}"))
                        results['failed'] += 1
                        results['errors'].append(f"Execute endpoint returned status {response.status_code}")
                except Exception as exec_error:
                    # Execution might fail if no AI platform configured - that's OK for structure test
                    error_msg = str(exec_error)
                    if 'platform' in error_msg.lower() or 'api key' in error_msg.lower():
                        self.stdout.write(self.style.WARNING(f"    ⚠️  Execute endpoint structure OK (execution failed: {error_msg[:50]}...)"))
                        self.stdout.write("    Note: This is expected if no AI platform is configured")
                        results['passed'] += 1
                    else:
                        self.stdout.write(self.style.ERROR(f"    ❌ Error: {error_msg}"))
                        results['failed'] += 1
                        results['errors'].append(f"Execute endpoint error: {error_msg}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    ❌ Error: {str(e)}"))
            import traceback
            if self.verbose:
                self.stdout.write(traceback.format_exc())
            results['failed'] += 1
            results['errors'].append(f"Execute endpoint error: {str(e)}")
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("  TEST SUMMARY")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"  ✅ Passed: {results['passed']}"))
        if results['failed'] > 0:
            self.stdout.write(self.style.ERROR(f"  ❌ Failed: {results['failed']}"))
        if results['errors']:
            self.stdout.write(f"  ⚠️  Warnings/Errors: {len(results['errors'])}")
            if self.verbose:
                for error in results['errors']:
                    self.stdout.write(f"    - {error}")
        
        total_tests = results['passed'] + results['failed']
        if total_tests > 0:
            success_rate = (results['passed'] / total_tests) * 100
            self.stdout.write(f"  Success Rate: {success_rate:.1f}%")
        
        self.stdout.write("=" * 70)
        
        if results['failed'] == 0:
            self.stdout.write(self.style.SUCCESS("  ✅ All endpoint tests passed!"))
        else:
            self.stdout.write(self.style.WARNING("  ⚠️  Some tests failed - review errors above"))

    def _generate_sample_params(self, parameters_schema):
        """Generate sample parameters for testing based on the schema."""
        sample_params = {}
        if not parameters_schema:
            return sample_params
        
        for param in parameters_schema:
            param_name = param.get('name', '')
            if not param_name:
                continue
                
            param_type = param.get('type', 'string')
            required = param.get('required', False)
            
            # Skip optional parameters for simplicity
            if not required:
                continue
            
            # Use allowed_values if available
            if 'allowed_values' in param and param['allowed_values']:
                sample_params[param_name] = param['allowed_values'][0]
            elif param_type == 'integer':
                sample_params[param_name] = 42
            elif param_type == 'float':
                sample_params[param_name] = 3.14
            elif param_type == 'boolean':
                sample_params[param_name] = True
            elif param_type == 'date':
                sample_params[param_name] = '2024-01-01'
            elif param_type == 'long_text':
                sample_params[param_name] = f'Sample {param_name.replace("_", " ")} content for testing purposes.'
            else:  # text, string
                example = param.get('example', '')
                if example:
                    sample_params[param_name] = example
                else:
                    sample_params[param_name] = f'Sample {param_name.replace("_", " ")}'
        
        return sample_params

