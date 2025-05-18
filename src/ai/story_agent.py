"""
Story generation agent for creating dynamic game narratives.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional
import aiohttp
from .agent_base import BaseAgent

# Configure logger
logger = logging.getLogger(__name__)

class StoryAgent(BaseAgent):
    """Agent responsible for generating and managing the game's story."""
    
    def __init__(self, api_key: Optional[str] = None, tileset=None):
        """Initialize the story agent.
        
        Args:
            api_key: Optional API key for AI service
            tileset: The game tileset to use for tile operations
        """
        super().__init__(api_key or os.getenv("XAI_API_KEY"))
        if not self.api_key:
            logger.warning("No API key provided for story agent")
        self.story_context = {
            "current_location": None,
            "active_quests": [],
            "completed_quests": [],
            "known_npcs": {},
            "player_choices": []
        }
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.tileset = tileset

    async def think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process story input and generate a response.
        
        Args:
            input_data: The input data containing story context and player actions
            
        Returns:
            The generated story response
        """
        # Update context with new information
        self.update_context(input_data)
        
        # Prepare the prompt for the AI
        prompt = self._create_story_prompt(input_data)
        
        # Call the xAI API
        response = await self._call_xai_api(prompt)
        
        return self._process_story_response(response)

    async def act(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Take action based on the story response.
        
        Args:
            response: The response from think()
            
        Returns:
            The result of the story action
        """
        # Update story state based on the response
        self._update_story_state(response)
        
        # Return the processed story action
        return {
            "story_update": response.get("story_update", {}),
            "npc_responses": response.get("npc_responses", {}),
            "quest_updates": response.get("quest_updates", [])
        }

    def _create_story_prompt(self, input_data: Dict[str, Any]) -> str:
        """Create a prompt for the AI based on current context.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The formatted prompt
        """
        context = self.state.context
        return f"""You are a game master for an RPG adventure. Generate a story response based on the following context:

Current Location: {context.get('current_location', 'Unknown')}
Active Quests: {json.dumps(context.get('active_quests', []))}
Player Choices: {json.dumps(context.get('player_choices', []))}

Player Action: {input_data.get('player_action', 'unknown')}
Player Choice: {input_data.get('player_choice', 'none')}

When describing scenes, use these basic elements:

Base Terrain:
- grass (plain or wild)
- path (dirt or stone)
- water

Structures:
- walls (stone or wood)
- doors (wood or metal)
- floors (stone or wood)

Features:
- trees
- rocks
- bushes
- flowers

Objects:
- chests
- barrels
- tables
- chairs

Characters:
- villagers
- merchants
- guards
- monsters (small or large)

Describe scenes using these elements. For example:
"A dirt path leads through a village, with wooden houses on either side. Trees and bushes dot the landscape, and villagers mill about near market stalls with barrels and tables."

Generate a response in the following JSON format:
{
    "story_update": "A narrative description of what happens next",
    "npc_responses": {
        "npc_id": "What the NPC says or does"
    },
    "quest_updates": [
        {
            "quest_id": "quest identifier",
            "status": "new/updated/completed",
            "description": "quest update description"
        }
    ]
}

Keep the response concise and focused on the immediate situation. Return ONLY the JSON response, no additional text."""

    async def _call_xai_api(self, prompt: str) -> Dict[str, Any]:
        """Call the xAI API with the given prompt.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The API response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "grok-3-latest",
            "messages": [
                {"role": "system", "content": "You are a game master for an RPG adventure. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    response_text = await response.text()
                    logger.info(f"\nAPI Response Status: {response.status}")
                    logger.info(f"API Response Headers: {response.headers}")
                    logger.info(f"API Response Body: {response_text[:500]}...")  # Print first 500 chars
                    
                    if response.status == 200:
                        result = json.loads(response_text)
                        # Try to extract the content from the response
                        try:
                            if "choices" in result and len(result["choices"]) > 0:
                                content = result["choices"][0]["message"]["content"]
                            else:
                                content = result.get("content", response_text)
                            
                            # Try to parse the content as JSON
                            try:
                                return json.loads(content)
                            except json.JSONDecodeError:
                                logger.error(f"Failed to parse response as JSON: {content}")
                                # Try to extract JSON from the text
                                import re
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    return json.loads(json_match.group())
                                raise
                        except Exception as e:
                            logger.error(f"Error processing API response: {str(e)}")
                            raise
                    else:
                        raise Exception(f"API call failed with status {response.status}: {response_text}")
        except Exception as e:
            logger.error(f"Error calling xAI API: {str(e)}")
            # Return a fallback response if the API call fails
            return {
                "story_update": "The story continues, but something seems to be interfering with the narrative...",
                "npc_responses": {},
                "quest_updates": []
            }

    def _process_story_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process the raw API response into a structured format.
        
        Args:
            response: The raw API response
            
        Returns:
            The processed response
        """
        # Validate the response structure
        required_keys = ["story_update", "npc_responses", "quest_updates"]
        for key in required_keys:
            if key not in response:
                response[key] = {} if key == "npc_responses" else [] if key == "quest_updates" else ""
        
        return response

    def _update_story_state(self, response: Dict[str, Any]):
        """Update the story state based on the response.
        
        Args:
            response: The story response
        """
        # Update quests
        if "quest_updates" in response:
            self.story_context["active_quests"] = response["quest_updates"]
        
        # Update NPCs
        if "npc_responses" in response:
            self.story_context["known_npcs"].update(response["npc_responses"])
        
        # Update memory
        self.update_memory({
            "timestamp": "current_time",  # TODO: Add proper timestamp
            "story_update": response.get("story_update", ""),
            "context": self.story_context.copy()
        }) 

    async def generate_intro(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a story introduction.
        
        Args:
            context: Optional context for story generation
            
        Returns:
            Generated story introduction
        """
        try:
            # Call AI service
            response = await self._call_xai_api(self._create_story_prompt(context))
            
            try:
                # Process the response
                story = self._process_story_response(response)
                return story
            except Exception as e:
                logger.error(f"Error processing API response: {str(e)}")
                return self._get_fallback_intro(context)
                
        except Exception as e:
            logger.error(f"Error calling xAI API: {str(e)}")
            return self._get_fallback_intro(context) 

    def _process_tile_request(self, tile_request: str) -> Optional[int]:
        """Process a tile request from the story agent.
        
        Args:
            tile_request: The tile request string
            
        Returns:
            A tile ID that matches the request, or None if no match found
        """
        try:
            # Check if we have a tileset
            if not self.tileset or not self.tileset.indexer:
                logger.warning("No tileset available for tile request")
                return None
                
            # Use the scene describer to convert the request into scene elements
            from core.scene_description import SceneDescriber, SceneElement
            scene_describer = SceneDescriber(self.tileset.indexer)
            
            # Map common descriptions to specific scene elements
            element = None
            request_lower = tile_request.lower()
            
            # Base terrain
            if "grass" in request_lower:
                element = SceneElement.GRASS_PLAIN if "plain" in request_lower else SceneElement.GRASS_WILD
            elif "path" in request_lower or "road" in request_lower:
                element = SceneElement.DIRT_PATH if "dirt" in request_lower else SceneElement.STONE_PATH
            elif "water" in request_lower:
                element = SceneElement.WATER
                
            # Structures
            elif "wall" in request_lower:
                element = SceneElement.WALL_STONE if "stone" in request_lower else SceneElement.WALL_WOOD
            elif "door" in request_lower:
                element = SceneElement.DOOR_METAL if "metal" in request_lower else SceneElement.DOOR_WOOD
            elif "floor" in request_lower:
                element = SceneElement.FLOOR_STONE if "stone" in request_lower else SceneElement.FLOOR_WOOD
                
            # Features
            elif "tree" in request_lower:
                element = SceneElement.TREE
            elif "rock" in request_lower:
                element = SceneElement.ROCK
            elif "bush" in request_lower:
                element = SceneElement.BUSH
            elif "flower" in request_lower:
                element = SceneElement.FLOWER
                
            # Objects
            elif "chest" in request_lower:
                element = SceneElement.CHEST
            elif "barrel" in request_lower:
                element = SceneElement.BARREL
            elif "table" in request_lower:
                element = SceneElement.TABLE
                
            # If no match found, default to grass plain
            if element is None:
                logger.debug(f"No direct mapping for tile request '{tile_request}', defaulting to grass")
                element = SceneElement.GRASS_PLAIN
            
            # Get the tile ID for the element
            tile_id = scene_describer.get_tile_for_element(element)
            if tile_id is None:
                logger.warning(f"Could not find tile ID for element {element}")
                return None
                
            return tile_id
            
        except Exception as e:
            logger.error(f"Error processing tile request '{tile_request}': {e}")
            return None 