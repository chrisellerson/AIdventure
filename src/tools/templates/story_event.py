"""
Story event template system for generating story events.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class EventType(Enum):
    """Types of story events."""
    DIALOGUE = "dialogue"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    CUTSCENE = "cutscene"
    DECISION = "decision"
    QUEST = "quest"
    WORLD = "world"  # World state changes

class EventImportance(Enum):
    """Importance levels of story events."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

@dataclass
class StoryEventTemplate:
    """Template for generating story events."""
    title: str
    description: str
    event_type: EventType
    importance: EventImportance
    location: str
    participants: List[str]  # List of NPC IDs involved
    choices: Optional[List[Dict[str, Any]]] = None  # Available choices for decision events
    consequences: Optional[Dict[str, Any]] = None  # Potential consequences
    requirements: Optional[Dict[str, Any]] = None  # Requirements for event to occur
    time_limit: Optional[int] = None  # Time limit in minutes, None for no limit
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary format."""
        return {
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type.value,
            "importance": self.importance.value,
            "location": self.location,
            "participants": self.participants,
            "choices": self.choices,
            "consequences": self.consequences,
            "requirements": self.requirements,
            "time_limit": self.time_limit,
            "created_at": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryEventTemplate':
        """Create template from dictionary."""
        return cls(
            title=data["title"],
            description=data["description"],
            event_type=EventType(data["event_type"]),
            importance=EventImportance(data["importance"]),
            location=data["location"],
            participants=data["participants"],
            choices=data.get("choices"),
            consequences=data.get("consequences"),
            requirements=data.get("requirements"),
            time_limit=data.get("time_limit")
        )

class StoryEventGenerator:
    """Generates story events from templates."""
    
    def __init__(self):
        """Initialize the story event generator."""
        self.templates: Dict[str, StoryEventTemplate] = {}
    
    def register_template(self, template_id: str, template: StoryEventTemplate):
        """Register a new story event template.
        
        Args:
            template_id: Unique identifier for the template
            template: The story event template
        """
        self.templates[template_id] = template
    
    def generate_event(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Generate a story event instance from a template.
        
        Args:
            template_id: ID of the template to use
            **kwargs: Additional parameters to override template values
            
        Returns:
            Generated story event data
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        event_data = template.to_dict()
        
        # Override template values with provided parameters
        for key, value in kwargs.items():
            if key in event_data:
                event_data[key] = value
        
        # Add instance-specific data
        event_data["event_id"] = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        event_data["status"] = "pending"
        event_data["start_time"] = None
        event_data["end_time"] = None
        event_data["player_choices"] = []
        event_data["outcomes"] = []
        
        return event_data
    
    def update_event_status(self, event_data: Dict[str, Any], status: str, outcome: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update event status and record outcome.
        
        Args:
            event_data: Current event data
            status: New status
            outcome: Optional outcome data
            
        Returns:
            Updated event data
        """
        event_data["status"] = status
        
        if status == "started":
            event_data["start_time"] = datetime.now().isoformat()
        elif status in ["completed", "failed"]:
            event_data["end_time"] = datetime.now().isoformat()
            if outcome:
                event_data["outcomes"].append({
                    "timestamp": datetime.now().isoformat(),
                    **outcome
                })
        
        return event_data
    
    def record_player_choice(self, event_data: Dict[str, Any], choice: Dict[str, Any]) -> Dict[str, Any]:
        """Record a player's choice during the event.
        
        Args:
            event_data: Current event data
            choice: Choice data
            
        Returns:
            Updated event data
        """
        event_data["player_choices"].append({
            "timestamp": datetime.now().isoformat(),
            **choice
        })
        return event_data 