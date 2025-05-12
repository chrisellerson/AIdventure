"""
Test script for core game components.
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.game import Game
from src.core.ui import UIManager, Button, TextBox, Panel
from src.core.game_state import GameState
from src.core.scene import SceneManager, MainMenuScene, GameplayScene

def test_ui_system():
    """Test the UI system components."""
    print("Starting UI system test...")
    
    # Initialize pygame
    import pygame
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("UI System Test")
    
    # Create UI manager
    ui_manager = UIManager()
    
    # Create test panel
    panel = Panel(100, 100, 600, 400)
    
    # Add buttons to panel
    new_game_btn = Button(250, 200, 300, 50, "New Game")
    load_game_btn = Button(250, 300, 300, 50, "Load Game")
    quit_btn = Button(250, 400, 300, 50, "Quit")
    
    # Add text box
    title_text = TextBox(250, 100, 300, 50, "Game Menu",
                        background_color=(30, 30, 30))
    
    # Add elements to panel
    panel.add_element(title_text)
    panel.add_element(new_game_btn)
    panel.add_element(load_game_btn)
    panel.add_element(quit_btn)
    
    # Add panel to UI manager
    ui_manager.add_element("main_panel", panel)
    
    # Set up button callbacks
    def on_new_game():
        print("New Game clicked")
        title_text.set_text("Starting new game...")
    
    def on_load_game():
        print("Load Game clicked")
        title_text.set_text("Loading game...")
    
    def on_quit():
        print("Quit clicked")
        pygame.quit()
        sys.exit()
    
    new_game_btn.on_click = on_new_game
    load_game_btn.on_click = on_load_game
    quit_btn.on_click = on_quit
    
    print("UI elements created and configured")
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    frame_count = 0
    max_frames = 60  # Run for 1 second at 60 FPS
    
    while running and frame_count < max_frames:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                ui_manager.handle_event(event)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Render UI
        ui_manager.render(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap frame rate and increment counter
        clock.tick(60)
        frame_count += 1
        
        if frame_count % 30 == 0:  # Log every half second
            print(f"Frame {frame_count}/{max_frames}")
    
    pygame.quit()
    print("UI system test completed")

def test_game_state():
    """Test the game state management."""
    print("Starting game state test...")
    
    # Create game state
    game_state = GameState()
    
    # Test starting new game
    game_state.new_game("Test Player")
    print("New game started")
    
    # Test saving game state
    game_state.save_game("test_save")
    print("Game state saved")
    
    # Test loading game state
    game_state.load_game("test_save")
    print("Game state loaded")
    
    # Test updating quest progress
    game_state.update_quest_progress("test_quest", "objective_1", 1)
    print("Quest progress updated")
    
    # Test recording NPC interaction
    game_state.record_npc_interaction("test_npc", {"text": "Hello!"})
    print("NPC interaction recorded")
    
    print("Game state tests passed!")

def test_scene_system():
    """Test the scene management system."""
    print("Starting scene system test...")
    
    # Create game state
    game_state = GameState()
    
    # Create scene manager
    scene_manager = SceneManager(game_state)
    
    # Register test scenes
    scene_manager.register_scene("main_menu", MainMenuScene(game_state))
    scene_manager.register_scene("gameplay", GameplayScene(game_state))
    print("Scenes registered")
    
    # Test scene transitions
    scene_manager.change_scene("main_menu")
    assert scene_manager.current_scene.__class__.__name__ == "MainMenuScene"
    print("Changed to main menu scene")
    
    scene_manager.change_scene("gameplay")
    assert scene_manager.current_scene.__class__.__name__ == "GameplayScene"
    print("Changed to gameplay scene")
    
    print("Scene system tests passed!")

def main():
    """Run all tests."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run tests
        print("\n=== Testing UI system ===")
        test_ui_system()
        
        print("\n=== Testing game state ===")
        test_game_state()
        
        print("\n=== Testing scene system ===")
        test_scene_system()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 