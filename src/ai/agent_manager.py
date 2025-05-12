"""
Agent manager for coordinating all game agents.
"""
from typing import Dict, Any, Optional
import asyncio
from .agent_base import BaseAgent
from .story_agent import StoryAgent

class AgentManager:
    """Manages all game agents and their interactions."""
    
    def __init__(self, api_key: str):
        """Initialize the agent manager.
        
        Args:
            api_key: The xAI API key to use for all agents
        """
        self.api_key = api_key
        self.agents: Dict[str, BaseAgent] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all game agents."""
        self.agents["story"] = StoryAgent(self.api_key)
        # TODO: Add more agents as needed (NPC agents, combat agents, etc.)

    async def process_story_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process story-related input through the story agent.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The processed story response
        """
        story_agent = self.agents["story"]
        response = await story_agent.think(input_data)
        return await story_agent.act(response)

    async def process_npc_interaction(self, npc_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process NPC interaction input.
        
        Args:
            npc_id: The ID of the NPC to interact with
            input_data: The interaction input data
            
        Returns:
            The NPC's response
        """
        # TODO: Implement NPC agent processing
        return {"response": "NPC interaction not yet implemented"}

    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get an agent by type.
        
        Args:
            agent_type: The type of agent to get
            
        Returns:
            The requested agent, or None if not found
        """
        return self.agents.get(agent_type) 