"""
Intelligent tile selection system that uses AI understanding for coherent map generation.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass
import random

@dataclass
class TileContext:
    """Context information for tile selection."""
    tile_type: str
    surrounding_types: Dict[str, int]  # Count of each surrounding tile type
    biome_type: str
    terrain_height: float
    moisture_level: float
    distance_from_center: float
    zone_type: str
    
class IntelligentTileSelector:
    """Intelligent tile selection system that maintains coherence."""
    
    def __init__(self, tile_indexer):
        """Initialize the intelligent tile selector.
        
        Args:
            tile_indexer: The TileIndexer instance to use
        """
        self.tile_indexer = tile_indexer
        self.tile_weights = {}  # Cache for computed tile weights
        
        # Define biome-specific tile distributions
        self.biome_distributions = {
            "forest": {
                "trees": 0.6,
                "grass": 0.3,
                "water": 0.05,
                "mountains": 0.05
            },
            "village": {
                "grass": 0.5,
                "paths": 0.2,
                "houses": 0.15,
                "trees": 0.1,
                "water": 0.05
            },
            "mountains": {
                "mountains": 0.6,
                "grass": 0.2,
                "trees": 0.15,
                "water": 0.05
            }
        }
        
        # Define tile transition rules
        self.transition_rules = {
            "water": {
                "grass": "water_edge",
                "mountains": "water_edge",
                "trees": "water_edge"
            },
            "mountains": {
                "grass": "mountain_base",
                "trees": "mountain_forest"
            },
            "houses": {
                "grass": "path",
                "paths": "path"
            }
        }
    
    def get_tile_context(self, tile_map, x: int, y: int, zone_type: str) -> TileContext:
        """Get the context for a tile position.
        
        Args:
            tile_map: The tile map
            x: X coordinate
            y: Y coordinate
            zone_type: Type of zone being generated
            
        Returns:
            TileContext object with surrounding information
        """
        surrounding_types = {}
        
        # Check surrounding tiles in a 3x3 area
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                check_x = x + dx
                check_y = y + dy
                
                if 0 <= check_x < tile_map.width and 0 <= check_y < tile_map.height:
                    tile_type = tile_map.get_tile_type(check_x, check_y)
                    surrounding_types[tile_type] = surrounding_types.get(tile_type, 0) + 1
        
        # Calculate distance from center
        center_x = tile_map.width / 2
        center_y = tile_map.height / 2
        distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        normalized_distance = distance / (((tile_map.width/2) ** 2 + (tile_map.height/2) ** 2) ** 0.5)
        
        # Use noise maps for height and moisture
        height = tile_map.height_map[y][x] if hasattr(tile_map, 'height_map') else random.random()
        moisture = tile_map.moisture_map[y][x] if hasattr(tile_map, 'moisture_map') else random.random()
        
        # Determine most likely tile type based on surroundings
        current_type = max(surrounding_types.items(), key=lambda x: x[1])[0] if surrounding_types else "grass"
        
        return TileContext(
            tile_type=current_type,
            surrounding_types=surrounding_types,
            biome_type=zone_type,
            terrain_height=height,
            moisture_level=moisture,
            distance_from_center=normalized_distance,
            zone_type=zone_type
        )
    
    def select_tile(self, context: TileContext) -> str:
        """Select the most appropriate tile based on context.
        
        Args:
            context: The tile context
            
        Returns:
            ID of the selected tile
        """
        # Get the distribution for this biome
        distribution = self.biome_distributions.get(context.biome_type, self.biome_distributions["forest"])
        
        # Adjust probabilities based on surroundings
        adjusted_weights = self._adjust_weights(distribution.copy(), context)
        
        # Select tile type based on adjusted weights
        tile_type = self._weighted_choice(adjusted_weights)
        
        # Check if we need a transition tile
        if context.surrounding_types:
            dominant_surrounding = max(context.surrounding_types.items(), key=lambda x: x[1])[0]
            if tile_type in self.transition_rules and dominant_surrounding in self.transition_rules[tile_type]:
                transition_type = self.transition_rules[tile_type][dominant_surrounding]
                return self.tile_indexer.get_random_tile_id(transition_type)
        
        return self.tile_indexer.get_random_tile_id(tile_type)
    
    def _adjust_weights(self, weights: Dict[str, float], context: TileContext) -> Dict[str, float]:
        """Adjust tile weights based on context.
        
        Args:
            weights: Base weights for tile types
            context: The tile context
            
        Returns:
            Adjusted weights
        """
        # Adjust for terrain height
        if context.terrain_height > 0.7:
            weights["mountains"] = weights.get("mountains", 0) * 2
            weights["trees"] = weights.get("trees", 0) * 0.5
        elif context.terrain_height < 0.3:
            weights["water"] = weights.get("water", 0) * 2
            weights["mountains"] = weights.get("mountains", 0) * 0.1
        
        # Adjust for moisture
        if context.moisture_level > 0.6:
            weights["trees"] = weights.get("trees", 0) * 1.5
            weights["water"] = weights.get("water", 0) * 1.3
        
        # Adjust for distance from center
        if context.zone_type == "village":
            if context.distance_from_center < 0.3:
                weights["houses"] = weights.get("houses", 0) * 2
                weights["paths"] = weights.get("paths", 0) * 1.5
            else:
                weights["houses"] = weights.get("houses", 0) * 0.5
                weights["trees"] = weights.get("trees", 0) * 1.5
        
        # Normalize weights
        total = sum(weights.values())
        if total > 0:
            return {k: v/total for k, v in weights.items()}
        return weights
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Make a weighted random choice.
        
        Args:
            weights: Dictionary of options and their weights
            
        Returns:
            Selected option
        """
        options = list(weights.keys())
        weights = list(weights.values())
        return random.choices(options, weights=weights, k=1)[0] 