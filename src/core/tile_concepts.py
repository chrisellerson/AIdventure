"""
System for mapping high-level tile concepts to actual available tiles.
"""
import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class TileConcept(Enum):
    """High-level concepts that can be represented by tiles."""
    # Terrain concepts
    GRASS = auto()
    WATER = auto()
    PATH = auto()
    WALL = auto()
    FLOOR = auto()
    
    # Structure concepts
    BUILDING = auto()
    DOOR = auto()
    SHRINE = auto()
    DECORATION = auto()
    
    # Character concepts
    HUMANOID = auto()
    MONSTER = auto()
    BEAST = auto()
    MAGICAL_BEING = auto()
    
    # Item concepts
    WEAPON = auto()
    ARMOR = auto()
    MAGICAL_ITEM = auto()
    TREASURE = auto()
    
    # Effect concepts
    MAGIC_EFFECT = auto()
    NATURAL_EFFECT = auto()

@dataclass
class ConceptMatch:
    """Represents a match between a concept and actual tiles."""
    concept: TileConcept
    priority: int
    tags: Set[str]

class ConceptMapper:
    """Maps high-level concepts to actual available tiles."""
    
    def __init__(self, tile_indexer):
        """Initialize the concept mapper.
        
        Args:
            tile_indexer: The TileIndexer instance to use
        """
        self.tile_indexer = tile_indexer
        self._initialize_concept_mappings()
    
    def _initialize_concept_mappings(self):
        """Initialize the mappings between concepts and tile categories/patterns."""
        self.concept_matches = {
            # Terrain
            TileConcept.GRASS: ConceptMatch(
                TileConcept.GRASS,
                1,
                {"grass", "natural", "ground"}
            ),
            TileConcept.WATER: ConceptMatch(
                TileConcept.WATER,
                1,
                {"water", "liquid", "pool", "river"}
            ),
            TileConcept.PATH: ConceptMatch(
                TileConcept.PATH,
                1,
                {"path", "road", "dirt", "cobble"}
            ),
            TileConcept.WALL: ConceptMatch(
                TileConcept.WALL,
                1,
                {"wall", "barrier", "stone", "brick"}
            ),
            TileConcept.FLOOR: ConceptMatch(
                TileConcept.FLOOR,
                1,
                {"floor", "ground", "indoor"}
            ),
            
            # Structures
            TileConcept.BUILDING: ConceptMatch(
                TileConcept.BUILDING,
                2,
                {"house", "building", "structure", "shop"}
            ),
            TileConcept.DOOR: ConceptMatch(
                TileConcept.DOOR,
                2,
                {"door", "gate", "entrance"}
            ),
            TileConcept.SHRINE: ConceptMatch(
                TileConcept.SHRINE,
                2,
                {"altar", "shrine", "statue", "monument"}
            ),
            TileConcept.DECORATION: ConceptMatch(
                TileConcept.DECORATION,
                3,
                {"decoration", "ornament", "feature"}
            ),
            
            # Characters
            TileConcept.HUMANOID: ConceptMatch(
                TileConcept.HUMANOID,
                1,
                {"human", "elf", "dwarf", "player"}
            ),
            TileConcept.MONSTER: ConceptMatch(
                TileConcept.MONSTER,
                1,
                {"monster", "creature", "demon", "undead"}
            ),
            TileConcept.BEAST: ConceptMatch(
                TileConcept.BEAST,
                1,
                {"beast", "animal", "wolf", "bear"}
            ),
            TileConcept.MAGICAL_BEING: ConceptMatch(
                TileConcept.MAGICAL_BEING,
                2,
                {"magical", "elemental", "spirit", "ghost"}
            ),
            
            # Items
            TileConcept.WEAPON: ConceptMatch(
                TileConcept.WEAPON,
                1,
                {"weapon", "sword", "axe", "staff"}
            ),
            TileConcept.ARMOR: ConceptMatch(
                TileConcept.ARMOR,
                1,
                {"armor", "shield", "helmet", "boots"}
            ),
            TileConcept.MAGICAL_ITEM: ConceptMatch(
                TileConcept.MAGICAL_ITEM,
                2,
                {"magic", "scroll", "potion", "ring"}
            ),
            TileConcept.TREASURE: ConceptMatch(
                TileConcept.TREASURE,
                2,
                {"treasure", "gold", "gem", "valuable"}
            ),
            
            # Effects
            TileConcept.MAGIC_EFFECT: ConceptMatch(
                TileConcept.MAGIC_EFFECT,
                3,
                {"effect", "magic", "spell", "rune"}
            ),
            TileConcept.NATURAL_EFFECT: ConceptMatch(
                TileConcept.NATURAL_EFFECT,
                3,
                {"effect", "natural", "mist", "fire"}
            )
        }
    
    def get_tile_for_concept(self, concept: Union[TileConcept, str], context: Optional[Dict[str, str]] = None) -> Optional[int]:
        """Get a tile ID that best represents a concept.
        
        Args:
            concept: The concept to represent (can be enum or string)
            context: Optional context hints for better matching
            
        Returns:
            A tile ID that represents the concept, or None if no match found
        """
        # Convert string to enum if needed
        if isinstance(concept, str):
            try:
                concept = TileConcept[concept.upper()]
            except KeyError:
                # If not an exact match, try to map the string to a concept
                concept = self._map_string_to_concept(concept)
                if not concept:
                    logger.warning(f"Could not map string '{concept}' to any concept")
                    return None
        
        # Get the concept match
        match = self.concept_matches.get(concept)
        if not match:
            return None
            
        # Try to find a tile that matches the concept
        best_tile = None
        
        # First try category-based matching
        for category, tiles in self.tile_indexer.tile_categories.items():
            if any(tag in category.lower() for tag in match.tags):
                if tiles:
                    # Use context to pick the best tile if available
                    if context:
                        for tile in tiles:
                            if any(hint.lower() in str(tile).lower() for hint in context.values()):
                                return self.tile_indexer.get_tile_id(tile)
                    # Otherwise pick a random appropriate tile
                    import random
                    return self.tile_indexer.get_tile_id(random.choice(tiles))
        
        # If no category match, try individual tile matching
        for category, tiles in self.tile_indexer.tile_categories.items():
            for tile in tiles:
                tile_str = str(tile).lower()
                if any(tag in tile_str for tag in match.tags):
                    best_tile = tile
                    break
            if best_tile:
                break
        
        if best_tile:
            return self.tile_indexer.get_tile_id(best_tile)
            
        return None
    
    def _map_string_to_concept(self, string: str) -> Optional[TileConcept]:
        """Map a string description to the most appropriate concept.
        
        Args:
            string: String to map to a concept
            
        Returns:
            The most appropriate concept, or None if no good match
        """
        string = string.lower()
        
        # Try to match against concept tags
        best_match = None
        best_score = 0
        
        for concept, match in self.concept_matches.items():
            score = sum(1 for tag in match.tags if tag in string)
            if score > best_score:
                best_score = score
                best_match = concept
        
        return best_match 