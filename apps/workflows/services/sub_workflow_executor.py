"""
Sub-workflow Executor Service

Handles execution of nested workflows (sub-workflows) within parent workflows.
"""

import logging
import uuid
from typing import Dict, Any, Optional, TYPE_CHECKING
from django.core.exceptions import ObjectDoesNotExist
from apps.workflows.models import Workflow
from .workflow_parser import workflow_parser, ParsedStep

if TYPE_CHECKING:
    from .workflow_executor import WorkflowExecutor

logger = logging.getLogger(__name__)


class SubWorkflowExecutionError(Exception):
    """Raised when sub-workflow execution fails."""
    pass


async def execute_sub_workflow(
    parent_executor: "WorkflowExecutor",
    parent_execution_id: str,
    step: ParsedStep,
    context: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a sub-workflow step.
    
    Args:
        parent_executor: Parent workflow executor instance
        parent_execution_id: Parent workflow execution ID
        step: Sub-workflow step definition
        context: Current workflow context
        user_id: Optional user ID
        
    Returns:
        Dictionary with sub-workflow execution results
        
    Raises:
        SubWorkflowExecutionError: If sub-workflow execution fails
    """
    if not step.sub_workflow:
        raise SubWorkflowExecutionError(f"Step {step.id} is not a sub-workflow step")
    
    sub_workflow_config = step.sub_workflow
    workflow_id_or_slug = sub_workflow_config.get('workflow_id')
    
    if not workflow_id_or_slug:
        raise SubWorkflowExecutionError(f"Sub-workflow step {step.id} must specify 'workflow_id'")
    
    # Load the sub-workflow
    try:
        # Try as UUID first
        try:
            workflow_uuid = uuid.UUID(workflow_id_or_slug)
            sub_workflow = Workflow.objects.get(id=workflow_uuid)
        except (ValueError, ObjectDoesNotExist):
            # Try as slug
            sub_workflow = Workflow.objects.get(slug=workflow_id_or_slug)
    except ObjectDoesNotExist:
        raise SubWorkflowExecutionError(
            f"Sub-workflow '{workflow_id_or_slug}' not found for step {step.id}"
        )
    
    # Parse the sub-workflow definition
    try:
        parsed_sub_workflow = workflow_parser.parse(sub_workflow.definition)
    except Exception as e:
        raise SubWorkflowExecutionError(
            f"Failed to parse sub-workflow '{workflow_id_or_slug}': {str(e)}"
        )
    
    # Map inputs from parent context to sub-workflow inputs
    input_mapping = sub_workflow_config.get('input_mapping', {})
    sub_workflow_inputs = {}
    
    for sub_key, parent_path in input_mapping.items():
        try:
            # Resolve parent path
            if isinstance(parent_path, str) and parent_path.startswith('{{') and parent_path.endswith('}}'):
                parent_path = parent_path[2:-2].strip()
            
            value = _get_nested_value(context, parent_path)
            sub_workflow_inputs[sub_key] = value
        except KeyError as e:
            logger.warning(
                f"Could not map input '{sub_key}' from parent path '{parent_path}' "
                f"in sub-workflow step {step.id}: {str(e)}"
            )
            # Use None as default
            sub_workflow_inputs[sub_key] = None
    
    # Execute the sub-workflow
    # Import here to avoid circular import
    from .workflow_executor import workflow_executor
    
    try:
        sub_execution_result = await workflow_executor.execute(
            workflow=sub_workflow,
            input_data=sub_workflow_inputs,
            user_id=user_id
        )
        
        if not sub_execution_result.get('success', False):
            raise SubWorkflowExecutionError(
                f"Sub-workflow '{workflow_id_or_slug}' execution failed: "
                f"{sub_execution_result.get('error', 'Unknown error')}"
            )
        
        sub_output = sub_execution_result.get('output', {})
        
        # Map outputs from sub-workflow back to parent context
        output_mapping = sub_workflow_config.get('output_mapping', {})
        
        mapped_outputs = {}
        for parent_key, sub_path in output_mapping.items():
            try:
                if isinstance(sub_path, str):
                    # If sub_path is a string, treat it as a key in sub_output
                    value = sub_output.get(sub_path) if isinstance(sub_output, dict) else sub_output
                else:
                    # If sub_path is a path, resolve it
                    if isinstance(sub_path, str) and sub_path.startswith('{{') and sub_path.endswith('}}'):
                        sub_path = sub_path[2:-2].strip()
                    value = _get_nested_value(sub_output, sub_path) if isinstance(sub_output, dict) else sub_output
                
                mapped_outputs[parent_key] = value
            except (KeyError, AttributeError) as e:
                logger.warning(
                    f"Could not map output '{parent_key}' from sub-workflow path '{sub_path}' "
                    f"in sub-workflow step {step.id}: {str(e)}"
                )
        
        # If no output mapping specified, use entire sub-workflow output
        if not output_mapping:
            mapped_outputs = sub_output
        
        return {
            'success': True,
            'output': mapped_outputs,
            'sub_workflow_id': str(sub_workflow.id),
            'sub_workflow_name': sub_workflow.name,
            'sub_execution_id': sub_execution_result.get('execution_id')
        }
        
    except Exception as e:
        raise SubWorkflowExecutionError(
            f"Error executing sub-workflow '{workflow_id_or_slug}': {str(e)}"
        )


def _get_nested_value(context: Dict[str, Any], path: str) -> Any:
    """
    Get nested value from context using dot notation.
    
    Args:
        context: Context dictionary
        path: Dot-separated path (e.g., "steps.triage.output.severity")
        
    Returns:
        Value at the path
        
    Raises:
        KeyError: If path doesn't exist
    """
    parts = path.split('.')
    value = context
    
    for part in parts:
        if value is None:
            raise KeyError(f"Value is None at '{part}' in path {path}")
        
        if isinstance(value, dict):
            if part not in value:
                raise KeyError(f"Key '{part}' not found in path {path}")
            value = value[part]
        elif isinstance(value, (list, tuple)):
            try:
                index = int(part)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    raise KeyError(f"Index {index} out of range for list in path {path}")
            except ValueError:
                raise KeyError(f"Cannot access '{part}' in list/tuple value in path {path}")
        else:
            raise KeyError(f"Cannot access '{part}' in non-dict value (type: {type(value).__name__}) in path {path}")
    
    return value



