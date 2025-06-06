#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CondaWiz: Conda Environment Wizard
==================================

A beautiful, feature-rich tool for creating and managing Conda environments.

Features:
- User-friendly colored interface with emoji support
- Python version detection and selection from conda
- Cross-platform support (Windows, macOS, Linux)
- Templated environment.yml creation
- Package installation
- Comprehensive activation instructions
- IDE integration options

Author: Enhanced from original script
Version: 2.0.0
License: MIT
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Set version
__version__ = "2.0.0"

# Try to import colorama for cross-platform color support
try:
    from colorama import Fore, Back, Style, init
    has_colorama = True
    init(autoreset=True)
except ImportError:
    has_colorama = False
    # Create mock colorama classes if not available
    class MockStyle:
        NORMAL = BRIGHT = RESET_ALL = ""
    class MockFore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    class MockBack:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    Fore = MockFore()
    Back = MockBack()
    Style = MockStyle()

# Define emoji constants
class Emoji:
    """Emoji constants for better UI"""
    PYTHON = "🐍"
    CONDA = "🪅"
    WRENCH = "🛠️"
    CHECK = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    FOLDER = "📁"
    DELETE = "🗑️"
    SKIP = "⏭️"
    ROCKET = "🚀"
    NOTE = "📝"
    PARTY = "🎉"
    QUESTION = "❓"
    EXIT = "🚪"
    GEAR = "⚙️"
    PACKAGE = "📦"
    SEARCH = "🔍"
    SAVE = "💾"
    STAR = "⭐"

# Default environment.yml templates
BASIC_TEMPLATE = """# Basic Conda Environment
# Generated by CondaWiz

name: {env_name}
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - pip
  - pytest>=7.0.0
  - black>=23.0.0
  - flake8>=6.0.0
  - pip:
    # Define pip packages here
    - pytest-cov>=4.0.0
"""

WEB_TEMPLATE = """# Web Development Conda Environment
# Generated by CondaWiz

name: {env_name}
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - flask>=2.2.0
  - requests>=2.28.0
  - gunicorn>=20.1.0
  - pip
  - pytest>=7.0.0
  - black>=23.0.0
  - pip:
    # Define pip-only packages here
    - pytest-flask>=1.2.0
"""

DATA_TEMPLATE = """# Data Science Conda Environment
# Generated by CondaWiz

name: {env_name}
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - numpy>=1.22.0
  - pandas>=1.4.0
  - matplotlib>=3.5.0
  - seaborn>=0.11.2
  - scikit-learn>=1.0.0
  - jupyter>=1.0.0
  - ipykernel>=6.9.0
  - pip
  - pip:
    # Define pip-only packages here
    - yellowbrick>=1.4
"""

ML_TEMPLATE = """# Machine Learning Conda Environment
# Generated by CondaWiz

name: {env_name}
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - numpy>=1.22.0
  - pandas>=1.4.0
  - scikit-learn>=1.0.0
  - tensorflow>=2.8.0
  - pytorch>=1.10.0
  - matplotlib>=3.5.0
  - jupyter>=1.0.0
  - pip
  - pip:
    # Define pip-only packages here
    - tensorboard>=2.8.0
"""

TEMPLATES = {
    "basic": BASIC_TEMPLATE,
    "web": WEB_TEMPLATE,
    "data": DATA_TEMPLATE,
    "ml": ML_TEMPLATE,
}

