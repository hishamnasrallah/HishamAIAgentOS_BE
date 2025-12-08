"""
Workflow Parser Service

Validates and parses workflow definitions against the JSON schema.
Builds workflow execution graph and validates dependencies.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field


@dataclass
class ParsedStep:
    """Represents a parsed workflow step."""
    id: str
    name: Optional[str]
    agent: str
    inputs: Dict
    condition: Optional[str]
    on_success: Optional[str]
    on_failure: Optional[str]
    max_retries: int
    timeout_seconds: int
    skip_if: Optional[str]
    parallel: bool = False
    parallel_group: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    step_type: str = "agent"  # agent, merge, loop, sub_workflow
    branch_group: Optional[str] = None
    merge_after: Optional[str] = None
    loop: Optional[Dict] = None  # Loop configuration
    sub_workflow: Optional[Dict] = None  # Sub-workflow configuration


@dataclass
class ParsedWorkflow:
    """Represents a fully parsed and validated workflow."""
    name: str
    version: str
    description: Optional[str]
    steps: List[ParsedStep]
    step_map: Dict[str, ParsedStep]  # step_id -> ParsedStep
    entry_step: ParsedStep


class WorkflowParseError(Exception):
    """Raised when workflow parsing fails."""
    pass


class WorkflowParser:
    """
    Parse and validate workflow definitions.
    
    Responsibilities:
    - Validate against JSON schema
    - Build workflow graph
    - Validate step dependencies
    - Check for circular dependencies
    - Ensure all step references are valid
    """
    
    def __init__(self):
        """Load the JSON schema on initialization."""
        schema_path = Path(__file__).parent.parent / 'schemas' / 'workflow_schema.json'
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def parse(self, definition: Dict) -> ParsedWorkflow:
        """
        Parse and validate a workflow definition.
        
        Args:
            definition: Workflow definition dict (from YAML/JSON)
            
        Returns:
            ParsedWorkflow object
            
        Raises:
            WorkflowParseError: If validation or parsing fails
        """
        # Step 1: Validate against JSON schema
        try:
            jsonschema.validate(instance=definition, schema=self.schema)
        except jsonschema.ValidationError as e:
            raise WorkflowParseError(f"Schema validation failed: {e.message}")
        
        # Step 2: Parse steps
        steps = []
        step_map = {}
        
        for step_def in definition['steps']:
            # Determine step type
            step_type = step_def.get('step_type', 'agent')
            
            # For non-agent steps, agent field is optional
            agent = step_def.get('agent', '')
            if step_type == 'agent' and not agent:
                raise WorkflowParseError(f"Step '{step_def['id']}' of type 'agent' must have an 'agent' field")
            
            step = ParsedStep(
                id=step_def['id'],
                name=step_def.get('name'),
                agent=agent,
                inputs=step_def.get('inputs', {}),
                condition=step_def.get('condition'),
                on_success=step_def.get('on_success'),
                on_failure=step_def.get('on_failure'),
                max_retries=step_def.get('max_retries', 3),
                timeout_seconds=step_def.get('timeout_seconds', 300),
                skip_if=step_def.get('skip_if'),
                parallel=step_def.get('parallel', False),
                parallel_group=step_def.get('parallel_group'),
                depends_on=step_def.get('depends_on', []) if step_def.get('depends_on') else [],
                step_type=step_type,
                branch_group=step_def.get('branch_group'),
                merge_after=step_def.get('merge_after'),
                loop=step_def.get('loop'),
                sub_workflow=step_def.get('sub_workflow')
            )
            
            # Check for duplicate step IDs
            if step.id in step_map:
                raise WorkflowParseError(f"Duplicate step ID: {step.id}")
            
            steps.append(step)
            step_map[step.id] = step
        
        # Step 3: Validate step references
        self._validate_step_references(steps, step_map)
        
        # Step 4: Check for circular dependencies
        self._check_circular_dependencies(steps, step_map)
        
        # Step 5: Identify entry step (first step)
        entry_step = steps[0]
        
        return ParsedWorkflow(
            name=definition['name'],
            version=definition['version'],
            description=definition.get('description'),
            steps=steps,
            step_map=step_map,
            entry_step=entry_step
        )
    
    def _validate_step_references(self, steps: List[ParsedStep], step_map: Dict[str, ParsedStep]):
        """
        Validate that all step references (on_success, on_failure) point to valid steps.
        
        Args:
            steps: List of all steps
            step_map: Map of step_id -> ParsedStep
            
        Raises:
            WorkflowParseError: If invalid reference found
        """
        all_step_ids = set(step_map.keys())
        
        for step in steps:
            # Check on_success reference
            if step.on_success and step.on_success not in all_step_ids:
                raise WorkflowParseError(
                    f"Step '{step.id}' references non-existent step '{step.on_success}' in on_success"
                )
            
            # Check on_failure reference
            if step.on_failure and step.on_failure not in all_step_ids:
                raise WorkflowParseError(
                    f"Step '{step.id}' references non-existent step '{step.on_failure}' in on_failure"
                )
    
    def _check_circular_dependencies(self, steps: List[ParsedStep], step_map: Dict[str, ParsedStep]):
        """
        Check for circular dependencies in the workflow graph.
        
        Uses depth-first search to detect cycles.
        
        Args:
            steps: List of all steps
            step_map: Map of step_id -> ParsedStep
            
        Raises:
            WorkflowParseError: If circular dependency detected
        """
        visited = set()
        rec_stack = set()
        
        def dfs(step_id: str, path: List[str]) -> bool:
            """
            DFS to detect cycles.
            
            Returns:
                True if cycle detected, False otherwise
            """
            if step_id in rec_stack:
                # Cycle detected
                cycle_path = ' -> '.join(path + [step_id])
                raise WorkflowParseError(
                    f"Circular dependency detected: {cycle_path}"
                )
            
            if step_id in visited:
                return False
            
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = step_map[step_id]
            
            # Check both success and failure paths
            for next_step_id in [step.on_success, step.on_failure]:
                if next_step_id:
                    dfs(next_step_id, path + [step_id])
            
            rec_stack.remove(step_id)
            return False
        
        # Start DFS from entry point (first step)
        if steps:
            dfs(steps[0].id, [])
    
    def validate_agent_exists(self, agent_name: str, available_agents: Set[str]) -> bool:
        """
        Validate that the agent exists in the system.
        
        Args:
            agent_name: Agent name from workflow definition
            available_agents: Set of available agent names
            
        Returns:
            True if agent exists, False otherwise
        """
        return agent_name in available_agents
    
    def get_execution_order(self, parsed_workflow: ParsedWorkflow) -> List[str]:
        """
        Get suggested execution order (topological sort).
        
        Note: Actual execution may differ based on conditions and failures.
        This is just the "happy path" order.
        
        Args:
            parsed_workflow: Parsed workflow
            
        Returns:
            List of step IDs in suggested execution order
        """
        order = []
        visited = set()
        
        def visit(step_id: str):
            if step_id in visited or step_id is None:
                return
            visited.add(step_id)
            order.append(step_id)
            
            step = parsed_workflow.step_map[step_id]
            # Follow success path for "happy path"
            if step.on_success:
                visit(step.on_success)
        
        visit(parsed_workflow.entry_step.id)
        return order


# Global instance
workflow_parser = WorkflowParser()
