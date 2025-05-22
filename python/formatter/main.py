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
    "markdown": "markdownlint",
    "yaml": "yamllint",
    "dockerfile": "hadolint",
    "perl": "perltidy",
    "lua": "luafmt"
}


class CodeFormatterApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.title("Ultimate Code Formatter")
        self.geometry("1600x1000")
        self.current_file_path = None
        self.current_file_modified = False
        self.file_history = []
        self._setup_ui()
        self._load_file_history()
        logger.info("App initialized successfully.")

    def _setup_ui(self):
        self.content_widget = ctk.CTkTextbox(self, wrap=ctk.NONE, activate_scrollbars=True)
        self.content_widget.pack(fill=ctk.BOTH, expand=True)
        self.bind("<Control-s>", self._save_file)
        self.bind("<Control-o>", self.load_file)

        self.menu_bar = ctk.CTkFrame(self)
        self.menu_bar.pack(fill=ctk.X)
        ctk.CTkButton(self.menu_bar, text="Load File", command=self.load_file).pack(side=ctk.LEFT, padx=5, pady=5)
        ctk.CTkButton(self.menu_bar, text="Save File", command=self._save_file).pack(side=ctk.LEFT, padx=5, pady=5)
        ctk.CTkButton(self.menu_bar, text="Format Code", command=self._format_code).pack(side=ctk.LEFT, padx=5, pady=5)
        ctk.CTkButton(self.menu_bar, text="Lint Code", command=self._lint_code).pack(side=ctk.LEFT, padx=5, pady=5)

        # Status bar for real-time feedback
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor='w')
        self.status_bar.pack(fill=ctk.X)

    def _show_toast(self, message, status="info"):
        color_map = {"info": "#50fa7b", "warn": "#f1fa8c", "error": "#ff5555", "success": "#8be9fd"}
        self.status_bar.configure(text=message, fg_color=color_map.get(status, "#50fa7b"))
        self.after(5000, lambda: self.status_bar.configure(text="Ready", fg_color=None))

    def _lint_code(self):
        current_code = self.content_widget.get("1.0", ctk.END).rstrip()
        lexer = get_lexer(self.current_file_path, current_code)
        lexer_name = lexer.name.lower() if lexer else "text"
        lint_cmd = SUPPORTED_FORMATTERS.get(lexer_name)
        if not lint_cmd:
            self._show_toast(f"No linter configured for '{lexer_name}'.", status="warn")
            return

        try:
            process = subprocess.run(
                [lint_cmd, '-'],
                input=self._sanitize_code(current_code),
                capture_output=True,
                text=True
            )
            lint_output = process.stderr or process.stdout
            if lint_output.strip():
                self._show_toast("Linting completed with issues. Check console for details.", status="warn")
                logger.warning(f"Linting issues found: {lint_output.strip()}")
            else:
                self._show_toast("No linting issues found.", status="success")
        except Exception as e:
            logger.error(f"Linting error: {e}", exc_info=True)
            self._show_toast(f"An error occurred while linting: {e}", status="error")

    def _sanitize_code(self, code):
        clean_code = re.sub(r'[\uD800-\uDFFF]', '', code)
        try:
            clean_code = clean_code.encode('utf-8', errors='ignore').decode('utf-8')
            logger.info("Code successfully sanitized for UTF-8.")
        except UnicodeEncodeError as e:
            logger.error(f"Failed to sanitize code: {e}", exc_info=True)
            self._show_toast(f"Failed to sanitize code for UTF-8: {e}", status="error")
        return clean_code


if __name__ == '__main__':
    app = CodeFormatterApp()
    app.mainloop()
