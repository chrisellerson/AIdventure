"""
Test script for the zone-tile integration system that doesn't require pygame.
"""
import os
import sys
import json
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_zone_integration(no_graphics=True):
    """Test the zone-tile integration without pygame.
    
    Args:
        no_graphics: If True, disable pygame imports
    """
    if no_graphics:
        # Create a simple mock for pygame to avoid the import error
        class MockPygame:
            class Surface:
                def __init__(self, size):
                    self.size = size
                
                def get_width(self):
                    return self.size[0]
                
                def get_height(self):
                    return self.size[1]
                
                def fill(self, color):
                    pass
                
                def blit(self, surface, position):
                    pass
                
                def subsurface(self, rect):
                    return MockPygame.Surface((rect[2], rect[3]))
                
                def convert_alpha(self):
                    return self
            
            class Rect:
                def __init__(self, x, y, width, height):
                    self.x = x
                    self.y = y
                    self.width = width
                    self.height = height
            
            @staticmethod
            def image_load(path):
                return MockPygame.Surface((32, 32))
            
            @staticmethod
            def transform_scale(surface, size):
                return MockPygame.Surface(size)
        
        # Create the mock module
        sys.modules['pygame'] = MockPygame
        sys.modules['pygame.image'] = type('', (), {'load': MockPygame.image_load})
        sys.modules['pygame.transform'] = type('', (), {'scale': MockPygame.transform_scale})
    
    print("Testing zone-tile integration...")
    
    # First, test the tile indexing system
    from src.core.tile_indexer import TileIndexer
    
    # Initialize the tile indexer
    print("Initializing tile indexer...")
    indexer = TileIndexer()
    
    # Show available categories
    print("\nAvailable tile categories:")
    for category, tiles in indexer.tile_categories.items():
        print(f"  {category}: {len(tiles)} tiles")
    
    # Then test zone generation
    print("\nTesting zone generation...")
    
    # First, we'll need to hack together a minimal tileset
    # Create a temporary tileset config file if needed
    config_path = os.path.join(project_root, "game", "assets", "images", "tileset_config.json")
    if not os.path.exists(config_path):
        print("Creating minimal tileset config...")
        tile_config = {
            "grass": [0, 1, 2],
            "water": [3, 4, 5],
            "trees": [6, 7, 8],
            "mountains": [9, 10, 11],
            "houses": [12, 13, 14],
            "paths": [15, 16, 17]
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(tile_config, f, indent=2)
    
    # Now test zone integration
    try:
        print("\nTesting enhanced zone generation...")
        from src.core.zone_tile_integration import EnhancedZoneGenerator
        
        # Create the enhanced zone generator
        generator = EnhancedZoneGenerator()
        
        # Generate a village zone
        print("Generating village zone...")
        village_zone = generator.generate_zone("village", (1, 3), "Eldergrove")
        
        # Print zone info
        print(f"Generated zone: {village_zone.name} ({village_zone.zone_type})")
        print(f"Description: {village_zone.description}")
        print(f"Level range: {village_zone.level_range}")
        print(f"Map dimensions: {village_zone.map.width}x{village_zone.map.height}")
        print(f"NPCs: {len(village_zone.npcs)}")
        
        # Generate a forest zone
        print("\nGenerating forest zone...")
        forest_zone = generator.generate_zone("forest", (2, 5), "Darkwood")
        
        # Print zone info
        print(f"Generated zone: {forest_zone.name} ({forest_zone.zone_type})")
        print(f"Description: {forest_zone.description}")
        print(f"Level range: {forest_zone.level_range}")
        print(f"Map dimensions: {forest_zone.map.width}x{forest_zone.map.height}")
        print(f"Enemies: {len(forest_zone.enemies)}")
        
        print("\nZone-tile integration test successful!")
        
    except Exception as e:
        print(f"Error testing zone-tile integration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_zone_integration() 