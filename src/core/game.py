"""
Main game class to coordinate all systems and run the game loop.
"""
import pygame
import sys
import logging
from typing import Optional
from pathlib import Path

from .game_state import GameState
from .scene import SceneManager, MainMenuScene, GameplayScene

logger = logging.getLogger(__name__)

class Game:
    """Main game class."""
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "AI-Driven RPG Adventure"):
        """Initialize the game.
        
        Args:
            width: Window width
            height: Window height
            title: Window title
        """
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption(title)
        
        # Set up display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game state
        self.game_state = GameState()
        
        # Initialize scene manager
        self.scene_manager = SceneManager(self.game_state)
        self._register_scenes()
        
        # Start with main menu
        self.scene_manager.change_scene("main_menu")
    
    def _register_scenes(self) -> None:
        """Register all game scenes."""
        self.scene_manager.register_scene("main_menu", MainMenuScene(self.game_state))
        self.scene_manager.register_scene("gameplay", GameplayScene(self.game_state))
        # TODO: Register other scenes (character creation, inventory, etc.)
    
    def handle_events(self) -> None:
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.scene_manager.handle_event(event)
    
    def update(self, dt: float) -> None:
        """Update game state.
        
        Args:
            dt: Time since last update in seconds
        """
        self.scene_manager.update(dt)
    
    def render(self) -> None:
        """Render the game."""
        self.screen.fill((0, 0, 0))  # Clear screen
        self.scene_manager.render(self.screen)
        pygame.display.flip()  # Update display
    
    def run(self) -> None:
        """Run the main game loop."""
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0  # Convert to seconds
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render frame
            self.render()
        
        # Clean up
        pygame.quit()
        sys.exit()

def main():
    """Main entry point."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run game
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 