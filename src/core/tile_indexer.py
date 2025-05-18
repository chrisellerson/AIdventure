"""
Tile indexing system that maps organized tile folders to usable game tiles.
"""
import os
import json
import random
import pygame
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Union

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TileIndexer:
    """Class for indexing and organizing tiles from structured tile directories."""
    
    def __init__(self, base_path: str = "game/assets/images"):
        """Initialize the tile indexer.
        
        Args:
            base_path: Path to the image assets
        """
        self.base_path = Path(base_path)
        self.crawl_tiles_path = self.base_path / "crawl-tiles Oct-5-2010"
        self.tile_size = 32  # Default tile size
        
        # Verify the crawl tiles directory exists
        if not self.crawl_tiles_path.exists():
            raise RuntimeError(f"Crawl tiles directory not found at: {self.crawl_tiles_path}")
        
        # Cached tile surfaces
        self.tiles_cache: Dict[str, pygame.Surface] = {}
        
        # Tile type categories and paths
        self.tile_categories = {
            "grass": [],
            "water": [],
            "trees": [],
            "mountains": [],
            "houses": [],
            "paths": [],
            "walls": [],
            "floors": [],
            "doors": [],
            "special": [],
            "items": [],
            "player": [],
            "monster": []
        }
        
        # Map tile names to numeric IDs
        self.name_to_id: Dict[str, int] = {}
        self.id_to_name: Dict[int, str] = {}
        self.current_id = 1  # Start from 1, 0 reserved for empty
        
        # Initialize by indexing only the tiles we use
        self._index_tiles()
    
    def _register_tile(self, tile_path: str, category: str):
        """Register a tile with a unique ID.
        
        Args:
            tile_path: Path to the tile file
            category: Category the tile belongs to
        """
        try:
            tile_path_str = str(tile_path)
            logger.debug(f"Registering tile: {tile_path_str} in category: {category}")
            
            # Check if the tile file exists
            full_path = self.crawl_tiles_path / tile_path_str
            if not full_path.exists():
                logger.warning(f"Tile file does not exist: {full_path}")
                return
                
            if tile_path_str not in self.name_to_id:
                self.name_to_id[tile_path_str] = self.current_id
                self.id_to_name[self.current_id] = tile_path_str
                self.current_id += 1
                logger.debug(f"Assigned ID {self.current_id-1} to tile: {tile_path_str}")
            
            category_str = str(category)
            if category_str in self.tile_categories:
                if tile_path_str not in self.tile_categories[category_str]:
                    self.tile_categories[category_str].append(tile_path_str)
                    logger.debug(f"Added tile to category {category_str}: {tile_path_str}")
        except Exception as e:
            logger.error(f"Error registering tile {tile_path} in category {category}: {e}")

    def _index_tiles(self):
        """Index all available tiles in the directory structure."""
        # Reset all categories before indexing
        for category in self.tile_categories:
            self.tile_categories[category] = []
            
        # Reset ID mappings
        self.name_to_id.clear()
        self.id_to_name.clear()
        self.current_id = 1  # Start from 1, 0 reserved for empty
        
        # Get the structured paths from scene_description.py
        from .scene_description import SceneElement, SceneDescriber
        
        # Import the scene element mappings
        scene_describer = SceneDescriber(self)
        
        # Index only the specific tiles we use
        for element, tile_paths in scene_describer.element_to_tiles.items():
            # Determine the category based on the element name
            if "GRASS" in element.name or "PATH" in element.name or "WATER" in element.name:
                category = "grass" if "GRASS" in element.name else "paths" if "PATH" in element.name else "water"
            elif "WALL" in element.name:
                category = "walls"
            elif "DOOR" in element.name:
                category = "doors"
            elif "FLOOR" in element.name:
                category = "floors"
            elif "TREE" in element.name or "BUSH" in element.name or "FLOWER" in element.name:
                category = "trees"
            elif "ROCK" in element.name:
                category = "mountains"
            elif "CHEST" in element.name or "BARREL" in element.name or "TABLE" in element.name:
                category = "items"
            else:
                category = "special"
            
            # Register each tile path for this element
            for tile_path in tile_paths:
                self._register_tile(tile_path, category)
                
        # Log the final tile counts
        for category, tiles in self.tile_categories.items():
            if tiles:
                logger.info(f"Indexed {len(tiles)} {category} tiles")
                logger.debug(f"Sample tiles for {category}: {tiles[:3]}")
                
    def get_tile_id(self, identifier: Union[str, int]) -> Optional[int]:
        """Get the numeric ID for a tile identifier.
        
        Args:
            identifier: The tile identifier (can be a path, name, or existing ID)
            
        Returns:
            The tile ID or None if not found
        """
        # If it's already a numeric ID, verify it exists
        if isinstance(identifier, int):
            return identifier if identifier in self.id_to_name else None
            
        # Convert to string for all other cases
        try:
            identifier_str = str(identifier)
            logger.debug(f"Looking up tile ID for identifier: {identifier_str}")
            
            # If it's already a registered path, return its ID
            if identifier_str in self.name_to_id:
                logger.debug(f"Found registered path: {identifier_str}")
                return self.name_to_id[identifier_str]
            
            # Try to find a matching tile path in our categories
            for category, tiles in self.tile_categories.items():
                logger.debug(f"Searching in category {category} with {len(tiles)} tiles")
                for tile in tiles:
                    logger.debug(f"Comparing with tile: {tile}")
                    if identifier_str == tile:  # Use exact matching
                        logger.debug(f"Found matching tile: {tile}")
                        return self.name_to_id.get(str(tile))
            
            # If no match found, log a warning and return None
            logger.warning(f"Could not find tile ID for identifier: {identifier}")
            return None
            
        except Exception as e:
            logger.error(f"Error looking up tile ID for {identifier}: {e}")
            return None

    def get_random_tile(self, category: str) -> Optional[str]:
        """Get a random tile path from the specified category.
        
        Args:
            category: Tile category (grass, water, trees, etc.)
            
        Returns:
            Path to a random tile in the category, or None if category is empty
        """
        tiles = self.tile_categories.get(category, [])
        if not tiles:
            return None
        
        return random.choice(tiles)
    
    def get_tile_path(self, tile_id: str) -> Path:
        """Get the full path to a tile.
        
        Args:
            tile_id: Tile identifier
            
        Returns:
            Full path to the tile file
        """
        try:
            # The tile_id should already be a proper path relative to the crawl tiles directory
            return self.crawl_tiles_path / tile_id
        except Exception as e:
            logger.error(f"Error resolving path for tile {tile_id}: {e}")
            return self.crawl_tiles_path / tile_id
    
    def get_tile_surface(self, tile_id: str) -> Optional[pygame.Surface]:
        """Get a pygame surface for the specified tile.
        
        Args:
            tile_id: Tile identifier
            
        Returns:
            Pygame surface for the tile, or None if not found
        """
        if tile_id in self.tiles_cache:
            return self.tiles_cache[tile_id]
        
        try:
            path = self.get_tile_path(tile_id)
            logger.debug(f"Loading tile from path: {path}")
            if not path.exists():
                logger.warning(f"Tile file does not exist: {path}")
                return None
                
            surface = pygame.image.load(str(path)).convert_alpha()
            
            # Resize if needed
            if surface.get_width() != self.tile_size or surface.get_height() != self.tile_size:
                surface = pygame.transform.scale(surface, (self.tile_size, self.tile_size))
                
            # Cache the surface
            self.tiles_cache[tile_id] = surface
            return surface
        except Exception as e:
            logger.error(f"Error loading tile {tile_id}: {e}")
            return None
    
    def generate_tileset_config(self, output_path: Optional[str] = None) -> Dict[str, List[str]]:
        """Generate a tileset configuration based on the indexed tiles.
        
        Args:
            output_path: Optional path to save the configuration
            
        Returns:
            Dictionary of tile categories and their tile IDs
        """
        config = {category: tiles for category, tiles in self.tile_categories.items() if tiles}
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        return config

    def _load_tileset_config(self) -> bool:
        """Load tile configuration from file.
        
        Returns:
            True if config was successfully loaded, False otherwise
        """
        config_path = self.base_path / "tileset_config.json"
        if not config_path.exists():
            return False
            
        try:
            with open(config_path, 'r') as f:
                tile_config = json.load(f)
                
            # Validate and load the configuration
            if not isinstance(tile_config, dict):
                logger.error("Invalid tileset configuration format")
                return False
                
            # Clear existing categories
            for category in self.tile_categories:
                self.tile_categories[category] = []
                
            # Load categories and generate IDs
            for category, tile_paths in tile_config.items():
                if category in self.tile_categories and isinstance(tile_paths, list):
                    for tile_path in tile_paths:
                        # Register the tile with its path
                        self._register_tile(tile_path, category)
                        
            logger.info("Successfully loaded tileset configuration")
            return True
            
        except Exception as e:
            logger.error(f"Error loading tileset configuration: {e}")
            return False 