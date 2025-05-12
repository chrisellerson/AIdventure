"""
Test script for the template system.
"""
import os
import sys
from pathlib import Path
import json
import asyncio
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.tools.template_manager import TemplateManager
from src.tools.templates.npc import NPCTemplate
from src.tools.templates.quest import QuestTemplate, QuestType, QuestObjective
from src.tools.templates.story_event import StoryEventTemplate, EventType, EventImportance

async def test_template_system():
    """Test the template system functionality."""
    # Initialize template manager
    template_manager = TemplateManager()
    
    # Create test NPC template
    npc_template = NPCTemplate(
        name="Test NPC",
        role="Merchant",
        background="A traveling merchant who sells rare items",
        personality={
            "friendly": 0.8,
            "greedy": 0.6,
            "honest": 0.7
        },
        dialogue_style="formal",
        appearance={
            "height": "tall",
            "build": "slim",
            "clothing": "traveling merchant robes"
        },
        skills=["bargaining", "appraisal", "survival"],
        relationships={
            "player": "neutral",
            "other_merchants": "friendly"
        }
    )
    
    # Save NPC template
    template_manager.save_template("npc", "test_merchant", npc_template.to_dict())
    
    # Create test quest template
    quest_template = QuestTemplate(
        title="Gather Rare Materials",
        description="Collect rare materials for the merchant",
        quest_type=QuestType.SIDE,
        objectives=[
            QuestObjective(
                description="Collect dragon scales",
                target="dragon_scale",
                count=5
            ),
            QuestObjective(
                description="Find ancient scrolls",
                target="ancient_scroll",
                count=3,
                is_optional=True
            )
        ],
        rewards={
            "gold": 1000,
            "items": ["rare_potion", "enchanted_ring"]
        },
        prerequisites=[],
        time_limit=1440,  # 24 hours
        repeatable=True
    )
    
    # Save quest template
    template_manager.save_template("quest", "gather_materials", quest_template.to_dict())
    
    # Create test story event template
    event_template = StoryEventTemplate(
        title="Merchant's Request",
        description="The merchant asks for help gathering rare materials",
        event_type=EventType.DIALOGUE,
        importance=EventImportance.MODERATE,
        location="market_square",
        participants=["test_merchant"],
        choices=[
            {
                "text": "Accept the quest",
                "consequence": "quest_started"
            },
            {
                "text": "Decline politely",
                "consequence": "quest_declined"
            },
            {
                "text": "Ask for more information",
                "consequence": "more_info"
            }
        ],
        consequences={
            "quest_started": {
                "quest_id": "gather_materials",
                "reputation_change": 5
            },
            "quest_declined": {
                "reputation_change": -2
            },
            "more_info": {
                "reputation_change": 0
            }
        }
    )
    
    # Save story event template
    template_manager.save_template("event", "merchant_request", event_template.to_dict())
    
    # Generate instances from templates
    npc = template_manager.generate_npc("test_merchant")
    quest = template_manager.generate_quest("gather_materials")
    event = template_manager.generate_story_event("merchant_request")
    
    # Test NPC interaction
    interaction = {
        "type": "dialogue",
        "content": "Hello, traveler! I have a proposition for you.",
        "player_response": "What kind of proposition?"
    }
    npc = template_manager.update_npc(npc, interaction)
    
    # Test quest progress
    quest = template_manager.update_quest_progress(quest, "Collect dragon scales", 2)
    
    # Test event status
    event = template_manager.update_event_status(event, "started")
    event = template_manager.record_player_choice(event, {
        "choice": "Accept the quest",
        "timestamp": datetime.now().isoformat()
    })
    event = template_manager.update_event_status(event, "completed", {
        "outcome": "quest_started",
        "details": "Player accepted the quest"
    })
    
    # Print results
    print("\nGenerated NPC:")
    print(json.dumps(npc, indent=2))
    
    print("\nGenerated Quest:")
    print(json.dumps(quest, indent=2))
    
    print("\nGenerated Event:")
    print(json.dumps(event, indent=2))

if __name__ == "__main__":
    asyncio.run(test_template_system()) 