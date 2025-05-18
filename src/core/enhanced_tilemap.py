"""
Enhanced tile-based map system using structured tile folders and metadata.
"""
import pygame
import random
import json
import os
import math
import logging
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import numpy as np

from .tile_indexer import TileIndexer

# Set up logger
logger = logging.getLogger(__name__)

# Add Perlin noise implementation for coherent map generation
class PerlinNoise:
    """Simple implementation of Perlin noise for 2D map generation."""
    
    def __init__(self, seed=None):
        """Initialize the Perlin noise generator.
        
        Args:
            seed: Optional random seed for reproducible results
        """
        if seed is not None:
            random.seed(seed)
            
        # Generate permutation table
        self.p = list(range(256))
        random.shuffle(self.p)
        self.p += self.p  # Duplicate to avoid overflow
    
    def fade(self, t):
        """Fade function for smoother interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, t, a, b):
        """Linear interpolation between a and b."""
        return a + t * (b - a)
    
    def grad(self, hash, x, y, z):
        """Calculate gradient."""
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise(self, x, y, z=0):
        """Generate noise value at position (x, y, z)."""
        # Find unit cube containing point
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        Z = int(math.floor(z)) & 255
        
        # Find relative position in cube
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)
        
        # Compute fade curves
        u = self.fade(x)
        v = self.fade(y)
        w = self.fade(z)
        
        # Hash coordinates of cube corners
        A = self.p[X] + Y
        AA = self.p[A] + Z
        AB = self.p[A + 1] + Z
        B = self.p[X + 1] + Y
        BA = self.p[B] + Z
        BB = self.p[B + 1] + Z
        
        # Add blended results from 8 corners of cube
        return self.lerp(w, 
            self.lerp(v, 
                self.lerp(u, 
                    self.grad(self.p[AA], x, y, z),
                    self.grad(self.p[BA], x - 1, y, z)
                ),
                self.lerp(u,
                    self.grad(self.p[AB], x, y - 1, z),
                    self.grad(self.p[BB], x - 1, y - 1, z)
                )
            ),
            self.lerp(v,
                self.lerp(u,
                    self.grad(self.p[AA + 1], x, y, z - 1),
                    self.grad(self.p[BA + 1], x - 1, y, z - 1)
                ),
                self.lerp(u,
                    self.grad(self.p[AB + 1], x, y - 1, z - 1),
                    self.grad(self.p[BB + 1], x - 1, y - 1, z - 1)
                )
            )
        )
    
    def generate_noise_map(self, width, height, scale=0.1, octaves=1, persistence=0.5, lacunarity=2.0):
        """Generate a 2D noise map.
        
        Args:
            width: Width of the map
            height: Height of the map
            scale: Scale of the noise (smaller = more zoomed out)
            octaves: Number of layers of noise
            persistence: How much each octave contributes to the overall noise
            lacunarity: How much detail is added at each octave
            
        Returns:
            A 2D list containing noise values between 0 and 1
        """
        noise_map = [[0 for _ in range(width)] for _ in range(height)]
        
        # To avoid division by zero
        if scale <= 0:
            scale = 0.0001
            
        max_noise_height = float('-inf')
        min_noise_height = float('inf')
        
        for y in range(height):
            for x in range(width):
                amplitude = 1
                frequency = 1
                noise_height = 0
                
                # Calculate noise for each octave
                for _ in range(octaves):
                    sample_x = x / scale * frequency
                    sample_y = y / scale * frequency
                    
                    # Get Perlin noise and convert from -1...1 to 0...1
                    noise_value = self.noise(sample_x, sample_y) * 0.5 + 0.5
                    noise_height += noise_value * amplitude
                    
                    # Prepare values for next octave
                    amplitude *= persistence
                    frequency *= lacunarity
                    
                # Track min and max values for normalization
                if noise_height > max_noise_height:
                    max_noise_height = noise_height
                if noise_height < min_noise_height:
                    min_noise_height = noise_height
                    
                noise_map[y][x] = noise_height
                
        # Normalize values to 0...1
        for y in range(height):
            for x in range(width):
                if max_noise_height - min_noise_height > 0:
                    noise_map[y][x] = (noise_map[y][x] - min_noise_height) / (max_noise_height - min_noise_height)
                else:
                    noise_map[y][x] = 0
                    
        return noise_map

class EnhancedTileset:
    """Enhanced tileset that uses organized tile directories."""
    
    def __init__(self, base_path: str = "game/assets/images", tile_size: int = 32):
        """Initialize the enhanced tileset.
        
        Args:
            base_path: Path to the image assets directory
            tile_size: Size of each tile in pixels
        """
        self.base_path = base_path
        self.tile_size = tile_size
        
        # Initialize the tile indexer
        self.indexer = TileIndexer(base_path)
        
        # Load the tile categorization for mapping numeric IDs to tile types
        self.id_to_type: Dict[int, str] = {}
        self.id_to_path: Dict[int, str] = {}
        self.type_to_ids: Dict[str, List[int]] = {}
        
        # Initialize mappings
        self._initialize_tile_mappings()
    
    def _initialize_tile_mappings(self):
        """Initialize mappings between tile IDs, types, and file paths."""
        # Initialize empty mappings
        self.id_to_type = {}
        self.id_to_path = {}
        self.type_to_ids = {}
        
        # Process each category and its tiles
        for category, tile_paths in self.indexer.tile_categories.items():
            if not tile_paths:
                continue
            
            # Initialize category list if needed
            if category not in self.type_to_ids:
                self.type_to_ids[category] = []
            
            # Process each tile in the category
            for tile_path in tile_paths:
                tile_id = self.indexer.get_tile_id(tile_path)
                if tile_id is not None:
                    self.id_to_type[tile_id] = category
                    self.id_to_path[tile_id] = tile_path
                    self.type_to_ids[category].append(tile_id)
    
    def get_tile(self, tile_id: int) -> Optional[pygame.Surface]:
        """Get a tile surface by its ID.
        
        Args:
            tile_id: ID of the tile to get
            
        Returns:
            The tile surface, or None if not found
        """
        if tile_id in self.id_to_path:
            tile_path = self.id_to_path[tile_id]
            return self.indexer.get_tile_surface(tile_path)
        return None
    
    def get_tile_id(self, identifier: Union[str, int]) -> int:
        """Get a tile ID from an identifier.
        
        Args:
            identifier: Tile identifier (name, type, path, or existing ID)
            
        Returns:
            The tile ID, or 0 if not found
        """
        # If it's already a numeric ID and it's valid, return it
        if isinstance(identifier, int):
            if identifier in self.id_to_type:
                return identifier
            return 0
            
        # Otherwise, try to get the ID from the indexer
        tile_id = self.indexer.get_tile_id(identifier)
        return tile_id if tile_id is not None else 0
    
    def get_random_tile_id(self, tile_type: str) -> int:
        """Get a random tile ID of the specified type.
        
        Args:
            tile_type: Type of tile to get
            
        Returns:
            A random tile ID of the specified type, or 0 if none found
        """
        if tile_type in self.type_to_ids and self.type_to_ids[tile_type]:
            return random.choice(self.type_to_ids[tile_type])
        return 0

class EnhancedTileMap:
    """Enhanced tile-based map using structured tile folders."""
    
    def __init__(self, width: int, height: int, tile_size: int = 32):
        """Initialize the enhanced tile map.
        
        Args:
            width: Width of the map in tiles
            height: Height of the map in tiles
            tile_size: Size of each tile in pixels
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.map_data: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
        self.tileset: Optional[EnhancedTileset] = None
        self.layers: Dict[str, List[List[Optional[int]]]] = {}
    
    def set_tileset(self, tileset: EnhancedTileset):
        """Set the tileset to use for this map.
        
        Args:
            tileset: The tileset to use
        """
        self.tileset = tileset
    
    def set_tile(self, x: int, y: int, tile_id: int):
        """Set a tile at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            tile_id: ID of the tile to set
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.map_data[y][x] = tile_id
    
    def get_tile_id(self, x: int, y: int) -> int:
        """Get the ID of the tile at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            The ID of the tile at the specified position
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.map_data[y][x]
        return 0
    
    def get_tile_type(self, x: int, y: int) -> str:
        """Get the type of the tile at the specified position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            The type of the tile at the specified position
        """
        if not self.tileset:
            return "unknown"
            
        tile_id = self.get_tile_id(x, y)
        return self.tileset.id_to_type.get(tile_id, "unknown")
    
    def render(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """Render the tile map.
        
        Args:
            surface: Surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.tileset:
            return
        
        # Calculate the range of tiles to render based on the camera position
        start_x = max(0, camera_x // self.tile_size)
        start_y = max(0, camera_y // self.tile_size)
        end_x = min(self.width, start_x + surface.get_width() // self.tile_size + 2)
        end_y = min(self.height, start_y + surface.get_height() // self.tile_size + 2)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.map_data[y][x]
                tile = self.tileset.get_tile(tile_id)
                dest_x = x * self.tile_size - camera_x
                dest_y = y * self.tile_size - camera_y
                surface.blit(tile, (dest_x, dest_y))

class EnhancedMapGenerator:
    """Generates enhanced tile-based maps."""
    
    def __init__(self, tileset):
        """Initialize the map generator.
        
        Args:
            tileset: The tileset to use for map generation
        """
        self.tileset = tileset
        self.perlin = PerlinNoise()
        
        # Import scene elements and create scene describer
        from .scene_description import SceneElement, SceneDescriber
        self.SceneElement = SceneElement
        self.scene_describer = SceneDescriber(self.tileset.indexer)
    
    def _get_tile_id_for_element(self, element: 'SceneElement') -> Optional[int]:
        """Get a tile ID for a scene element.
        
        Args:
            element: The scene element to get a tile for
            
        Returns:
            A tile ID for the element, or None if not found
        """
        return self.scene_describer.get_tile_for_element(element)
    
    def generate_map(self, width: int, height: int, zone_type: str) -> 'EnhancedTileMap':
        """Generate a new map.
        
        Args:
            width: Map width in tiles
            height: Map height in tiles
            zone_type: Type of zone to generate
            
        Returns:
            The generated map
        """
        # Create a new map
        tilemap = EnhancedTileMap(width, height)
        tilemap.set_tileset(self.tileset)
        
        # Generate terrain heightmap
        heightmap = self.perlin.generate_noise_map(
            width, height,
            scale=10.0,
            octaves=4,
            persistence=0.5,
            lacunarity=2.0
        )
        
        # Generate moisture map for terrain variation
        moisture = self.perlin.generate_noise_map(
            width, height,
            scale=15.0,
            octaves=2,
            persistence=0.5,
            lacunarity=2.0
        )
        
        # Create layers for different tile types
        ground_layer = [[0 for _ in range(width)] for _ in range(height)]
        feature_layer = [[None for _ in range(width)] for _ in range(height)]
        
        # Generate base terrain
        self._generate_terrain(ground_layer, heightmap, moisture, zone_type)
        
        # Generate zone-specific features
        if zone_type == "village":
            self._generate_village_features(feature_layer, ground_layer)
        elif zone_type == "forest":
            self._generate_forest_features(feature_layer, ground_layer)
        
        # Apply layers to the map
        for y in range(height):
            for x in range(width):
                # Set ground tile
                tilemap.set_tile(x, y, ground_layer[y][x])
                
                # Set feature tile if present
                if feature_layer[y][x] is not None:
                    tilemap.set_tile(x, y, feature_layer[y][x])
        
        return tilemap
    
    def _generate_terrain(self, layer: List[List[int]], heightmap: List[List[float]], 
                         moisture: List[List[float]], zone_type: str):
        """Generate terrain based on heightmap and moisture."""
        height = len(layer)
        width = len(layer[0])
        
        for y in range(height):
            for x in range(width):
                height_val = heightmap[y][x]
                moisture_val = moisture[y][x]
                tile_id = None
                
                # Get appropriate tile based on height and moisture
                if zone_type == "village":
                    # Villages are mostly flat with grass
                    if height_val < 0.4:
                        tile_id = self._get_tile_id_for_element(self.SceneElement.GRASS_PLAIN)
                    elif height_val < 0.6:
                        tile_id = self._get_tile_id_for_element(self.SceneElement.GRASS_WILD)
                    else:
                        tile_id = self._get_tile_id_for_element(self.SceneElement.DIRT_PATH)
                        
                elif zone_type == "forest":
                    # Forests have more varied terrain
                    if height_val < 0.3:
                        tile_id = self._get_tile_id_for_element(self.SceneElement.GRASS_PLAIN)
                    elif height_val < 0.6:
                        tile_id = self._get_tile_id_for_element(self.SceneElement.GRASS_WILD)
                    else:
                        tile_id = self._get_tile_id_for_element(self.SceneElement.DIRT_PATH)
                
                # Set the tile, defaulting to GRASS_PLAIN if no valid tile found
                if tile_id is None:
                    tile_id = self._get_tile_id_for_element(self.SceneElement.GRASS_PLAIN)
                    if tile_id is None:
                        logger.warning("Could not get tile ID for GRASS_PLAIN")
                        tile_id = 0
                        
                layer[y][x] = tile_id
    
    def _generate_village_features(self, layer: List[List[Optional[int]]], ground_layer: List[List[int]]):
        """Generate village-specific features."""
        height = len(layer)
        width = len(layer[0])
        
        # Generate path points
        path_points = self._generate_path_points(width, height)
        
        # Create paths between points
        self._create_path(layer, path_points)
        
        # Place houses near paths
        house_locations = self._find_house_locations(path_points, width, height)
        for x, y in house_locations:
            if 0 <= x < width and 0 <= y < height:
                # Use proper SceneElement for walls
                wall_tile = self._get_tile_id_for_element(self.SceneElement.WALL_STONE)
                if wall_tile is not None:
                    layer[y][x] = wall_tile
                else:
                    logger.warning("Could not get tile ID for WALL_STONE")
                    
    def _generate_forest_features(self, layer: List[List[Optional[int]]], ground_layer: List[List[int]]):
        """Generate forest-specific features."""
        height = len(layer)
        width = len(layer[0])
        
        # Add trees and rocks
        for y in range(height):
            for x in range(width):
                if random.random() < 0.1:  # 10% chance for a feature
                    if random.random() < 0.8:  # 80% chance for tree vs rock
                        tree_tile = self._get_tile_id_for_element(self.SceneElement.TREE)
                        if tree_tile is not None:
                            layer[y][x] = tree_tile
                    else:
                        rock_tile = self._get_tile_id_for_element(self.SceneElement.ROCK)
                        if rock_tile is not None:
                            layer[y][x] = rock_tile
    
    def _generate_path_points(self, width: int, height: int) -> List[Tuple[int, int]]:
        """Generate points for path creation."""
        return [(random.randint(0, width-1), random.randint(0, height-1)) for _ in range(3)]
    
    def _create_path(self, layer: List[List[Optional[int]]], points: List[Tuple[int, int]]):
        """Create paths between points."""
        if not points:
            return
            
        # Get the dirt path tile ID
        path_tile = self._get_tile_id_for_element(self.SceneElement.DIRT_PATH)
        if path_tile is None:
            logger.warning("Could not get tile ID for DIRT_PATH")
            return
            
        # Connect each point to the next
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            
            # Simple line drawing
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            x, y = x1, y1
            n = 1 + dx + dy
            x_inc = 1 if x2 > x1 else -1
            y_inc = 1 if y2 > y1 else -1
            error = dx - dy
            dx *= 2
            dy *= 2
            
            for _ in range(n):
                if 0 <= x < len(layer[0]) and 0 <= y < len(layer):
                    layer[y][x] = path_tile
                if error > 0:
                    x += x_inc
                    error -= dy
                else:
                    y += y_inc
                    error += dx
    
    def _find_house_locations(self, path_points: List[Tuple[int, int]], width: int, height: int) -> List[Tuple[int, int]]:
        """Find suitable locations for houses near paths."""
        house_locations = []
        for x, y in path_points:
            # Add some random offset from the path
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            new_x = max(0, min(width-1, x + offset_x))
            new_y = max(0, min(height-1, y + offset_y))
            house_locations.append((new_x, new_y))
        return house_locations 