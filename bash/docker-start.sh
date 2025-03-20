#!/bin/bash
#======================================================================
# Docker Compose Startup Helper
# 
# This script automatically finds and runs Docker Compose files with
# proper error handling and status reporting.
#
# Features:
# - Automatically detects common Docker Compose filenames
# - Provides clear visual feedback with emoji indicators
# - Handles errors gracefully with descriptive messages
# - Includes optional debugging capabilities
#======================================================================

#----------------------------------------------------------------------
# Configuration Options
#----------------------------------------------------------------------

# Enable debug mode to see every command executed (uncomment to enable)
# set -x

# Set error handling: exit on command errors and unbound variables
set -euo pipefail

# Color definitions for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#----------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------

# Function to print colored status messages
print_status() {
    local icon="$1"
    local message="$2"
    local color="$3"
    
    echo -e "${color}${icon} ${message}${NC}"
}

# Function to check Docker daemon status
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_status "❌" "Docker daemon is not running! Please start Docker first." "$RED"
        exit 3
    fi
}

# Function to check Docker Compose availability
check_docker_compose() {
    if ! docker compose version >/dev/null 2>&1; then
        print_status "❌" "Docker Compose is not available. Please install it first." "$RED"
        exit 4
    fi
}

#----------------------------------------------------------------------
# Main Script
#----------------------------------------------------------------------

# Display script header
print_status "🐳" "Docker Compose Startup Helper" "$BLUE"
echo "---------------------------------------"

# Check prerequisites
print_status "🔍" "Checking prerequisites..." "$YELLOW"
check_docker
check_docker_compose

# Array of Docker Compose filenames to check (in order of preference)
compose_files=("compose.yaml" "compose.yml" "docker-compose.yaml" "docker-compose.yml")

# Get current directory for reference
current_dir=$(pwd)
print_status "📂" "Searching for Docker Compose files in: $current_dir" "$YELLOW"

# Initialize variables
compose_file=""
found=false

# Loop through potential filenames and check existence
for file in "${compose_files[@]}"; do
    if [[ -f "$file" ]]; then
        compose_file="$file"
        print_status "✅" "Found: $compose_file" "$GREEN"
        found=true
        break
    else
        print_status "❌" "Not found: $file" "$RED"
    fi
done

# Check if a file was found, exit with error if not
if ! $found; then
    print_status "❌" "Error: No valid Docker Compose file found in $current_dir!" "$RED"
    echo
    print_status "💡" "Tip: Create one of these files: ${compose_files[*]}" "$YELLOW"
    exit 1
fi

# Run Docker Compose with error handling
print_status "🚀" "Starting services from $compose_file..." "$BLUE"
echo

# Try to start the services, capture exit code for error handling
if docker compose -f "$compose_file" up -d; then
    echo
    print_status "✅" "Services started successfully!" "$GREEN"
    
    # Display running containers for user convenience
    echo
    print_status "📋" "Currently running containers:" "$BLUE"
    docker compose -f "$compose_file" ps
else
    exit_code=$?
    echo
    print_status "❌" "Docker Compose failed with exit code: $exit_code" "$RED"
    print_status "🔍" "Possible issues:" "$YELLOW"
    echo "  - Check the syntax in $compose_file"
    echo "  - Ensure Docker daemon is running properly"
    echo "  - Verify network connectivity for image pulling"
    echo "  - Check for port conflicts with existing services"
    exit 2
fi

# Optional pause to view results (useful when running from GUI)
echo
read -p "Press Enter to exit..."