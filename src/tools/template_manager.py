"""
Template manager to coordinate all template systems.
"""
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging
from datetime import datetime

from .templates.npc import NPCTemplate, NPCGenerator
from .templates.quest import QuestTemplate, QuestGenerator
from .templates.story_event import StoryEventTemplate, StoryEventGenerator

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages all template systems and their interactions."""
    
    def __init__(self, template_dir: str = "game/templates"):
        """Initialize the template manager.
        
        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template generators
        self.npc_generator = NPCGenerator()
        self.quest_generator = QuestGenerator()
        self.story_event_generator = StoryEventGenerator()
        
        # Load templates
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from files."""
        # Load NPC templates
        npc_dir = self.template_dir / "npcs"
        npc_dir.mkdir(exist_ok=True)
        for template_file in npc_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                template = NPCTemplate.from_dict(template_data)
                self.npc_generator.register_template(template_file.stem, template)
            except Exception as e:
                logger.error(f"Failed to load NPC template {template_file}: {e}")
        
        # Load quest templates
        quest_dir = self.template_dir / "quests"
        quest_dir.mkdir(exist_ok=True)
        for template_file in quest_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                template = QuestTemplate.from_dict(template_data)
                self.quest_generator.register_template(template_file.stem, template)
            except Exception as e:
                logger.error(f"Failed to load quest template {template_file}: {e}")
        
        # Load story event templates
        event_dir = self.template_dir / "events"
        event_dir.mkdir(exist_ok=True)
        for template_file in event_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                template = StoryEventTemplate.from_dict(template_data)
                self.story_event_generator.register_template(template_file.stem, template)
            except Exception as e:
                logger.error(f"Failed to load story event template {template_file}: {e}")
    
    def save_template(self, template_type: str, template_id: str, template_data: Dict[str, Any]):
        """Save a template to file.
        
        Args:
            template_type: Type of template ("npc", "quest", or "event")
            template_id: Unique identifier for the template
            template_data: Template data to save
        """
        template_dir = self.template_dir / f"{template_type}s"
        template_dir.mkdir(exist_ok=True)
        
        template_file = template_dir / f"{template_id}.json"
        with open(template_file, "w") as f:
            json.dump(template_data, f, indent=2)
        
        # Reload templates
        self._load_templates()
    
    def generate_npc(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Generate an NPC instance.
        
        Args:
            template_id: ID of the template to use
            **kwargs: Additional parameters to override template values
            
        Returns:
            Generated NPC data
        """
        return self.npc_generator.generate_npc(template_id, **kwargs)
    
    def generate_quest(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Generate a quest instance.
        
        Args:
            template_id: ID of the template to use
            **kwargs: Additional parameters to override template values
            
        Returns:
            Generated quest data
        """
        return self.quest_generator.generate_quest(template_id, **kwargs)
    
    def generate_story_event(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Generate a story event instance.
        
        Args:
            template_id: ID of the template to use
            **kwargs: Additional parameters to override template values
            
        Returns:
            Generated story event data
        """
        return self.story_event_generator.generate_event(template_id, **kwargs)
    
    def update_npc(self, npc_data: Dict[str, Any], interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Update NPC with new interaction data.
        
        Args:
            npc_data: Current NPC data
            interaction: New interaction data
            
        Returns:
            Updated NPC data
        """
        return self.npc_generator.update_npc(npc_data, interaction)
    
    def update_quest_progress(self, quest_data: Dict[str, Any], objective: str, progress: int) -> Dict[str, Any]:
        """Update quest progress.
        
        Args:
            quest_data: Current quest data
            objective: Description of the objective to update
            progress: New progress value
            
        Returns:
            Updated quest data
        """
        return self.quest_generator.update_quest_progress(quest_data, objective, progress)
    
    def update_event_status(self, event_data: Dict[str, Any], status: str, outcome: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update event status.
        
        Args:
            event_data: Current event data
            status: New status
            outcome: Optional outcome data
            
        Returns:
            Updated event data
        """
        return self.story_event_generator.update_event_status(event_data, status, outcome)
    
    def record_player_choice(self, event_data: Dict[str, Any], choice: Dict[str, Any]) -> Dict[str, Any]:
        """Record a player's choice during an event.
        
        Args:
            event_data: Current event data
            choice: Choice data
            
        Returns:
            Updated event data
        """
        return self.story_event_generator.record_player_choice(event_data, choice) 