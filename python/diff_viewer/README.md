# 🔍 Diff Viewer

A powerful side-by-side file comparison tool built with Python and CustomTkinter.

![Diff Viewer Screenshot](https://via.placeholder.com/800x450.png?text=GitDiff+Viewer+Screenshot)

## ✨ Features

- **Side-by-side or top-bottom diff visualization** with clear highlighting for additions, deletions, and modifications
- **Syntax highlighting** for various programming languages using Pygments
- **Character-level diff** within changed lines to pinpoint exact modifications
- **Customizable font** selection with various size options
- **Word wrap** toggle for better readability of long lines
- **Synchronized scrolling** between panes
- **Line numbers** with special highlighting for changed sections
- **Dark mode** interface for reduced eye strain
- **Edit mode** for modifying and saving compared files
- **File history** keeps track of recently compared file pairs
- **Advanced comparison options**:
  - Ignore whitespace
  - Ignore case sensitivity
  - Ignore line endings
  - Fold equal blocks (collapses large unchanged sections)
- **Search functionality** to find text within files
- **Navigation features** to jump between differences or to specific line numbers
- **File status indicators** to show when files have been modified
- **Detailed statistics** showing counts of added, deleted, and changed blocks

## 🛠️ Requirements

- Python 3.6+
- Dependencies:
  - customtkinter
  - Pygments

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/gitdiff-viewer.git
   cd gitdiff-viewer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

Start the application by running:

```bash
python main.py
```

### Basic Workflow:

1. Click **Open File A** to select the first file for comparison
2. Click **Open File B** to select the second file for comparison
3. The diff view will automatically appear once both files are loaded
4. Use the options to customize the comparison and view

## 🎮 Interface Guide

### Top Controls:
- **File A/B**: Load files for comparison
- **Save A/B**: Save edited files
- **History Dropdown**: Access recently compared file pairs

### Appearance Controls:
- **View Mode**: Switch between side-by-side and top-bottom views
- **Style**: Choose from various syntax highlighting themes
- **Font**: Select your preferred monospace font
- **Size**: Adjust text size for better readability
- **Word Wrap**: Toggle word wrapping for long lines
- **Ignore Options**: Toggle whitespace, case, and line ending sensitivity
- **Fold Equal**: Collapse large unchanged sections for easier navigation
- **Edit Mode**: Enable editing of files
- **Re-Compare**: Refresh the comparison after making changes

### Navigation and Search:
- **Prev/Next Diff**: Navigate between changes
- **Go To Line**: Jump to a specific line number
- **Search**: Find text within the files
- **Clear**: Remove search highlights

### Diff Highlighting:
- **Green background**: Added lines
- **Red background**: Deleted lines
- **Yellow background**: Modified lines
- **Character highlighting**: Specific changes within modified lines are highlighted in brighter colors

## 💡 Tips

- For best results, compare files with similar formats
- Monospaced fonts like Consolas, Courier New, or Source Code Pro work best
- The syntax highlighter automatically detects the file type based on content and extension
- Use keyboard scroll or mouse wheel to navigate through the files
- Both panes scroll synchronously for easy comparison
- When editing files, save them using the "Save A" or "Save B" buttons
- Use "Edit Mode" to make changes to files directly within the application
- The history feature remembers up to 10 recent file pairs
- An asterisk (*) before the filename indicates unsaved changes

## 🔄 Troubleshooting

- If syntax highlighting doesn't appear correctly, try selecting a different style
- For large files, give the application a moment to process the diff
- If the application crashes unexpectedly, check the console log for detailed error messages
- If file comparison options like "Ignore Whitespace" don't seem to work, try toggling the option off and on again
- When "Fold Equal" is enabled, large identical blocks will be collapsed - click "Re-Compare" to refresh the view

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
