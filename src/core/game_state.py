"""
Game state manager to handle overall game state and coordinate between systems.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from src.tools.template_manager import TemplateManager
from src.utils.document_manager import DocumentManager

@dataclass
class PlayerState:
    """Player's current state."""
    name: str
    level: int = 1
    experience: int = 0
    health: int = 100
    max_health: int = 100
    inventory: Dict[str, Any] = None
    active_quests: List[str] = None  # List of quest IDs
    completed_quests: List[str] = None  # List of quest IDs
    location: str = "starting_area"
    reputation: Dict[str, int] = None  # Faction/group reputations
    
    def __post_init__(self):
        """Initialize default values for mutable attributes."""
        if self.inventory is None:
            self.inventory = {}
        if self.active_quests is None:
            self.active_quests = []
        if self.completed_quests is None:
            self.completed_quests = []
        if self.reputation is None:
            self.reputation = {}

class GameState:
    """Manages the overall game state and coordinates between systems."""
    
    def __init__(self, save_dir: str = "saves"):
        """Initialize the game state manager.
        
        Args:
            save_dir: Directory for save files
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize managers
        self.template_manager = TemplateManager()
        self.document_manager = DocumentManager()
        
        # Game state
        self.player: Optional[PlayerState] = None
        self.current_scene: Optional[str] = None
        self.game_time: datetime = datetime.now()
        self.world_state: Dict[str, Any] = {}
        self.active_events: List[Dict[str, Any]] = []
        self.game_settings: Dict[str, Any] = {
            "difficulty": "normal",
            "text_speed": "medium",
            "music_volume": 0.7,
            "sfx_volume": 0.7
        }
    
    def new_game(self, player_name: str) -> None:
        """Start a new game.
        
        Args:
            player_name: Name of the player character
        """
        self.player = PlayerState(name=player_name)
        self.current_scene = "main_menu"
        self.game_time = datetime.now()
        self.world_state = {}
        self.active_events = []
        
        # Initialize starting area
        self._initialize_starting_area()
    
    def _initialize_starting_area(self) -> None:
        """Initialize the starting area with NPCs and quests."""
        # Generate starting NPCs
        merchant = self.template_manager.generate_npc("test_merchant")
        self.document_manager.save_npc_state(merchant["instance_id"], merchant)
        
        # Generate starting quest
        quest = self.template_manager.generate_quest("gather_materials")
        self.document_manager.save_quest_state(quest["quest_id"], quest)
        
        # Generate starting event
        event = self.template_manager.generate_story_event("merchant_request")
        self.active_events.append(event)
    
    def save_game(self, save_name: str) -> None:
        """Save the current game state.
        
        Args:
            save_name: Name of the save file
        """
        save_data = {
            "player": self.player.__dict__,
            "current_scene": self.current_scene,
            "game_time": self.game_time.isoformat(),
            "world_state": self.world_state,
            "active_events": self.active_events,
            "game_settings": self.game_settings
        }
        
        save_file = self.save_dir / f"{save_name}.json"
        with open(save_file, "w") as f:
            json.dump(save_data, f, indent=2)
    
    def load_game(self, save_name: str) -> None:
        """Load a saved game.
        
        Args:
            save_name: Name of the save file
        """
        save_file = self.save_dir / f"{save_name}.json"
        if not save_file.exists():
            raise FileNotFoundError(f"Save file {save_name} not found")
        
        with open(save_file, "r") as f:
            save_data = json.load(f)
        
        self.player = PlayerState(**save_data["player"])
        self.current_scene = save_data["current_scene"]
        self.game_time = datetime.fromisoformat(save_data["game_time"])
        self.world_state = save_data["world_state"]
        self.active_events = save_data["active_events"]
        self.game_settings = save_data["game_settings"]
    
    def update_quest_progress(self, quest_id: str, objective: str, progress: int) -> None:
        """Update progress for a quest objective.
        
        Args:
            quest_id: ID of the quest
            objective: Description of the objective
            progress: New progress value
        """
        quest_data = self.document_manager.get_quest_state(quest_id)
        if quest_data:
            updated_quest = self.template_manager.update_quest_progress(
                quest_data, objective, progress
            )
            self.document_manager.save_quest_state(quest_id, updated_quest)
    
    def record_npc_interaction(self, npc_id: str, interaction: Dict[str, Any]) -> None:
        """Record an interaction with an NPC.
        
        Args:
            npc_id: ID of the NPC
            interaction: Interaction data
        """
        npc_data = self.document_manager.get_npc_state(npc_id)
        if npc_data:
            updated_npc = self.template_manager.update_npc(npc_data, interaction)
            self.document_manager.save_npc_state(npc_id, updated_npc)
    
    def update_event_status(self, event_id: str, status: str, outcome: Optional[Dict[str, Any]] = None) -> None:
        """Update the status of a story event.
        
        Args:
            event_id: ID of the event
            status: New status
            outcome: Optional outcome data
        """
        for event in self.active_events:
            if event["event_id"] == event_id:
                updated_event = self.template_manager.update_event_status(event, status, outcome)
                if status in ["completed", "failed"]:
                    self.active_events.remove(event)
                break
    
    def get_active_quests(self) -> List[Dict[str, Any]]:
        """Get all active quests.
        
        Returns:
            List of active quest data
        """
        return [
            self.document_manager.get_quest_state(quest_id)
            for quest_id in self.player.active_quests
        ]
    
    def get_nearby_npcs(self) -> List[Dict[str, Any]]:
        """Get NPCs in the current location.
        
        Returns:
            List of NPC data
        """
        # TODO: Implement location-based NPC filtering
        return []
    
    def get_available_events(self) -> List[Dict[str, Any]]:
        """Get events available in the current location.
        
        Returns:
            List of event data
        """
        return [
            event for event in self.active_events
            if event["location"] == self.player.location
        ] 