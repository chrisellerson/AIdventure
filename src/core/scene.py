"""
Scene system to manage different game screens and transitions.
"""
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import pygame
import logging
import os
import asyncio
import re
import random

from .game_state import GameState
from .enhanced_tilemap import EnhancedTileset

# Import zone management system
from .zone import ZoneManager, Zone
# Import enhanced zone system
from .zone_tile_integration import EnhancedZoneManager

logger = logging.getLogger(__name__)

class Scene(ABC):
    """Base class for all game scenes."""
    
    def __init__(self, game_state: GameState):
        """Initialize the scene.
        
        Args:
            game_state: The game state manager
        """
        self.game_state = game_state
        self.next_scene: Optional[str] = None
        self.is_running = True
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events.
        
        Args:
            event: The pygame event to handle
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene state.
        
        Args:
            dt: Time since last update in seconds
        """
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """Render the scene.
        
        Args:
            surface: The surface to render to
        """
        pass
    
    def change_scene(self, scene_name: str) -> None:
        """Request a scene change.
        
        Args:
            scene_name: Name of the scene to change to
        """
        self.next_scene = scene_name
        self.is_running = False

class MainMenuScene(Scene):
    """Main menu scene."""
    
    def __init__(self, game_state: GameState):
        """Initialize the main menu scene."""
        super().__init__(game_state)
        self.font = pygame.font.Font(None, 36)
        self.menu_items = [
            "New Game",
            "Load Game",
            "Settings",
            "Quit"
        ]
        self.selected_item = 0
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu navigation and selection."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                self._handle_selection()
    
    def _handle_selection(self) -> None:
        """Handle menu item selection."""
        if self.menu_items[self.selected_item] == "New Game":
            self.change_scene("character_creation")
        elif self.menu_items[self.selected_item] == "Load Game":
            self.change_scene("load_game")
        elif self.menu_items[self.selected_item] == "Settings":
            self.change_scene("settings")
        elif self.menu_items[self.selected_item] == "Quit":
            pygame.quit()
            exit()
    
    def update(self, dt: float) -> None:
        """Update menu state."""
        pass
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the menu."""
        surface.fill((0, 0, 0))  # Black background
        
        # Render title
        title = self.font.render("AI-Driven RPG Adventure", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title, title_rect)
        
        # Render menu items
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            text = self.font.render(item, True, color)
            rect = text.get_rect(center=(surface.get_width() // 2, 250 + i * 50))
            surface.blit(text, rect)

class GameplayScene(Scene):
    """Main gameplay scene."""
    
    def __init__(self, game_state: GameState):
        """Initialize the gameplay scene."""
        super().__init__(game_state)
        self.font = pygame.font.Font(None, 24)
        self.dialogue_active = False
        self.current_dialogue: Optional[Dict[str, Any]] = None
        self.story_initialized = False
        self.story_initializing = False
        self.story_init_failed = False
        self.current_story_text = ""
        self.story_queue = []
        
        # Game world components
        self.tilemap = None
        self.player = None
        self.camera_x = 0
        self.camera_y = 0
        self.zone_manager = None
        self.current_zone = None
        self.tileset = None
        
        # Import modules
        try:
            # Import these at the class level to avoid circular imports
            import src.core.player
            self.Player = src.core.player.Player
            
            # Initialize enhanced tileset
            assets_path = os.path.join("game", "assets", "images")
            self.tileset = EnhancedTileset(assets_path)
            
            if not self.tileset:
                logger.error("Failed to initialize enhanced tileset")
                self.story_init_failed = True
                return
            
            # Initialize zone manager with enhanced version
            try:
                self.zone_manager = EnhancedZoneManager(self.tileset)
                logger.info("Using enhanced zone manager with structured tile folders")
            except Exception as e:
                logger.error(f"Error initializing enhanced zone manager: {e}")
                self.story_init_failed = True
                return
                
        except Exception as e:
            logger.error(f"Error loading modules: {e}")
            self.story_init_failed = True
            return
        
        # Initialize the story agent
        from src.ai.agent_manager import AgentManager
        self.agent_manager = AgentManager(os.getenv("XAI_API_KEY", ""), self.tileset)
    
    async def initialize_story(self):
        """Initialize the game story and starting area."""
        if self.story_init_failed:
            self.current_story_text = "Error initializing game. Please restart."
            self.story_initialized = True
            return
            
        try:
            self.story_initializing = True
            
            # Initialize story with AI
            story_intro = await self.agent_manager.get_story_intro(self.game_state.player)
            
            if not story_intro:
                raise ValueError("Failed to get story introduction from AI")
            
            # Format the story text
            if story_intro:
                # Clean up any HTML-like formatting and use color formatting instead
                # Replace [text] style highlights with proper formatting that the game can display
                # First extract any highlighted parts to preserve them
                highlights = []
                if "[" in story_intro and "]" in story_intro:
                    highlights = re.findall(r'\[(.*?)\]', story_intro)
                
                # Process special variables like ${player.name} with actual values
                if "${" in story_intro:
                    for match in re.findall(r'\${(.*?)}', story_intro):
                        try:
                            # Evaluate simple player attributes
                            if match.startswith("player."):
                                attr = match.split(".")[1]
                                if hasattr(self.game_state.player, attr):
                                    value = getattr(self.game_state.player, attr)
                                    story_intro = story_intro.replace(f"${{{match}}}", str(value))
                        except Exception as e:
                            logger.error(f"Error processing variable {match}: {e}")
                
                # Remove any HTML-style tags and replace with game-friendly formatting
                formatted_story = story_intro.replace("<span style='color:#ffcc00'>", "*").replace("</span>", "*")
                formatted_story = formatted_story.replace("[", "*").replace("]", "*")
                
                # Split into paragraphs for display
                paragraphs = formatted_story.split("\n\n")
                self.current_story_text = paragraphs[0] if paragraphs else ""
                self.story_queue = paragraphs[1:] if len(paragraphs) > 1 else []
                
                # Extract location information for map generation
                location_type = "village"  # Default
                for highlight in highlights:
                    # Convert highlight to string and ensure it's lowercase
                    highlight_str = str(highlight).lower()
                    if any(keyword in highlight_str for keyword in ["village", "town", "forest", "mountains", "cave"]):
                        for keyword in ["village", "town", "forest", "mountains", "cave"]:
                            if keyword in highlight_str:
                                location_type = keyword
                                break
                        break
                
                # Normalize location type for map generation
                location_type_str = str(location_type).lower()
                if any(keyword in location_type_str for keyword in ["town", "village", "settlement"]):
                    map_type = "village"
                elif any(keyword in location_type_str for keyword in ["forest", "woods", "jungle"]):
                    map_type = "forest"
                else:
                    map_type = "village"  # Default
                
                # Generate starting zone
                if self.zone_manager:
                    try:
                        # Generate a starting village zone
                        starting_zone = self.zone_manager.generate_zone(
                            zone_type=map_type,
                            level_range=(1, 3),
                            name="Eldergrove"  # Default name which may be overridden by the generator
                        )
                        
                        if not starting_zone:
                            raise ValueError("Failed to generate starting zone")
                        
                        # Set current zone
                        self.zone_manager.set_current_zone(starting_zone.zone_id)
                        self.current_zone = starting_zone
                        
                        # Use the map from the zone
                        self.tilemap = self.current_zone.map
                        
                        # Create player at the center of the starting village
                        if hasattr(self, 'Player'):
                            self.player = self.Player(self.tilemap.width // 2, self.tilemap.height // 2)
                            
                    except Exception as e:
                        logger.error(f"Error generating zone: {e}")
                        raise
                else:
                    raise ValueError("Zone manager not initialized")
                
                self.story_initialized = True
            else:
                self.current_story_text = "Once upon a time in a magical land..."
                self.story_initialized = True
                
        except Exception as e:
            logger.error(f"Error initializing story: {e}")
            self.story_init_failed = True
            self.current_story_text = "Error initializing story. Please restart the game."
            self.story_initialized = True
        finally:
            self.story_initializing = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle gameplay events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.story_queue:
                    self.current_story_text = self.story_queue.pop(0)
                    if not self.story_queue and not self.current_story_text:
                        # Last story text, clear it and start gameplay
                        self.current_story_text = ""
                elif self.current_story_text:
                    # Clear story text to start gameplay
                    self.current_story_text = ""
                elif not self.dialogue_active:
                    # Check for NPC interactions
                    pass
            elif event.key == pygame.K_ESCAPE:
                self.change_scene("main_menu")  # Changed from pause_menu to main_menu
            elif event.key == pygame.K_i:
                self.change_scene("inventory")
            elif event.key == pygame.K_m:
                self.change_scene("map")
    
    def update(self, dt: float) -> None:
        """Update gameplay state."""
        if not self.story_initialized and not self.story_initializing:
            # Initialize story asynchronously
            asyncio.create_task(self.initialize_story())
        elif self.player and self.tilemap and not self.story_queue:
            # Only handle player movement when not displaying story text
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.tilemap)
            
            # Check for zone transitions
            if self.current_zone:
                self._check_zone_transitions()
            
            # Update camera to follow player
            self.camera_x = self.player.pixel_x - (800 // 2)
            self.camera_y = self.player.pixel_y - (600 // 2)
            
            # Keep camera within map bounds
            self.camera_x = max(0, min(self.camera_x, self.tilemap.width * self.tilemap.tile_size - 800))
            self.camera_y = max(0, min(self.camera_y, self.tilemap.height * self.tilemap.tile_size - 600))
    
    def _check_zone_transitions(self):
        """Check if player has reached a zone transition point."""
        if not self.current_zone:
            return
            
        # Check all connections in the current zone
        for direction, connection in self.current_zone.connections.items():
            target_zone_id = connection["target_zone_id"]
            connection_x = connection["x"]
            connection_y = connection["y"]
            
            # Check if player is at the connection point
            if (self.player.tile_x == connection_x and 
                self.player.tile_y == connection_y):
                
                # Get the target zone
                target_zone = self.zone_manager.get_zone(target_zone_id)
                if target_zone:
                    # Find the reverse connection point
                    reverse_direction = {
                        "north": "south",
                        "south": "north",
                        "east": "west",
                        "west": "east"
                    }.get(direction)
                    
                    # Find the entry point in the target zone
                    entry_x, entry_y = 0, 0
                    if reverse_direction in target_zone.connections:
                        rev_conn = target_zone.connections[reverse_direction]
                        if rev_conn["target_zone_id"] == self.current_zone.zone_id:
                            entry_x = rev_conn["x"]
                            entry_y = rev_conn["y"]
                    
                    # Switch to the new zone
                    self.zone_manager.set_current_zone(target_zone_id)
                    self.current_zone = target_zone
                    self.tilemap = target_zone.map
                    
                    # Position player at entry point
                    self.player.tile_x = entry_x
                    self.player.tile_y = entry_y
                    self.player.pixel_x = entry_x * self.player.tile_size
                    self.player.pixel_y = entry_y * self.player.tile_size
                    
                    # Add a story text about entering the new zone
                    self.current_story_text = f"You have entered {target_zone.name}. {target_zone.description}"
                    break

    def render(self, surface: pygame.Surface) -> None:
        """Render the gameplay scene."""
        surface.fill((0, 0, 0))  # Black background
        
        if not self.story_initialized:
            # Show loading message
            loading = self.font.render("Initializing your adventure...", True, (255, 255, 255))
            surface.blit(loading, (surface.get_width() // 2 - loading.get_width() // 2, 
                                 surface.get_height() // 2))
        elif self.current_story_text:
            # First render the game world if it exists
            if self.current_zone and self.player:
                # Render the current zone and its entities
                self.current_zone.render(surface, self.camera_x, self.camera_y)
                self.player.render(surface, self.camera_x, self.camera_y)
            elif self.tilemap and self.player:
                # Fallback to basic rendering if no zone is available
                self.tilemap.render(surface, self.camera_x, self.camera_y)
                self.player.render(surface, self.camera_x, self.camera_y)
            
            # Then show story text
            self._render_story(surface)
        else:
            # Show gameplay
            self._render_gameplay(surface)
    
    def _render_story(self, surface: pygame.Surface) -> None:
        """Render the story text."""
        # Create story box
        box_rect = pygame.Rect(50, surface.get_height() - 200, surface.get_width() - 100, 150)
        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (255, 255, 255), box_rect, 2)
        
        # Render story text with word wrapping
        max_line_width = box_rect.width - 40
        max_lines = 5  # Maximum lines to show at once
        
        if self.current_story_text:
            # Process text with highlighting
            # Use * as markers for highlighted text (e.g., *Village* would be highlighted)
            text_parts = self.current_story_text.split('*')
            highlight_mode = False
            
            lines = []
            current_line = []
            current_line_text = ""
            
            for part in text_parts:
                if not part:  # Skip empty parts
                    highlight_mode = not highlight_mode
                    continue
                
                color = (255, 255, 0) if highlight_mode else (255, 255, 255)
                words = part.split()
                
                for word in words:
                    test_line = current_line_text + (" " if current_line_text else "") + word
                    text_surface = self.font.render(test_line, True, (255, 255, 255))
                    
                    if text_surface.get_width() < max_line_width:
                        current_line.append((word, color))
                        current_line_text = test_line
                    else:
                        if current_line:  # Only append if there are words
                            lines.append(current_line)
                        current_line = [(word, color)]
                        current_line_text = word
                
                highlight_mode = not highlight_mode
            
            if current_line:
                lines.append(current_line)
            
            # Only show a subset of lines if there are many
            visible_lines = lines[:max_lines]
            
            # Render each line
            for i, line in enumerate(visible_lines):
                x_pos = box_rect.x + 20
                for word, color in line:
                    word_surface = self.font.render(word, True, color)
                    surface.blit(word_surface, (x_pos, box_rect.y + 20 + i * 30))
                    x_pos += word_surface.get_width() + self.font.size(" ")[0]  # Add space width
        
        # Render continue prompt
        if self.story_queue:
            prompt = self.font.render("Press SPACE to continue...", True, (200, 200, 200))
        else:
            prompt = self.font.render("Press SPACE to start your adventure...", True, (200, 200, 200))
            
        surface.blit(prompt, (box_rect.x + 20, box_rect.y + box_rect.height - 30))
    
    def _render_gameplay(self, surface: pygame.Surface) -> None:
        """Render the main gameplay view."""
        if self.current_zone and self.player:
            # Render zone with all its entities
            self.current_zone.render(surface, self.camera_x, self.camera_y)
            self.player.render(surface, self.camera_x, self.camera_y)
        elif self.tilemap and self.player:
            # Fallback to basic rendering
            self.tilemap.render(surface, self.camera_x, self.camera_y)
            self.player.render(surface, self.camera_x, self.camera_y)
        else:
            # Extra fallback to basic rendering
            player_rect = pygame.Rect(surface.get_width() // 2 - 25, surface.get_height() // 2 - 25, 50, 50)
            pygame.draw.rect(surface, (0, 255, 0), player_rect)
        
        # Render UI elements
        self._render_ui(surface)
    
    def _render_ui(self, surface: pygame.Surface) -> None:
        """Render UI elements."""
        # Health bar
        health_rect = pygame.Rect(20, 20, 200, 20)
        pygame.draw.rect(surface, (255, 0, 0), health_rect)
        health_fill = pygame.Rect(20, 20, 200 * (self.game_state.player.health / self.game_state.player.max_health), 20)
        pygame.draw.rect(surface, (0, 255, 0), health_fill)
        
        # Location name
        location_name = self.current_zone.name if self.current_zone else self.game_state.player.location
        location = self.font.render(location_name, True, (255, 255, 255))
        surface.blit(location, (surface.get_width() - location.get_width() - 20, 20))
        
        # Character info
        char_info = self.font.render(
            f"{self.game_state.player.name} - Level {self.game_state.player.level} {self.game_state.player.character_class}",
            True, (255, 255, 255)
        )
        surface.blit(char_info, (20, 50))

class CharacterCreationScene(Scene):
    """Character creation scene."""
    
    def __init__(self, game_state: GameState):
        """Initialize the character creation scene."""
        super().__init__(game_state)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.name = ""
        self.name_active = True
        self.selected_class = 0
        self.classes = ["Warrior", "Mage", "Rogue"]
        self.class_descriptions = {
            "Warrior": "A mighty warrior skilled in combat and heavy armor.",
            "Mage": "A powerful spellcaster who wields arcane magic.",
            "Rogue": "A stealthy adventurer who excels in agility and precision."
        }
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle character creation events."""
        if event.type == pygame.KEYDOWN:
            if self.name_active:
                if event.key == pygame.K_RETURN and self.name:
                    self.name_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.change_scene("main_menu")
                elif len(self.name) < 20:  # Limit name length
                    self.name += event.unicode
            else:
                if event.key == pygame.K_UP:
                    self.selected_class = (self.selected_class - 1) % len(self.classes)
                elif event.key == pygame.K_DOWN:
                    self.selected_class = (self.selected_class + 1) % len(self.classes)
                elif event.key == pygame.K_RETURN:
                    self._create_character()
                elif event.key == pygame.K_ESCAPE:
                    self.name_active = True
    
    def _create_character(self) -> None:
        """Create the character and start the game."""
        # Initialize player state with selected class
        self.game_state.new_game(self.name)
        self.game_state.player.character_class = self.classes[self.selected_class]
        
        # Set class-specific starting stats
        if self.classes[self.selected_class] == "Warrior":
            self.game_state.player.health = 120
            self.game_state.player.max_health = 120
            self.game_state.player.strength = 10
            self.game_state.player.defense = 8
        elif self.classes[self.selected_class] == "Mage":
            self.game_state.player.health = 80
            self.game_state.player.max_health = 80
            self.game_state.player.magic = 12
            self.game_state.player.mana = 100
        else:  # Rogue
            self.game_state.player.health = 90
            self.game_state.player.max_health = 90
            self.game_state.player.agility = 12
            self.game_state.player.stealth = 10
        
        # Start the game
        self.change_scene("gameplay")
    
    def update(self, dt: float) -> None:
        """Update character creation state."""
        pass
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the character creation screen."""
        surface.fill((0, 0, 0))  # Black background
        
        # Render title
        title = self.font.render("Create Your Character", True, (255, 255, 255))
        title_rect = title.get_rect(center=(surface.get_width() // 2, 100))
        surface.blit(title, title_rect)
        
        # Render name input
        name_label = self.font.render("Enter your name:", True, (255, 255, 255))
        surface.blit(name_label, (surface.get_width() // 2 - 200, 200))
        
        name_box = pygame.Rect(surface.get_width() // 2 - 200, 250, 400, 40)
        pygame.draw.rect(surface, (255, 255, 255) if self.name_active else (100, 100, 100), name_box, 2)
        
        name_text = self.font.render(self.name + ("|" if self.name_active else ""), True, (255, 255, 255))
        surface.blit(name_text, (name_box.x + 10, name_box.y + 5))
        
        if not self.name_active:
            # Render class selection
            class_label = self.font.render("Choose your class:", True, (255, 255, 255))
            surface.blit(class_label, (surface.get_width() // 2 - 200, 350))
            
            for i, class_name in enumerate(self.classes):
                color = (255, 255, 0) if i == self.selected_class else (255, 255, 255)
                class_text = self.font.render(class_name, True, color)
                surface.blit(class_text, (surface.get_width() // 2 - 200, 400 + i * 50))
                
                # Render class description
                desc = self.small_font.render(self.class_descriptions[class_name], True, (200, 200, 200))
                surface.blit(desc, (surface.get_width() // 2 - 200, 425 + i * 50))
            
            # Render instructions
            instructions = self.small_font.render("Use UP/DOWN to select class, ENTER to confirm, ESC to go back", True, (150, 150, 150))
            surface.blit(instructions, (surface.get_width() // 2 - 300, 600))

class SceneManager:
    """Manages scene transitions and updates."""
    
    def __init__(self, game_state: GameState):
        """Initialize the scene manager.
        
        Args:
            game_state: The game state manager
        """
        self.game_state = game_state
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
    
    def register_scene(self, scene_name: str, scene: Scene) -> None:
        """Register a new scene.
        
        Args:
            scene_name: Name of the scene
            scene: Scene instance
        """
        self.scenes[scene_name] = scene
    
    def change_scene(self, scene_name: str) -> None:
        """Change to a different scene.
        
        Args:
            scene_name: Name of the scene to change to
        """
        if scene_name not in self.scenes:
            raise ValueError(f"Scene {scene_name} not found")
        
        self.current_scene = self.scenes[scene_name]
        self.game_state.current_scene = scene_name
    
    def update(self, dt: float) -> None:
        """Update the current scene.
        
        Args:
            dt: Time since last update in seconds
        """
        if self.current_scene:
            self.current_scene.update(dt)
            
            if not self.current_scene.is_running:
                self.change_scene(self.current_scene.next_scene)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events for the current scene.
        
        Args:
            event: The pygame event to handle
        """
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the current scene.
        
        Args:
            surface: The surface to render to
        """
        if self.current_scene:
            self.current_scene.render(surface) 