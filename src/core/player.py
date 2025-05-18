"""
Player entity for the game.
"""
import pygame
from typing import Tuple, Dict, Any

class Player:
    """Player character that can move around the game world."""
    
    def __init__(self, x: int, y: int, tile_size: int = 32):
        """Initialize the player.
        
        Args:
            x: Initial X position in tiles
            y: Initial Y position in tiles
            tile_size: Size of each tile in pixels
        """
        self.tile_x = x
        self.tile_y = y
        self.pixel_x = x * tile_size
        self.pixel_y = y * tile_size
        self.tile_size = tile_size
        self.speed = 4  # Pixels per frame
        self.moving = False
        self.direction = "down"
        self.frame = 0
        self.animations = {}
        self.collision_rects = []
        
        # Create a basic player sprite for now
        self.sprite = pygame.Surface((tile_size, tile_size))
        self.sprite.fill((0, 255, 0))  # Green square
        
        # Movement direction vectors
        self.directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }
    
    def set_animations(self, animations: Dict[str, Any]):
        """Set player animations.
        
        Args:
            animations: Dictionary of animation sequences
        """
        self.animations = animations
    
    def set_collision_map(self, collision_rects):
        """Set collision rectangles to avoid.
        
        Args:
            collision_rects: List of collision rectangles
        """
        self.collision_rects = collision_rects
    
    def move(self, direction: str, tile_map):
        """Move the player in the specified direction.
        
        Args:
            direction: Direction to move ("up", "down", "left", "right")
            tile_map: The tile map for collision detection
        """
        self.direction = direction
        
        if direction not in self.directions:
            return
        
        # Get movement delta
        dx, dy = self.directions[direction]
        next_tile_x = self.tile_x + dx
        next_tile_y = self.tile_y + dy
        
        # Check map boundaries
        if 0 <= next_tile_x < tile_map.width and 0 <= next_tile_y < tile_map.height:
            # Check tile collision - each tile type has different collision properties
            tile_id = tile_map.get_tile_id(next_tile_x, next_tile_y)
            
            # Get tile type for collision checking
            tile_type = self._get_tile_type(tile_id, tile_map.tileset)
            
            # Check if tile is walkable
            if self._is_walkable(tile_type):
                self.tile_x = next_tile_x
                self.tile_y = next_tile_y
                self.pixel_x = self.tile_x * self.tile_size
                self.pixel_y = self.tile_y * self.tile_size
    
    def _get_tile_type(self, tile_id: int, tileset) -> str:
        """Determine the type of a tile.
        
        Args:
            tile_id: ID of the tile
            tileset: The tileset to check
            
        Returns:
            The type of the tile
        """
        if not hasattr(tileset, 'tile_types'):
            return "unknown"
            
        for tile_type, ids in tileset.tile_types.items():
            if tile_id in ids:
                return tile_type
        
        return "unknown"
    
    def _is_walkable(self, tile_type: str) -> bool:
        """Check if a tile type is walkable.
        
        Args:
            tile_type: Type of the tile
            
        Returns:
            True if the tile is walkable, False otherwise
        """
        # Define which tile types are walkable
        walkable_types = ["grass", "paths", "unknown"]
        return tile_type in walkable_types
    
    def update(self, keys, tile_map):
        """Update the player state based on keyboard input.
        
        Args:
            keys: Dictionary of pressed keys
            tile_map: The tile map for collision detection
        """
        moved = False
        
        if keys[pygame.K_UP]:
            self.move("up", tile_map)
            moved = True
        elif keys[pygame.K_DOWN]:
            self.move("down", tile_map)
            moved = True
        elif keys[pygame.K_LEFT]:
            self.move("left", tile_map)
            moved = True
        elif keys[pygame.K_RIGHT]:
            self.move("right", tile_map)
            moved = True
        
        # Animate the player sprite only if moving
        if moved:
            self.frame = (self.frame + 0.1) % 4
    
    def render(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Render the player.
        
        Args:
            surface: Surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        screen_x = self.pixel_x - camera_x
        screen_y = self.pixel_y - camera_y
        
        # Use animations if available, otherwise use basic sprite
        if self.direction in self.animations:
            frame_index = int(self.frame)
            sprite = self.animations[self.direction][frame_index]
            surface.blit(sprite, (screen_x, screen_y))
        else:
            surface.blit(self.sprite, (screen_x, screen_y))
    
    def get_position(self) -> Tuple[int, int]:
        """Get the player's position in tiles.
        
        Returns:
            Tuple of (x, y) tile coordinates
        """
        return (self.tile_x, self.tile_y) 