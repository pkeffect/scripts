# 🔍 GitDiff Viewer

A powerful side-by-side file comparison tool built with Python and CustomTkinter.

![GitDiff Viewer Screenshot](https://via.placeholder.com/800x450.png?text=GitDiff+Viewer+Screenshot)

## ✨ Features

- **Side-by-side diff visualization** with clear highlighting for additions, deletions, and modifications
- **Syntax highlighting** for various programming languages using Pygments
- **Character-level diff** within changed lines to pinpoint exact modifications
- **Customizable font** selection with various size options
- **Word wrap** toggle for better readability of long lines
- **Synchronized scrolling** between panes
- **Line numbers** with special highlighting for changed sections
- **Dark mode** interface for reduced eye strain

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

## 🎮 Interface Guide

### Controls:
- **Open File A/B**: Load files for comparison
- **Style**: Choose from various syntax highlighting themes
- **Font**: Select your preferred monospace font
- **Size**: Adjust text size for better readability
- **Word Wrap**: Toggle word wrapping for long lines

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

## 🔄 Troubleshooting

- If syntax highlighting doesn't appear correctly, try selecting a different style
- For large files, give the application a moment to process the diff
- If the application crashes unexpectedly, check the console log for detailed error messages

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.