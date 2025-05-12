"""
Basic UI system for rendering game elements.
"""
import pygame
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class UIElement:
    """Base class for UI elements."""
    x: int
    y: int
    width: int
    height: int
    visible: bool = True
    enabled: bool = True
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if point is within element bounds."""
        return (self.x <= point[0] <= self.x + self.width and
                self.y <= point[1] <= self.y + self.height)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the element."""
        pass

class Button(UIElement):
    """Clickable button element."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, color: Tuple[int, int, int] = (200, 200, 200),
                 hover_color: Tuple[int, int, int] = (150, 150, 150),
                 text_color: Tuple[int, int, int] = (0, 0, 0),
                 font_size: int = 24):
        """Initialize button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            color: Normal button color
            hover_color: Color when mouse hovers
            text_color: Text color
            font_size: Font size
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.on_click = None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        if not self.enabled or not self.visible:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.contains_point(event.pos)
            return self.hovered
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.contains_point(event.pos):
                if self.on_click:
                    self.on_click()
                return True
                
        return False
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the button."""
        if not self.visible:
            return
            
        # Draw button background
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        
        # Draw button border
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width/2,
                                                 self.y + self.height/2))
        surface.blit(text_surface, text_rect)

class TextBox(UIElement):
    """Text display element."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str = "", color: Tuple[int, int, int] = (255, 255, 255),
                 background_color: Optional[Tuple[int, int, int]] = None,
                 font_size: int = 24):
        """Initialize text box.
        
        Args:
            x: X position
            y: Y position
            width: Box width
            height: Box height
            text: Text to display
            color: Text color
            background_color: Background color (None for transparent)
            font_size: Font size
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.background_color = background_color
        self.font = pygame.font.Font(None, font_size)
    
    def set_text(self, text: str) -> None:
        """Update text content."""
        self.text = text
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        # TextBox doesn't handle any events by default
        return False
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the text box."""
        if not self.visible:
            return
            
        # Draw background if specified
        if self.background_color:
            pygame.draw.rect(surface, self.background_color,
                           (self.x, self.y, self.width, self.height))
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=(self.x + self.width/2,
                                                 self.y + self.height/2))
        surface.blit(text_surface, text_rect)

class Panel(UIElement):
    """Container for other UI elements."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 color: Tuple[int, int, int] = (50, 50, 50),
                 border_color: Tuple[int, int, int] = (100, 100, 100)):
        """Initialize panel.
        
        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            color: Background color
            border_color: Border color
        """
        super().__init__(x, y, width, height)
        self.color = color
        self.border_color = border_color
        self.elements: List[UIElement] = []
    
    def add_element(self, element: UIElement) -> None:
        """Add a UI element to the panel."""
        self.elements.append(element)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for all child elements."""
        if not self.enabled or not self.visible:
            return False
            
        for element in self.elements:
            if element.handle_event(event):
                return True
        return False
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the panel and all child elements."""
        if not self.visible:
            return
            
        # Draw panel background
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw panel border
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height), 2)
        
        # Render child elements
        for element in self.elements:
            element.render(surface)

class UIManager:
    """Manages all UI elements."""
    
    def __init__(self):
        """Initialize UI manager."""
        self.elements: Dict[str, UIElement] = {}
    
    def add_element(self, name: str, element: UIElement) -> None:
        """Add a UI element.
        
        Args:
            name: Element identifier
            element: UI element
        """
        self.elements[name] = element
    
    def get_element(self, name: str) -> Optional[UIElement]:
        """Get a UI element by name."""
        return self.elements.get(name)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events for all elements."""
        for element in self.elements.values():
            if element.handle_event(event):
                return True
        return False
    
    def render(self, surface: pygame.Surface) -> None:
        """Render all UI elements."""
        for element in self.elements.values():
            element.render(surface) 