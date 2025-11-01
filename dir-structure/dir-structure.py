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

# Statistics tracking
stats = {
    'total_files': 0,
    'total_dirs': 0,
    'total_size': 0
}

def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

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
        # Filter out exclusions and hidden files
        items = [item for item in items 
                 if item not in EXCLUSIONS 
                 and not item.startswith('.') 
                 and not item.endswith('.tmp')]
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
            stats['total_dirs'] += 1
            file_handle.write(f"{parent_prefix}{connector}{item_name}/\n")
            # Recursive call for the subdirectory
            process_directory(full_path, parent_prefix + child_prefix, file_handle)
        else:
            stats['total_files'] += 1
            try:
                file_size = os.path.getsize(full_path)
                stats['total_size'] += file_size
            except OSError:
                pass  # Skip if can't get file size
            file_handle.write(f"{parent_prefix}{connector}{item_name}\n")

def main():
    """Main function to generate the project structure file."""
    print("Generating project structure...")
    print(f"Script name: {SCRIPT_NAME}")
    print(f"Current directory: {os.getcwd()}")

    try:
        # Create a temporary file for the tree structure
        temp_file = OUTPUT_FILE + ".tmp"
        
        # Write tree to temp file
        with open(temp_file, 'w', encoding='utf-8') as f:
            # Get and write the root directory name
            root_dir_name = os.path.basename(os.getcwd())
            f.write(f"{root_dir_name}/\n")
            
            # Start the recursive processing from the current directory
            process_directory(".", "", file_handle=f)
        
        print(f"Statistics after processing:")
        print(f"  Directories: {stats['total_dirs']}")
        print(f"  Files: {stats['total_files']}")
        print(f"  Size: {stats['total_size']}")
        
        # Read the temp file content
        with open(temp_file, 'r', encoding='utf-8') as f:
            tree_content = f.read()
        
        # Write final output with statistics at the top
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Project Directory Structure & Files\n\n")
            f.write("# Statistics\n")
            f.write(f"Total Directories: {stats['total_dirs']}\n")
            f.write(f"Total Files: {stats['total_files']}\n")
            f.write(f"Total Size: {format_size(stats['total_size'])}\n\n")
            f.write(tree_content)
        
        # Clean up temp file
        os.remove(temp_file)

        print(f"\nProject structure successfully saved to {OUTPUT_FILE}")
        print(f"Total Directories: {stats['total_dirs']}")
        print(f"Total Files: {stats['total_files']}")
        print(f"Total Size: {format_size(stats['total_size'])}")

    except IOError as e:
        print(f"Error writing to file {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    main()