"""
Main menu scene for the game.
"""
import pygame
from ..core.scene import Scene
from ..core.config import WHITE, BLACK

class MenuScene(Scene):
    def __init__(self, game):
        """Initialize the menu scene.
        
        Args:
            game: The main game instance
        """
        super().__init__(game)
        self.font = pygame.font.Font(None, 36)
        self.title = self.font.render("AI-Driven RPG Adventure", True, WHITE)
        self.start_text = self.font.render("Press SPACE to Start", True, WHITE)
        self.quit_text = self.font.render("Press ESC to Quit", True, WHITE)

    def update(self):
        """Update the menu state."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # TODO: Change to game scene
            pass

    def draw(self, screen: pygame.Surface):
        """Draw the menu.
        
        Args:
            screen: The pygame surface to draw on
        """
        screen.fill(BLACK)
        
        # Center the text
        title_rect = self.title.get_rect(center=(screen.get_width() // 2, 200))
        start_rect = self.start_text.get_rect(center=(screen.get_width() // 2, 300))
        quit_rect = self.quit_text.get_rect(center=(screen.get_width() // 2, 400))
        
        screen.blit(self.title, title_rect)
        screen.blit(self.start_text, start_rect)
        screen.blit(self.quit_text, quit_rect) 