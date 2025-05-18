"""
Test script for the enhanced zone generation system.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_enhanced_zones():
    """Test the enhanced zone generation."""
    print("Testing enhanced zone generation...")
    
    # Import here to avoid circular imports
    from src.core.zone_tile_integration import EnhancedZoneManager
    
    # Create the enhanced zone manager
    zone_manager = EnhancedZoneManager()
    
    # Generate a village zone
    print("\nGenerating village zone...")
    village_zone = zone_manager.generate_zone("village", (1, 3), "Eldergrove")
    
    # Print zone info
    print(f"Generated zone: {village_zone.name} ({village_zone.zone_type})")
    print(f"Description: {village_zone.description}")
    print(f"Level range: {village_zone.level_range}")
    print(f"Map dimensions: {village_zone.map.width}x{village_zone.map.height}")
    print(f"NPCs: {len(village_zone.npcs)}")
    print(f"Quests: {len(village_zone.quests)}")
    
    # Generate a forest zone
    print("\nGenerating forest zone...")
    forest_zone = zone_manager.generate_zone("forest", (2, 5), "Darkwood")
    
    # Print zone info
    print(f"Generated zone: {forest_zone.name} ({forest_zone.zone_type})")
    print(f"Description: {forest_zone.description}")
    print(f"Level range: {forest_zone.level_range}")
    print(f"Map dimensions: {forest_zone.map.width}x{forest_zone.map.height}")
    print(f"Enemies: {len(forest_zone.enemies)}")
    print(f"Landmarks: {len(forest_zone.landmarks)}")
    
    # Connect the zones
    print("\nConnecting zones...")
    # Add connection from village to forest
    village_zone.add_connection(
        "east", 
        forest_zone.zone_id,
        village_zone.map.width - 1,
        village_zone.map.height // 2
    )
    
    # Add connection from forest to village
    forest_zone.add_connection(
        "west",
        village_zone.zone_id,
        0,
        forest_zone.map.height // 2
    )
    
    print(f"Connected {village_zone.name} to {forest_zone.name}")
    
    print("\nEnhanced zone generation test completed successfully.")
    print("You can now integrate this into your game using:")
    print("from src.core.zone_tile_integration import EnhancedZoneManager")
    print("zone_manager = EnhancedZoneManager()")
    print("village = zone_manager.generate_zone('village', (1, 3))")

if __name__ == "__main__":
    test_enhanced_zones() 