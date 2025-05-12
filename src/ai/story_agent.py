"""
Story generation agent for creating dynamic game narratives.
"""
import json
from typing import Any, Dict, List
import aiohttp
from .agent_base import BaseAgent

class StoryAgent(BaseAgent):
    """Agent responsible for generating and managing the game's story."""
    
    def __init__(self, api_key: str):
        """Initialize the story agent.
        
        Args:
            api_key: The xAI API key
        """
        super().__init__(api_key)
        self.story_context = {
            "current_location": None,
            "active_quests": [],
            "completed_quests": [],
            "known_npcs": {},
            "player_choices": []
        }
        self.api_url = "https://api.x.ai/v1/chat/completions"

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

Generate a response in the following JSON format:
{{
    "story_update": "A narrative description of what happens next",
    "npc_responses": {{
        "npc_id": "What the NPC says or does"
    }},
    "quest_updates": [
        {{
            "quest_id": "quest identifier",
            "status": "new/updated/completed",
            "description": "quest update description"
        }}
    ]
}}

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
                    print(f"\nAPI Response Status: {response.status}")
                    print(f"API Response Headers: {response.headers}")
                    print(f"API Response Body: {response_text[:500]}...")  # Print first 500 chars
                    
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
                                print(f"Failed to parse response as JSON: {content}")
                                # Try to extract JSON from the text
                                import re
                                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                                if json_match:
                                    return json.loads(json_match.group())
                                raise
                        except Exception as e:
                            print(f"Error processing API response: {str(e)}")
                            raise
                    else:
                        raise Exception(f"API call failed with status {response.status}: {response_text}")
        except Exception as e:
            print(f"Error calling xAI API: {str(e)}")
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