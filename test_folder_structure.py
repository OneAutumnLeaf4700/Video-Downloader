#!/usr/bin/env python3
"""
Test script to demonstrate the new format-based folder organization.
This script shows how the folder structure will look without actually downloading.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from video_downloader.downloader import create_organized_folders, sanitize_filename
from utils.folder_utils import get_organized_output_path


def test_folder_structure():
    """Test the new folder organization structure."""
    
    print("🎯 Testing Format-Based Folder Organization Structure\n")
    
    # Test base directory
    base_dir = "downloaded_content"
    
    # Test cases
    test_cases = [
        {
            "name": "MP4 Single Video",
            "is_playlist": False,
            "video_info": {
                "title": "How to Build a Python App",
                "uploader": "Tech Channel"
            },
            "file_format": "mp4"
        },
        {
            "name": "MP3 Single Video",
            "is_playlist": False,
            "video_info": {
                "title": "Amazing Song by Artist",
                "uploader": "Music Channel"
            },
            "file_format": "mp3"
        },
        {
            "name": "MP4 Playlist",
            "is_playlist": True,
            "playlist_info": {
                "title": "Python Tutorial Series",
                "uploader": "CodeAcademy",
                "entry_count": 15
            },
            "file_format": "mp4"
        },
        {
            "name": "MP3 Playlist",
            "is_playlist": True,
            "playlist_info": {
                "title": "Best of 2024 Hits",
                "uploader": "Music Compilation",
                "entry_count": 25
            },
            "file_format": "mp3"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📁 Test Case {i}: {test_case['name']}")
        print("=" * 50)
        
        # Create the folder structure
        folder_path = create_organized_folders(
            base_path=base_dir,
            is_playlist=test_case["is_playlist"],
            playlist_info=test_case.get("playlist_info"),
            video_info=test_case.get("video_info"),
            file_format=test_case["file_format"]
        )
        
        # Get the full output path
        output_path = get_organized_output_path(
            base_path=base_dir,
            is_playlist=test_case["is_playlist"],
            playlist_info=test_case.get("playlist_info"),
            video_info=test_case.get("video_info"),
            file_format=test_case["file_format"]
        )
        
        print(f"📂 Folder: {folder_path}")
        print(f"📄 Output: {output_path}")
        
        # Show the structure
        if test_case["is_playlist"]:
            info = test_case["playlist_info"]
            print(f"🎵 Content: {info['title']} by {info['uploader']} ({info['entry_count']} items)")
        else:
            info = test_case["video_info"]
            print(f"🎥 Content: {info['title']} by {info['uploader']}")
        
        print()
    
    # Show final directory structure
    print("🌳 Final Directory Structure:")
    print("=" * 50)
    
    # Create a visual representation
    structure = {
        "downloaded_content/": {
            "mp3/": {
                "videos/": {
                    "Amazing Song by Artist/": ["Amazing Song by Artist.mp3"]
                },
                "playlists/": {
                    "Music Compilation - Best of 2024 Hits/": ["Various songs..."]
                }
            },
            "mp4/": {
                "videos/": {
                    "How to Build a Python App/": ["How to Build a Python App.mp4"]
                },
                "playlists/": {
                    "CodeAcademy - Python Tutorial Series/": ["Tutorial videos..."]
                }
            }
        }
    }
    
    def print_structure(structure, indent=0):
        for key, value in structure.items():
            print("  " * indent + f"📁 {key}")
            if isinstance(value, dict):
                print_structure(value, indent + 1)
            elif isinstance(value, list):
                for item in value:
                    print("  " * (indent + 1) + f"📄 {item}")
    
    print_structure(structure)
    
    print("\n✅ All folder structures created successfully!")
    print(f"\n💡 Benefits of this structure:")
    print("   • Format separation (MP3/MP4)")
    print("   • Content type separation (videos/playlists)")
    print("   • Individual folders for each video/playlist")
    print("   • Clean, organized download directory")


if __name__ == "__main__":
    test_folder_structure()
