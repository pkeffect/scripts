# 🧙‍♂️ Python Environment Wizards

> Beautiful, feature-rich tools for creating and managing Python environments across different package managers

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/yourusername/python-env-wizards)

## 🌟 Overview

This collection provides three powerful wizards for setting up Python development environments, each tailored to different package management systems:

- **🪅 CondaWiz** - For Conda environments
- **🚀 uvWiz** - For uv virtual environments  
- **🐍 VEnvWiz** - For standard Python virtual environments

All wizards feature beautiful colored interfaces, emoji support, cross-platform compatibility, and intelligent defaults to make environment setup effortless.

## 🚀 Quick Start

### Installation

No installation required! Simply download the scripts and run them directly:

```bash
# For Conda environments
python setup_conda.py

# For uv environments  
python setup_uv.py

# For standard venv environments
python setup_venv.py
```

### Basic Usage

```bash
# Interactive mode (recommended)
python setup_conda.py

# Quick setup with defaults
python setup_conda.py -n myproject --python 3.11 --template data --force

# Non-interactive mode
python setup_uv.py --non-interactive -n myapp --template web
```

## 🛠️ Features

### ✨ Common Features (All Wizards)

- 🎨 **Beautiful CLI Interface** - Colored output with emoji support
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux
- 📝 **Template System** - Pre-configured templates for different project types
- ⚡ **Progress Indicators** - Visual feedback during operations
- 🔧 **Interactive & Non-Interactive Modes** - Flexible usage options
- 🛡️ **Error Handling** - Robust error detection and recovery
- 📚 **Comprehensive Help** - Detailed activation and usage instructions

### 🪅 CondaWiz Specific Features

- 🔍 **Python Version Detection** - Automatically finds available Python versions from conda
- 📄 **environment.yml Generation** - Creates templated environment files
- 🔗 **Channel Management** - Support for custom conda channels
- 📦 **Package Installation** - Direct installation from environment.yml
- 🎯 **Strict Channel Priority** - Enhanced dependency resolution

### 🚀 uvWiz Specific Features

- ⚡ **Lightning Fast** - Leverages uv's speed for package operations
- 🖥️ **VS Code Integration** - Automatic workspace configuration
- 📁 **Git Integration** - Automatic .gitignore creation
- 🔧 **Advanced pip Features** - Dependency resolution and lockfiles
- 🎛️ **Smart Caching** - Utilizes uv's intelligent caching system

### 🐍 VEnvWiz Specific Features

- 🌈 **Enhanced Color Schemes** - Optimized for light and dark terminals
- 🔗 **Symlink Support** - Efficient environment creation on Unix systems
- 🎨 **Better Formatting** - Improved text alignment and spacing
- 🛠️ **IDE Integration Tips** - Comprehensive setup guidance for popular IDEs

## 📋 Available Templates

### Basic Templates (All Wizards)
- **basic** - Minimal setup with testing and linting tools
- **web** - Web development with Flask, requests, gunicorn
- **data** - Data science with numpy, pandas, matplotlib, jupyter

### Additional Templates
- **ml** (CondaWiz) - Machine learning with scikit-learn, tensorflow, pytorch
- **ai** (uvWiz) - AI/ML development with deep learning frameworks

## 🎯 Command Line Options

### 🪅 CondaWiz Options

```bash
# Basic options
-n, --name              Environment name
-p, --python            Python version (e.g., 3.11)
--conda-exe             Path to conda executable

# Environment options  
-c, --channels          Comma-separated conda channels
--strict-channel-priority   Enable strict channel priority
--no-env-file           Skip environment.yml creation

# Package options
--template              Template choice (basic|web|data|ml)
--install               Install packages from environment.yml
--no-install            Skip package installation

# Behavioral options
-f, --force             Delete existing environment
--non-interactive       Use defaults, no prompts

# UI options
-q, --quiet             Minimal output
--no-color              Disable colors
--no-emoji              Disable emojis
```

### 🚀 uvWiz Options

```bash
# Basic options
-n, --name              Environment name  
-p, --python            Python path/command
--uv-exe                Path to uv executable

# Environment options
--system-site-packages  Access to system packages

# Requirements options
--no-requirements       Skip requirements.txt creation
--template              Template choice (basic|web|data|ai)
--pip-install           Install from requirements.txt
--no-pip-install        Skip package installation

# IDE integration
--vscode                Create VS Code settings
--gitignore             Create .gitignore file
--no-uv-settings        Skip uv-specific VS Code settings

# Behavioral options  
-f, --force             Delete existing environment
--non-interactive       Use defaults, no prompts

# UI options
-q, --quiet             Minimal output
--no-color              Disable colors  
--no-emoji              Disable emojis
```

