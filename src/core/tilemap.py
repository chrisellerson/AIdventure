"""
Tile-based map system for game world.
"""
import pygame
import random
import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

# Configure logger
logger = logging.getLogger(__name__)

class Tileset:
    """Manages tileset images and provides methods for accessing tiles."""
    
    def __init__(self, tileset_path: str, tile_size: int = 32):
        """Initialize the tileset.
        
        Args:
            tileset_path: Path to the tileset image
            tile_size: Size of each tile in pixels
        """
        self.tileset_path = tileset_path
        self.tile_size = tile_size
        self.tileset_image = pygame.image.load(tileset_path).convert_alpha()
        
        # Calculate the number of tiles in the tileset
        self.tileset_width = self.tileset_image.get_width() // tile_size
        self.tileset_height = self.tileset_image.get_height() // tile_size
        
        # Dictionary to cache extracted tiles
        self.tiles: Dict[int, pygame.Surface] = {}
        
        # Load tile configuration if it exists
        config_path = os.path.splitext(tileset_path)[0] + "_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.tile_types = json.load(f)
                logger.info(f"Loaded tile configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading tile configuration: {e}")
                self._set_default_tile_types()
        else:
            logger.info(f"No tile configuration found at {config_path}, using defaults")
            self._set_default_tile_types()
    
    def _set_default_tile_types(self):
        """Set default tile type mappings based on visual inspection of common tilesets."""
        # Analyze the tileset to find common patterns
        total_tiles = self.tileset_width * self.tileset_height
        
        # Create evenly distributed ranges for different tile types
        sixth = total_tiles // 6
        
        self.tile_types = {
            "grass": list(range(0, sixth)),
            "water": list(range(sixth, sixth*2)),
            "trees": list(range(sixth*2, sixth*3)),
            "mountains": list(range(sixth*3, sixth*4)),
            "houses": list(range(sixth*4, sixth*5)),
            "paths": list(range(sixth*5, total_tiles))
        }
        
        # Ensure each category has at least one tile
        for tile_type, tile_list in self.tile_types.items():
            if not tile_list:
                self.tile_types[tile_type] = [0]  # Default to first tile
    
    def get_tile(self, tile_id: int) -> pygame.Surface:
        """Get a tile by its ID.
        
        Args:
            tile_id: ID of the tile to get
            
        Returns:
            The requested tile surface
        """
        if tile_id in self.tiles:
            return self.tiles[tile_id]
        
        # Calculate the position of the tile in the tileset
        tile_x = (tile_id % self.tileset_width) * self.tile_size
        tile_y = (tile_id // self.tileset_width) * self.tile_size
        
        # Extract the tile from the tileset
        tile_rect = pygame.Rect(tile_x, tile_y, self.tile_size, self.tile_size)
        tile = self.tileset_image.subsurface(tile_rect)
        
        # Cache the tile for future use
        self.tiles[tile_id] = tile
        
        return tile
    
    def get_random_tile(self, tile_type: str) -> pygame.Surface:
        """Get a random tile of the specified type.
        
        Args:
            tile_type: Type of tile to get
            
        Returns:
            A random tile of the specified type
        """
        if tile_type not in self.tile_types:
            # Default to grass if type not found
            tile_type = "grass"
        
        tile_id = random.choice(self.tile_types[tile_type])
        return self.get_tile(tile_id)

class TileMap:
    """Represents a tile-based map."""
    
    def __init__(self, width: int, height: int, tile_size: int = 32):
        """Initialize the tile map.
        
        Args:
            width: Width of the map in tiles
            height: Height of the map in tiles
            tile_size: Size of each tile in pixels
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.map_data: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
        self.tileset: Optional[Tileset] = None
        
        # Try to load default tileset configuration
        try:
            with open("game/config/tileset.json", "r") as f:
                self.tile_config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading tile configuration: {e}")
            self.tile_config = {}
    
    def set_tileset(self, tileset: Tileset):
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
    
    def save(self, file_path: str):
        """Save the map to a file.
        
        Args:
            file_path: Path to save the map to
        """
        map_data = {
            "width": self.width,
            "height": self.height,
            "tile_size": self.tile_size,
            "tiles": self.map_data
        }
        
        with open(file_path, "w") as f:
            json.dump(map_data, f)
    
    def load(self, file_path: str):
        """Load a map from a file.
        
        Args:
            file_path: Path to load the map from
        """
        with open(file_path, "r") as f:
            map_data = json.load(f)
        
        self.width = map_data["width"]
        self.height = map_data["height"]
        self.tile_size = map_data["tile_size"]
        self.map_data = map_data["tiles"]

class MapGenerator:
    """Generates game maps based on story elements."""
    
    def __init__(self, tileset: Tileset):
        """Initialize the map generator.
        
        Args:
            tileset: The tileset to use for generating maps
        """
        self.tileset = tileset
    
    def generate_village(self, width: int = 30, height: int = 30) -> TileMap:
        """Generate a village map.
        
        Args:
            width: Width of the map
            height: Height of the map
            
        Returns:
            The generated map
        """
        # Create a new map
        map = TileMap(width, height, self.tileset.tile_size)
        map.set_tileset(self.tileset)
        
        # Get tile types
        grass_tiles = self.tileset.tile_types.get("grass", [0])
        path_tiles = self.tileset.tile_types.get("paths", [0])
        house_tiles = self.tileset.tile_types.get("houses", [0])
        tree_tiles = self.tileset.tile_types.get("trees", [0])
        
        # If any category is empty, use grass tiles as fallback
        if not grass_tiles:
            grass_tiles = [0]
        if not path_tiles:
            path_tiles = grass_tiles
        if not house_tiles:
            house_tiles = grass_tiles
        if not tree_tiles:
            tree_tiles = grass_tiles
        
        # Fill the map with grass
        for y in range(height):
            for x in range(width):
                map.set_tile(x, y, random.choice(grass_tiles))
        
        # Generate a path through the village
        path_start_x = random.randint(0, width // 4)
        path_width = 2
        
        # Horizontal main path
        for x in range(path_start_x, width):
            for pw in range(path_width):
                y = height // 2 + pw
                if 0 <= y < height:
                    map.set_tile(x, y, random.choice(path_tiles))
        
        # Add a vertical crossing path
        cross_x = width // 2
        for y in range(height):
            for pw in range(path_width):
                x = cross_x + pw
                if 0 <= x < width:
                    map.set_tile(x, y, random.choice(path_tiles))
        
        # Add houses along the path (but not on the path)
        for _ in range(8):
            # Try to place houses in appropriate locations
            for attempt in range(10):  # Try up to 10 times to find a good spot
                # Choose random spot near path
                house_x = random.randint(2, width - 4)
                house_y = random.randint(2, height - 4)
                
                # Check if we're not on a path
                if (abs(house_y - height // 2) > 3 or abs(house_x - cross_x) > 3):
                    # Check if we're not too close to another house
                    valid_spot = True
                    for check_y in range(house_y - 2, house_y + 4):
                        for check_x in range(house_x - 2, house_x + 4):
                            if 0 <= check_x < width and 0 <= check_y < height:
                                tile_id = map.get_tile_id(check_x, check_y)
                                if tile_id in house_tiles:
                                    valid_spot = False
                                    break
                    
                    if valid_spot:
                        # Place a 2x2 house
                        base_house_tile = random.choice(house_tiles)
                        map.set_tile(house_x, house_y, base_house_tile)
                        map.set_tile(house_x + 1, house_y, base_house_tile)
                        map.set_tile(house_x, house_y + 1, base_house_tile)
                        map.set_tile(house_x + 1, house_y + 1, base_house_tile)
                        break
        
        # Add trees around the edges and in empty areas
        for _ in range(width * 3):
            tree_x = random.randint(0, width - 1)
            tree_y = random.randint(0, height - 1)
            
            # Don't place trees on paths or houses
            tile_id = map.get_tile_id(tree_x, tree_y)
            if tile_id not in path_tiles and tile_id not in house_tiles:
                map.set_tile(tree_x, tree_y, random.choice(tree_tiles))
        
        return map
    
    def generate_forest(self, width: int = 30, height: int = 30) -> TileMap:
        """Generate a forest map.
        
        Args:
            width: Width of the map
            height: Height of the map
            
        Returns:
            The generated map
        """
        # Create a new map
        map = TileMap(width, height, self.tileset.tile_size)
        map.set_tileset(self.tileset)
        
        # Get tile types
        grass_tiles = self.tileset.tile_types.get("grass", [0])
        tree_tiles = self.tileset.tile_types.get("trees", [0])
        path_tiles = self.tileset.tile_types.get("paths", [0])
        
        # If any category is empty, use grass tiles as fallback
        if not grass_tiles:
            grass_tiles = [0]
        if not tree_tiles:
            tree_tiles = grass_tiles
        if not path_tiles:
            path_tiles = grass_tiles
        
        # Fill the map with grass
        for y in range(height):
            for x in range(width):
                map.set_tile(x, y, random.choice(grass_tiles))
        
        # Create a winding path through the forest
        path_points = []
        
        # Start at a random edge point
        if random.choice([True, False]):
            # Horizontal edge
            start_x = random.randint(0, width - 1)
            start_y = random.choice([0, height - 1])
        else:
            # Vertical edge
            start_x = random.choice([0, width - 1])
            start_y = random.randint(0, height - 1)
        
        path_points.append((start_x, start_y))
        
        # Generate a few random points for the path to go through
        num_points = random.randint(3, 5)
        for _ in range(num_points):
            point_x = random.randint(width // 4, width * 3 // 4)
            point_y = random.randint(height // 4, height * 3 // 4)
            path_points.append((point_x, point_y))
        
        # Connect the points with path tiles
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            
            # Draw a line between the points
            if x1 == x2:  # Vertical line
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    map.set_tile(x1, y, random.choice(path_tiles))
            elif y1 == y2:  # Horizontal line
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    map.set_tile(x, y1, random.choice(path_tiles))
            else:  # Diagonal-ish line
                dx = x2 - x1
                dy = y2 - y1
                steps = max(abs(dx), abs(dy))
                x_inc = dx / steps
                y_inc = dy / steps
                
                x, y = x1, y1
                for _ in range(steps + 1):
                    map.set_tile(int(x), int(y), random.choice(path_tiles))
                    x += x_inc
                    y += y_inc
        
        # Add trees (avoiding the path)
        tree_density = random.uniform(0.3, 0.5)  # 30-50% tree coverage
        for y in range(height):
            for x in range(width):
                # Don't place trees on the path
                if map.get_tile_id(x, y) not in path_tiles and random.random() < tree_density:
                    map.set_tile(x, y, random.choice(tree_tiles))
        
        # Add a clearing in the center or at a random path point
        clearing_center = random.choice(path_points[1:])  # Skip the edge start point
        clearing_x, clearing_y = clearing_center
        clearing_radius = random.randint(3, 6)
        
        for y in range(clearing_y - clearing_radius, clearing_y + clearing_radius + 1):
            for x in range(clearing_x - clearing_radius, clearing_x + clearing_radius + 1):
                if 0 <= x < width and 0 <= y < height:
                    # Calculate distance from clearing center
                    distance = ((x - clearing_x) ** 2 + (y - clearing_y) ** 2) ** 0.5
                    
                    # Clear trees in the clearing, but keep the path
                    if distance < clearing_radius:
                        if map.get_tile_id(x, y) not in path_tiles:
                            map.set_tile(x, y, random.choice(grass_tiles))
        
        return map
    
    def generate_map_for_location(self, location_type: str, width: int = 30, height: int = 30) -> TileMap:
        """Generate a map based on the location type.
        
        Args:
            location_type: Type of location to generate
            width: Width of the map
            height: Height of the map
            
        Returns:
            The generated map
        """
        if location_type.lower() in ["village", "town", "settlement"]:
            return self.generate_village(width, height)
        elif location_type.lower() in ["forest", "woods", "jungle"]:
            return self.generate_forest(width, height)
        else:
            # Default to a village
            return self.generate_village(width, height) 