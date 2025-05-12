"""
Game configuration settings.
"""
from typing import Dict, Any
import os
from pathlib import Path

# Game window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
TITLE = "AI-Driven RPG Adventure"

# Asset paths
ASSET_DIR = Path(__file__).parent.parent.parent / "assets"
SPRITE_DIR = ASSET_DIR / "sprites"
SOUND_DIR = ASSET_DIR / "sounds"
FONT_DIR = ASSET_DIR / "fonts"

# Game settings
TILE_SIZE = 32
PLAYER_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game states
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    BATTLE = "battle"
    DIALOGUE = "dialogue"
    GAME_OVER = "game_over"

# Load environment variables
def load_env_vars() -> Dict[str, Any]:
    """Load environment variables for API keys and other sensitive data."""
    return {
        "XAI_API_KEY": os.getenv("XAI_API_KEY", ""),
    } 