"""
Main entry point for the game.
"""
from src.core.game import Game
from src.ui.menu import MenuScene

def main():
    """Initialize and run the game."""
    game = Game()
    game.current_scene = MenuScene(game)
    game.run()

if __name__ == "__main__":
    main() 