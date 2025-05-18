"""
Integration between the zone system and enhanced tile system.
"""
import random
import os
import json
import uuid
import logging
from typing import Dict, List, Tuple, Optional

from .zone import Zone, ZoneManager
from .tilemap import TileMap
from .enhanced_tilemap import EnhancedTileset, EnhancedMapGenerator, EnhancedTileMap

# Set up logger
logger = logging.getLogger(__name__)

class EnhancedZoneGenerator:
    """Enhanced zone generator that uses the structured tile folders."""
    
    def __init__(self, base_path: str = "game/assets/images"):
        """Initialize the enhanced zone generator.
        
        Args:
            base_path: Path to the image assets directory
        """
        self.base_path = base_path
        self.tileset = EnhancedTileset(base_path)
        self.map_generator = EnhancedMapGenerator(self.tileset)
    
    def generate_zone(self, zone_type: str, level_range: Tuple[int, int], 
                      name: Optional[str] = None, width: int = 40, height: int = 40) -> Zone:
        """Generate a new zone with enhanced tile maps.
        
        Args:
            zone_type: Type of zone to generate (village, forest, etc.)
            level_range: Range of levels for the zone
            name: Optional name for the zone
            width: Width of the zone map
            height: Height of the zone map
            
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
        zone = Zone(zone_id, name, f"A {zone_type} area for levels {level_range[0]}-{level_range[1]}", 
                   zone_type, level_range)
        
        # Generate map based on zone type
        enhanced_map = self.map_generator.generate_map(width, height, zone_type)
        
        # Convert the enhanced map to a standard map for compatibility
        standard_map = self._convert_to_standard_map(enhanced_map)
        
        zone.set_map(standard_map)
        
        # Populate the zone based on type
        if zone_type == "village":
            self._populate_village(zone)
        elif zone_type == "forest":
            self._populate_forest(zone)
        
        return zone
    
    def _convert_to_standard_map(self, enhanced_map: EnhancedTileMap) -> TileMap:
        """Convert an enhanced map to a standard map for compatibility.
        
        Args:
            enhanced_map: The enhanced map to convert
            
        Returns:
            A standard TileMap
        """
        from .tilemap import Tileset, TileMap
        
        # Create a standard map with the same dimensions
        standard_map = TileMap(enhanced_map.width, enhanced_map.height, enhanced_map.tile_size)
        
        # We need to assign a proper tileset to the standard map
        # First, check if we already have a standard tileset
        tileset_path = os.path.join("game", "assets", "images", "tileset.png")
        if os.path.exists(tileset_path):
            standard_tileset = Tileset(tileset_path)
            standard_map.set_tileset(standard_tileset)
        
        # Copy the map data
        standard_map.map_data = enhanced_map.map_data
        
        return standard_map
    
    def _populate_village(self, zone: Zone):
        """Populate a village zone with NPCs and quests.
        
        Args:
            zone: The zone to populate
        """
        # These would be identical to the ZoneManager methods
        # Here's a simplified version for demonstration
        
        # Add some NPCs based on the map locations
        if zone.map:
            # Find suitable house tiles for NPCs
            house_locations = []
            for y in range(zone.map.height):
                for x in range(zone.map.width):
                    tile_id = zone.map.get_tile_id(x, y)
                    tile_type = self.tileset.id_to_type.get(tile_id)
                    if tile_type in ["houses", "doors"]:
                        house_locations.append((x, y))
            
            # Add a merchant near one of the houses
            if house_locations:
                merchant_pos = random.choice(house_locations)
                from .zone import NPC
                merchant = NPC(
                    "merchant_01",
                    "Marcus",
                    "Merchant",
                    merchant_pos[0], merchant_pos[1],
                    100  # Placeholder sprite ID
                )
                merchant.set_dialogue({
                    "greeting": "Welcome to my shop, traveler! I have the finest goods in all of Eldergrove.",
                    "farewell": "Come back soon!",
                    "quest": "I need help restocking my supplies. The forest has grown dangerous lately..."
                })
                zone.add_npc(merchant)
                
                # Add a quest
                from .zone import Quest
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
    
    def _populate_forest(self, zone: Zone):
        """Populate a forest zone with enemies and landmarks.
        
        Args:
            zone: The zone to populate
        """
        # Again, similar to ZoneManager but using our enhanced map data
        # Add enemies in appropriate locations
        if zone.map:
            # Find suitable locations for enemies (not on paths)
            enemy_locations = []
            for y in range(zone.map.height):
                for x in range(zone.map.width):
                    tile_id = zone.map.get_tile_id(x, y)
                    tile_type = self.tileset.id_to_type.get(tile_id)
                    if tile_type == "grass" or tile_type == "trees":
                        enemy_locations.append((x, y))
            
            # Add some wolves in the forest
            min_level, max_level = zone.level_range
            num_enemies = random.randint(5, 10)
            
            for i in range(num_enemies):
                if enemy_locations:
                    pos = random.choice(enemy_locations)
                    enemy_locations.remove(pos)  # Don't place two enemies at the same spot
                    
                    from .zone import Enemy
                    enemy_level = random.randint(min_level, max_level)
                    enemy = Enemy(
                        f"wolf_{i}",
                        "Wolf",
                        pos[0], pos[1],
                        300,  # Placeholder sprite ID
                        health=enemy_level * 10
                    )
                    zone.add_enemy(enemy)
            
            # Add a landmark in a clearing
            # Look for a cluster of grass tiles away from paths
            clearing_locations = []
            for y in range(2, zone.map.height - 2):
                for x in range(2, zone.map.width - 2):
                    # Check if we have a 3x3 area of grass
                    is_clearing = True
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            tile_id = zone.map.get_tile_id(x + dx, y + dy)
                            tile_type = self.tileset.id_to_type.get(tile_id)
                            if tile_type != "grass":
                                is_clearing = False
                                break
                        if not is_clearing:
                            break
                    
                    if is_clearing:
                        clearing_locations.append((x, y))
            
            if clearing_locations:
                pos = random.choice(clearing_locations)
                zone.add_landmark(
                    "Ancient Tree",
                    pos[0], pos[1],
                    "A massive tree that seems to be hundreds of years old"
                )

class EnhancedZoneManager:
    """Enhanced zone manager that uses structured tile folders."""
    
    def __init__(self, tileset):
        """Initialize the enhanced zone manager.
        
        Args:
            tileset: The enhanced tileset to use for map generation
        """
        # Validate tileset
        if not tileset:
            raise ValueError("Tileset cannot be None")
            
        if not isinstance(tileset, EnhancedTileset):
            raise ValueError("Tileset must be an EnhancedTileset instance")
            
        # Ensure tileset is properly initialized
        if not hasattr(tileset, 'indexer') or not tileset.indexer:
            raise ValueError("Tileset must have an initialized indexer")
            
        self.tileset = tileset
        self.zones = {}
        self.current_zone_id = None
        
        # Initialize the map generator with the tileset
        from .enhanced_tilemap import EnhancedMapGenerator
        self.map_generator = EnhancedMapGenerator(self.tileset)
        
        # Load zone configuration if available
        self.zone_config = self._load_zone_config()
    
    def _load_zone_config(self):
        """Load zone configuration from file."""
        config_path = os.path.join("game", "config", "zones.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading zone config: {e}")
        return {}
    
    def generate_zone(self, zone_type: str, level_range: Tuple[int, int], name: str) -> Zone:
        """Generate a new zone.
        
        Args:
            zone_type: Type of zone to generate
            level_range: Range of levels for this zone
            name: Name of the zone
            
        Returns:
            The generated zone
        """
        # Generate a unique ID for this zone
        zone_id = str(uuid.uuid4())
        
        # Get zone size from config or use defaults
        zone_config = self.zone_config.get(zone_type, {})
        width = zone_config.get("width", 32)
        height = zone_config.get("height", 32)
        
        try:
            # Generate the map using the enhanced map generator
            zone_map = self.map_generator.generate_map(width, height, zone_type)
            if not zone_map:
                raise ValueError(f"Failed to generate map for zone type: {zone_type}")
            
            # Create the zone
            zone = Zone(
                zone_id=zone_id,
                name=name,
                description=f"A {zone_type} area for levels {level_range[0]}-{level_range[1]}",
                zone_type=zone_type,
                level_range=level_range
            )
            
            # Set the map
            zone.set_map(zone_map)
            
            # Store the zone
            self.zones[zone_id] = zone
            
            return zone
            
        except Exception as e:
            logger.error(f"Error generating zone {name} of type {zone_type}: {e}")
            return None
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get a zone by ID.
        
        Args:
            zone_id: ID of the zone to get
            
        Returns:
            The zone if found, None otherwise
        """
        return self.zones.get(zone_id)
    
    def set_current_zone(self, zone_id: str) -> None:
        """Set the current zone.
        
        Args:
            zone_id: ID of the zone to set as current
        """
        if zone_id in self.zones:
            self.current_zone_id = zone_id
    
    def get_current_zone(self) -> Optional[Zone]:
        """Get the current zone.
        
        Returns:
            The current zone if set, None otherwise
        """
        if self.current_zone_id:
            return self.zones.get(self.current_zone_id)
        return None 