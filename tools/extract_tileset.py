#!/usr/bin/env python3
"""
Tool to save a tileset image from a file.
"""
import os
import sys
import shutil
from pathlib import Path

def save_tileset(src_path, dest_path):
    """
    Save the tileset image to the game assets directory.
    
    Args:
        src_path: Source path of the tileset image
        dest_path: Destination path to save the tileset
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Copy the file
    shutil.copy(src_path, dest_path)
    print(f"Tileset saved to: {dest_path}")

def main():
    """Process command line arguments and save tileset."""
    if len(sys.argv) < 2:
        print("Usage: python extract_tileset.py <tileset_image_path>")
        return
    
    src_path = sys.argv[1]
    if not os.path.exists(src_path):
        print(f"Error: File not found at {src_path}")
        return
    
    # Determine the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Set destination path
    dest_path = os.path.join(project_root, "game", "assets", "images", "tileset.png")
    
    save_tileset(src_path, dest_path)

if __name__ == "__main__":
    main() 