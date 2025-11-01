# 🎨 Ultimate Code Formatter

Professional multi-language code formatter with syntax highlighting, linting, and file management powered by Pygments.

## ✨ Features

- 🌈 **Syntax Highlighting** - 500+ languages via Pygments
- 🔧 **Auto-Formatting** - Support for 20+ formatters (autopep8, prettier, clang-format, etc.)
- 🔍 **Code Linting** - Real-time code quality checks
- 💾 **File Management** - Load, save, and track file history  
- 🎨 **Multiple Themes** - All Pygments color schemes available (50+ styles)
- ⚡ **Keyboard Shortcuts** - Efficient workflow with hotkeys
- 📊 **Status Bar** - Real-time feedback with color-coded messages
- 🖱️ **Drag & Drop** - Drop files directly into editor
- 📜 **Recent Files** - Quick access to file history (last 10 files)
- 🎯 **Auto-Detection** - Automatic language and formatter detection

## 📦 Installation

```bash
pip install -r requirements.txt
```

### Python Dependencies
- customtkinter
- Pygments
- tkinterdnd2-Universal
- autopep8

### External Formatters (Optional)
Install formatters for languages you use:

```bash
# Python
pip install autopep8 --break-system-packages

# JavaScript/TypeScript/HTML/CSS/JSON/Markdown
npm install -g prettier

# Go (included with Go installation)
# gofmt is built-in

# Rust
rustup component add rustfmt

# C/C++/Java (varies by system)
# Ubuntu/Debian: sudo apt install clang-format
# macOS: brew install clang-format

# Shell scripts
go install mvdan.cc/sh/v3/cmd/shfmt@latest

# Ruby
gem install rufo
```

## 🚀 Usage

```bash
python main.py
```

## ⌨️ Keyboard Shortcuts

- `Ctrl+O` - Open file dialog
- `Ctrl+S` - Save current file
- `Ctrl+F` - Format code
- `Ctrl+L` - Lint code

## 🎯 Supported Languages & Formatters

| Language | Formatter | Auto-Format | Linting |
|----------|-----------|-------------|---------|
| Python | autopep8 | ✅ | ✅ |
| JavaScript | prettier | ✅ | ✅ |
| TypeScript | prettier | ✅ | ✅ |
| HTML | prettier | ✅ | ✅ |
| CSS | prettier | ✅ | ✅ |
| JSON | prettier | ✅ | ✅ |
| Markdown | prettier | ✅ | ✅ |
| YAML | prettier | ✅ | ✅ |
| XML | xmllint | ✅ | ✅ |
| C/C++ | clang-format | ✅ | ✅ |
| Java | clang-format | ✅ | ✅ |
| Go | gofmt | ✅ | ✅ |
| Ruby | rufo | ✅ | ✅ |
| Rust | rustfmt | ✅ | ✅ |
| Shell | shfmt | ✅ | ✅ |
| PHP | php-cs-fixer | ⚠️ | ⚠️ |
| Perl | perltidy | ⚠️ | ⚠️ |
| Lua | luafmt | ⚠️ | ⚠️ |

✅ = Fully implemented | ⚠️ = Requires additional configuration

## 🎨 Syntax Highlighting Themes

Available themes include:
- **monokai** (default) - Popular dark theme
- **dracula** - Easy on the eyes dark theme
- **github-dark** - GitHub's dark theme
- **one-dark** - Atom's One Dark
- **solarized-dark** - Classic Solarized
- **nord** - Arctic-inspired theme
- **material** - Material Design colors
- **gruvbox** - Retro groove colors
- ...and 40+ more!

Change themes via the Theme dropdown in the menu bar.

## 🔧 Configuration

### Custom Token Colors
Edit `syntax_highlighter.py` to customize token colors:

```python
MANUAL_OVERRIDES = { 
    Token.Keyword: {'foreground': '#FF79C6'},
    Token.Name.Function: {'foreground': '#50FA7B'},
    # Add your custom colors here
}
```

