# 📁 Directory Structure Generator

Cross-platform scripts that generate a visual tree representation of your project's directory structure and save it to a text file.

## 🎯 What It Does

These scripts recursively scan your project directory and create a clean, formatted tree structure showing all files and folders. The output is saved to `project-structure.txt` in the same directory where the script is run.

## 📦 Available Scripts

- **`dir-structure.py`** - Python version (cross-platform)
- **`dir-structure.sh`** - Bash version (Linux/Mac/WSL)
- **`dir-structure.bat`** - Batch version (Windows CMD)
- **`dir-structure.ps1`** - PowerShell version (Windows/Linux/Mac)

All four scripts produce identical output.

## 🚀 Usage

### Python
```bash
python dir-structure.py
```

### Bash (Linux/Mac)
```bash
chmod +x dir-structure.sh
./dir-structure.sh
```

### Windows Batch
```cmd
dir-structure.bat
```

### PowerShell
```powershell
.\dir-structure.ps1
```

## 📋 Example Output

```
# Project Directory Structure & Files

# Statistics
Total Directories: 4
Total Files: 9
Total Size: 1.23 MB

my-project/
├── index.html
├── package.json
├── README.md
├── css/
│   ├── main.css
│   └── theme.css
├── js/
│   ├── app.js
│   └── utils.js
└── assets/
    ├── logo.png
    └── images/
        ├── banner.jpg
        └── icon.svg
```

## 🚫 Excluded Items

The scripts automatically exclude:
- The script file itself
- The output file (`project-structure.txt`)
- Hidden files and directories (`.git`, `.env`, etc.)
- `node_modules/`
- `__pycache__/`
- `.venv/` and `venv/`
- `.DS_Store`
- System files

## 💾 Output File

The generated `project-structure.txt` file contains:
- Header indicating it's a project structure
- Statistics summary at the top (total directories, files, and size)
- Root directory name
- Complete tree with proper indentation
- Files listed before directories at each level
- Unix-style tree characters (`├──`, `└──`, `│`)

## ⚙️ Requirements

- **Python**: Python 3.x (no external dependencies)
- **Bash**: Standard bash shell
- **Batch**: Windows Command Prompt
- **PowerShell**: PowerShell 5.1+ (Windows/Linux/Mac)

## 📝 Notes

- All scripts sort items alphabetically
- Files are listed before directories at each level
- Empty directories are shown with `/` suffix
- The output file is created in the current working directory