#!/bin/bash

# --- Configuration ---
outputFile="project-structure.txt"
# Get the name of this script file to exclude it from the output
scriptName=$(basename "$0")

# Statistics tracking
total_files=0
total_dirs=0
total_size=0

# Function to format bytes to human-readable size
format_size() {
    local size=$1
    local units=("B" "KB" "MB" "GB" "TB")
    local unit_index=0
    local size_float=$size
    
    while (( $(echo "$size_float >= 1024" | bc -l) )) && (( unit_index < 4 )); do
        size_float=$(echo "scale=2; $size_float / 1024" | bc)
        ((unit_index++))
    done
    
    printf "%.2f %s" "$size_float" "${units[$unit_index]}"
}

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
            ((total_dirs++))
            echo "${parentPrefix}${connector}${itemName}/"
            # Recursive call for the subdirectory
            process_directory "$fullPath" "${parentPrefix}${childPrefix}"
        else
            ((total_files++))
            local file_size=$(stat -c%s "$fullPath" 2>/dev/null || stat -f%z "$fullPath" 2>/dev/null || echo 0)
            total_size=$((total_size + file_size))
            echo "${parentPrefix}${connector}${itemName}"
        fi
    done
}

# --- Step 2: Append the rest of the structure to a temp file ---
tempFile="${outputFile}.tmp"

(
    # Print the root directory name
    echo "$(basename "$PWD")/"
    
    # Start the recursive processing from the current directory
    process_directory "." ""

) > "$tempFile"

# --- Step 3: Write final output with stats at top ---
(
    echo "# Project Directory Structure & Files"
    echo ""
    echo "# Statistics"
    echo "Total Directories: $total_dirs"
    echo "Total Files: $total_files"
    echo "Total Size: $(format_size $total_size)"
    echo ""
    cat "$tempFile"
) > "$outputFile"

# Cleanup temp file
rm "$tempFile"

echo
echo "Project structure successfully saved to $outputFile"
echo "Total Directories: $total_dirs"
echo "Total Files: $total_files"
echo "Total Size: $(format_size $total_size)"