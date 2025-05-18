"""
Test script for the tile indexer system.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.tile_indexer import TileIndexer

def main():
    """Run the tile indexer test."""
    print("Testing the tile indexer system...")
    
    # Initialize the tile indexer
    indexer = TileIndexer()
    
    # Display all tile categories and counts
    print("\nAvailable tile categories:")
    for category, tiles in indexer.tile_categories.items():
        print(f"  {category}: {len(tiles)} tiles")
    
    # Show some example tiles from each category
    print("\nExample tiles:")
    for category, tiles in indexer.tile_categories.items():
        if tiles:
            examples = tiles[:3] if len(tiles) > 3 else tiles
            print(f"  {category}:")
            for tile in examples:
                print(f"    - {tile}")
    
    # Generate a new tileset configuration
    config_path = os.path.join(project_root, "game/assets/images/enhanced_tileset_config.json")
    print(f"\nGenerating enhanced tileset configuration to: {config_path}")
    indexer.generate_tileset_config(config_path)
    print("Configuration generated.")
    
    print("\nYou can now use the enhanced tile configuration in your game.")
    print("To use it, update your tilemap generator to use the TileIndexer class.")

if __name__ == "__main__":
    main() 