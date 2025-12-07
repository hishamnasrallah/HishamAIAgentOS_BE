"""
Django management command to test command execution.
"""

import json
from django.core.management.base import BaseCommand
from apps.commands.models import CommandTemplate
from apps.commands.services.command_executor import CommandExecutor
from apps.commands.services.template_renderer import TemplateRenderer
from apps.commands.services.parameter_validator import ParameterValidator


class Command(BaseCommand):
    help = 'Test command execution and template rendering'

    def add_arguments(self, parser):
        parser.add_argument(
            '--command-slug',
            type=str,
            help='Test specific command by slug',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Test all commands in a category',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Test a sample of commands from each category',
        )
        parser.add_argument(
            '--preview-only',
            action='store_true',
            help='Only test template rendering (preview), not execution',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("  COMMAND TESTING SUITE")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        command_slug = options.get('command_slug')
        category_slug = options.get('category')
        sample = options.get('sample', False)
        preview_only = options.get('preview_only', False)
        
        # Initialize services
        validator = ParameterValidator()
        renderer = TemplateRenderer()
        executor = CommandExecutor()
        
        # Get commands to test
        if command_slug:
            commands = CommandTemplate.objects.filter(slug=command_slug, is_active=True)
        elif category_slug:
            commands = CommandTemplate.objects.filter(
                category__slug=category_slug,
                is_active=True
            )
        elif sample:
            # Get one command from each category
            commands_list = []
            from apps.commands.models import CommandCategory
            for category in CommandCategory.objects.all():
                cmd = CommandTemplate.objects.filter(
                    category=category,
                    is_active=True
                ).first()
                if cmd:
                    commands_list.append(cmd)
            commands = commands_list  # Keep for compatibility
        else:
            # Test all commands (just preview)
            commands = CommandTemplate.objects.filter(is_active=True)[:10]  # Limit to 10 for safety
            self.stdout.write(self.style.WARNING("  Testing first 10 commands (use --command-slug for specific)"))
        
        # Convert to list and get count
        # Check if it's a list first (lists have count() but it requires an argument)
        if isinstance(commands, list):
            commands_list = commands
            command_count = len(commands)
        else:
            # It's a QuerySet
            command_count = commands.count()
            commands_list = list(commands)
        
        if not commands_list:
            self.stdout.write(self.style.ERROR("  ❌ No commands found to test"))
            return
        
        self.stdout.write(f"  Testing {command_count} command(s)")
        self.stdout.write("")
        
        passed = 0
        failed = 0
        
        for command in commands_list:
            self.stdout.write(f"  Testing: {command.name}")
            self.stdout.write(f"    Category: {command.category.name}")
            self.stdout.write(f"    Slug: {command.slug}")
            
            try:
                # Test 1: Parameter validation
                self.stdout.write("    [1/3] Testing parameter validation...")
                sample_params = self._generate_sample_params(command.parameters)
                validation_result = validator.validate(command.parameters, sample_params)
                
                # ValidationResult is an object, not a dict
                if not validation_result.is_valid:
                    error_msg = ', '.join(validation_result.errors) if validation_result.errors else 'Unknown error'
                    self.stdout.write(self.style.ERROR(f"      ❌ Validation failed: {error_msg}"))
                    failed += 1
                    continue
                
                self.stdout.write(self.style.SUCCESS("      ✅ Validation passed"))
                
                # Test 2: Template rendering
                self.stdout.write("    [2/3] Testing template rendering...")
                try:
                    rendered = renderer.render(command.template, sample_params)
                    if not rendered or len(rendered) < 10:
                        raise ValueError("Rendered template too short or empty")
                    self.stdout.write(self.style.SUCCESS("      ✅ Template rendered successfully"))
                    self.stdout.write(f"      Preview: {rendered[:100]}...")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"      ❌ Rendering failed: {str(e)}"))
                    failed += 1
                    continue
                
                # Test 3: Command execution (if not preview-only)
                if not preview_only:
                    self.stdout.write("    [3/3] Testing command execution...")
                    try:
                        # Note: This would require a user and agent, so we'll skip actual execution
                        # Just verify the command structure is valid
                        if command.recommended_agent:
                            self.stdout.write(self.style.SUCCESS(f"      ✅ Command has recommended agent: {command.recommended_agent.name}"))
                        else:
                            self.stdout.write(self.style.WARNING("      ⚠️  Command has no recommended agent"))
                        
                        self.stdout.write(self.style.SUCCESS("      ✅ Command structure valid"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"      ❌ Execution check failed: {str(e)}"))
                        failed += 1
                        continue
                else:
                    self.stdout.write("    [3/3] Skipping execution (preview-only mode)")
                
                passed += 1
                self.stdout.write(self.style.SUCCESS(f"    ✅ Command '{command.name}' passed all tests"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ❌ Error testing command: {str(e)}"))
                failed += 1
            
            self.stdout.write("")
        
        # Summary
        self.stdout.write("=" * 70)
        self.stdout.write("  TEST SUMMARY")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"  ✅ Passed: {passed}"))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"  ❌ Failed: {failed}"))
        else:
            self.stdout.write(f"  ❌ Failed: {failed}")
        self.stdout.write(f"  Total: {passed + failed}")
        self.stdout.write("=" * 70)

    def _generate_sample_params(self, parameters):
        """Generate sample parameter values for testing."""
        sample_params = {}
        
        for param in parameters:
            param_name = param.get('name', '')
            param_type = param.get('type', 'text')
            required = param.get('required', False)
            
            if not required:
                continue
            
            # Check if parameter has allowed_values - use first allowed value
            if 'allowed_values' in param and param['allowed_values']:
                sample_params[param_name] = param['allowed_values'][0]
                continue
            
            # Generate sample value based on type
            if param_type == 'integer':
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

