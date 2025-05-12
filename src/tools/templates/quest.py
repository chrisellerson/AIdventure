"""
Quest template system for generating quest instances.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class QuestType(Enum):
    """Types of quests available in the game."""
    MAIN = "main"
    SIDE = "side"
    FACTION = "faction"
    DAILY = "daily"
    EVENT = "event"

class QuestStatus(Enum):
    """Possible states of a quest."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QuestObjective:
    """Individual objective within a quest."""
    description: str
    target: str
    count: int
    current: int = 0
    is_optional: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert objective to dictionary format."""
        return {
            "description": self.description,
            "target": self.target,
            "count": self.count,
            "current": self.current,
            "is_optional": self.is_optional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestObjective':
        """Create objective from dictionary."""
        return cls(
            description=data["description"],
            target=data["target"],
            count=data["count"],
            current=data.get("current", 0),
            is_optional=data.get("is_optional", False)
        )

@dataclass
class QuestTemplate:
    """Template for generating quests."""
    title: str
    description: str
    quest_type: QuestType
    objectives: List[QuestObjective]
    rewards: Dict[str, Any]
    prerequisites: List[str]  # List of quest IDs that must be completed
    time_limit: Optional[int] = None  # Time limit in minutes, None for no limit
    repeatable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary format."""
        return {
            "title": self.title,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards,
            "prerequisites": self.prerequisites,
            "time_limit": self.time_limit,
            "repeatable": self.repeatable,
            "created_at": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestTemplate':
        """Create template from dictionary."""
        return cls(
            title=data["title"],
            description=data["description"],
            quest_type=QuestType(data["quest_type"]),
            objectives=[QuestObjective.from_dict(obj) for obj in data["objectives"]],
            rewards=data["rewards"],
            prerequisites=data["prerequisites"],
            time_limit=data.get("time_limit"),
            repeatable=data.get("repeatable", False)
        )

class QuestGenerator:
    """Generates quest instances from templates."""
    
    def __init__(self):
        """Initialize the quest generator."""
        self.templates: Dict[str, QuestTemplate] = {}
    
    def register_template(self, template_id: str, template: QuestTemplate):
        """Register a new quest template.
        
        Args:
            template_id: Unique identifier for the template
            template: The quest template
        """
        self.templates[template_id] = template
    
    def generate_quest(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Generate a quest instance from a template.
        
        Args:
            template_id: ID of the template to use
            **kwargs: Additional parameters to override template values
            
        Returns:
            Generated quest data
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        quest_data = template.to_dict()
        
        # Override template values with provided parameters
        for key, value in kwargs.items():
            if key in quest_data:
                quest_data[key] = value
        
        # Add instance-specific data
        quest_data["quest_id"] = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        quest_data["status"] = QuestStatus.NOT_STARTED.value
        quest_data["start_time"] = None
        quest_data["completion_time"] = None
        quest_data["progress"] = {obj["description"]: 0 for obj in quest_data["objectives"]}
        
        return quest_data
    
    def update_quest_progress(self, quest_data: Dict[str, Any], objective: str, progress: int) -> Dict[str, Any]:
        """Update quest progress for a specific objective.
        
        Args:
            quest_data: Current quest data
            objective: Description of the objective to update
            progress: New progress value
            
        Returns:
            Updated quest data
        """
        if objective not in quest_data["progress"]:
            raise ValueError(f"Objective {objective} not found in quest")
        
        quest_data["progress"][objective] = progress
        
        # Update status if all objectives are complete
        all_complete = all(
            quest_data["progress"][obj["description"]] >= obj["count"]
            for obj in quest_data["objectives"]
            if not obj["is_optional"]
        )
        
        if all_complete and quest_data["status"] == QuestStatus.IN_PROGRESS.value:
            quest_data["status"] = QuestStatus.COMPLETED.value
            quest_data["completion_time"] = datetime.now().isoformat()
        
        return quest_data 