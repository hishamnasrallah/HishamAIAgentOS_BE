"""
Agent Dispatcher - Intelligently selects and routes tasks to appropriate agents.

Provides automatic agent selection based on:
- Task requirements and capabilities
- Agent availability and health
- Load balancing
- Priority and preferences
"""

from typing import Optional, List, Dict, Any
import logging

from asgiref.sync import sync_to_async
from apps.agents.models import Agent
from apps.agents.engine import AgentCapability


logger = logging.getLogger(__name__)


class AgentDispatcher:
    """
    Dispatches tasks to appropriate agents based on capabilities and load.
    
    The dispatcher analyzes task requirements and selects the best agent
    considering capability matching, availability, and performance metrics.
    """
    
    async def select_agent(
        self,
        required_capabilities: List[str],
        preferred_agent_id: Optional[str] = None,
        exclude_agents: Optional[List[str]] = None
    ) -> Optional[Agent]:
        """
        Select the best agent for a task.
        
        Args:
            required_capabilities: Required agent capabilities
            preferred_agent_id: Preferred agent ID (if any)
            exclude_agents: Agent IDs to exclude
            
        Returns:
            Selected Agent instance or None
        """
        # If preferred agent specified, try to use it
        if preferred_agent_id:
            agent = await self._get_agent_if_suitable(
                preferred_agent_id,
                required_capabilities
            )
            if agent:
                logger.info(f"Using preferred agent: {agent.agent_id}")
                return agent
        
        # Find all suitable agents
        candidates = await self._find_candidate_agents(
            required_capabilities,
            exclude_agents or []
        )
        
        if not candidates:
            logger.warning(f"No agents found with capabilities: {required_capabilities}")
            return None
        
        # Score and rank candidates
        best_agent = await self._rank_and_select(candidates)
        
        logger.info(f"Selected agent: {best_agent.agent_id} for capabilities: {required_capabilities}")
        return best_agent
    
    async def select_agent_for_task(
        self,
        task_description: str,
        task_type: Optional[str] = None,
        preferred_agent_id: Optional[str] = None
    ) -> Optional[Agent]:
        """
        Select agent based on task description.
        
        Analyzes task and infers required capabilities.
        
        Args:
            task_description: Description of the task
            task_type: Optional task type hint
            preferred_agent_id: Preferred agent
            
        Returns:
            Selected Agent or None
        """
        # Infer capabilities from task
        required_capabilities = self._infer_capabilities(
            task_description,
            task_type
        )
        
        return await self.select_agent(
            required_capabilities=required_capabilities,
            preferred_agent_id=preferred_agent_id
        )
    
    async def _get_agent_if_suitable(
        self,
        agent_id: str,
        required_capabilities: List[str]
    ) -> Optional[Agent]:
        """Get agent if it has required capabilities."""
        try:
            agent = await sync_to_async(Agent.objects.get)(
                agent_id=agent_id,
                status='active'
            )
            
            # Check capabilities
            agent_capabilities = agent.capabilities or []
            if all(cap in agent_capabilities for cap in required_capabilities):
                return agent
            else:
                logger.warning(
                    f"Agent {agent_id} lacks required capabilities. "
                    f"Has: {agent_capabilities}, Needs: {required_capabilities}"
                )
                return None
                
        except Agent.DoesNotExist:
            logger.warning(f"Agent {agent_id} not found")
            return None
    
    async def _find_candidate_agents(
        self,
        required_capabilities: List[str],
        exclude_agents: List[str]
    ) -> List[Agent]:
        """Find all agents with required capabilities."""
        # Get all active agents
        agents = await sync_to_async(list)(
            Agent.objects.filter(status='active')
        )
        
        # Filter by capabilities
        candidates = []
        for agent in agents:
            # Skip excluded agents
            if agent.agent_id in exclude_agents:
                continue
            
            # Check capabilities
            agent_capabilities = agent.capabilities or []
            if all(cap in agent_capabilities for cap in required_capabilities):
                candidates.append(agent)
        
        return candidates
    
    async def _rank_and_select(self, candidates: List[Agent]) -> Agent:
        """
        Rank candidate agents and select the best one.
        
        Scoring factors:
        - Success rate (40%)
        - Average response time (30%)
        - Total invocations (20% - prefer experienced agents)
        - Priority (10%)
        
        Args:
            candidates: List of candidate agents
            
        Returns:
            Best agent
        """
        if len(candidates) == 1:
            return candidates[0]
        
        scored_agents = []
        
        for agent in candidates:
            score = 0.0
            
            # Success rate (0-40 points)
            score += (agent.success_rate / 100) * 40
            
            # Response time (0-30 points, lower is better)
            # Normalize: agents with <5s get full points
            if agent.average_response_time > 0:
                time_score = max(0, 30 * (1 - min(agent.average_response_time / 10, 1)))
                score += time_score
            else:
                score += 15  # No data, middle score
            
            # Experience (0-20 points)
            # Normalize: 100+ invocations = full points
            experience_score = min(20, (agent.total_invocations / 100) * 20)
            score += experience_score
            
            # Priority (0-10 points)
            # Assuming priority is 0-10
            score += agent.priority
            
            scored_agents.append((agent, score))
            
            logger.debug(
                f"Agent {agent.agent_id} score: {score:.2f} "
                f"(success: {agent.success_rate}%, "
                f"time: {agent.average_response_time}s, "
                f"invocations: {agent.total_invocations})"
            )
        
        # Sort by score (highest first)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        best_agent = scored_agents[0][0]
        return best_agent
    
    def _infer_capabilities(
        self,
        task_description: str,
        task_type: Optional[str] = None
    ) -> List[str]:
        """
        Infer required capabilities from task description.
        
        Simple keyword-based inference. Can be enhanced with ML later.
        
        Args:
            task_description: Task description
            task_type: Optional task type
            
        Returns:
            List of inferred capabilities
        """
        description_lower = task_description.lower()
        capabilities = []
        
        # Code-related
        if any(word in description_lower for word in ['code', 'function', 'class', 'programming', 'implement']):
            capabilities.append('CODE_GENERATION')
        
        if any(word in description_lower for word in ['review', 'audit', 'check code']):
            capabilities.append('CODE_REVIEW')
        
        # Testing
        if any(word in description_lower for word in ['test', 'testing', 'unit test', 'integration test']):
            capabilities.append('TESTING')
        
        # Documentation
        if any(word in description_lower for word in ['document', 'documentation', 'readme', 'api docs']):
            capabilities.append('DOCUMENTATION')
        
        # Requirements
        if any(word in description_lower for word in ['requirement', 'user story', 'feature']):
            capabilities.append('REQUIREMENTS_ANALYSIS')
        
        # Project management
        if any(word in description_lower for word in ['project', 'plan', 'schedule', 'sprint']):
            capabilities.append('PROJECT_MANAGEMENT')
        
        # DevOps
        if any(word in description_lower for word in ['deploy', 'ci/cd', 'pipeline', 'docker', 'kubernetes']):
            capabilities.append('DEVOPS')
        
        # If task_type provided, use it
        if task_type:
            type_mapping = {
                'code': 'CODE_GENERATION',
                'review': 'CODE_REVIEW',
                'test': 'TESTING',
                'docs': 'DOCUMENTATION',
                'requirements': 'REQUIREMENTS_ANALYSIS',
                'project': 'PROJECT_MANAGEMENT',
            }
            if task_type.lower() in type_mapping:
                cap = type_mapping[task_type.lower()]
                if cap not in capabilities:
                    capabilities.append(cap)
        
        # Default to task execution if nothing found
        if not capabilities:
            capabilities.append('TASK_EXECUTION')
        
        return capabilities
    
    async def get_agent_load_stats(self) -> Dict[str, Any]:
        """
        Get load statistics for all agents.
        
        Useful for monitoring and load balancing.
        
        Returns:
            Dictionary with agent load stats
        """
        agents = await sync_to_async(list)(
            Agent.objects.filter(status='active')
        )
        
        stats = {
            'total_agents': len(agents),
            'agents': []
        }
        
        for agent in agents:
            # Count pending/running executions
            from apps.agents.models import AgentExecution
            
            pending_count = await sync_to_async(
                agent.executions.filter(status='pending').count
            )()
            
            running_count = await sync_to_async(
                agent.executions.filter(status='running').count
            )()
            
            stats['agents'].append({
                'agent_id': agent.agent_id,
                'name': agent.name,
                'pending_tasks': pending_count,
                'running_tasks': running_count,
                'total_invocations': agent.total_invocations,
                'success_rate': agent.success_rate,
                'avg_response_time': agent.average_response_time
            })
        
        return stats


# Global dispatcher instance
dispatcher = AgentDispatcher()
