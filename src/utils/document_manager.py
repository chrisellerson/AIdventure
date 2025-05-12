"""
Document manager for handling game state persistence.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

class DocumentManager:
    """Manages game documents and state persistence."""
    
    def __init__(self, base_path: str = "docs"):
        """Initialize the document manager.
        
        Args:
            base_path: Base path for document storage
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            "story",
            "story/locations",
            "npcs/active",
            "npcs/history",
            "quests/active",
            "quests/completed",
            "game_state"
        ]
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
    
    def save_story_state(self, state: Dict[str, Any]):
        """Save the current story state.
        
        Args:
            state: The story state to save
        """
        # Add timestamp
        state["last_updated"] = datetime.now().isoformat()
        
        # Save current state
        with open(self.base_path / "story/current_state.json", "w") as f:
            json.dump(state, f, indent=2)
        
        # Append to history
        history_file = self.base_path / "story/history.json"
        history = []
        if history_file.exists():
            with open(history_file, "r") as f:
                history = json.load(f)
        
        history.append(state)
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
    
    def get_story_state(self) -> Dict[str, Any]:
        """Get the current story state.
        
        Returns:
            The current story state
        """
        state_file = self.base_path / "story/current_state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                return json.load(f)
        return {}
    
    def save_npc_state(self, npc_id: str, state: Dict[str, Any]):
        """Save NPC state.
        
        Args:
            npc_id: The NPC's unique identifier
            state: The NPC's state to save
        """
        # Add timestamp
        state["last_updated"] = datetime.now().isoformat()
        
        # Save to active NPCs
        with open(self.base_path / f"npcs/active/{npc_id}.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def get_npc_state(self, npc_id: str) -> Optional[Dict[str, Any]]:
        """Get NPC state.
        
        Args:
            npc_id: The NPC's unique identifier
            
        Returns:
            The NPC's state, or None if not found
        """
        npc_file = self.base_path / f"npcs/active/{npc_id}.json"
        if npc_file.exists():
            with open(npc_file, "r") as f:
                return json.load(f)
        return None
    
    def archive_npc(self, npc_id: str):
        """Move NPC from active to history.
        
        Args:
            npc_id: The NPC's unique identifier
        """
        active_file = self.base_path / f"npcs/active/{npc_id}.json"
        history_file = self.base_path / f"npcs/history/{npc_id}.json"
        
        if active_file.exists():
            with open(active_file, "r") as f:
                state = json.load(f)
            state["archived_at"] = datetime.now().isoformat()
            
            with open(history_file, "w") as f:
                json.dump(state, f, indent=2)
            
            active_file.unlink()
    
    def save_quest_state(self, quest_id: str, state: Dict[str, Any]):
        """Save quest state.
        
        Args:
            quest_id: The quest's unique identifier
            state: The quest's state to save
        """
        # Add timestamp
        state["last_updated"] = datetime.now().isoformat()
        
        # Determine if quest is active or completed
        directory = "active" if state.get("status") != "completed" else "completed"
        
        with open(self.base_path / f"quests/{directory}/{quest_id}.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def get_quest_state(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get quest state.
        
        Args:
            quest_id: The quest's unique identifier
            
        Returns:
            The quest's state, or None if not found
        """
        # Check active quests first
        quest_file = self.base_path / f"quests/active/{quest_id}.json"
        if not quest_file.exists():
            # Check completed quests
            quest_file = self.base_path / f"quests/completed/{quest_id}.json"
        
        if quest_file.exists():
            with open(quest_file, "r") as f:
                return json.load(f)
        return None
    
    def save_game_state(self, state: Dict[str, Any]):
        """Save overall game state.
        
        Args:
            state: The game state to save
        """
        # Add timestamp
        state["last_updated"] = datetime.now().isoformat()
        
        with open(self.base_path / "game_state/world_state.json", "w") as f:
            json.dump(state, f, indent=2)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get overall game state.
        
        Returns:
            The current game state
        """
        state_file = self.base_path / "game_state/world_state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                return json.load(f)
        return {} 