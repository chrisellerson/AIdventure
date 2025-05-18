"""
Zone management system for creating structured game areas.
"""
import random
from typing import Dict, List, Any, Tuple, Optional
import pygame

from .tilemap import TileMap, Tileset, MapGenerator

class NPC:
    """Represents a non-player character in the game world."""
    
    def __init__(self, npc_id: str, name: str, role: str, x: int, y: int, sprite_id: int):
        """Initialize an NPC.
        
        Args:
            npc_id: Unique identifier for the NPC
            name: Name of the NPC
            role: Role or profession of the NPC
            x: X position in tiles
            y: Y position in tiles
            sprite_id: ID of the sprite to use
        """
        self.npc_id = npc_id
        self.name = name
        self.role = role
        self.x = x
        self.y = y
        self.sprite_id = sprite_id
        self.dialogue = {}
        self.quests = []
        
        # Create sprite
        self.sprite = pygame.Surface((32, 32))
        self.sprite.fill((255, 255, 0))  # Yellow default
    
    def set_dialogue(self, dialogue: Dict[str, str]):
        """Set dialogue options for the NPC.
        
        Args:
            dialogue: Dictionary of dialogue options
        """
        self.dialogue = dialogue
    
    def add_quest(self, quest_id: str):
        """Add a quest to the NPC.
        
        Args:
            quest_id: ID of the quest
        """
        self.quests.append(quest_id)
    
    def render(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Render the NPC.
        
        Args:
            surface: Surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        screen_x = self.x * 32 - camera_x
        screen_y = self.y * 32 - camera_y
        surface.blit(self.sprite, (screen_x, screen_y))

class Enemy:
    """Represents an enemy in the game world."""
    
    def __init__(self, enemy_id: str, name: str, x: int, y: int, sprite_id: int, health: int = 10):
        """Initialize an enemy.
        
        Args:
            enemy_id: Unique identifier for the enemy
            name: Name of the enemy
            x: X position in tiles
            y: Y position in tiles
            sprite_id: ID of the sprite to use
            health: Health points
        """
        self.enemy_id = enemy_id
        self.name = name
        self.x = x
        self.y = y
        self.sprite_id = sprite_id
        self.health = health
        self.max_health = health
        self.level = 1
        self.is_aggressive = True
        self.patrol_area = [(x, y)]
        
        # Create sprite
        self.sprite = pygame.Surface((32, 32))
        self.sprite.fill((255, 0, 0))  # Red default
    
    def set_patrol_area(self, points: List[Tuple[int, int]]):
        """Set the patrol area for the enemy.
        
        Args:
            points: List of (x, y) points to patrol
        """
        self.patrol_area = points
    
    def render(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Render the enemy.
        
        Args:
            surface: Surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        screen_x = self.x * 32 - camera_x
        screen_y = self.y * 32 - camera_y
        surface.blit(self.sprite, (screen_x, screen_y))

class Quest:
    """Represents a quest in the game."""
    
    def __init__(self, quest_id: str, title: str, description: str, giver_id: str):
        """Initialize a quest.
        
        Args:
            quest_id: Unique identifier for the quest
            title: Title of the quest
            description: Description of the quest
            giver_id: ID of the NPC who gives the quest
        """
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.giver_id = giver_id
        self.objectives = []
        self.rewards = {}
        self.completed = False
    
    def add_objective(self, description: str, target: str, amount: int):
        """Add an objective to the quest.
        
        Args:
            description: Description of the objective
            target: Target object or enemy
            amount: Amount needed
        """
        self.objectives.append({
            "description": description,
            "target": target,
            "amount": amount,
            "current": 0
        })
    
    def set_rewards(self, rewards: Dict[str, Any]):
        """Set the rewards for completing the quest.
        
        Args:
            rewards: Dictionary of rewards
        """
        self.rewards = rewards
    
    def update_progress(self, target: str, amount: int):
        """Update progress for a quest objective.
        
        Args:
            target: Target object or enemy
            amount: Amount to add
        """
        for objective in self.objectives:
            if objective["target"] == target:
                objective["current"] += amount
                # Check if completed
                if all(obj["current"] >= obj["amount"] for obj in self.objectives):
                    self.completed = True

class Zone:
    """Represents a game zone with a map, NPCs, enemies, and quests."""
    
    def __init__(self, zone_id: str, name: str, description: str, zone_type: str, level_range: Tuple[int, int]):
        """Initialize a zone.
        
        Args:
            zone_id: Unique identifier for the zone
            name: Name of the zone
            description: Description of the zone
            zone_type: Type of zone (village, forest, dungeon, etc.)
            level_range: Range of levels for enemies in the zone
        """
        self.zone_id = zone_id
        self.name = name
        self.description = description
        self.zone_type = zone_type
        self.level_range = level_range
        self.map = None
        self.npcs = {}
        self.enemies = {}
        self.quests = {}
        self.landmarks = []
        self.connections = {}  # Connections to other zones
        
    def set_map(self, tile_map: TileMap):
        """Set the map for the zone.
        
        Args:
            tile_map: The tile map for this zone
        """
        self.map = tile_map
    
    def add_npc(self, npc: NPC):
        """Add an NPC to the zone.
        
        Args:
            npc: The NPC to add
        """
        self.npcs[npc.npc_id] = npc
    
    def add_enemy(self, enemy: Enemy):
        """Add an enemy to the zone.
        
        Args:
            enemy: The enemy to add
        """
        self.enemies[enemy.enemy_id] = enemy
    
    def add_quest(self, quest: Quest):
        """Add a quest to the zone.
        
        Args:
            quest: The quest to add
        """
        self.quests[quest.quest_id] = quest
    
    def add_landmark(self, name: str, x: int, y: int, description: str):
        """Add a landmark to the zone.
        
        Args:
            name: Name of the landmark
            x: X position in tiles
            y: Y position in tiles
            description: Description of the landmark
        """
        self.landmarks.append({
            "name": name,
            "x": x,
            "y": y,
            "description": description
        })
    
    def add_connection(self, direction: str, target_zone_id: str, x: int, y: int):
        """Add a connection to another zone.
        
        Args:
            direction: Direction of the connection (north, south, east, west)
            target_zone_id: ID of the target zone
            x: X position of the connection point
            y: Y position of the connection point
        """
        self.connections[direction] = {
            "target_zone_id": target_zone_id,
            "x": x,
            "y": y
        }
    
    def render(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Render the zone.
        
        Args:
            surface: Surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        # Render map
        if self.map:
            self.map.render(surface, camera_x, camera_y)
        
        # Render NPCs
        for npc in self.npcs.values():
            npc.render(surface, camera_x, camera_y)
        
        # Render enemies
        for enemy in self.enemies.values():
            enemy.render(surface, camera_x, camera_y)

class ZoneManager:
    """Manages zones and zone generation."""
    
    def __init__(self, tileset: Tileset):
        """Initialize the zone manager.
        
        Args:
            tileset: Tileset to use for map generation
        """
        self.tileset = tileset
        self.map_generator = MapGenerator(tileset)
        self.zones = {}
        self.current_zone_id = None
    
    def generate_zone(self, zone_type: str, level_range: Tuple[int, int], name: Optional[str] = None) -> Zone:
        """Generate a new zone.
        
        Args:
            zone_type: Type of zone (village, forest, dungeon, etc.)
            level_range: Range of levels for enemies in the zone
            name: Optional name for the zone
            
        Returns:
            The generated zone
        """
        # Generate zone ID and name if not provided
        zone_id = f"{zone_type}_{level_range[0]}_{level_range[1]}_{random.randint(1000, 9999)}"
        if not name:
            if zone_type == "village":
                name = random.choice(["Eldergrove", "Riversend", "Oakvale", "Willowhaven"])
            elif zone_type == "forest":
                name = random.choice(["Darkwood", "Whispering Forest", "Ancient Grove", "Misty Woods"])
            else:
                name = f"{zone_type.capitalize()} {random.randint(1, 10)}"
        
        # Create zone
        zone = Zone(zone_id, name, f"A {zone_type} area for levels {level_range[0]}-{level_range[1]}", zone_type, level_range)
        
        # Generate map based on zone type
        if zone_type == "village":
            tile_map = self.map_generator.generate_village(40, 40)
        elif zone_type == "forest":
            tile_map = self.map_generator.generate_forest(40, 40)
        else:
            tile_map = self.map_generator.generate_village(40, 40)
        
        zone.set_map(tile_map)
        
        # Generate NPCs
        if zone_type == "village":
            self._populate_village(zone)
        elif zone_type == "forest":
            self._populate_forest(zone)
        
        # Store and return the zone
        self.zones[zone_id] = zone
        return zone
    
    def _populate_village(self, zone: Zone):
        """Populate a village zone with NPCs and quests.
        
        Args:
            zone: The zone to populate
        """
        # Add NPCs
        self._add_merchant(zone)
        self._add_innkeeper(zone)
        self._add_villagers(zone, random.randint(3, 6))
        
        # Add quests
        self._add_starter_quests(zone)
    
    def _populate_forest(self, zone: Zone):
        """Populate a forest zone with enemies and landmarks.
        
        Args:
            zone: The zone to populate
        """
        # Add enemies
        min_level, max_level = zone.level_range
        num_enemies = random.randint(5, 10)
        
        for i in range(num_enemies):
            enemy_level = random.randint(min_level, max_level)
            enemy = Enemy(
                f"wolf_{i}",
                "Wolf",
                random.randint(5, zone.map.width - 5),
                random.randint(5, zone.map.height - 5),
                300,  # Placeholder sprite ID
                health=enemy_level * 10
            )
            zone.add_enemy(enemy)
        
        # Add landmarks
        zone.add_landmark(
            "Ancient Tree",
            zone.map.width // 2,
            zone.map.height // 2,
            "A massive tree that seems to be hundreds of years old"
        )
    
    def _add_merchant(self, zone: Zone):
        """Add a merchant NPC to a zone.
        
        Args:
            zone: The zone to add the merchant to
        """
        # Find a good position for the merchant (near houses)
        # For simplicity, just put in center for now
        merchant = NPC(
            "merchant_01",
            "Marcus",
            "Merchant",
            zone.map.width // 2 + 2,
            zone.map.height // 2 - 2,
            100  # Placeholder sprite ID
        )
        
        # Add dialogue
        merchant.set_dialogue({
            "greeting": "Welcome to my shop, traveler! I have the finest goods in all of Eldergrove.",
            "farewell": "Come back soon!",
            "quest": "I need help restocking my supplies. The forest has grown dangerous lately..."
        })
        
        # Add a quest
        quest = Quest(
            "gather_supplies",
            "Gather Supplies",
            "Help Marcus gather supplies from the forest",
            merchant.npc_id
        )
        quest.add_objective("Collect wolf pelts", "wolf", 5)
        quest.set_rewards({"gold": 100, "item": "leather_armor"})
        
        zone.add_quest(quest)
        merchant.add_quest(quest.quest_id)
        zone.add_npc(merchant)
    
    def _add_innkeeper(self, zone: Zone):
        """Add an innkeeper NPC to a zone.
        
        Args:
            zone: The zone to add the innkeeper to
        """
        innkeeper = NPC(
            "innkeeper_01",
            "Elara",
            "Innkeeper",
            zone.map.width // 2 - 2,
            zone.map.height // 2 - 2,
            101  # Placeholder sprite ID
        )
        
        innkeeper.set_dialogue({
            "greeting": "Welcome to the Sleeping Dragon Inn! Can I get you a room or a drink?",
            "farewell": "Rest well, adventurer!",
            "quest": "We've been having trouble with rats in the cellar. Could you help clear them out?"
        })
        
        zone.add_npc(innkeeper)
    
    def _add_villagers(self, zone: Zone, count: int):
        """Add random villagers to a zone.
        
        Args:
            zone: The zone to add villagers to
            count: Number of villagers to add
        """
        roles = ["Farmer", "Blacksmith", "Guard", "Child", "Elder"]
        
        for i in range(count):
            role = random.choice(roles)
            villager = NPC(
                f"villager_{i}",
                f"Villager {i+1}",
                role,
                random.randint(5, zone.map.width - 5),
                random.randint(5, zone.map.height - 5),
                102 + i  # Placeholder sprite ID
            )
            
            villager.set_dialogue({
                "greeting": f"Hello there! I'm a {role.lower()} in this village.",
                "farewell": "Goodbye!",
                "gossip": "I hear there are strange things happening in the forest lately..."
            })
            
            zone.add_npc(villager)
    
    def _add_starter_quests(self, zone: Zone):
        """Add starter quests to a zone.
        
        Args:
            zone: The zone to add quests to
        """
        # Additional quests will be added through NPCs
        pass
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get a zone by ID.
        
        Args:
            zone_id: ID of the zone to get
            
        Returns:
            The zone, or None if not found
        """
        return self.zones.get(zone_id)
    
    def set_current_zone(self, zone_id: str):
        """Set the current active zone.
        
        Args:
            zone_id: ID of the zone to set as current
        """
        if zone_id in self.zones:
            self.current_zone_id = zone_id
    
    def get_current_zone(self) -> Optional[Zone]:
        """Get the current active zone.
        
        Returns:
            The current zone, or None if not set
        """
        if self.current_zone_id:
            return self.zones.get(self.current_zone_id)
        return None 