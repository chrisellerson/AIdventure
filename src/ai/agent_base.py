"""
Base agent class implementing Smol Agents patterns.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel

class AgentState(BaseModel):
    """Base state model for agents."""
    memory: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}

class BaseAgent(ABC):
    """Base agent class that all game agents will inherit from."""
    
    def __init__(self, api_key: str):
        """Initialize the agent.
        
        Args:
            api_key: The xAI API key for this agent
        """
        self.api_key = api_key
        self.state = AgentState()

    @abstractmethod
    async def think(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and generate a response.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The agent's response
        """
        pass

    @abstractmethod
    async def act(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Take action based on the response.
        
        Args:
            response: The response from think()
            
        Returns:
            The result of the action
        """
        pass

    def update_memory(self, memory_item: Dict[str, Any]):
        """Update the agent's memory.
        
        Args:
            memory_item: The memory item to add
        """
        self.state.memory.append(memory_item)

    def update_context(self, context_updates: Dict[str, Any]):
        """Update the agent's context.
        
        Args:
            context_updates: The context updates to apply
        """
        self.state.context.update(context_updates) 