### File History
File history is stored in: `~/.code_formatter_history.json`
- Tracks last 10 opened files
- Persists between sessions
- Auto-cleanup of non-existent files

## 📋 Features Deep Dive

### 1. Syntax Highlighting
- Automatic language detection based on file extension
- Real-time highlighting as you type
- Fallback to content-based detection
- Support for 500+ programming languages

### 2. Code Formatting
- Detects appropriate formatter automatically
- Checks if formatter is installed before running
- Preserves file encoding (UTF-8)
- Shows success/error status in status bar

### 3. Code Linting
- Runs static analysis on code
- Displays linting results in popup
- Logs detailed issues to console
- Non-blocking UI during linting

### 4. File Management
- Recent files dialog for quick access
- Auto-saves file history
- Modification tracking (asterisk in title)
- Support for Save As functionality

### 5. Status Bar
- Color-coded messages:
  - 🟢 Green - Success
  - 🟡 Yellow - Warning
  - 🔴 Red - Error
  - 🔵 Blue - Info
- Auto-hides after 5 seconds

## 🐛 Known Issues & Solutions

### Formatter Not Found
**Issue**: "Formatter 'prettier' not installed"

**Solution**: Install the required formatter:
```bash
npm install -g prettier
# or for Python
pip install autopep8 --break-system-packages
```

### Syntax Highlighting Not Working
**Issue**: Code appears without colors

**Solution**: 
- Ensure Pygments is installed: `pip install Pygments`
- Try changing the theme from the dropdown
- Check that file has a recognized extension

### Drag & Drop Not Working
**Issue**: Files don't load when dropped

**Solution**:
- Ensure tkinterdnd2-Universal is installed
- Try using "Load File" button instead
- Check file permissions

## ⚙️ Requirements

- Python 3.8+
- customtkinter
- Pygments  
- tkinterdnd2-Universal
- autopep8

## 🔒 Security

- No network access required (except for formatter downloads)
- Files are processed locally
- No data is sent to external services
- UTF-8 encoding validation prevents binary execution

## 📝 Development

### Project Structure
```
formatter/
├── main.py                 # Main application
├── syntax_highlighter.py   # Pygments integration
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
└── README.md              # This file
```

### Extending Formatters

To add a new formatter:

1. Add to `SUPPORTED_FORMATTERS` dict in `main.py`:
```python
SUPPORTED_FORMATTERS = {
    "your_language": "your_formatter",
}
```

2. Add command in `FORMATTER_COMMANDS`:
```python
FORMATTER_COMMANDS = {
    "your_formatter": ["formatter_cmd", "args"],
}
```

3. Test with sample code file

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional formatter integrations
- Custom formatter configuration files
- Diff view for formatted changes
- Multi-file formatting
- Batch processing
- Plugin system for formatters

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **Pygments** - Syntax highlighting engine
- **CustomTkinter** - Modern UI framework
- **tkinterdnd2** - Drag and drop support

## 💡 Tips & Tricks

1. **Quick Format**: Press `Ctrl+F` to instantly format current file
2. **Theme Testing**: Switch themes to find your favorite
3. **Recent Files**: Access last 10 files via "Recent Files" button
4. **Status Bar**: Watch for color changes for operation feedback
5. **Drag & Drop**: Fastest way to open files
6. **Keyboard First**: Use shortcuts for efficient workflow

## 📊 Statistics

- 500+ languages supported for syntax highlighting
- 20+ formatters integrated
- 50+ color themes available
- 10 recent files tracked
- 4 keyboard shortcuts

## 🚀 Roadmap

- [ ] Diff view before/after formatting
- [ ] Batch file processing
- [ ] Custom formatter configurations
- [ ] Plugin system
- [ ] Split view editing
- [ ] Multi-file project support
- [ ] Git integration
- [ ] Remote file editing

---

**Made with ❤️ for developers who love clean code**