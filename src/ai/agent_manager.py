"""
Agent manager for coordinating all game agents.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import asyncio
from .agent_base import BaseAgent
from .story_agent import StoryAgent

# Configure logger
logger = logging.getLogger(__name__)

class AgentManager:
    """Manages all game agents and their interactions."""
    
    def __init__(self, api_key: str, tileset=None):
        """Initialize the agent manager.
        
        Args:
            api_key: The xAI API key to use for all agents
            tileset: The game tileset to use for tile operations
        """
        self.api_key = api_key
        self.tileset = tileset
        self.agents: Dict[str, BaseAgent] = {}
        self.story_agent = None
        self.dialogue_agent = None
        self.quest_agent = None
        
        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all game agents."""
        try:
            self.agents["story"] = StoryAgent(self.api_key, self.tileset)
            self.story_agent = self.agents["story"]
            # TODO: Add more agents as needed (NPC agents, combat agents, etc.)
            
            logger.info("Successfully initialized all AI agents")
        except Exception as e:
            logger.error(f"Error initializing AI agents: {e}")

    async def get_story_intro(self, player) -> str:
        """Generate a story introduction based on the player's character.
        
        Args:
            player: The player's character data
            
        Returns:
            A story introduction text
        """
        try:
            # Create input data for the story agent
            input_data = {
                "player_action": "start_game",
                "player_class": player.character_class,
                "player_name": player.name,
                "current_location": "starting_area"
            }
            
            # Process through the story agent
            response = await self.process_story_input(input_data)
            
            # Create a formatted story intro
            intro = f"You are {player.name}, a brave {player.character_class} "
            
            # Add class-specific flavor
            if player.character_class == "Warrior":
                intro += "skilled in the art of combat, with strength and courage as your allies. "
            elif player.character_class == "Mage":
                intro += "versed in the arcane arts, with knowledge and magical power at your fingertips. "
            elif player.character_class == "Rogue":
                intro += "mastering stealth and cunning, with agility and quick thinking as your greatest tools. "
            
            # Add story context
            intro += "\n\nYour adventure begins in the village of Eldergrove, a peaceful settlement surrounded by "
            intro += "farmlands and bordered by the Whispering Woods to the east. The townsfolk go about their "
            intro += "daily business, but there's a sense of unease in the air.\n\n"
            
            # Add the AI-generated story content if available
            if response and "story_update" in response:
                intro += response["story_update"]
            else:
                # Fallback intro if API call fails
                intro += "As you walk through the village square, you notice the local merchant waving to get your attention. "
                intro += "\"Ah, a traveler! Just what we needed. We've been having some trouble with wolves in the nearby forest. "
                intro += "Perhaps someone of your skills could help us?\""
            
            return intro
        except Exception as e:
            logger.error(f"Error generating story intro: {e}")
            # Return a fallback intro if there's an error
            return f"You are {player.name}, a {player.character_class} ready to embark on a grand adventure. Your journey begins in the village of Eldergrove."

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