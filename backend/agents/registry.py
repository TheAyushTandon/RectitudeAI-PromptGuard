"""
Agent Registry — central catalog of all available agents.

Usage:
    from backend.agents.registry import agent_registry
    agent = agent_registry.get_agent("hr_database")
    agents = agent_registry.list_agents()

Agents register themselves by calling registry.register(agent_instance).
"""

from __future__ import annotations
from typing import Dict, List, Optional

from backend.agents.base import BaseAgent
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """Thread-safe singleton registry for all agents."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent instance.

        Args:
            agent: BaseAgent subclass instance
        """
        if agent.name in self._agents:
            logger.warning("Overwriting existing agent: %s", agent.name)
        self._agents[agent.name] = agent
        logger.info(
            "Registered agent: '%s' — %s (tools: %s)",
            agent.name, agent.description, agent.allowed_tools,
        )

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        Retrieve an agent by name.

        Args:
            name: The agent's unique name

        Returns:
            BaseAgent instance or None if not found
        """
        agent = self._agents.get(name)
        if agent is None:
            logger.warning("Agent not found: '%s'", name)
        return agent

    def list_agents(self) -> List[Dict[str, str]]:
        """
        List all registered agents with their metadata.

        Returns:
            List of dicts with name, description, and allowed_tools
        """
        return [
            {
                "name": a.name,
                "description": a.description,
                "allowed_tools": a.allowed_tools,
            }
            for a in self._agents.values()
        ]

    @property
    def agent_names(self) -> List[str]:
        """List of all registered agent names."""
        return list(self._agents.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._agents

    def __len__(self) -> int:
        return len(self._agents)


# Module-level singleton
agent_registry = AgentRegistry()
