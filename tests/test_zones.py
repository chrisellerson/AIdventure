"""
Test script for the zone system.
"""
import os
import sys
import pygame
import asyncio
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.zone import ZoneManager, Tileset

class ZoneTestApp:
    """Test application for visualizing zones."""
    
    def __init__(self):
        """Initialize the test application."""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Zone System Test")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize test assets
        assets_dir = Path(project_root, "game", "assets", "images")
        if not assets_dir.exists():
            assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to find a tileset
        tileset_path = None
        for path in ["tileset.png", "game/assets/images/tileset.png", "../game/assets/images/tileset.png"]:
            if os.path.exists(path):
                tileset_path = path
                break
        
        if not tileset_path:
            print("Tileset not found. Please ensure a tileset.png exists in the game/assets/images directory.")
            pygame.quit()
            sys.exit(1)
        
        # Initialize zone system
        self.tileset = Tileset(tileset_path)
        self.zone_manager = ZoneManager(self.tileset)
        
        # Test variables
        self.current_zone = None
        self.camera_x = 0
        self.camera_y = 0
        self.font = pygame.font.Font(None, 24)
        self.test_char_x = 0
        self.test_char_y = 0
        self.messages = []
        
        # Controls info
        self.controls = [
            "Controls:",
            "Arrow keys: Move test character",
            "Z: Generate village zone",
            "F: Generate forest zone",
            "C: Connect zones (select two zones first)",
            "Tab: Switch between zones",
            "Esc: Quit"
        ]
        
        # Selected zones for connecting
        self.selected_zones = []
        
        print("Zone System Test initialized")
    
    def generate_test_zone(self, zone_type):
        """Generate a test zone and set it as current."""
        level_range = (1, 3)
        name = None  # Let the generator name it
        
        zone = self.zone_manager.generate_zone(zone_type, level_range, name)
        self.zone_manager.set_current_zone(zone.zone_id)
        self.current_zone = zone
        
        # Place test character in the center of the zone
        self.test_char_x = zone.map.width // 2
        self.test_char_y = zone.map.height // 2
        
        self.messages.append(f"Generated {zone_type} zone: {zone.name}")
        return zone
    
    def connect_zones(self):
        """Connect two selected zones."""
        if len(self.selected_zones) < 2:
            self.messages.append("Select at least two zones first (use Tab to select zones)")
            return
        
        zone1 = self.selected_zones[0]
        zone2 = self.selected_zones[1]
        
        # Connect zone1 to zone2 (east to west)
        zone1.add_connection(
            "east",
            zone2.zone_id,
            zone1.map.width - 1,
            zone1.map.height // 2
        )
        
        # Connect zone2 to zone1 (west to east)
        zone2.add_connection(
            "west",
            zone1.zone_id,
            0,
            zone2.map.height // 2
        )
        
        self.messages.append(f"Connected {zone1.name} to {zone2.name}")
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_z:
                    # Generate village zone
                    zone = self.generate_test_zone("village")
                    if zone not in self.selected_zones:
                        self.selected_zones.append(zone)
                        if len(self.selected_zones) > 2:
                            self.selected_zones.pop(0)
                elif event.key == pygame.K_f:
                    # Generate forest zone
                    zone = self.generate_test_zone("forest")
                    if zone not in self.selected_zones:
                        self.selected_zones.append(zone)
                        if len(self.selected_zones) > 2:
                            self.selected_zones.pop(0)
                elif event.key == pygame.K_c:
                    # Connect zones
                    self.connect_zones()
                elif event.key == pygame.K_TAB:
                    # Switch to the next zone
                    zones = list(self.zone_manager.zones.values())
                    if zones:
                        current_index = zones.index(self.current_zone) if self.current_zone in zones else -1
                        next_index = (current_index + 1) % len(zones)
                        self.current_zone = zones[next_index]
                        self.zone_manager.set_current_zone(self.current_zone.zone_id)
                        self.messages.append(f"Switched to zone: {self.current_zone.name}")
    
    def update(self):
        """Update the test application state."""
        keys = pygame.key.get_pressed()
        
        if self.current_zone and self.current_zone.map:
            # Move test character
            new_x, new_y = self.test_char_x, self.test_char_y
            
            if keys[pygame.K_UP]:
                new_y -= 1
            if keys[pygame.K_DOWN]:
                new_y += 1
            if keys[pygame.K_LEFT]:
                new_x -= 1
            if keys[pygame.K_RIGHT]:
                new_x += 1
                
            # Check map boundaries
            if 0 <= new_x < self.current_zone.map.width and 0 <= new_y < self.current_zone.map.height:
                self.test_char_x, self.test_char_y = new_x, new_y
            
            # Check for zone transitions
            self._check_zone_transitions()
            
            # Update camera to follow character
            tile_size = self.current_zone.map.tile_size
            self.camera_x = self.test_char_x * tile_size - 400 + tile_size // 2
            self.camera_y = self.test_char_y * tile_size - 300 + tile_size // 2
            
            # Limit camera to map boundaries
            map_width = self.current_zone.map.width * tile_size
            map_height = self.current_zone.map.height * tile_size
            self.camera_x = max(0, min(self.camera_x, map_width - 800))
            self.camera_y = max(0, min(self.camera_y, map_height - 600))
    
    def _check_zone_transitions(self):
        """Check if test character has reached a zone transition point."""
        if not self.current_zone:
            return
            
        # Check all connections in the current zone
        for direction, connection in self.current_zone.connections.items():
            target_zone_id = connection["target_zone_id"]
            connection_x = connection["x"]
            connection_y = connection["y"]
            
            # Check if character is at the connection point
            if (self.test_char_x == connection_x and 
                self.test_char_y == connection_y):
                
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
                    
                    # Position character at entry point
                    self.test_char_x = entry_x
                    self.test_char_y = entry_y
                    
                    # Add a message about entering the new zone
                    self.messages.append(f"Entered {target_zone.name}")
                    break
    
    def render(self):
        """Render the test application."""
        self.screen.fill((0, 0, 0))  # Black background
        
        # Render current zone if available
        if self.current_zone and self.current_zone.map:
            # Render the zone
            self.current_zone.render(self.screen, self.camera_x, self.camera_y)
            
            # Render zone connections
            for direction, connection in self.current_zone.connections.items():
                conn_x = connection["x"] * self.current_zone.map.tile_size - self.camera_x
                conn_y = connection["y"] * self.current_zone.map.tile_size - self.camera_y
                
                # Draw connection point
                pygame.draw.rect(self.screen, (255, 255, 0), 
                                 (conn_x, conn_y, self.current_zone.map.tile_size, self.current_zone.map.tile_size), 2)
                
                # Draw direction label
                dir_label = self.font.render(direction, True, (255, 255, 0))
                self.screen.blit(dir_label, (conn_x, conn_y - 20))
            
            # Render test character
            char_x = self.test_char_x * self.current_zone.map.tile_size - self.camera_x
            char_y = self.test_char_y * self.current_zone.map.tile_size - self.camera_y
            pygame.draw.rect(self.screen, (255, 0, 0), 
                             (char_x, char_y, self.current_zone.map.tile_size, self.current_zone.map.tile_size))
            
            # Render zone info
            zone_info = self.font.render(
                f"Zone: {self.current_zone.name} ({self.current_zone.zone_type}) - Level {self.current_zone.level_range}", 
                True, (255, 255, 255)
            )
            self.screen.blit(zone_info, (10, 10))
            
            # Render NPCs, enemies, and landmarks count
            counts = self.font.render(
                f"NPCs: {len(self.current_zone.npcs)} | Enemies: {len(self.current_zone.enemies)} | Landmarks: {len(self.current_zone.landmarks)}", 
                True, (255, 255, 255)
            )
            self.screen.blit(counts, (10, 40))
            
            # Render player position
            pos_info = self.font.render(
                f"Position: ({self.test_char_x}, {self.test_char_y})", 
                True, (255, 255, 255)
            )
            self.screen.blit(pos_info, (10, 70))
        else:
            # Render instructions if no zone is available
            text = self.font.render("Press Z to generate a village zone or F for a forest zone", True, (255, 255, 255))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 
                                  self.screen.get_height() // 2))
        
        # Render selected zones list
        if self.selected_zones:
            selected_text = self.font.render(
                f"Selected zones: {', '.join(zone.name for zone in self.selected_zones)}", 
                True, (255, 255, 0)
            )
            self.screen.blit(selected_text, (10, 100))
        
        # Render controls
        for i, control in enumerate(self.controls):
            ctrl = self.font.render(control, True, (200, 200, 200))
            self.screen.blit(ctrl, (10, 400 + i * 25))
        
        # Render messages
        if self.messages:
            for i, message in enumerate(self.messages[-5:]):  # Show last 5 messages
                msg = self.font.render(message, True, (0, 255, 0))
                self.screen.blit(msg, (10, 130 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        """Run the test application."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    """Run the zone system test."""
    app = ZoneTestApp()
    app.run()

if __name__ == "__main__":
    main() 