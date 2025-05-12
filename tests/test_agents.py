"""
Test script for the agent system.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from src.ai.agent_manager import AgentManager

async def test_story_agent():
    """Test the story agent with a simple input."""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        print("Error: XAI_API_KEY not found in environment variables")
        return
    
    # Initialize the agent manager
    manager = AgentManager(api_key)
    
    # Create a test input
    test_input = {
        "player_action": "explore",
        "current_location": "Starting Town",
        "player_choice": "Talk to the innkeeper"
    }
    
    try:
        # Process the input
        print("Sending test input to story agent...")
        response = await manager.process_story_input(test_input)
        
        # Print the response
        print("\nStory Agent Response:")
        print("-------------------")
        print(f"Story Update: {response.get('story_update', 'No story update')}")
        print(f"NPC Responses: {response.get('npc_responses', {})}")
        print(f"Quest Updates: {response.get('quest_updates', [])}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

def main():
    """Run the test."""
    print("Starting agent system test...")
    asyncio.run(test_story_agent())

if __name__ == "__main__":
    main() 