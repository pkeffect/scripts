import os
import sys
import shutil
import re
import glob
import fnmatch

# --- OS Specific: Enable ANSI Colors on Windows ---
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# --- Configuration ---
SCRIPT_NAME = os.path.basename(sys.argv[0])
SYSTEM_EXCLUDES = {
    SCRIPT_NAME, '__pycache__', '.git', '.venv', 'venv', 'node_modules',
    '.DS_Store', '.env', '.gitignore', 'thumbs.db', '.idea', '.vscode'
}

# --- Styling & UI ---
class Style:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'

def print_header(title):
    print(f"\n{Style.BOLD}{Style.MAGENTA}==={Style.RESET} {Style.BOLD}{title.upper()}{Style.RESET} {Style.BOLD}{Style.MAGENTA}==={Style.RESET}")

def print_step(text):
    print(f"\n{Style.BOLD}{Style.CYAN}→ {text}{Style.RESET}")

def log_action(action, path, details="", status="ok"):
    color = Style.GREEN
    if action == "DIR": color = Style.BLUE + Style.BOLD
    if action == "MOVE": color = Style.YELLOW
    if action == "SKIP": color = Style.DIM
    if action == "ERR": color = Style.RED
    if action == "REN": color = Style.MAGENTA

    icon_map = {
        "DIR": "[DIR ]", 
        "NEW": "[FILE]", 
        "MOVE": "[MOVE]", 
        "REN": "[REN ]",
        "SKIP": "[SKIP]", 
        "ERR": "[FAIL]"
    }
    icon = icon_map.get(action, "[INFO]")
    
    try:
        display_path = os.path.relpath(path)
    except ValueError:
        display_path = path

    prefix = f"{color}{icon}{Style.RESET}"
    if details:
        print(f" {prefix}  {display_path:<50} {Style.DIM}({details}){Style.RESET}")
    else:
        print(f" {prefix}  {display_path}")

# ==============================================================================
# --- PART 0: UTILITIES (Robustness Layer) ---
# ==============================================================================

