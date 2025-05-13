"""
Main game entry point.
"""
import pygame
import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from src.core.game_state import GameState
from src.core.scene import SceneManager, MainMenuScene, GameplayScene, CharacterCreationScene

async def main():
    """Initialize and run the game."""
    # Initialize pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("AI-Driven RPG Adventure")
    
    # Create game state
    game_state = GameState()
    
    # Create scene manager
    scene_manager = SceneManager(game_state)
    
    # Register scenes
    scene_manager.register_scene("main_menu", MainMenuScene(game_state))
    scene_manager.register_scene("character_creation", CharacterCreationScene(game_state))
    scene_manager.register_scene("gameplay", GameplayScene(game_state))
    
    # Start with main menu
    scene_manager.change_scene("main_menu")
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                scene_manager.handle_event(event)
        
        # Update
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        scene_manager.update(dt)
        
        # Render
        screen.fill((0, 0, 0))  # Clear screen
        scene_manager.render(screen)
        pygame.display.flip()
        
        # Allow other tasks to run
        await asyncio.sleep(0)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main()) 