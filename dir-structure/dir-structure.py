import os
import sys

# --- Configuration ---
OUTPUT_FILE = "project-structure.txt"
# Get the name of this script file to exclude it from the output
SCRIPT_NAME = os.path.basename(sys.argv[0])

# Files and directories to exclude
EXCLUSIONS = {
    SCRIPT_NAME,
    OUTPUT_FILE,
    '__pycache__',
    '.git',
    '.venv',
    'venv',
    'node_modules',
    '.DS_Store',
    '.env',
    '.gitignore',
    'thumbs.db'
}

def process_directory(current_dir, parent_prefix, file_handle):
    """
    Recursively processes a directory to build a tree structure.

    Args:
        current_dir (str): The path of the directory to process.
        parent_prefix (str): The prefix string for indentation and tree lines.
        file_handle (file): The file object to write the output to.
    """
    # Get a list of items in the directory, excluding specified files/folders
    try:
        items = sorted(os.listdir(current_dir))
        items = [item for item in items if item not in EXCLUSIONS and not item.startswith('.')]
    except OSError as e:
        print(f"Error reading directory {current_dir}: {e}")
        return

    # Separate items into files and directories
    files = [item for item in items if not os.path.isdir(os.path.join(current_dir, item))]
    dirs = [item for item in items if os.path.isdir(os.path.join(current_dir, item))]

    # Combine lists to process files first, then directories
    sorted_items = files + dirs
    total_items = len(sorted_items)

    for i, item_name in enumerate(sorted_items):
        full_path = os.path.join(current_dir, item_name)
        is_last = (i == total_items - 1)

        # Determine the connector and child prefix for the tree structure
        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "

        if os.path.isdir(full_path):
            file_handle.write(f"{parent_prefix}{connector}{item_name}/\n")
            # Recursive call for the subdirectory
            process_directory(full_path, parent_prefix + child_prefix, file_handle)
        else:
            file_handle.write(f"{parent_prefix}{connector}{item_name}\n")

def main():
    """Main function to generate the project structure file."""
    print("Generating project structure...")

    try:
        # Create the output file and write the header
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Project Directory Structure & Files\n")

            # Get and write the root directory name
            root_dir_name = os.path.basename(os.getcwd())
            f.write(f"{root_dir_name}/\n")
            
            # Start the recursive processing from the current directory
            process_directory(".", "", file_handle=f)

        print(f"\nProject structure successfully saved to {OUTPUT_FILE}")

    except IOError as e:
        print(f"Error writing to file {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    main()