def read_text_file(filepath):
    """
    Robust file reader. Handles BOM, fallback encodings, and binary detection.
    Returns: list of lines or None if binary/unreadable.
    """
    # 1. Check for binary (null bytes)
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk: return None 
    except Exception:
        return None

    # 2. Try encodings
    encodings = ['utf-8-sig', 'utf-8', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None

def resolve_collision(target_path):
    """
    If target exists, find a non-conflicting name: file.txt -> file_1.txt
    Returns: (new_path, was_renamed_bool)
    """
    if not os.path.exists(target_path):
        return target_path, False
    
    base, ext = os.path.splitext(target_path)
    counter = 1
    while True:
        new_path = f"{base}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path, True
        counter += 1

# ==============================================================================
# --- PART 1: DISCOVERY ---
# ==============================================================================

def is_likely_structure_file(filepath):
    if os.path.isdir(filepath): return False
    tree_markers = [r'├──', r'└──', r'\+--', r'\|--', r'\|\s\s', r'^\s*-\s']
    
    lines = read_text_file(filepath)
    if not lines: return False

    head = lines[:15]
    content = "".join(head)
    for marker in tree_markers:
        if re.search(marker, content, re.MULTILINE): return True
    if len([line for line in head if line.startswith(' ') or line.startswith('\t')]) > 3: return True
    return False

def find_structure_file():
    print_step("Scanning for structure file...")
    candidates = ['directory-structure.txt', 'dir-structure.txt', 'structure.txt', 'tree.txt']
    for c in candidates:
        if os.path.exists(c):
            print(f" {Style.GREEN}✓ Found:{Style.RESET} {c}")
            return c
            
    files = glob.glob("*.txt") + glob.glob("*.md")
    files = [f for f in files if f not in SYSTEM_EXCLUDES]
    for f in files:
        if is_likely_structure_file(f):
            print(f" {Style.GREEN}✓ Detected content in:{Style.RESET} {f}")
            return f
            
    print(f" {Style.RED}× No structure file found.{Style.RESET}")
    return None

# ==============================================================================
# --- PART 2: PARSING ---
# ==============================================================================

def sanitize_name(name):
    # Security: Remove Traversal and Invalid Chars
    if '..' in name: name = name.replace('..', '')
    name = re.sub(r'[<>:"|?*]', '', name)
    return name.strip()

def parse_line_content(line):
    line = line.split('#')[0].rstrip()
    if not line.strip(): return None, 0

    match = re.match(r'^([\s│├└─|+\-\\t]*)(.*)', line)
    if not match: return line.strip(), 0

    prefix = match.group(1)
    raw_name = match.group(2).strip()
    if not raw_name: return None, 0

    expanded_prefix = prefix.replace('\t', '    ')
    return raw_name, len(expanded_prefix)

def identify_nodes(lines):
    nodes = []
    for i, line in enumerate(lines):
        name, indent = parse_line_content(line)
        if not name: continue
        
        name = name.strip('*"`\'')
        name = name.lstrip('/\\') 
        name = sanitize_name(name)
        
        if not name: continue
        nodes.append({'name': name, 'indent': indent, 'is_dir': None})

    for i, node in enumerate(nodes):
        name = node['name']
        if name.endswith('/') or name.endswith('\\'):
            node['is_dir'] = True
            node['name'] = name.strip('/\\')
            continue
        if '.' in name and not name.startswith('.'):
            node['is_dir'] = False
            continue
        if i + 1 < len(nodes) and nodes[i+1]['indent'] > node['indent']:
            node['is_dir'] = True
            continue
        
        common_dirs = {'src', 'public', 'assets', 'components', 'bin', 'lib', 'tests', 'docs', 'config', 'dist', 'build', 'utils', 'styles'}
        node['is_dir'] = True if name.lower() in common_dirs else False
            
    return nodes

def build_tree_from_nodes(nodes):
    path_stack = [] 
    stats = {'dirs': 0, 'files': 0, 'moved': 0, 'skipped': 0}
    
    # Robust root detection (Case insensitive for Windows)
    root_dir_name = os.path.basename(os.getcwd())
    root_path = os.getcwd()

    print_step("Executing Build Plan")
    print(f"{Style.DIM}{'-'*70}{Style.RESET}")

    for i, node in enumerate(nodes):
        name = node['name']
        indent = node['indent']
        is_dir = node['is_dir']
        
        # --- ROOT WRAP CHECK ---
        if i == 0 and is_dir and name.lower() == root_dir_name.lower():
            path_stack.append((indent, root_path))
            log_action("SKIP", name, "Detected Root Wrapper - Mapping to CWD")
            continue

        while path_stack and path_stack[-1][0] >= indent:
            path_stack.pop()
            
        current_parent = path_stack[-1][1] if path_stack else root_path
        target_path = os.path.join(current_parent, name)
        
        if is_dir:
            path_stack.append((indent, target_path))
            try:
                if not os.path.exists(target_path):
                    log_action("DIR", target_path)
                    os.makedirs(target_path, exist_ok=True)
                    stats['dirs'] += 1
                else:
                    pass
            except OSError as e:
                 log_action("ERR", target_path, str(e))
        else:
            if os.path.exists(target_path):
                stats['skipped'] += 1
            elif os.path.exists(name) and os.path.isfile(name):
                # --- SMART MOVE ---
                final_path, renamed = resolve_collision(target_path)
                
                if renamed:
                    log_action("REN", final_path, f"Collision detected. Renamed from {name}")
                else:
                    log_action("MOVE", final_path, f"from ./{name}")
                
                try:
                    shutil.move(name, final_path)
                    stats['moved'] += 1
                except Exception as e:
                    log_action("ERR", final_path, str(e))
            else:
                # Scaffold
                log_action("NEW", target_path)
                try:
                    parent = os.path.dirname(target_path)
                    if not os.path.exists(parent):
                        os.makedirs(parent, exist_ok=True)
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Placeholder for {name}")
                    stats['files'] += 1
                except Exception as e:
                    log_action("ERR", target_path, str(e))

    print(f"{Style.DIM}{'-'*70}{Style.RESET}")
    print(f"{Style.BOLD}Summary:{Style.RESET} {stats['dirs']} Dirs | {stats['files']} Files | {stats['moved']} Moved")

# ==============================================================================
# --- PART 3: GENERATION ---
# ==============================================================================

def parse_gitignore(root_dir="."):
    patterns = []
    gitignore_path = os.path.join(root_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        lines = read_text_file(gitignore_path)
        if lines:
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def should_ignore(name, relative_path, ignore_patterns):
    if not ignore_patterns: return False
    for pattern in ignore_patterns:
        clean_pattern = pattern.rstrip('/')
        if fnmatch.fnmatch(name, clean_pattern): return True
        if fnmatch.fnmatch(relative_path, clean_pattern): return True
    return False

def generate_tree_string(dir_path, prefix="", stats=None, ignore_patterns=None):
    if stats is None: stats = {'files': 0, 'dirs': 0}
    if ignore_patterns is None: ignore_patterns = []
    
    output = ""
    try:
        all_items = sorted(os.listdir(dir_path))
        items = []
        for item in all_items:
            if item in SYSTEM_EXCLUDES: continue
            if item.startswith('.'): continue
            
            rel_path = os.path.relpath(os.path.join(dir_path, item))
            if should_ignore(item, rel_path, ignore_patterns): continue
            
            items.append(item)
            
    except OSError: return "", stats

    for i, item in enumerate(items):
        full_path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        
        # --- SYMLINK & LOOP PREVENTION ---
        if os.path.islink(full_path):
            try:
                target = os.readlink(full_path)
                output += f"{prefix}{connector}{item} -> {target}\n"
                stats['files'] += 1
            except OSError:
                output += f"{prefix}{connector}{item} (link)\n"
            # Do NOT recurse into symlinks to prevent infinite loops
            continue
        # ---------------------------------

        if os.path.isdir(full_path):
            stats['dirs'] += 1
            output += f"{prefix}{connector}{item}/\n"
            new_prefix = prefix + ("    " if is_last else "│   ")
            child, _ = generate_tree_string(full_path, new_prefix, stats, ignore_patterns)
            output += child
        else:
            stats['files'] += 1
            output += f"{prefix}{connector}{item}\n"
    return output, stats

def generate_structure_file():
    target_file = "directory-structure.txt"
    print_step(f"Generatng '{target_file}'...")
    
    ignore_patterns = parse_gitignore()
    if ignore_patterns:
        print(f" {Style.DIM}i Loaded {len(ignore_patterns)} patterns from .gitignore{Style.RESET}")

    tree_str, stats = generate_tree_string(".", stats=None, ignore_patterns=ignore_patterns)
    content = f"# Generated Structure\n# Files: {stats['files']} | Dirs: {stats['dirs']}\n\n{os.path.basename(os.getcwd())}/\n{tree_str}"
    
    try:
        with open(target_file, "w", encoding="utf-8") as f: f.write(content)
        print(f"{Style.DIM}\n{tree_str.strip()}\n{Style.RESET}")
        print(f" {Style.GREEN}✓ Success:{Style.RESET} Saved to {target_file}")
    except Exception as e:
        print(f" {Style.RED}× Error saving file:{Style.RESET} {e}")

# ==============================================================================
# --- MAIN MENU ---
# ==============================================================================

def main():
    print_header("Directory Controller v0.0.7")
    print(f"{Style.DIM}Manage your project structure with LLM outputs.{Style.RESET}")
    print("\n1. SCAN & GENERATE 'directory-structure.txt'")
    print("2. READ & BUILD structure from file")
    
    choice = input(f"\n{Style.BOLD}Select Option (1/2):{Style.RESET} ").strip()
    
    if choice == '1':
        generate_structure_file()
    elif choice == '2':
        target_file = find_structure_file()
        if target_file:
            # Use robust reader
            lines = read_text_file(target_file)
            if not lines:
                print(f" {Style.RED}× Error:{Style.RESET} File is unreadable or binary.")
                return

            nodes = identify_nodes(lines)
            
            if not nodes:
                print(f" {Style.RED}× Error:{Style.RESET} No valid nodes found in file.")
                return

            print_step(f"Preview: {target_file}")
            print(f" Working Root: {Style.YELLOW}{os.getcwd()}{Style.RESET}")
            print(f" Parsed Items: {Style.BOLD}{len(nodes)}{Style.RESET}")
            
            confirm = input(f"\nProceed with changes? ({Style.BOLD}y/n{Style.RESET}): ").lower()
            if confirm == 'y':
                build_tree_from_nodes(nodes)
                print(f"\n {Style.GREEN}✓ Operation Complete{Style.RESET}")
            else:
                print(f"\n {Style.YELLOW}- Cancelled -{Style.RESET}")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Style.YELLOW}\nExited by user.{Style.RESET}")
        sys.exit(0)