### 🐍 VEnvWiz Options

```bash
# Basic options
-n, --name              Environment name
-p, --python            Python executable path/command

# Venv options
-s, --system-site-packages  Access to system packages
--symlinks              Use symlinks (Unix only)
--no-pip                Skip pip installation

# Requirements options
--no-requirements       Skip requirements.txt creation
--template              Template choice (basic|web|data)
--pip-install           Install from requirements.txt
--no-pip-install        Skip package installation

# Behavioral options
-f, --force             Delete existing directory
--non-interactive       Use defaults, no prompts

# UI options
-q, --quiet             Minimal output
--no-color              Disable colors
--no-emoji              Disable emojis  
--light-bg              Optimize for light terminals
```

## 💡 Usage Examples

### 🪅 CondaWiz Examples

```bash
# Interactive setup
python setup_conda.py

# Data science environment with Python 3.11
python setup_conda.py -n datascience --python 3.11 --template data --install

# ML environment with custom channels
python setup_conda.py -n ml_project --template ml --channels conda-forge,pytorch

# Force recreate existing environment
python setup_conda.py -n myenv --force --non-interactive
```

### 🚀 uvWiz Examples

```bash
# Web development setup with VS Code integration
python setup_uv.py -n webapp --template web --vscode --gitignore

# AI project with specific Python version
python setup_uv.py -n aiproject --python python3.11 --template ai --pip-install

# Quick minimal setup
python setup_uv.py -n quicktest --template basic --non-interactive
```

### 🐍 VEnvWiz Examples  

```bash
# Interactive setup with Python version selection
python setup_venv.py

# Data science environment with package installation
python setup_venv.py -n datasci --template data --pip-install

# Minimal environment with system packages access
python setup_venv.py -n minimal --system-site-packages --no-requirements

# Light terminal optimized
python setup_venv.py -n myproject --light-bg
```

## 🔧 Requirements

### System Requirements
- Python 3.8 or higher
- Respective package managers installed:
  - **Conda** (Anaconda/Miniconda) for CondaWiz
  - **uv** for uvWiz
  - **venv** (included with Python) for VEnvWiz

### Optional Dependencies
- `colorama` - For enhanced cross-platform color support (auto-detected)

### Installing Dependencies

```bash
# For enhanced colors (optional)
pip install colorama

# For conda environments
# Install Anaconda or Miniconda from https://conda.io

# For uv environments  
pip install uv

# For venv environments
# No additional installation needed (venv is built-in)
```

## 🎨 Customization

### Disabling Visual Features

```bash
# Minimal output
python setup_conda.py --quiet --no-color --no-emoji

# Light terminal backgrounds
python setup_venv.py --light-bg --no-emoji
```

### Environment Variables

The wizards respect standard environment variables:
- `CONDA_EXE` - Custom conda executable path
- `PYTHON` - Default Python executable
- `NO_COLOR` - Disable colors when set

## 🐛 Troubleshooting

### Common Issues

**🔍 "Command not found" errors:**
```bash
# Specify full path to executable
python setup_conda.py --conda-exe /path/to/conda
python setup_uv.py --uv-exe /path/to/uv
```

**📁 Permission errors:**
```bash
# Ensure you have write permissions in the current directory
# On Unix systems, check with: ls -la
```

**🐍 Python version issues:**
```bash
# List available Python versions
python setup_venv.py    # Then choose 'list' option
python setup_uv.py      # Then choose 'list' option
```

**🎨 Color/emoji display issues:**
```bash
# Disable problematic features
python setup_conda.py --no-color --no-emoji
```

### Getting Help

Each wizard provides comprehensive help:

```bash
python setup_conda.py --help
python setup_uv.py --help  
python setup_venv.py --help
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🐛 **Bug Reports** - Open an issue with details
2. 💡 **Feature Requests** - Suggest improvements
3. 🔧 **Code Contributions** - Submit pull requests
4. 📚 **Documentation** - Improve docs and examples

### Development Setup

```bash
git clone https://github.com/yourusername/python-env-wizards.git
cd python-env-wizards

# Test the wizards
python setup_conda.py --help
python setup_uv.py --help
python setup_venv.py --help
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the Python community
- Inspired by the need for better environment management tools
- Thanks to the maintainers of conda, uv, and venv

## 📊 Project Status

- ✅ **CondaWiz** v2.0.0 - Stable
- ✅ **uvWiz** v2.0.0 - Stable  
- ✅ **VEnvWiz** v2.1.0 - Stable

---

**🎉 Happy Environment Building!** 🐍✨