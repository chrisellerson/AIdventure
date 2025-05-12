"""
Scene system to manage different game screens and transitions.
"""
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod
import pygame
import logging

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
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle gameplay events."""
        if self.dialogue_active:
            self._handle_dialogue_event(event)
        else:
            self._handle_gameplay_event(event)
    
    def _handle_dialogue_event(self, event: pygame.event.Event) -> None:
        """Handle dialogue-related events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Advance dialogue
                pass
            elif event.key == pygame.K_ESCAPE:
                # Close dialogue
                self.dialogue_active = False
                self.current_dialogue = None
    
    def _handle_gameplay_event(self, event: pygame.event.Event) -> None:
        """Handle gameplay-related events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_scene("pause_menu")
            elif event.key == pygame.K_i:
                self.change_scene("inventory")
            elif event.key == pygame.K_m:
                self.change_scene("map")
    
    def update(self, dt: float) -> None:
        """Update gameplay state."""
        if not self.dialogue_active:
            # Update player position, animations, etc.
            pass
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the gameplay scene."""
        surface.fill((0, 0, 0))  # Black background
        
        if self.dialogue_active:
            self._render_dialogue(surface)
        else:
            self._render_gameplay(surface)
    
    def _render_dialogue(self, surface: pygame.Surface) -> None:
        """Render the dialogue interface."""
        if not self.current_dialogue:
            return
        
        # Render dialogue box
        box_rect = pygame.Rect(50, surface.get_height() - 200, surface.get_width() - 100, 150)
        pygame.draw.rect(surface, (0, 0, 0), box_rect)
        pygame.draw.rect(surface, (255, 255, 255), box_rect, 2)
        
        # Render dialogue text
        text = self.font.render(self.current_dialogue["text"], True, (255, 255, 255))
        surface.blit(text, (box_rect.x + 20, box_rect.y + 20))
        
        # Render choices if any
        if "choices" in self.current_dialogue:
            for i, choice in enumerate(self.current_dialogue["choices"]):
                choice_text = self.font.render(choice["text"], True, (255, 255, 255))
                surface.blit(choice_text, (box_rect.x + 20, box_rect.y + 60 + i * 30))
    
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