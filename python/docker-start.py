#!/usr/bin/env python3
"""
Docker Compose Startup Helper (Python Version)

This script automatically finds and runs Docker Compose files with
proper error handling and status reporting.

Features:
- Automatically detects common Docker Compose filenames
- Provides clear visual feedback with colored output
- Handles errors gracefully with descriptive messages
- Cross-platform support (Windows, macOS, Linux)
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color

# Status icons
class Icons:
    SUCCESS = "✅"
    ERROR = "❌"
    INFO = "ℹ️"
    ROCKET = "🚀"
    FOLDER = "📂"
    SEARCH = "🔍"
    TIP = "💡"
    DOCKER = "🐳"
    LIST = "📋"

def print_status(icon: str, message: str, color: str) -> None:
    """Print a colored status message with an icon."""
    print(f"{color}{icon} {message}{Colors.NC}")

def check_command_exists(command: str) -> bool:
    """Check if a command exists and is executable."""
    try:
        result = subprocess.run(
            ["which" if sys.platform != "win32" else "where", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False

def run_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)

def check_docker() -> bool:
    """Check if Docker daemon is running."""
    exit_code, _, _ = run_command(["docker", "info"])
    if exit_code != 0:
        print_status(Icons.ERROR, "Docker daemon is not running! Please start Docker first.", Colors.RED)
        return False
    return True

def check_docker_compose() -> bool:
    """Check if Docker Compose is available."""
    exit_code, _, _ = run_command(["docker", "compose", "version"])
    if exit_code != 0:
        print_status(Icons.ERROR, "Docker Compose is not available. Please install it first.", Colors.RED)
        return False
    return True

def find_compose_file(current_dir: Path) -> Optional[str]:
    """Find a Docker Compose file in the current directory."""
    compose_files = ["compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"]
    
    for file in compose_files:
        file_path = current_dir / file
        if file_path.exists():
            print_status(Icons.SUCCESS, f"Found: {file}", Colors.GREEN)
            return file
        else:
            print_status(Icons.ERROR, f"Not found: {file}", Colors.RED)
    
    return None

def main() -> int:
    """Main function to run the Docker Compose startup script."""
    # Display script header
    print_status(Icons.DOCKER, "Docker Compose Startup Helper", Colors.BLUE)
    print("---------------------------------------")
    
    # Check prerequisites
    print_status(Icons.SEARCH, "Checking prerequisites...", Colors.YELLOW)
    if not check_docker():
        return 3
    
    if not check_docker_compose():
        return 4
    
    # Get current directory
    current_dir = Path.cwd()
    print_status(Icons.FOLDER, f"Searching for Docker Compose files in: {current_dir}", Colors.YELLOW)
    
    # Find Docker Compose file
    compose_file = find_compose_file(current_dir)
    
    if not compose_file:
        print_status(Icons.ERROR, f"Error: No valid Docker Compose file found in {current_dir}!", Colors.RED)
        print()
        print_status(Icons.TIP, "Tip: Create one of these files: compose.yaml, compose.yml, docker-compose.yaml, docker-compose.yml", Colors.YELLOW)
        return 1
    
    # Run Docker Compose
    print_status(Icons.ROCKET, f"Starting services from {compose_file}...", Colors.BLUE)
    print()
    
    exit_code, stdout, stderr = run_command(["docker", "compose", "-f", compose_file, "up", "-d"])
    
    if stdout:
        print(stdout)
    
    if exit_code == 0:
        print()
        print_status(Icons.SUCCESS, "Services started successfully!", Colors.GREEN)
        
        # Display running containers
        print()
        print_status(Icons.LIST, "Currently running containers:", Colors.BLUE)
        run_command(["docker", "compose", "-f", compose_file, "ps"])
    else:
        print()
        print_status(Icons.ERROR, f"Docker Compose failed with exit code: {exit_code}", Colors.RED)
        
        if stderr:
            print(stderr)
            
        print_status(Icons.SEARCH, "Possible issues:", Colors.YELLOW)
        print("  - Check the syntax in", compose_file)
        print("  - Ensure Docker daemon is running properly")
        print("  - Verify network connectivity for image pulling")
        print("  - Check for port conflicts with existing services")
        return 2
    
    # Optional pause to view results
    print()
    input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print_status(Icons.ERROR, f"Unexpected error: {e}", Colors.RED)
        sys.exit(1)