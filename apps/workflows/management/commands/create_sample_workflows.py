"""
Django management command to create sample workflows for testing.

This command creates several example workflows with proper structure
that can be used for testing the workflow execution system.
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.workflows.models import Workflow
from apps.agents.models import Agent

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class Command(BaseCommand):
    help = 'Create sample workflows for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing workflows before creating new ones',
        )
        parser.add_argument(
            '--from-yaml',
            action='store_true',
            help='Load workflows from YAML definition files',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing workflows...')
            Workflow.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing workflows'))

        if options['from_yaml']:
            self.load_from_yaml()
        else:
            self.create_sample_workflows()

    def load_from_yaml(self):
        """Load workflows from YAML definition files."""
        if not HAS_YAML:
            self.stdout.write(self.style.ERROR(
                'PyYAML is not installed. Install it with: pip install PyYAML'
            ))
            return

        definitions_dir = Path(__file__).parent.parent.parent / 'definitions'
        
        if not definitions_dir.exists():
            self.stdout.write(self.style.WARNING(
                f'Definitions directory not found: {definitions_dir}'
            ))
            return

        yaml_files = list(definitions_dir.glob('*.yaml'))
        
        if not yaml_files:
            self.stdout.write(self.style.WARNING('No YAML definition files found'))
            return

        self.stdout.write(f'Found {len(yaml_files)} YAML definition files')

        # Get all agent names for validation
        agent_names = set(Agent.objects.values_list('name', flat=True))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    definition = yaml.safe_load(f)
                
                # Ensure definition has required fields
                if not isinstance(definition, dict):
                    self.stdout.write(self.style.WARNING(
                        f'Invalid YAML in {yaml_file.name}: not a dictionary'
                    ))
                    continue

                # Validate agent names in steps
                missing_agents = []
                if 'steps' in definition:
                    for step in definition['steps']:
                        agent_name = step.get('agent')
                        if agent_name and agent_name not in agent_names:
                            missing_agents.append(agent_name)
                
                if missing_agents:
                    self.stdout.write(self.style.WARNING(
                        f'{yaml_file.name}: Missing agents: {", ".join(set(missing_agents))}'
                    ))
                    # Replace with first available agent or create placeholder
                    first_agent = Agent.objects.first()
                    if first_agent:
                        for step in definition.get('steps', []):
                            if step.get('agent') in missing_agents:
                                step['agent'] = first_agent.name
                                self.stdout.write(f'  Replaced agent with: {first_agent.name}')

                # Get or create workflow
                name = definition.get('name', yaml_file.stem.replace('_', ' ').title())
                slug = slugify(name)
                
                workflow, created = Workflow.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'description': definition.get('description', ''),
                        'definition': definition,
                        'version': definition.get('version', '1.0.0'),
                        'status': 'active',
                        'is_template': False,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Created workflow: {name}'
                    ))
                else:
                    # Update existing workflow
                    workflow.name = name
                    workflow.description = definition.get('description', '')
                    workflow.definition = definition
                    workflow.version = definition.get('version', '1.0.0')
                    workflow.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Updated workflow: {name}'
                    ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error loading {yaml_file.name}: {str(e)}'
                ))

    def create_sample_workflows(self):
        """Create sample workflows programmatically."""
        # Get or create some agents first
        agents = self.ensure_agents_exist()
        
        if not agents:
            self.stdout.write(self.style.ERROR(
                'No agents available. Please create at least one agent first.'
            ))
            return
        
        agent_name = agents[0].name

        # Create simple test workflow
        simple_workflow = {
            'name': 'Simple Test Workflow',
            'version': '1.0.0',
            'description': 'A simple single-step workflow for testing',
            'steps': [
                {
                    'id': 'step1',
                    'name': 'Execute Task',
                    'agent': agent_name,
                    'inputs': {
                        'task_description': '{{input.task}}'
                    }
                }
            ]
        }

        workflow, created = Workflow.objects.get_or_create(
            slug='simple-test-workflow',
            defaults={
                'name': simple_workflow['name'],
                'description': simple_workflow['description'],
                'definition': simple_workflow,
                'version': simple_workflow['version'],
                'status': 'active',
                'is_template': False,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Created workflow: {simple_workflow["name"]}'
            ))

        # Create multi-step workflow
        multi_step_workflow = {
            'name': 'Multi-Step Test Workflow',
            'version': '1.0.0',
            'description': 'A multi-step workflow for testing sequential execution',
            'steps': [
                {
                    'id': 'step1',
                    'name': 'First Step',
                    'agent': agent_name,
                    'inputs': {
                        'task_description': 'Process the input: {{input.message}}'
                    },
                    'on_success': 'step2'
                },
                {
                    'id': 'step2',
                    'name': 'Second Step',
                    'agent': agent_name,
                    'inputs': {
                        'task_description': 'Continue processing: {{steps.step1.output}}'
                    }
                }
            ]
        }

        workflow, created = Workflow.objects.get_or_create(
            slug='multi-step-test-workflow',
            defaults={
                'name': multi_step_workflow['name'],
                'description': multi_step_workflow['description'],
                'definition': multi_step_workflow,
                'version': multi_step_workflow['version'],
                'status': 'active',
                'is_template': False,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Created workflow: {multi_step_workflow["name"]}'
            ))

        # Create conditional workflow
        conditional_workflow = {
            'name': 'Conditional Test Workflow',
            'version': '1.0.0',
            'description': 'A workflow with conditional logic',
            'steps': [
                {
                    'id': 'check',
                    'name': 'Check Condition',
                    'agent': agent_name,
                    'inputs': {
                        'task_description': 'Evaluate: {{input.value}}'
                    },
                    'on_success': 'process',
                    'on_failure': 'skip'
                },
                {
                    'id': 'process',
                    'name': 'Process Data',
                    'agent': agent_name,
                    'inputs': {
                        'task_description': 'Process: {{steps.check.output}}'
                    },
                    'condition': '{{steps.check.output.success}} == true'
                },
                {
                    'id': 'skip',
                    'name': 'Skip Processing',
                    'agent': agent_name,
                    'inputs': {
                        'task_description': 'Skip processing'
                    }
                }
            ]
        }

        workflow, created = Workflow.objects.get_or_create(
            slug='conditional-test-workflow',
            defaults={
                'name': conditional_workflow['name'],
                'description': conditional_workflow['description'],
                'definition': conditional_workflow,
                'version': conditional_workflow['version'],
                'status': 'active',
                'is_template': False,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Created workflow: {conditional_workflow["name"]}'
            ))

        self.stdout.write(self.style.SUCCESS(
            '\nSuccessfully created sample workflows!'
        ))

    def ensure_agents_exist(self):
        """Ensure at least one agent exists for workflows to use."""
        agents = list(Agent.objects.filter(status='active')[:3])
        
        if not agents:
            self.stdout.write(self.style.WARNING(
                'No active agents found. Creating a test agent...'
            ))
            
            # Create a simple test agent
            agent, created = Agent.objects.get_or_create(
                agent_id='test-agent',
                defaults={
                    'name': 'Test Agent',
                    'description': 'A simple test agent for workflow testing',
                    'system_prompt': 'You are a helpful assistant for testing workflows.',
                    'preferred_platform': 'openai',
                    'model_name': 'gpt-3.5-turbo',
                    'status': 'active',
                    'capabilities': ['CODE_GENERATION', 'TESTING'],
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Created test agent'))
            agents = [agent]

        return agents

