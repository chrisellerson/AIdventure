"""
Scene system to manage different game screens and transitions.
"""
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import pygame
import logging
import os

from .game_state import GameState

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
        self.current_story_text = ""
        self.story_queue = []
        
        # Initialize the story agent
        from src.ai.agent_manager import AgentManager
        self.agent_manager = AgentManager(os.getenv("XAI_API_KEY", ""))
    
    async def initialize_story(self):
        """Initialize the game story and starting area."""
        if not self.story_initialized and not self.story_initializing:
            self.story_initializing = True
            try:
                # Create initial story input
                input_data = {
                    "player_action": "start_game",
                    "player_class": self.game_state.player.character_class,
                    "player_name": self.game_state.player.name,
                    "current_location": "starting_area"
                }
                
                # Get story response
                response = await self.agent_manager.process_story_input(input_data)
                
                # Update game state with story elements
                self.current_story_text = response["story_update"]
                self.story_queue = [self.current_story_text]  # Reset queue with only the initial story
                
                # Update NPCs and quests
                for npc_id, npc_response in response["npc_responses"].items():
                    self.game_state.record_npc_interaction(npc_id, {"text": npc_response})
                
                for quest_update in response["quest_updates"]:
                    self.game_state.update_quest_progress(
                        quest_update["quest_id"],
                        quest_update["description"],
                        0
                    )
                
                self.story_initialized = True
            except Exception as e:
                logger.error(f"Error initializing story: {e}")
                self.current_story_text = "Error initializing story. Please try again."
            finally:
                self.story_initializing = False
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle gameplay events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.story_queue:
                    self.current_story_text = self.story_queue.pop(0)
                elif not self.dialogue_active:
                    # Start player movement or interaction
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
            import asyncio
            asyncio.create_task(self.initialize_story())
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the gameplay scene."""
        surface.fill((0, 0, 0))  # Black background
        
        if not self.story_initialized:
            # Show loading message
            loading = self.font.render("Initializing your adventure...", True, (255, 255, 255))
            surface.blit(loading, (surface.get_width() // 2 - loading.get_width() // 2, 
                                 surface.get_height() // 2))
        elif self.current_story_text:
            # Show story text
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
        words = self.current_story_text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            text_surface = self.font.render(test_line, True, (255, 255, 255))
            if text_surface.get_width() < box_rect.width - 40:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Render each line
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (255, 255, 255))
            surface.blit(text, (box_rect.x + 20, box_rect.y + 20 + i * 25))
        
        # Render continue prompt
        if self.story_queue:
            prompt = self.font.render("Press SPACE to continue...", True, (200, 200, 200))
            surface.blit(prompt, (box_rect.x + 20, box_rect.y + box_rect.height - 30))
    
    def _render_gameplay(self, surface: pygame.Surface) -> None:
        """Render the main gameplay view."""
        # Render player
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
        location = self.font.render(self.game_state.player.location, True, (255, 255, 255))
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