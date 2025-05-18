"""
Scene description system that composes game scenes from basic elements.
"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum, auto
import random

logger = logging.getLogger(__name__)

class SceneElement(Enum):
    """Basic elements that can appear in a scene."""
    # Base terrain
    GRASS_PLAIN = auto()
    GRASS_WILD = auto()
    DIRT_PATH = auto()
    STONE_PATH = auto()
    WATER = auto()
    
    # Structures
    WALL_STONE = auto()
    WALL_WOOD = auto()
    DOOR_WOOD = auto()
    DOOR_METAL = auto()
    FLOOR_STONE = auto()
    FLOOR_WOOD = auto()
    
    # Features
    TREE = auto()
    ROCK = auto()
    BUSH = auto()
    FLOWER = auto()
    
    # Objects
    CHEST = auto()
    BARREL = auto()
    TABLE = auto()
    CHAIR = auto()
    
    # Characters
    PLAYER = auto()
    VILLAGER = auto()
    MERCHANT = auto()
    GUARD = auto()
    MONSTER_SMALL = auto()
    MONSTER_LARGE = auto()

@dataclass
class SceneComposition:
    """Represents how a scene should be composed."""
    base_terrain: SceneElement
    structures: List[Tuple[SceneElement, int, int]]  # element, x, y
    features: List[Tuple[SceneElement, int, int]]
    objects: List[Tuple[SceneElement, int, int]]
    characters: List[Tuple[SceneElement, int, int]]

class SceneDescriber:
    """Converts high-level scene descriptions into specific tile arrangements."""
    
    def __init__(self, tile_indexer):
        """Initialize the scene describer.
        
        Args:
            tile_indexer: The tile indexer to use for getting tile IDs
        """
        self.tile_indexer = tile_indexer
        self._initialize_element_mappings()
    
    def _initialize_element_mappings(self):
        """Initialize mappings between scene elements and actual tiles."""
        self.element_to_tiles = {
            # Base terrain
            SceneElement.GRASS_PLAIN: ["dc-dngn/floor/grass/grass0.png", "dc-dngn/floor/grass/grass1.png"],
            SceneElement.GRASS_WILD: ["dc-dngn/floor/grass/grass_flowers_blue1.png", "dc-dngn/floor/grass/grass_flowers_red1.png"],
            SceneElement.DIRT_PATH: ["dc-dngn/floor/dirt0.png", "dc-dngn/floor/dirt1.png"],
            SceneElement.STONE_PATH: ["dc-dngn/floor/pebble_brown0.png", "dc-dngn/floor/pebble_brown1.png"],
            SceneElement.WATER: ["dc-dngn/water/dngn_shallow_water.png", "dc-dngn/water/dngn_deep_water.png"],
            
            # Structures
            SceneElement.WALL_STONE: ["dc-dngn/wall/brick_brown0.png", "dc-dngn/wall/brick_brown1.png"],
            SceneElement.WALL_WOOD: ["dc-dngn/wall/lair0.png", "dc-dngn/wall/lair1.png"],
            SceneElement.DOOR_WOOD: ["dc-dngn/dngn_closed_door.png", "dc-dngn/dngn_open_door.png"],
            SceneElement.DOOR_METAL: ["dc-dngn/gate_closed_middle.png", "dc-dngn/gate_open_middle.png"],
            SceneElement.FLOOR_STONE: ["dc-dngn/floor/grey_dirt0.png", "dc-dngn/floor/grey_dirt1.png"],
            SceneElement.FLOOR_WOOD: ["dc-dngn/floor/lair0.png", "dc-dngn/floor/lair1.png"],
            
            # Features
            SceneElement.TREE: ["dc-dngn/tree1.png", "dc-dngn/tree2.png"],
            SceneElement.ROCK: ["dc-dngn/wall/brick_dark0.png", "dc-dngn/wall/brick_dark1.png"],
            SceneElement.BUSH: ["dc-dngn/bush1.png", "dc-dngn/bush2.png"],
            SceneElement.FLOWER: ["dc-dngn/floor/grass/grass_flowers_yellow1.png", "dc-dngn/floor/grass/grass_flowers_yellow2.png"],
            
            # Objects
            SceneElement.CHEST: ["dc-dngn/chest_closed.png", "dc-dngn/chest_open.png"],
            SceneElement.BARREL: ["dc-dngn/barrel.png", "dc-dngn/barrel_burning.png"],
            SceneElement.TABLE: ["dc-dngn/table_wood.png", "dc-dngn/table_stone.png"],
            SceneElement.CHAIR: ["dc-dngn/chair_wood.png", "dc-dngn/chair_stone.png"],
            
            # Characters
            SceneElement.PLAYER: ["player/base/human_m.png", "player/base/human_f.png"],
            SceneElement.VILLAGER: ["dc-mon/human.png"],
            SceneElement.MERCHANT: ["dc-mon/human.png"],
            SceneElement.GUARD: ["dc-mon/human.png"],
            SceneElement.MONSTER_SMALL: ["dc-mon/kobold.png", "dc-mon/goblin.png", "dc-mon/hobgoblin.png"],
            SceneElement.MONSTER_LARGE: ["dc-mon/ogre.png", "dc-mon/troll.png", "dc-mon/hill_giant.png"]
        }
    
    def get_tile_for_element(self, element: 'SceneElement') -> Optional[int]:
        """Get a tile ID for a scene element.
        
        Args:
            element: The scene element to get a tile for
            
        Returns:
            A tile ID for the element, or None if not found
        """
        if element not in self.element_to_tiles:
            logger.warning(f"No tiles defined for element: {element}")
            return None
            
        # Get the list of possible tiles for this element
        tile_paths = self.element_to_tiles[element]
        if not tile_paths:
            logger.warning(f"Empty tile list for element: {element}")
            return None
            
        # Pick a random tile from the list
        tile_path = random.choice(tile_paths)
            
        # Get the tile ID from the indexer
        tile_id = self.tile_indexer.get_tile_id(tile_path)
        if tile_id is None:
            logger.warning(f"Could not get tile ID for path: {tile_path}")
            
        return tile_id

    def describe_scene(self, description: str) -> SceneComposition:
        """Convert a text description into a scene composition.
        
        Args:
            description: Text description of the scene
            
        Returns:
            A SceneComposition object
        """
        # Default to grass plain as base
        base_terrain = SceneElement.GRASS_PLAIN
        structures = []
        features = []
        objects = []
        characters = []
        
        # Simple keyword matching for now
        description = description.lower()
        
        # Determine base terrain
        if "path" in description or "road" in description:
            base_terrain = SceneElement.DIRT_PATH
        elif "water" in description or "river" in description:
            base_terrain = SceneElement.WATER
        elif "wild" in description or "flower" in description:
            base_terrain = SceneElement.GRASS_WILD
            
        # Look for structures
        if "house" in description or "building" in description:
            structures.extend([
                (SceneElement.WALL_WOOD, 5, 5),
                (SceneElement.DOOR_WOOD, 5, 6),
                (SceneElement.FLOOR_WOOD, 5, 7)
            ])
            
        # Add features
        if "tree" in description or "forest" in description:
            features.extend([
                (SceneElement.TREE, 2, 2),
                (SceneElement.TREE, 8, 3),
                (SceneElement.BUSH, 3, 4)
            ])
            
        # Add objects
        if "market" in description or "shop" in description:
            objects.extend([
                (SceneElement.TABLE, 4, 4),
                (SceneElement.BARREL, 6, 4)
            ])
            
        # Add characters
        if "village" in description:
            characters.extend([
                (SceneElement.VILLAGER, 3, 3),
                (SceneElement.MERCHANT, 5, 5)
            ])
        elif "monster" in description:
            characters.append((SceneElement.MONSTER_SMALL, 7, 7))
        
        return SceneComposition(
            base_terrain=base_terrain,
            structures=structures,
            features=features,
            objects=objects,
            characters=characters
        ) 