class CondaWizard:
    """Main class for the Conda Environment Wizard"""
    
    def __init__(self, args: argparse.Namespace):
        """Initialize with command line arguments"""
        self.args = args
        
        # Configure UI settings
        self.use_colors = has_colorama and not args.no_color
        self.use_emojis = not args.no_emoji
        
        # Initialize state variables
        self.env_name = None
        self.conda_exe = args.conda_exe if args.conda_exe else "conda"
        self.python_version = None
        self.env_file = None
    
    def format_text(self, text: str, 
                   color: str = Fore.WHITE, 
                   style: str = Style.NORMAL, 
                   emoji: str = None,
                   indent: int = 0) -> str:
        """Format text with color, style, emoji and indentation"""
        # Apply styling conditionally based on preferences
        c_color = color if self.use_colors else ""
        c_style = style if self.use_colors else ""
        c_emoji = f"{emoji} " if emoji and self.use_emojis else ""
        c_indent = " " * indent
        
        return f"{c_style}{c_color}{c_indent}{c_emoji}{text}{Style.RESET_ALL if self.use_colors else ''}"
    
    def print(self, text: str, 
             color: str = Fore.WHITE, 
             style: str = Style.NORMAL, 
             emoji: str = None,
             indent: int = 0) -> None:
        """Print formatted text"""
        print(self.format_text(text, color, style, emoji, indent))
    
    def header(self, text: str, bg_color: str = Back.BLUE) -> None:
        """Print a formatted header"""
        if self.use_colors:
            print(f"\n{Fore.WHITE + bg_color + Style.BRIGHT}  {text}  {Style.RESET_ALL}\n")
        else:
            print(f"\n--- {text} ---\n")
    
    def input(self, prompt: str, 
             color: str = Fore.CYAN, 
             emoji: str = None,
             indent: int = 0) -> str:
        """Get input with formatted prompt"""
        formatted_prompt = self.format_text(prompt, color, Style.NORMAL, emoji, indent)
        return input(formatted_prompt)
    
    def progress(self, text: str, total: int = 10, seconds: float = 1.0) -> None:
        """Display a progress indicator"""
        if self.args.quiet:
            return
            
        self.print(f"{text}...", Fore.YELLOW, emoji=Emoji.GEAR)
        if seconds < 0.01:  # Skip animation for very short operations
            return
            
        bar_width = 40
        for i in range(total + 1):
            progress = i / total
            bar = "█" * int(bar_width * progress)
            spaces = " " * (bar_width - len(bar))
            
            # Use carriage return to update in place
            if self.use_colors:
                sys.stdout.write(f"\r{Fore.YELLOW}  {bar}{spaces} {int(progress * 100):3d}%")
            else:
                sys.stdout.write(f"\r  {bar}{spaces} {int(progress * 100):3d}%")
            sys.stdout.flush()
            
            time.sleep(seconds / total)
        
        sys.stdout.write("\r" + " " * (bar_width + 10) + "\r")
        sys.stdout.flush()
    
    def check_conda_installation(self) -> bool:
        """Check if conda is installed and available"""
        try:
            process = subprocess.run(
                [self.conda_exe, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                version = process.stdout.strip()
                self.print(f"Conda is installed: {version}", Fore.GREEN, emoji=Emoji.CHECK, indent=2)
                return True
            else:
                self.print("ERROR: Conda is not functioning correctly", Fore.RED, emoji=Emoji.ERROR, indent=2)
                self.print(f"Error message: {process.stderr}", Fore.RED, indent=4)
                return False
        except FileNotFoundError:
            self.print(f"ERROR: Conda executable '{self.conda_exe}' not found", Fore.RED, emoji=Emoji.ERROR, indent=2)
            self.print("Make sure conda is installed and in your PATH", Fore.YELLOW, indent=4)
            self.print("Or specify the conda executable with --conda-exe", Fore.YELLOW, indent=4)
            return False
    
    def get_env_name(self) -> str:
        """Determine the conda environment name and check if it exists"""
        # If name is provided as arg, use it
        if self.args.name:
            env_name = self.args.name
        # Otherwise prompt for name
        else:
            env_name = self.input("Enter conda environment name (e.g., my_env): ", emoji=Emoji.FOLDER)
            # Ensure name is provided
            while not env_name.strip():
                self.print("Environment name cannot be empty. Please provide a name.",
                         Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
                env_name = self.input("Enter conda environment name (e.g., my_env): ", emoji=Emoji.FOLDER)
        
        # Check if environment already exists
        env_exists = self._check_env_exists(env_name)
        
        if env_exists:
            # Auto delete if specified
            if self.args.force:
                self.print(f"Environment '{env_name}' already exists, deleting (--force)", 
                         Fore.YELLOW, emoji=Emoji.DELETE, indent=2)
                self._delete_environment(env_name)
            # Otherwise prompt for action
            else:
                self.print(f"Conda environment '{env_name}' already exists.", 
                         Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
                delete_existing = self.input(f"Delete existing '{env_name}' and create new? (y/N): ",
                                           emoji=Emoji.QUESTION, indent=4)
                
                if delete_existing.lower() == 'y':
                    self._delete_environment(env_name)
                else:
                    self.print("Please choose a different name.", Fore.YELLOW, indent=4)
                    return self.get_env_name()  # Recursively prompt for new name
        
        self.env_name = env_name
        return env_name
    
    def _check_env_exists(self, env_name: str) -> bool:
        """Check if a conda environment with the given name exists"""
        try:
            process = subprocess.run(
                [self.conda_exe, "env", "list", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            env_data = json.loads(process.stdout)
            env_names = [os.path.basename(env) for env in env_data.get("envs", [])]
            
            return env_name in env_names
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # Fall back to checking with env list if json format fails
            try:
                process = subprocess.run(
                    [self.conda_exe, "env", "list"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                
                env_lines = process.stdout.strip().splitlines()[2:]  # Skip header lines
                env_names = [line.split()[0] for line in env_lines]
                
                return env_name in env_names
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.print("Warning: Could not check for existing environments", 
                         Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
                return False
    
    def _delete_environment(self, env_name: str) -> bool:
        """Delete a conda environment"""
        self.print(f"Removing conda environment '{env_name}'...", Fore.YELLOW, emoji=Emoji.DELETE, indent=2)
        
        try:
            self.progress(f"Deleting environment {env_name}", total=5, seconds=1.0)
            
            process = subprocess.run(
                [self.conda_exe, "env", "remove", "--name", env_name, "--yes"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            self.print(f"Successfully deleted environment '{env_name}'", 
                     Fore.GREEN, emoji=Emoji.CHECK, indent=4)
            return True
        except subprocess.CalledProcessError as e:
            self.print(f"ERROR: Could not delete environment '{env_name}'", 
                     Fore.RED, emoji=Emoji.ERROR, indent=4)
            self.print(f"{e.stderr}", Fore.RED, indent=6)
            return False
    
    def get_available_python_versions(self) -> List[Dict[str, str]]:
        """Get available Python versions from conda"""
        self.print("Searching for available Python versions in conda...", 
                 Fore.CYAN, emoji=Emoji.SEARCH)
        
        try:
            process = subprocess.run(
                [self.conda_exe, "search", "python", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            python_data = json.loads(process.stdout)
            versions = []
            
            # Extract version info from the json response
            if "python" in python_data:
                for pkg in python_data["python"]:
                    if "version" in pkg:
                        version = pkg["version"]
                        # Only include standard Python versions (e.g., 3.9.7, not 3.9.7h)
                        if version[0].isdigit() and all(c.isdigit() or c == '.' for c in version):
                            versions.append({
                                "version": version,
                                "name": f"Python {version}",
                                "specifier": version
                            })
            
            # Remove duplicates and sort by version (newest first)
            unique_versions = {}
            for version in versions:
                # Get major.minor version (e.g., 3.9 from 3.9.7)
                major_minor = '.'.join(version["version"].split('.')[:2])
                # Keep the latest patch version for each major.minor
                if major_minor not in unique_versions or version["version"] > unique_versions[major_minor]["version"]:
                    unique_versions[major_minor] = version
            
            # Sort by version numbers
            sorted_versions = sorted(
                unique_versions.values(),
                key=lambda x: [int(v) for v in x["version"].split('.')],
                reverse=True
            )
            
            return sorted_versions
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
            self.print(f"Warning: Error getting Python versions from conda: {e}", 
                     Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
            # Provide fallback versions if conda search fails
            return [
                {"version": "3.11", "name": "Python 3.11", "specifier": "3.11"},
                {"version": "3.10", "name": "Python 3.10", "specifier": "3.10"},
                {"version": "3.9", "name": "Python 3.9", "specifier": "3.9"},
                {"version": "3.8", "name": "Python 3.8", "specifier": "3.8"}
            ]
    
    def get_python_version(self) -> str:
        """Select Python version for the conda environment"""
        # Check if version specified in args
        if self.args.python:
            self.print(f"Using specified Python version: {self.args.python}", 
                     Fore.GREEN, emoji=Emoji.PYTHON, indent=2)
            self.python_version = self.args.python
            return self.args.python
        
        # Check if non-interactive mode
        if self.args.non_interactive:
            # Use latest Python version
            self.python_version = "3.11"  # Default to a recent version
            self.print(f"Using default Python version: {self.python_version} (non-interactive mode)", 
                     Fore.GREEN, emoji=Emoji.PYTHON, indent=2)
            return self.python_version
        
        # Interactive mode - ask for version
        version_choice = self.input("Specify Python version? (y/N, or 'list' for versions): ", 
                                  emoji=Emoji.PYTHON)
        
        if version_choice.lower() == 'y':
            version = self.input("Enter Python version for conda (e.g., 3.9): ", indent=2)
            self.python_version = version
            return version
        elif version_choice.lower() == 'list':
            versions = self.get_available_python_versions()
            
            if not versions:
                self.print("No Python versions found. Using default Python.", 
                         Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
                self.python_version = "3.10"  # Fallback version
                return self.python_version
            
            # Display available versions
            self.print("\nAvailable Python versions:", Fore.GREEN, emoji=Emoji.STAR, indent=2)
            for i, version_info in enumerate(versions):
                self.print(f"{i+1:>2}. {version_info['name']}", Fore.CYAN, indent=4)
            
            # Let user choose
            while True:
                try:
                    choice = self.input(f"Choose version number (1-{len(versions)}, or Enter for latest): ", 
                                      indent=2)
                    
                    if not choice.strip():
                        # Use latest (first) version
                        self.python_version = versions[0]["version"]
                        self.print(f"Using latest Python: {self.python_version}", 
                                 Fore.GREEN, emoji=Emoji.CHECK, indent=4)
                        return self.python_version
                    
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(versions):
                        self.python_version = versions[choice_idx]["version"]
                        self.print(f"Using Python {self.python_version}", 
                                 Fore.GREEN, emoji=Emoji.CHECK, indent=4)
                        return self.python_version
                    else:
                        self.print(f"Invalid choice. Please enter 1-{len(versions)}", 
                                 Fore.YELLOW, emoji=Emoji.WARNING, indent=4)
                except ValueError:
                    self.print("Please enter a number", 
                             Fore.YELLOW, emoji=Emoji.WARNING, indent=4)
        
        # Default to a recent stable Python version
        self.python_version = "3.10"
        self.print(f"Using default Python version: {self.python_version}", 
                 Fore.GREEN, emoji=Emoji.PYTHON, indent=2)
        return self.python_version
    
    def create_environment(self) -> bool:
        """Create the conda environment"""
        env_name = self.env_name
        python_version = self.python_version
        
        self.print(f"\nCreating conda environment '{env_name}' with Python {python_version}...", 
                 Fore.CYAN, emoji=Emoji.WRENCH)
        
        # Prepare conda create command
        create_cmd = [self.conda_exe, "create", "--name", env_name, f"python={python_version}", "-y"]
        
        # Add extra flags if specified
        if self.args.strict_channel_priority:
            create_cmd.insert(2, "--strict-channel-priority")
        
        # Add channels if specified
        if self.args.channels:
            channels = self.args.channels.split(",")
            for channel in channels:
                create_cmd.extend(["-c", channel.strip()])
        
        try:
            self.progress("Creating conda environment", total=10, seconds=2.0)
            
            process = subprocess.run(
                create_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                self.print("ERROR: Failed to create conda environment", 
                         Fore.RED, emoji=Emoji.ERROR, indent=2)
                self.print(f"{process.stderr}", Fore.RED, indent=4)
                return False
            
            self.print(f"Conda environment '{env_name}' created successfully!", 
                     Fore.GREEN, emoji=Emoji.PARTY)
            return True
            
        except Exception as e:
            self.print("ERROR: Failed to create conda environment", 
                     Fore.RED, emoji=Emoji.ERROR, indent=2)
            self.print(f"{e}", Fore.RED, indent=4)
            return False
    
    def create_environment_file(self) -> None:
        """Create environment.yml file"""
        if self.args.no_env_file:
            return
            
        env_name = self.env_name
        python_version = self.python_version
        
        # Create directory for the environment file if it doesn't exist
        os.makedirs(env_name, exist_ok=True)
        env_file_path = os.path.join(env_name, "environment.yml")
        
        # Determine which template to use
        if self.args.template:
            template_name = self.args.template.lower()
            if template_name in TEMPLATES:
                content = TEMPLATES[template_name].format(env_name=env_name, python_version=python_version)
                self.print(f"Using '{template_name}' template for environment.yml", 
                         Fore.GREEN, emoji=Emoji.STAR, indent=2)
            else:
                self.print(f"Template '{template_name}' not found, using basic template", 
                         Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
                content = TEMPLATES["basic"].format(env_name=env_name, python_version=python_version)
        else:
            # Prompt for template choice if not quiet or non-interactive
            if not self.args.quiet and not self.args.non_interactive:
                self.print("\nSelect an environment.yml template:", 
                         Fore.CYAN, emoji=Emoji.NOTE, indent=2)
                self.print("1. Basic/minimal (default)", Fore.WHITE, indent=4)
                self.print("2. Web development", Fore.WHITE, indent=4)
                self.print("3. Data science", Fore.WHITE, indent=4)
                self.print("4. Machine learning", Fore.WHITE, indent=4)
                
                choice = self.input("Template choice [1-4]: ", indent=2)
                
                if choice == "2":
                    content = TEMPLATES["web"].format(env_name=env_name, python_version=python_version)
                    self.print("Using 'web' template", Fore.GREEN, emoji=Emoji.CHECK, indent=4)
                elif choice == "3":
                    content = TEMPLATES["data"].format(env_name=env_name, python_version=python_version)
                    self.print("Using 'data' template", Fore.GREEN, emoji=Emoji.CHECK, indent=4)
                elif choice == "4":
                    content = TEMPLATES["ml"].format(env_name=env_name, python_version=python_version)
                    self.print("Using 'ml' template", Fore.GREEN, emoji=Emoji.CHECK, indent=4)
                else:
                    content = TEMPLATES["basic"].format(env_name=env_name, python_version=python_version)
                    self.print("Using 'basic' template", Fore.GREEN, emoji=Emoji.CHECK, indent=4)
            else:
                content = TEMPLATES["basic"].format(env_name=env_name, python_version=python_version)
        
        try:
            with open(env_file_path, 'w') as f:
                f.write(content)
            self.print(f"Created environment.yml file", 
                     Fore.GREEN, emoji=Emoji.NOTE, indent=2)
            self.env_file = env_file_path
        except Exception as e:
            self.print(f"Warning: Could not create environment.yml file", 
                     Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
            self.print(f"{e}", Fore.YELLOW, indent=4)
    
    def install_packages(self) -> None:
        """Install packages from environment.yml"""
        if self.args.no_install or not self.env_file:
            return
            
        # Check if user wants to install
        if not self.args.install and not self.args.non_interactive:
            install = self.input("Install packages from environment.yml? [y/N]: ", 
                               emoji=Emoji.PACKAGE)
            if install.lower() != 'y':
                return
        
        env_name = self.env_name
        
        self.print("Installing packages from environment.yml...", 
                 Fore.CYAN, emoji=Emoji.PACKAGE)
        
        try:
            self.progress("Installing packages", total=10, seconds=2.0)
            
            # First update the environment using the environment.yml file
            process = subprocess.run(
                [self.conda_exe, "env", "update", "--name", env_name, "--file", self.env_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                self.print("Warning: Failed to install some packages", 
                         Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
                self.print(f"{process.stderr}", Fore.YELLOW, indent=4)
                return
            
            self.print("Packages installed successfully", 
                     Fore.GREEN, emoji=Emoji.CHECK, indent=2)
            
        except Exception as e:
            self.print("Warning: Error during package installation", 
                     Fore.YELLOW, emoji=Emoji.WARNING, indent=2)
            self.print(f"{e}", Fore.YELLOW, indent=4)
    
    def print_activation_instructions(self) -> None:
        """Print instructions for activating and using the conda environment"""
        env_name = self.env_name
        
        self.print("\nConda Environment Activation Instructions:", 
                 Fore.CYAN, emoji=Emoji.ROCKET)
        
        # Activation command (same for all platforms with conda)
        self.print("To activate this environment:", Fore.BLUE, indent=2)
        self.print(f"conda activate {env_name}", Fore.WHITE, indent=4)
        
        # Deactivation
        self.print("\nTo deactivate:", Fore.RED, indent=2)
        self.print("conda deactivate", Fore.WHITE, indent=4)
        
        # Managing packages
        self.print("\nPackage Management:", Fore.GREEN, emoji=Emoji.PACKAGE, indent=2)
        self.print("Install conda package: conda install -n %s <package-name>" % env_name, Fore.WHITE, indent=4)
        self.print("Install pip package: conda activate %s && pip install <package-name>" % env_name, Fore.WHITE, indent=4)
        self.print("List packages: conda list -n %s" % env_name, Fore.WHITE, indent=4)
        
        # Environment file usage
        self.print("\nEnvironment File Management:", Fore.MAGENTA, emoji=Emoji.SAVE, indent=2)
        self.print("Export environment: conda env export -n %s > environment.yml" % env_name, Fore.WHITE, indent=4)
        self.print("Update from file: conda env update -n %s -f environment.yml" % env_name, Fore.WHITE, indent=4)
    
    def run(self) -> None:
        """Main execution flow"""
        try:
            # Display banner
            self.header(f"🪅 Conda Environment Wizard v{__version__} 🪅")
            
            # Check conda installation
            if not self.check_conda_installation():
                sys.exit(1)
            
            # Get environment name
            env_name = self.get_env_name()
            
            # Get Python version
            python_version = self.get_python_version()
            
            # Create conda environment
            if not self.create_environment():
                sys.exit(1)
            
            # Create environment.yml file
            self.create_environment_file()
            
            # Install packages if requested
            self.install_packages()
            
            # Print activation instructions
            self.print_activation_instructions()
            
            # Final success message
            self.header(f"{Emoji.PARTY} Conda environment '{env_name}' setup complete! {Emoji.PARTY}")
            
        except KeyboardInterrupt:
            self.print("\nOperation canceled by user", Fore.YELLOW, emoji=Emoji.EXIT)
            sys.exit(0)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="CondaWiz: Conda Environment Wizard",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Basic options
    parser.add_argument("-n", "--name", 
                      help="Name of conda environment to create")
    parser.add_argument("-p", "--python", 
                      help="Python version to use (e.g., 3.9)")
    parser.add_argument("--conda-exe", 
                      help="Path to conda executable")
    
    # Environment options
    parser.add_argument("-c", "--channels", 
                      help="Comma-separated list of conda channels (e.g., conda-forge,bioconda)")
    parser.add_argument("--strict-channel-priority", action="store_true",
                      help="Enable strict channel priority")
    parser.add_argument("--no-env-file", action="store_true",
                      help="Don't create environment.yml file")
    
    # Package installation options
    parser.add_argument("--template", choices=["basic", "web", "data", "ml"],
                      help="Environment template to use")
    parser.add_argument("--install", action="store_true",
                      help="Install packages from environment.yml")
    parser.add_argument("--no-install", action="store_true",
                      help="Don't install packages from environment.yml")
    
    # Behavioral options
    parser.add_argument("-f", "--force", action="store_true",
                      help="Force creation (delete existing environment)")
    parser.add_argument("--non-interactive", action="store_true",
                      help="Non-interactive mode (use defaults)")
    
    # UI options
    parser.add_argument("-q", "--quiet", action="store_true",
                      help="Minimal output")
    parser.add_argument("--no-color", action="store_true",
                      help="Disable colored output")
    parser.add_argument("--no-emoji", action="store_true",
                      help="Disable emoji output")
    
    # Version
    parser.add_argument("--version", action="version",
                      version=f"CondaWiz v{__version__}")
    
    return parser.parse_args()


def main() -> None:
    """Main entry point"""
    # Parse arguments
    args = parse_args()
    
    # Create and run wizard
    wizard = CondaWizard(args)
    wizard.run()


if __name__ == "__main__":
    main()