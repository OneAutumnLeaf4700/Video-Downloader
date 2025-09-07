#!/usr/bin/env python3
"""
Cross-platform build script for Video Downloader
Supports Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Check if all required packages are installed
    required_packages = ["PyQt5", "yt-dlp"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"Installing {package}...")
            run_command([sys.executable, "-m", "pip", "install", package])

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.pyc", "*.pyo"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    # Clean Python cache files
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:
            if dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name))
                dirs.remove(dir_name)

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows build
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            "video_downloader.spec"
        ]
    elif system == "darwin":
        # macOS build
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            "--windowed",
            "video_downloader.spec"
        ]
    else:
        # Linux build
        cmd = [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            "video_downloader.spec"
        ]
    
    run_command(cmd)

def create_installer():
    """Create platform-specific installer."""
    system = platform.system().lower()
    
    if system == "windows":
        print("Creating Windows installer...")
        # You can add NSIS or other Windows installer creation here
        pass
    elif system == "darwin":
        print("Creating macOS app bundle...")
        # macOS app bundle is already created by PyInstaller
        pass
    else:
        print("Creating Linux package...")
        # You can add AppImage or other Linux package creation here
        pass

def main():
    """Main build process."""
    print("Video Downloader Build Script")
    print("=" * 40)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # Check dependencies
        check_dependencies()
        print()
        
        # Clean previous builds
        clean_build()
        print()
        
        # Build executable
        build_executable()
        print()
        
        # Create installer
        create_installer()
        print()
        
        print("Build completed successfully!")
        print(f"Executable location: {script_dir / 'dist' / 'VideoDownloader'}")
        
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
