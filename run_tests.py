#!/usr/bin/env python3
"""
Test runner script for the Video Downloader application.
This script runs all tests and generates coverage reports.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run tests for Video Downloader")
    parser.add_argument("--unit-only", action="store_true", 
                       help="Run only unit tests (skip integration tests)")
    parser.add_argument("--gui-only", action="store_true",
                       help="Run only GUI tests")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = True
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    if args.verbose:
        pytest_cmd.append("-v")
    
    # Add coverage if requested
    if args.coverage:
        pytest_cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Determine which tests to run
    if args.unit_only:
        # Run only unit tests (exclude integration tests that require FFmpeg)
        test_files = [
            "tests/test_config.py",
            "tests/test_worker.py",
            "tests/test_gui.py"
        ]
        for test_file in test_files:
            cmd = pytest_cmd + [test_file]
            if not run_command(cmd, f"Running {test_file}"):
                success = False
    
    elif args.gui_only:
        # Run only GUI tests
        cmd = pytest_cmd + ["tests/test_gui.py"]
        if not run_command(cmd, "Running GUI tests"):
            success = False
    
    else:
        # Run all tests
        cmd = pytest_cmd + ["tests/"]
        if not run_command(cmd, "Running all tests"):
            success = False
    
    # Code quality checks
    print(f"\n{'='*60}")
    print("Running code quality checks...")
    print(f"{'='*60}")
    
    # Check if flake8 is available and run it
    flake8_cmd = ["python", "-m", "flake8", "src/", "tests/", "--max-line-length=100"]
    if run_command(flake8_cmd, "Running flake8 linting"):
        print("✓ Code style checks passed")
    else:
        print("✗ Code style issues found")
        success = False
    
    # Check if black is available and run it
    black_cmd = ["python", "-m", "black", "--check", "src/", "tests/"]
    if run_command(black_cmd, "Running black formatting check"):
        print("✓ Code formatting is correct")
    else:
        print("✗ Code formatting issues found")
        print("  Run 'python -m black src/ tests/' to fix formatting")
        # Don't fail for formatting issues, just warn
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests passed successfully!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
