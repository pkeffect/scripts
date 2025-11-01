#!/bin/bash

# --- Configuration ---
outputFile="project-structure.txt"
# Get the name of this script file to exclude it from the output
scriptName=$(basename "$0")

echo "Generating project structure..."

# --- Step 1: Create the output file and write the header ---
echo "# Project Directory Structure & Files" > "$outputFile"

# --- Recursive function to process a directory ---
process_directory() {
    local currentDir="$1"
    local parentPrefix="$2"
    
    # Read all non-hidden items into an array, sorted.
    local all_items=()
    while IFS= read -r item; do
        all_items+=("$item")
    done < <(find "$currentDir" -mindepth 1 -maxdepth 1 -not -path '*/.*' -printf "%f\n" | sort)

    # Separate items into files and directories
    local files=()
    local dirs=()
    for itemName in "${all_items[@]}"; do
        # Exclude the script file, output file, and common directories
        if [[ "$itemName" == "$scriptName" || "$itemName" == "$outputFile" || \
              "$itemName" == "node_modules" || "$itemName" == "__pycache__" || \
              "$itemName" == ".venv" || "$itemName" == "venv" ]]; then
            continue
        fi

        if [[ -d "$currentDir/$itemName" ]]; then
            dirs+=("$itemName")
        else
            files+=("$itemName")
        fi
    done

    # Combine lists to process files first, then directories
    local sorted_items=("${files[@]}" "${dirs[@]}")
    local totalItems=${#sorted_items[@]}
    local currentItem=0

    for itemName in "${sorted_items[@]}"; do
        ((currentItem++))
        local fullPath="$currentDir/$itemName"

        # Determine the connector and child prefix based on whether it's the last item
        local connector="├── "
        local childPrefix="│   "
        if (( currentItem == totalItems )); then
            connector="└── "
            childPrefix="    "
        fi

        if [[ -d "$fullPath" ]]; then
            echo "${parentPrefix}${connector}${itemName}/"
            # Recursive call for the subdirectory
            process_directory "$fullPath" "${parentPrefix}${childPrefix}"
        else
            echo "${parentPrefix}${connector}${itemName}"
        fi
    done
}

# --- Step 2: Append the rest of the structure to the file ---
(
    # Print the root directory name
    echo "$(basename "$PWD")/"
    
    # Start the recursive processing from the current directory
    process_directory "." ""

) >> "$outputFile"

echo
echo "Project structure successfully saved to $outputFile"