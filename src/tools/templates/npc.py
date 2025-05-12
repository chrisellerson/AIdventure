"""
NPC template system for generating NPC instances.
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NPCTemplate:
    """Template for generating NPCs."""
    name: str
    role: str
    background: str
    personality: Dict[str, float]  # Personality traits and their values
    dialogue_style: str
    appearance: Dict[str, Any]
    skills: List[str]
    relationships: Dict[str, str]  # Other NPCs and relationship types
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary format.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            "name": self.name,
            "role": self.role,
            "background": self.background,
            "personality": self.personality,
            "dialogue_style": self.dialogue_style,
            "appearance": self.appearance,
            "skills": self.skills,
            "relationships": self.relationships,
            "created_at": datetime.now().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPCTemplate':
        """Create template from dictionary.
        
        Args:
            data: Dictionary containing NPC data
            
        Returns:
            NPCTemplate instance
        """
        return cls(
            name=data["name"],
            role=data["role"],
            background=data["background"],
            personality=data["personality"],
            dialogue_style=data["dialogue_style"],
            appearance=data["appearance"],
            skills=data["skills"],
            relationships=data["relationships"]
        )

class NPCGenerator:
    """Generates NPC instances from templates."""
    
    def __init__(self):
        """Initialize the NPC generator."""
        self.templates: Dict[str, NPCTemplate] = {}
    
    def register_template(self, template_id: str, template: NPCTemplate):
        """Register a new NPC template.
        
        Args:
            template_id: Unique identifier for the template
            template: The NPC template
        """
        self.templates[template_id] = template
    
    def generate_npc(self, template_id: str, **kwargs) -> Dict[str, Any]:
        """Generate an NPC instance from a template.
        
        Args:
            template_id: ID of the template to use
            **kwargs: Additional parameters to override template values
            
        Returns:
            Generated NPC data
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        npc_data = template.to_dict()
        
        # Override template values with provided parameters
        for key, value in kwargs.items():
            if key in npc_data:
                npc_data[key] = value
        
        # Add instance-specific data
        npc_data["instance_id"] = f"{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        npc_data["created_at"] = datetime.now().isoformat()
        npc_data["interaction_history"] = []
        
        return npc_data
    
    def update_npc(self, npc_data: Dict[str, Any], interaction: Dict[str, Any]):
        """Update NPC with new interaction data.
        
        Args:
            npc_data: Current NPC data
            interaction: New interaction data
            
        Returns:
            Updated NPC data
        """
        npc_data["interaction_history"].append({
            "timestamp": datetime.now().isoformat(),
            **interaction
        })
        return npc_data 