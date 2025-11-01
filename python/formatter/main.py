import os
import re
import logging
import sys
import json
import subprocess
import io
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog, TclError, font as tkfont
from tkinterdnd2 import DND_FILES, TkinterDnD
from syntax_highlighter import get_lexer, configure_tags, highlight_line, get_all_styles

# --- Global Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# File history location
HISTORY_FILE = os.path.expanduser("~/.code_formatter_history.json")
MAX_HISTORY = 10

SUPPORTED_FORMATTERS = {
    "python": "autopep8",
    "javascript": "prettier",
    "typescript": "prettier",
    "html": "prettier",
    "css": "prettier",
    "json": "prettier",
    "xml": "xmllint",
    "c": "clang-format",
    "cpp": "clang-format",
    "java": "clang-format",
    "go": "gofmt",
    "ruby": "rufo",
    "php": "php-cs-fixer",
    "rust": "rustfmt",
    "sh": "shfmt",
    "markdown": "prettier",
    "yaml": "prettier",
    "dockerfile": "hadolint",
    "perl": "perltidy",
    "lua": "luafmt"
}

FORMATTER_COMMANDS = {
    "autopep8": ["autopep8", "-"],
    "prettier": ["prettier", "--stdin-filepath", "temp.{ext}"],
    "xmllint": ["xmllint", "--format", "-"],
    "clang-format": ["clang-format"],
    "gofmt": ["gofmt"],
    "rufo": ["rufo", "-"],
    "rustfmt": ["rustfmt"],
    "shfmt": ["shfmt"],
}


class CodeFormatterApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Code Formatter")
        self.geometry("1600x1000")
        self.current_file_path = None
        self.current_file_modified = False
        self.file_history = []
        self.current_style = "monokai"
        self._setup_ui()
        self._load_file_history()
        self._bind_keyboard_shortcuts()
        logger.info("App initialized successfully.")

    def _setup_ui(self):
        """Setup the main UI components."""
        # Menu bar
        self.menu_bar = ctk.CTkFrame(self)
        self.menu_bar.pack(fill=ctk.X)
        
        ctk.CTkButton(
            self.menu_bar, 
            text="Load File", 
            command=self.load_file
        ).pack(side=ctk.LEFT, padx=5, pady=5)
        
        ctk.CTkButton(
            self.menu_bar, 
            text="Save File", 
            command=self._save_file
        ).pack(side=ctk.LEFT, padx=5, pady=5)
        
        ctk.CTkButton(
            self.menu_bar, 
            text="Format Code", 
            command=self._format_code
        ).pack(side=ctk.LEFT, padx=5, pady=5)
        
        ctk.CTkButton(
            self.menu_bar, 
            text="Lint Code", 
            command=self._lint_code
        ).pack(side=ctk.LEFT, padx=5, pady=5)
        
        # Style selector
        ctk.CTkLabel(self.menu_bar, text="Theme:").pack(side=ctk.LEFT, padx=(20, 5))
        
        available_styles = list(get_all_styles())
        self.style_selector = ctk.CTkComboBox(
            self.menu_bar,
            values=available_styles,
            command=self._change_style,
            width=150
        )
        self.style_selector.set(self.current_style)
        self.style_selector.pack(side=ctk.LEFT, padx=5, pady=5)
        
        ctk.CTkButton(
            self.menu_bar, 
            text="Recent Files", 
            command=self._show_recent_files
        ).pack(side=ctk.LEFT, padx=5, pady=5)

        # Content text widget
        self.content_widget = ctk.CTkTextbox(self, wrap=ctk.NONE, activate_scrollbars=True)
        self.content_widget.pack(fill=ctk.BOTH, expand=True)
        self.content_widget.bind("<<Modified>>", self._on_text_modified)
        
        # Configure initial syntax highlighting
        configure_tags(self.content_widget._textbox, self.current_style)

        # Status bar for real-time feedback
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor='w')
        self.status_bar.pack(fill=ctk.X)
        
        # Enable drag and drop
        self.content_widget.drop_target_register(DND_FILES)
        self.content_widget.dnd_bind("<<Drop>>", self._on_file_drop)

    def _bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.bind("<Control-s>", self._save_file)
        self.bind("<Control-o>", self.load_file)
        self.bind("<Control-f>", lambda e: self._format_code())
        self.bind("<Control-l>", lambda e: self._lint_code())

    def _on_file_drop(self, event):
        """Handle file drop event."""
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.load_file(filepath=file_path)

    def _on_text_modified(self, event=None):
        """Track if content has been modified."""
        if self.content_widget.edit_modified():
            if not self.current_file_modified:
                self.current_file_modified = True
                self._update_title()
            self.content_widget.edit_modified(False)

    def _update_title(self):
        """Update window title with current file and modification status."""
        title = "Ultimate Code Formatter"
        if self.current_file_path:
            filename = os.path.basename(self.current_file_path)
            title = f"{filename}{'*' if self.current_file_modified else ''} - {title}"
        self.title(title)

    def _show_toast(self, message, status="info"):
        """Show status message with color coding."""
        color_map = {
            "info": "#50fa7b", 
            "warn": "#f1fa8c", 
            "error": "#ff5555", 
            "success": "#8be9fd"
        }
        self.status_bar.configure(text=message, fg_color=color_map.get(status, "#50fa7b"))
        self.after(5000, lambda: self.status_bar.configure(text="Ready", fg_color=None))

    def load_file(self, event=None, filepath=None):
        """Load a file into the editor."""
        try:
            if not filepath:
                filepath = filedialog.askopenfilename(
                    title="Select File to Format",
                    filetypes=[
                        ("All Files", "*.*"),
                        ("Python Files", "*.py"),
                        ("JavaScript Files", "*.js"),
                        ("TypeScript Files", "*.ts"),
                        ("HTML Files", "*.html"),
                        ("CSS Files", "*.css"),
                        ("JSON Files", "*.json"),
                    ]
                )
            
            if not filepath:
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file_path = filepath
            self.current_file_modified = False
            self.content_widget.delete("1.0", ctk.END)
            self.content_widget.insert("1.0", content)
            
            # Apply syntax highlighting
            self._apply_syntax_highlighting()
            
            # Add to history
            self._add_to_history(filepath)
            
            self._update_title()
            self._show_toast(f"Loaded: {os.path.basename(filepath)}", status="success")
            logger.info(f"Loaded file: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load file: {e}", exc_info=True)
            self._show_toast(f"Failed to load file: {e}", status="error")
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def _save_file(self, event=None):
        """Save the current file."""
        try:
            if not self.current_file_path:
                filepath = filedialog.asksaveasfilename(
                    title="Save File As",
                    defaultextension=".txt",
                    filetypes=[
                        ("All Files", "*.*"),
                        ("Python Files", "*.py"),
                        ("JavaScript Files", "*.js"),
                        ("TypeScript Files", "*.ts"),
                        ("HTML Files", "*.html"),
                        ("CSS Files", "*.css"),
                        ("JSON Files", "*.json"),
                    ]
                )
                if not filepath:
                    return
                self.current_file_path = filepath
            
            content = self.content_widget.get("1.0", ctk.END)
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file_modified = False
            self._update_title()
            self._add_to_history(self.current_file_path)
            self._show_toast(f"Saved: {os.path.basename(self.current_file_path)}", status="success")
            logger.info(f"Saved file: {self.current_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            self._show_toast(f"Failed to save file: {e}", status="error")
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def _format_code(self):
        """Format the current code using appropriate formatter."""
        if not self.current_file_path:
            self._show_toast("Please load a file first", status="warn")
            return
        
        current_code = self.content_widget.get("1.0", ctk.END).rstrip()
        lexer = get_lexer(self.current_file_path, current_code)
        
        if not lexer:
            self._show_toast("Could not detect file type", status="warn")
            return
        
        lexer_name = lexer.name.lower()
        formatter = SUPPORTED_FORMATTERS.get(lexer_name)
        
        if not formatter:
            self._show_toast(f"No formatter configured for '{lexer_name}'", status="warn")
            logger.warning(f"No formatter configured for language: {lexer_name}")
            return
        
        # Check if formatter is available
        if not self._is_formatter_available(formatter):
            self._show_toast(f"Formatter '{formatter}' not installed", status="error")
            messagebox.showwarning(
                "Formatter Not Found",
                f"The formatter '{formatter}' is not installed.\n\n"
                f"Please install it to format {lexer_name} files."
            )
            return
        
        try:
            formatted_code = self._run_formatter(formatter, current_code, lexer_name)
            
            if formatted_code and formatted_code != current_code:
                self.content_widget.delete("1.0", ctk.END)
                self.content_widget.insert("1.0", formatted_code)
                self._apply_syntax_highlighting()
                self.current_file_modified = True
                self._update_title()
                self._show_toast("Code formatted successfully", status="success")
                logger.info(f"Formatted code using {formatter}")
            else:
                self._show_toast("Code already formatted", status="info")
                
        except Exception as e:
            logger.error(f"Formatting error: {e}", exc_info=True)
            self._show_toast(f"Formatting failed: {e}", status="error")

    def _run_formatter(self, formatter, code, language):
        """Run the specified formatter on the code."""
        sanitized_code = self._sanitize_code(code)
        
        # Get formatter command
        if formatter == "prettier":
            ext_map = {
                "javascript": "js",
                "typescript": "ts",
                "html": "html",
                "css": "css",
                "json": "json",
                "markdown": "md",
                "yaml": "yaml"
            }
            ext = ext_map.get(language, "txt")
            cmd = ["prettier", "--stdin-filepath", f"temp.{ext}"]
        elif formatter == "autopep8":
            cmd = ["autopep8", "-"]
        else:
            cmd = FORMATTER_COMMANDS.get(formatter, [formatter])
        
        process = subprocess.run(
            cmd,
            input=sanitized_code,
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            error_msg = process.stderr or "Unknown error"
            logger.error(f"Formatter error: {error_msg}")
            raise Exception(error_msg)
        
        return process.stdout

    def _is_formatter_available(self, formatter):
        """Check if a formatter is available in PATH."""
        try:
            subprocess.run(
                [formatter, "--version"],
                capture_output=True,
                timeout=2
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _lint_code(self):
        """Lint the current code."""
        if not self.current_file_path:
            self._show_toast("Please load a file first", status="warn")
            return
        
        current_code = self.content_widget.get("1.0", ctk.END).rstrip()
        lexer = get_lexer(self.current_file_path, current_code)
        
        if not lexer:
            self._show_toast("Could not detect file type", status="warn")
            return
        
        lexer_name = lexer.name.lower()
        linter = SUPPORTED_FORMATTERS.get(lexer_name)
        
        if not linter:
            self._show_toast(f"No linter configured for '{lexer_name}'", status="warn")
            return

        try:
            process = subprocess.run(
                [linter, "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Run linter
            lint_cmd = [linter]
            if linter == "autopep8":
                lint_cmd = ["autopep8", "--diff", "-"]
            
            process = subprocess.run(
                lint_cmd,
                input=self._sanitize_code(current_code),
                capture_output=True,
                text=True
            )
            
            lint_output = process.stderr or process.stdout
            if lint_output.strip():
                self._show_toast("Linting completed with issues", status="warn")
                logger.warning(f"Linting issues:\n{lint_output.strip()}")
                messagebox.showinfo("Lint Results", f"Issues found:\n\n{lint_output[:500]}")
            else:
                self._show_toast("No linting issues found", status="success")
                
        except FileNotFoundError:
            self._show_toast(f"Linter '{linter}' not installed", status="error")
        except Exception as e:
            logger.error(f"Linting error: {e}", exc_info=True)
            self._show_toast(f"Linting failed: {e}", status="error")

    def _sanitize_code(self, code):
        """Sanitize code for UTF-8 encoding."""
        clean_code = re.sub(r'[\uD800-\uDFFF]', '', code)
        try:
            clean_code = clean_code.encode('utf-8', errors='ignore').decode('utf-8')
            logger.debug("Code successfully sanitized for UTF-8.")
        except UnicodeEncodeError as e:
            logger.error(f"Failed to sanitize code: {e}", exc_info=True)
        return clean_code

    def _apply_syntax_highlighting(self):
        """Apply syntax highlighting to the current content."""
        if not self.current_file_path:
            return
        
        try:
            content = self.content_widget.get("1.0", ctk.END)
            lexer = get_lexer(self.current_file_path, content)
            
            if lexer:
                # Reconfigure tags for current style
                configure_tags(self.content_widget._textbox, self.current_style)
                
                # Apply highlighting line by line
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line_start = f"{line_num}.0"
                    line_end = f"{line_num}.end"
                    
                    # Clear existing tags for this line
                    for tag in self.content_widget._textbox.tag_names(line_start):
                        if tag.startswith("pygments_"):
                            self.content_widget._textbox.tag_remove(tag, line_start, line_end)
                
                logger.info("Syntax highlighting applied")
        except Exception as e:
            logger.error(f"Failed to apply syntax highlighting: {e}", exc_info=True)

    def _change_style(self, style_name):
        """Change the syntax highlighting style."""
        self.current_style = style_name
        configure_tags(self.content_widget._textbox, style_name)
        self._apply_syntax_highlighting()
        self._show_toast(f"Style changed to: {style_name}", status="info")

    def _load_file_history(self):
        """Load file history from disk."""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    self.file_history = json.load(f)
                logger.info(f"Loaded {len(self.file_history)} files from history")
            else:
                self.file_history = []
                logger.info("No history file found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load file history: {e}", exc_info=True)
            self.file_history = []

    def _save_file_history(self):
        """Save file history to disk."""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.file_history, f, indent=2)
            logger.info(f"Saved {len(self.file_history)} files to history")
        except Exception as e:
            logger.error(f"Failed to save file history: {e}", exc_info=True)

    def _add_to_history(self, filepath):
        """Add a file to history."""
        # Remove if already exists
        if filepath in self.file_history:
            self.file_history.remove(filepath)
        
        # Add to beginning
        self.file_history.insert(0, filepath)
        
        # Limit history size
        self.file_history = self.file_history[:MAX_HISTORY]
        
        # Save history
        self._save_file_history()

    def _show_recent_files(self):
        """Show recent files dialog."""
        if not self.file_history:
            messagebox.showinfo("Recent Files", "No recent files")
            return
        
        # Create dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Recent Files")
        dialog.geometry("600x400")
        
        ctk.CTkLabel(dialog, text="Recent Files:", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Create listbox frame
        list_frame = ctk.CTkFrame(dialog)
        list_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(list_frame)
        scrollable_frame.pack(fill=ctk.BOTH, expand=True)
        
        def load_selected(path):
            self.load_file(filepath=path)
            dialog.destroy()
        
        for filepath in self.file_history:
            if os.path.exists(filepath):
                btn = ctk.CTkButton(
                    scrollable_frame,
                    text=filepath,
                    command=lambda p=filepath: load_selected(p),
                    anchor="w"
                )
                btn.pack(fill=ctk.X, pady=2)
        
        ctk.CTkButton(dialog, text="Close", command=dialog.destroy).pack(pady=10)


if __name__ == '__main__':
    app = CodeFormatterApp()
    app.mainloop()