"""
Management command to create test workflows demonstrating Phase 22 features.

These workflows demonstrate:
- Parallel execution
- Conditional branching (if/else/elif)
- Loop support (for and while loops)
- Sub-workflow support
"""

from django.core.management.base import BaseCommand
from apps.workflows.models import Workflow
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test workflows demonstrating Phase 22 advanced features'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing workflows with same slugs',
        )

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        
        # Get or create a system user for test workflows
        user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@hishamos.local', 'is_active': True}
        )
        
        workflows_data = [
            {
                'name': 'Parallel Processing Test',
                'slug': 'phase22-parallel-test',
                'description': 'Test workflow demonstrating parallel step execution',
                'definition': {
                    'name': 'Parallel Processing Test',
                    'version': '1.0.0',
                    'description': 'Demonstrates parallel execution of independent steps',
                    'steps': [
                        {
                            'id': 'init',
                            'name': 'Initialize',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Initialize data processing'
                            }
                        },
                        {
                            'id': 'process_a',
                            'name': 'Process Data A',
                            'agent': 'coding_agent',
                            'parallel': True,
                            'parallel_group': 'processing',
                            'inputs': {
                                'task': 'Process data set A'
                            },
                            'depends_on': ['init']
                        },
                        {
                            'id': 'process_b',
                            'name': 'Process Data B',
                            'agent': 'coding_agent',
                            'parallel': True,
                            'parallel_group': 'processing',
                            'inputs': {
                                'task': 'Process data set B'
                            },
                            'depends_on': ['init']
                        },
                        {
                            'id': 'merge_results',
                            'name': 'Merge Results',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Merge results from A and B'
                            },
                            'depends_on': ['process_a', 'process_b']
                        }
                    ]
                },
                'is_template': True
            },
            {
                'name': 'Conditional Branching Test',
                'slug': 'phase22-conditional-test',
                'description': 'Test workflow demonstrating conditional branching with if/else/elif',
                'definition': {
                    'name': 'Conditional Branching Test',
                    'version': '1.0.0',
                    'description': 'Demonstrates conditional branching with multiple paths',
                    'steps': [
                        {
                            'id': 'check_priority',
                            'name': 'Check Priority',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Evaluate priority level and set output.priority to "high", "medium", or "low"'
                            }
                        },
                        {
                            'id': 'high_priority_branch',
                            'name': 'High Priority Path',
                            'agent': 'coding_agent',
                            'branch_group': 'priority_branch',
                            'condition': '{{steps.check_priority.output.priority}} == "high"',
                            'inputs': {
                                'task': 'Handle high priority task'
                            },
                            'depends_on': ['check_priority']
                        },
                        {
                            'id': 'medium_priority_branch',
                            'name': 'Medium Priority Path',
                            'agent': 'coding_agent',
                            'branch_group': 'priority_branch',
                            'condition': '{{steps.check_priority.output.priority}} == "medium"',
                            'inputs': {
                                'task': 'Handle medium priority task'
                            },
                            'depends_on': ['check_priority']
                        },
                        {
                            'id': 'low_priority_branch',
                            'name': 'Low Priority Path',
                            'agent': 'coding_agent',
                            'branch_group': 'priority_branch',
                            'condition': '{{steps.check_priority.output.priority}} == "low"',
                            'inputs': {
                                'task': 'Handle low priority task'
                            },
                            'depends_on': ['check_priority']
                        },
                        {
                            'id': 'merge_branches',
                            'name': 'Merge Branches',
                            'step_type': 'merge',
                            'agent': '',
                            'merge_after': 'priority_branch',
                            'depends_on': ['high_priority_branch', 'medium_priority_branch', 'low_priority_branch']
                        }
                    ]
                },
                'is_template': True
            },
            {
                'name': 'For Loop Test',
                'slug': 'phase22-for-loop-test',
                'description': 'Test workflow demonstrating for loop iteration over an array',
                'definition': {
                    'name': 'For Loop Test',
                    'version': '1.0.0',
                    'description': 'Demonstrates for loop iteration over an array',
                    'steps': [
                        {
                            'id': 'get_items',
                            'name': 'Get Items',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Retrieve list of items to process. Return output.items as an array of strings.'
                            }
                        },
                        {
                            'id': 'process_items',
                            'name': 'Process Items Loop',
                            'step_type': 'loop',
                            'agent': '',
                            'loop': {
                                'type': 'for',
                                'over': '{{steps.get_items.output.items}}',
                                'variable': 'item',
                                'max_iterations': 100,
                                'steps': [
                                    {
                                        'id': 'process_item',
                                        'name': 'Process Item',
                                        'agent': 'coding_agent',
                                        'inputs': {
                                            'task': 'Process item: {{loop.item}}'
                                        }
                                    }
                                ]
                            },
                            'depends_on': ['get_items']
                        }
                    ]
                },
                'is_template': True
            },
            {
                'name': 'While Loop Test',
                'slug': 'phase22-while-loop-test',
                'description': 'Test workflow demonstrating while loop with condition',
                'definition': {
                    'name': 'While Loop Test',
                    'version': '1.0.0',
                    'description': 'Demonstrates while loop with condition',
                    'steps': [
                        {
                            'id': 'initialize',
                            'name': 'Initialize Counter',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Initialize counter to 0. Return output.counter = 0'
                            }
                        },
                        {
                            'id': 'increment_loop',
                            'name': 'Increment Loop',
                            'step_type': 'loop',
                            'agent': '',
                            'loop': {
                                'type': 'while',
                                'condition': '{{steps.initialize.output.counter}} < 5',
                                'max_iterations': 20,
                                'steps': [
                                    {
                                        'id': 'increment',
                                        'name': 'Increment Counter',
                                        'agent': 'coding_agent',
                                        'inputs': {
                                            'task': 'Increment counter by 1. Update output.counter = {{steps.initialize.output.counter}} + 1'
                                        }
                                    }
                                ]
                            },
                            'depends_on': ['initialize']
                        }
                    ]
                },
                'is_template': True
            },
            {
                'name': 'Complex Workflow Test',
                'slug': 'phase22-complex-test',
                'description': 'Test workflow combining parallel execution, branching, and loops',
                'definition': {
                    'name': 'Complex Workflow Test',
                    'version': '1.0.0',
                    'description': 'Demonstrates parallel execution, branching, loops, and sub-workflows together',
                    'steps': [
                        {
                            'id': 'init',
                            'name': 'Initialize',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Initialize workflow. Return output.items = ["item1", "item2", "item3"]'
                            }
                        },
                        {
                            'id': 'parallel_task_1',
                            'name': 'Parallel Task 1',
                            'agent': 'coding_agent',
                            'parallel': True,
                            'parallel_group': 'parallel_tasks',
                            'inputs': {
                                'task': 'Execute parallel task 1'
                            },
                            'depends_on': ['init']
                        },
                        {
                            'id': 'parallel_task_2',
                            'name': 'Parallel Task 2',
                            'agent': 'coding_agent',
                            'parallel': True,
                            'parallel_group': 'parallel_tasks',
                            'inputs': {
                                'task': 'Execute parallel task 2'
                            },
                            'depends_on': ['init']
                        },
                        {
                            'id': 'check_condition',
                            'name': 'Check Condition',
                            'agent': 'coding_agent',
                            'inputs': {
                                'task': 'Evaluate condition. Return output.result = true'
                            },
                            'depends_on': ['parallel_task_1', 'parallel_task_2']
                        },
                        {
                            'id': 'branch_if',
                            'name': 'If Branch',
                            'agent': 'coding_agent',
                            'branch_group': 'condition_branch',
                            'condition': '{{steps.check_condition.output.result}} == true',
                            'inputs': {
                                'task': 'Execute if branch'
                            },
                            'depends_on': ['check_condition']
                        },
                        {
                            'id': 'branch_else',
                            'name': 'Else Branch',
                            'agent': 'coding_agent',
                            'branch_group': 'condition_branch',
                            'condition': '{{steps.check_condition.output.result}} == false',
                            'inputs': {
                                'task': 'Execute else branch'
                            },
                            'depends_on': ['check_condition']
                        },
                        {
                            'id': 'merge_branches',
                            'name': 'Merge',
                            'step_type': 'merge',
                            'agent': '',
                            'merge_after': 'condition_branch',
                            'depends_on': ['branch_if', 'branch_else']
                        },
                        {
                            'id': 'process_loop',
                            'name': 'Process Loop',
                            'step_type': 'loop',
                            'agent': '',
                            'loop': {
                                'type': 'for',
                                'over': '{{steps.init.output.items}}',
                                'variable': 'item',
                                'max_iterations': 50,
                                'steps': [
                                    {
                                        'id': 'process_item',
                                        'name': 'Process Item',
                                        'agent': 'coding_agent',
                                        'inputs': {
                                            'task': 'Process {{loop.item}}'
                                        }
                                    }
                                ]
                            },
                            'depends_on': ['merge_branches']
                        }
                    ]
                },
                'is_template': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for workflow_data in workflows_data:
            slug = workflow_data['slug']
            
            if overwrite:
                Workflow.objects.filter(slug=slug).delete()
            
            workflow, created = Workflow.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': workflow_data['name'],
                    'description': workflow_data['description'],
                    'definition': workflow_data['definition'],
                    'version': workflow_data['definition']['version'],
                    'status': 'active',
                    'is_template': workflow_data.get('is_template', False),
                    'created_by': user
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created workflow: {workflow.name} ({slug})')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated workflow: {workflow.name} ({slug})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully processed {len(workflows_data)} test workflows: '
                f'{created_count} created, {updated_count} updated'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\nTest workflows created:'
                '\n  - phase22-parallel-test: Parallel execution'
                '\n  - phase22-conditional-test: Conditional branching'
                '\n  - phase22-for-loop-test: For loop iteration'
                '\n  - phase22-while-loop-test: While loop'
                '\n  - phase22-complex-test: Combined features'
            )
        )

