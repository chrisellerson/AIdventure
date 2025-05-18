#!/usr/bin/env python3
"""
Tool to configure tile types for the game tileset.
"""
import os
import sys
import json
from pathlib import Path
import pygame

# Initialize pygame
pygame.init()

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_COLOR = (50, 50, 50)
SELECTION_COLOR = (255, 0, 0)
BG_COLOR = (20, 20, 20)

# Tile type colors
TYPE_COLORS = {
    "grass": (0, 200, 0),
    "water": (0, 0, 200),
    "trees": (0, 100, 0),
    "mountains": (100, 80, 60),
    "houses": (150, 75, 0),
    "paths": (200, 200, 100)
}

class TileConfigurator:
    """Tool to configure tiles in a tileset."""
    
    def __init__(self, tileset_path):
        """Initialize the tile configurator.
        
        Args:
            tileset_path: Path to the tileset image
        """
        self.tileset_path = tileset_path
        self.tileset_image = pygame.image.load(tileset_path)
        
        # Calculate the number of tiles in the tileset
        self.tileset_width = self.tileset_image.get_width() // TILE_SIZE
        self.tileset_height = self.tileset_image.get_height() // TILE_SIZE
        
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tile Configurator")
        
        # Set up the font
        self.font = pygame.font.Font(None, 24)
        
        # Tile configurations
        self.tile_types = {
            "grass": [],
            "water": [],
            "trees": [],
            "mountains": [],
            "houses": [],
            "paths": []
        }
        
        # Current state
        self.current_type = "grass"
        self.selected_tile = None
        self.scroll_x = 0
        self.scroll_y = 0
        self.max_scroll_x = max(0, self.tileset_width * TILE_SIZE - SCREEN_WIDTH)
        self.max_scroll_y = max(0, self.tileset_height * TILE_SIZE - SCREEN_HEIGHT + 100)  # Extra space for UI
    
    def run(self):
        """Run the configurator tool."""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(event)
            
            # Render the screen
            self.screen.fill(BG_COLOR)
            self._render_tileset()
            self._render_ui()
            pygame.display.flip()
            
            clock.tick(60)
        
        # Save the configuration before quitting
        self._save_config()
        pygame.quit()
    
    def _handle_keydown(self, event):
        """Handle keyboard input.
        
        Args:
            event: The pygame event
        """
        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.key == pygame.K_1:
            self.current_type = "grass"
        elif event.key == pygame.K_2:
            self.current_type = "water"
        elif event.key == pygame.K_3:
            self.current_type = "trees"
        elif event.key == pygame.K_4:
            self.current_type = "mountains"
        elif event.key == pygame.K_5:
            self.current_type = "houses"
        elif event.key == pygame.K_6:
            self.current_type = "paths"
        elif event.key == pygame.K_UP:
            self.scroll_y = max(0, self.scroll_y - TILE_SIZE)
        elif event.key == pygame.K_DOWN:
            self.scroll_y = min(self.max_scroll_y, self.scroll_y + TILE_SIZE)
        elif event.key == pygame.K_LEFT:
            self.scroll_x = max(0, self.scroll_x - TILE_SIZE)
        elif event.key == pygame.K_RIGHT:
            self.scroll_x = min(self.max_scroll_x, self.scroll_x + TILE_SIZE)
        elif event.key == pygame.K_s:
            self._save_config()
        elif event.key == pygame.K_l:
            self._load_config()
    
    def _handle_mouse_click(self, event):
        """Handle mouse clicks.
        
        Args:
            event: The pygame event
        """
        if event.button == 1:  # Left click
            mouse_x, mouse_y = event.pos
            
            # Only process clicks within the tileset area
            if mouse_y < SCREEN_HEIGHT - 100:
                # Calculate the tile coordinates
                tile_x = (mouse_x + self.scroll_x) // TILE_SIZE
                tile_y = (mouse_y + self.scroll_y) // TILE_SIZE
                
                if 0 <= tile_x < self.tileset_width and 0 <= tile_y < self.tileset_height:
                    # Calculate the tile ID
                    tile_id = tile_y * self.tileset_width + tile_x
                    
                    # Toggle the tile in the current type
                    self.selected_tile = tile_id
                    
                    # Add or remove the tile from the current type
                    if tile_id in self.tile_types[self.current_type]:
                        self.tile_types[self.current_type].remove(tile_id)
                    else:
                        # Remove from other types first
                        for type_name in self.tile_types:
                            if tile_id in self.tile_types[type_name]:
                                self.tile_types[type_name].remove(tile_id)
                        
                        # Add to current type
                        self.tile_types[self.current_type].append(tile_id)
                        self.tile_types[self.current_type].sort()
    
    def _render_tileset(self):
        """Render the tileset with grid and selections."""
        # Draw the tileset
        self.screen.blit(self.tileset_image, (-self.scroll_x, -self.scroll_y))
        
        # Draw grid lines
        for x in range(0, self.tileset_width * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(
                self.screen, GRID_COLOR, 
                (x - self.scroll_x, 0), 
                (x - self.scroll_x, self.tileset_height * TILE_SIZE - self.scroll_y)
            )
        
        for y in range(0, self.tileset_height * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(
                self.screen, GRID_COLOR,

                (0, y - self.scroll_y), 
                (self.tileset_width * TILE_SIZE - self.scroll_x, y - self.scroll_y)
            )
        
        # Draw selections for each tile type
        for type_name, tile_ids in self.tile_types.items():
            color = TYPE_COLORS.get(type_name, (200, 200, 200))
            
            for tile_id in tile_ids:
                tile_x = (tile_id % self.tileset_width) * TILE_SIZE - self.scroll_x
                tile_y = (tile_id // self.tileset_width) * TILE_SIZE - self.scroll_y
                
                # Only draw if visible
                if (0 <= tile_x < SCREEN_WIDTH and 0 <= tile_y < SCREEN_HEIGHT - 100 and
                    tile_x + TILE_SIZE > 0 and tile_y + TILE_SIZE > 0):
                    pygame.draw.rect(
                        self.screen, color, 
                        (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 
                        2
                    )
    
    def _render_ui(self):
        """Render the UI elements."""
        # Draw background for UI area
        pygame.draw.rect(self.screen, (40, 40, 40), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        
        # Draw current type
        current_type_text = self.font.render(f"Current Type: {self.current_type}", True, (255, 255, 255))
        self.screen.blit(current_type_text, (20, SCREEN_HEIGHT - 90))
        
        # Draw keyboard shortcuts
        shortcuts_text = self.font.render("1-6: Select Type | Arrows: Scroll | S: Save | L: Load | ESC: Quit", True, (200, 200, 200))
        self.screen.blit(shortcuts_text, (20, SCREEN_HEIGHT - 60))
        
        # Draw type counts
        count_text = self.font.render(
            " | ".join([f"{type_name}: {len(tile_ids)}" for type_name, tile_ids in self.tile_types.items()]), 
            True, (200, 200, 200)
        )
        self.screen.blit(count_text, (20, SCREEN_HEIGHT - 30))
    
    def _save_config(self):
        """Save the tile configurations to a file."""
        config_path = os.path.splitext(self.tileset_path)[0] + "_config.json"
        
        with open(config_path, "w") as f:
            json.dump(self.tile_types, f, indent=2)
        
        print(f"Configuration saved to: {config_path}")
    
    def _load_config(self):
        """Load the tile configurations from a file."""
        config_path = os.path.splitext(self.tileset_path)[0] + "_config.json"
        
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.tile_types = json.load(f)
            
            print(f"Configuration loaded from: {config_path}")
        else:
            print(f"Configuration file not found: {config_path}")

def main():
    """Process command line arguments and run the configurator."""
    if len(sys.argv) < 2:
        print("Usage: python configure_tiles.py <tileset_image_path>")
        return
    
    tileset_path = sys.argv[1]
    if not os.path.exists(tileset_path):
        print(f"Error: File not found at {tileset_path}")
        return
    
    configurator = TileConfigurator(tileset_path)
    configurator.run()

if __name__ == "__main__":
    main() 