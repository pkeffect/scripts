# main.py - Corrected _clear_pane
import customtkinter as ctk
from tkinter import filedialog, messagebox, TclError, font as tkfont
import difflib
import os
import re
import logging
import sys

# ... (Global Logging Setup and syntax_highlighter import - same as before) ...
# --- Global Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    from syntax_highlighter import get_lexer, configure_tags, highlight_line, get_all_styles
except ImportError:
    logger.critical("Failed to import syntax_highlighter.py. Make sure it exists and has no syntax errors.")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Error during syntax_highlighter import: {e}", exc_info=True)
    sys.exit(1)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class DiffApp(ctk.CTk):
    def __init__(self): # Same as before
        logger.info("Initializing DiffApp (Side-by-Side)...")
        try:
            super().__init__()
            self.title("GitDiff Viewer - Side-by-Side")
            self.geometry("1600x900")
            self.file_a_path_var = ctk.StringVar(value="<File A>")
            self.file_b_path_var = ctk.StringVar(value="<File B>")
            self.file_a_lines = None
            self.file_b_lines = None
            self.lexer_a = None
            self.lexer_b = None
            self.current_font_family = ctk.StringVar(value="Consolas")
            self.current_font_size = ctk.IntVar(value=10)
            self.current_pygments_style = ctk.StringVar(value='monokai')
            self.word_wrap_var = ctk.BooleanVar(value=False)
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=1)
            self._create_widgets()
            self._update_font_and_style_configuration()
            self._setup_scrolling_sync()
            self._disable_text_widgets() # Initial disable
            logger.info("DiffApp (Side-by-Side) initialized successfully.")
        except Exception as e:
            logger.critical(f"CRITICAL ERROR during DiffApp __init__: {e}", exc_info=True)
            try: messagebox.showerror("Fatal Initialization Error", f"Application failed to start:\n{e}\n\nCheck console for details.")
            except: pass
            if hasattr(self, 'destroy'): self.destroy()
            sys.exit(1)

    def _update_font_and_style_configuration(self, event=None): # Same as before
        logger.info(f"Updating font/style/wrap: {self.current_font_family.get()} {self.current_font_size.get()}pt, Style: {self.current_pygments_style.get()}, Wrap: {self.word_wrap_var.get()}")
        new_content_font = (self.current_font_family.get(), self.current_font_size.get())
        new_ln_font = (self.current_font_family.get(), self.current_font_size.get() -1 if self.current_font_size.get() > 8 else self.current_font_size.get())
        wrap_mode = ctk.WORD if self.word_wrap_var.get() else ctk.NONE
        widgets_to_update = {
            self.content_a_widget: {'font': new_content_font, 'wrap': wrap_mode},
            self.content_b_widget: {'font': new_content_font, 'wrap': wrap_mode},
            self.line_numbers_a_widget: {'font': new_ln_font},
            self.line_numbers_b_widget: {'font': new_ln_font}
        }
        for widget_wrapper, config in widgets_to_update.items():
             tb = getattr(widget_wrapper, '_textbox', None)
             if tb:
                 try: tb.configure(**config)
                 except Exception as e: logger.error(f"Error configuring widget {widget_wrapper}: {e}")
        self._configure_all_tags_for_pane(self.content_a_widget, self.line_numbers_a_widget)
        self._configure_all_tags_for_pane(self.content_b_widget, self.line_numbers_b_widget)
        if self.file_a_lines is not None and self.file_b_lines is not None:
            logger.debug("Re-showing diff after font/style/wrap change.")
            self.show_diff_side_by_side()
        elif self.file_a_lines is not None:
            logger.debug("Re-showing single file A after font/style/wrap change.")
            self._display_single_file('a')
        elif self.file_b_lines is not None:
            logger.debug("Re-showing single file B after font/style/wrap change.")
            self._display_single_file('b')

    def _disable_text_widgets(self): # Same as before
        widgets = [self.content_a_widget, self.line_numbers_a_widget, self.content_b_widget, self.line_numbers_b_widget]
        for widget in widgets:
            if widget and hasattr(widget, 'configure'):
                try: widget.configure(state=ctk.DISABLED)
                except Exception as e: logger.error(f"Error disabling widget {widget}: {e}")

    def _enable_text_widgets(self): # Same as before
        widgets = [self.content_a_widget, self.line_numbers_a_widget, self.content_b_widget, self.line_numbers_b_widget]
        for widget in widgets:
            if widget and hasattr(widget, 'configure'):
                try: widget.configure(state=ctk.NORMAL)
                except Exception as e: logger.error(f"Error enabling widget {widget}: {e}")

    def _create_widgets(self): # Same as before (with font/style controls)
        logger.debug("Creating widgets (Side-by-Side)...")
        self.top_control_bar = ctk.CTkFrame(self, corner_radius=0)
        self.top_control_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        ctk.CTkButton(self.top_control_bar, text="Open File A", width=100, command=lambda: self.load_file('a')).pack(side=ctk.LEFT, padx=(0,5), pady=5)
        self.file_a_label = ctk.CTkLabel(self.top_control_bar, textvariable=self.file_a_path_var, anchor="w")
        self.file_a_label.pack(side=ctk.LEFT, padx=5, pady=5, fill=ctk.X, expand=True)
        ctk.CTkButton(self.top_control_bar, text="Open File B", width=100, command=lambda: self.load_file('b')).pack(side=ctk.LEFT, padx=(10,5), pady=5)
        self.file_b_label = ctk.CTkLabel(self.top_control_bar, textvariable=self.file_b_path_var, anchor="w")
        self.file_b_label.pack(side=ctk.LEFT, padx=5, pady=5, fill=ctk.X, expand=True)
        self.appearance_controls_frame = ctk.CTkFrame(self, corner_radius=0)
        self.appearance_controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))
        ctk.CTkLabel(self.appearance_controls_frame, text="Style:").pack(side=ctk.LEFT, padx=(0,2), pady=5)
        try:
            pygments_styles_list = sorted(list(get_all_styles())); default_style = 'monokai'
            if not pygments_styles_list: pygments_styles_list = [default_style]
            if self.current_pygments_style.get() not in pygments_styles_list: self.current_pygments_style.set(default_style if default_style in pygments_styles_list else pygments_styles_list[0])
        except Exception as e: logger.error(f"Failed to get Pygments styles: {e}", exc_info=True); pygments_styles_list = ['monokai', 'default']; self.current_pygments_style.set('monokai')
        self.style_menu = ctk.CTkOptionMenu(self.appearance_controls_frame, width=130, values=pygments_styles_list, variable=self.current_pygments_style, command=self._update_font_and_style_configuration)
        self.style_menu.pack(side=ctk.LEFT, padx=(0,10), pady=5)
        ctk.CTkLabel(self.appearance_controls_frame, text="Font:").pack(side=ctk.LEFT, padx=(0,2), pady=5)
        try:
            available_fonts = sorted([f for f in tkfont.families() if not f.startswith('@')]); default_font = "Consolas"
            if not available_fonts: available_fonts = [default_font, "Courier New", "Arial"]
            if self.current_font_family.get() not in available_fonts : self.current_font_family.set(default_font if default_font in available_fonts else available_fonts[0])
        except Exception as e: logger.error(f"Failed to get font families: {e}", exc_info=True); available_fonts = ["Consolas", "Courier New"]; self.current_font_family.set("Consolas")
        self.font_family_menu = ctk.CTkOptionMenu(self.appearance_controls_frame, width=160, values=available_fonts, variable=self.current_font_family, command=self._update_font_and_style_configuration, dynamic_resizing=False)
        self.font_family_menu.pack(side=ctk.LEFT, padx=(0,10), pady=5)
        ctk.CTkLabel(self.appearance_controls_frame, text="Size:").pack(side=ctk.LEFT, padx=(0,2), pady=5)
        font_sizes = [str(s) for s in range(8, 25)]
        self.font_size_var_for_menu = ctk.StringVar(value=str(self.current_font_size.get()))
        self.font_size_menu = ctk.CTkOptionMenu(self.appearance_controls_frame, width=70, values=font_sizes, variable=self.font_size_var_for_menu, command=lambda s: [self.current_font_size.set(int(s)), self.font_size_var_for_menu.set(s), self._update_font_and_style_configuration()])
        self.font_size_menu.pack(side=ctk.LEFT, padx=(0,10), pady=5)
        self.word_wrap_checkbox = ctk.CTkCheckBox(self.appearance_controls_frame, text="Word Wrap", variable=self.word_wrap_var, command=self._update_font_and_style_configuration)
        self.word_wrap_checkbox.pack(side=ctk.LEFT, padx=5, pady=5)
        self.main_diff_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_diff_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.main_diff_frame.grid_columnconfigure(0, weight=1); self.main_diff_frame.grid_columnconfigure(1, weight=1)
        self.main_diff_frame.grid_rowconfigure(0, weight=1)
        self.pane_a = ctk.CTkFrame(self.main_diff_frame, corner_radius=3)
        self.pane_a.grid(row=0, column=0, sticky="nsew", padx=(0,2))
        self.pane_a.grid_rowconfigure(0, weight=1); self.pane_a.grid_columnconfigure(0, weight=0); self.pane_a.grid_columnconfigure(1, weight=1)
        self.line_numbers_a_widget = ctk.CTkTextbox(self.pane_a, width=50, activate_scrollbars=False)
        self.line_numbers_a_widget.grid(row=0, column=0, sticky="nsw")
        self.content_a_widget = ctk.CTkTextbox(self.pane_a, wrap=ctk.NONE, activate_scrollbars=True)
        self.content_a_widget.grid(row=0, column=1, sticky="nsew")
        self.pane_b = ctk.CTkFrame(self.main_diff_frame, corner_radius=3)
        self.pane_b.grid(row=0, column=1, sticky="nsew", padx=(2,0))
        self.pane_b.grid_rowconfigure(0, weight=1); self.pane_b.grid_columnconfigure(0, weight=0); self.pane_b.grid_columnconfigure(1, weight=1)
        self.line_numbers_b_widget = ctk.CTkTextbox(self.pane_b, width=50, activate_scrollbars=False)
        self.line_numbers_b_widget.grid(row=0, column=0, sticky="nsw")
        self.content_b_widget = ctk.CTkTextbox(self.pane_b, wrap=ctk.NONE, activate_scrollbars=True)
        self.content_b_widget.grid(row=0, column=1, sticky="nsew")
        logger.debug("Widgets created.")

    def _configure_all_tags_for_pane(self, content_widget, line_numbers_widget): # Same as before
        logger.debug(f"Configuring tags for content widget: {content_widget}")
        content_tb = getattr(content_widget, '_textbox', None); ln_tb = getattr(line_numbers_widget, '_textbox', None)
        font_fam = self.current_font_family.get(); font_sz = self.current_font_size.get()
        if content_tb:
            configure_tags(content_tb, style_name=self.current_pygments_style.get(), base_font_family=font_fam, base_font_size=font_sz)
            content_tb.tag_configure("line_del_bg", background="#401C1F"); content_tb.tag_configure("line_add_bg", background="#163B1F")
            content_tb.tag_configure("line_changed_bg", background="#443A1F")
            try: fg_color_val = content_widget.cget("fg_color"); placeholder_bg_color = fg_color_val[1] if isinstance(fg_color_val, (list, tuple)) and len(fg_color_val) > 1 else fg_color_val if isinstance(fg_color_val, str) else content_widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
            except Exception: placeholder_bg_color = "#2a2d30"
            content_tb.tag_configure("placeholder_bg", background=placeholder_bg_color)
        else: logger.error(f"Content widget _textbox not available for tag configuration.")
        if ln_tb:
            ln_font_size = font_sz - 1 if font_sz > 8 else font_sz; ln_font = (font_fam, ln_font_size)
            ln_tb.tag_configure("line_no", foreground="#586069", font=ln_font); ln_tb.tag_configure("line_no_changed", foreground="#B08827", font=ln_font)
            ln_tb.tag_configure("line_no_empty", foreground="#44474A", font=ln_font)
        else: logger.error(f"Line numbers widget _textbox not available for tag configuration.")

    def _setup_scrolling_sync(self): # Same as before
        logger.debug("Setting up scrolling synchronization (Side-by-Side)...")
        ca_tb = getattr(self.content_a_widget, '_textbox', None); cb_tb = getattr(self.content_b_widget, '_textbox', None)
        lna_tb = getattr(self.line_numbers_a_widget, '_textbox', None); lnb_tb = getattr(self.line_numbers_b_widget, '_textbox', None)
        if not (ca_tb and cb_tb and lna_tb and lnb_tb): logger.error("Not all textboxes available for scroll sync setup."); return
        ca_scrollbar = getattr(self.content_a_widget, '_y_scrollbar', None); cb_scrollbar = getattr(self.content_b_widget, '_y_scrollbar', None)
        def yscroll_proxy_factory(source_tb, other_content_tb, own_ln_tb, other_ln_tb, source_own_scrollbar):
            def proxy(*args):
                if source_own_scrollbar and hasattr(source_own_scrollbar, 'set'):
                    try: source_own_scrollbar.set(*args)
                    except Exception as e: logger.debug(f"Non-critical error setting scrollbar for {source_tb}: {e}")
                current_yview = source_tb.yview()
                if current_yview and len(current_yview) == 2:
                    try:
                        self.after_idle(lambda: other_content_tb.yview_moveto(current_yview[0]) if other_content_tb and other_content_tb != source_tb else None)
                        self.after_idle(lambda: own_ln_tb.yview_moveto(current_yview[0]) if own_ln_tb else None)
                        self.after_idle(lambda: other_ln_tb.yview_moveto(current_yview[0]) if other_ln_tb else None)
                    except TclError as e: logger.warning(f"TclError during yscroll_proxy sync: {e}")
            return proxy
        if ca_tb: ca_tb.configure(yscrollcommand=yscroll_proxy_factory(ca_tb, cb_tb, lna_tb, lnb_tb, ca_scrollbar))
        if cb_tb: cb_tb.configure(yscrollcommand=yscroll_proxy_factory(cb_tb, ca_tb, lnb_tb, lna_tb, cb_scrollbar))
        all_tbs_for_mousewheel = [tb for tb in [ca_tb, cb_tb, lna_tb, lnb_tb] if tb]
        def on_mousewheel_universal(event, source_tb_for_event):
            delta = 0
            if event.num == 4: delta = -1
            elif event.num == 5: delta = 1
            elif event.delta: delta = -1 * (event.delta // 120)
            else: return
            if delta != 0: source_tb_for_event.yview_scroll(delta, "units")
            return "break"
        for tb in all_tbs_for_mousewheel:
            tb.bind("<MouseWheel>", lambda e, current_tb=tb: on_mousewheel_universal(e, current_tb), add="+")
            tb.bind("<Button-4>", lambda e, current_tb=tb: on_mousewheel_universal(e, current_tb), add="+")
            tb.bind("<Button-5>", lambda e, current_tb=tb: on_mousewheel_universal(e, current_tb), add="+")
        logger.debug("Scrolling synchronization setup complete (Side-by-Side).")

    def load_file(self, file_id): # Same as before
        logger.info(f"Loading file for ID: {file_id}")
        filepath = filedialog.askopenfilename( title=f"Select File {file_id.upper()}")
        if not filepath: logger.debug("File load cancelled."); return
        logger.info(f"Selected filepath: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f: content_lines = f.readlines()
            logger.debug(f"File '{os.path.basename(filepath)}' loaded, {len(content_lines)} lines.")
        except Exception as e:
            logger.error(f"Error loading file {os.path.basename(filepath)}: {e}", exc_info=True)
            messagebox.showerror("File Load Error", f"Error loading file {os.path.basename(filepath)}:\n{e}")
            target_var = self.file_a_path_var if file_id == 'a' else self.file_b_path_var
            target_var.set(f"Error: {os.path.basename(filepath)}")
            if file_id == 'a': self.file_a_lines = None; self.lexer_a = None; self._clear_pane('a')
            else: self.file_b_lines = None; self.lexer_b = None; self._clear_pane('b')
            return
        current_lexer = get_lexer(filepath, "".join(content_lines[:20]))
        if file_id == 'a':
            self.file_a_path_var.set(filepath); self.file_a_lines = content_lines; self.lexer_a = current_lexer
            self._display_single_file('a')
        else:
            self.file_b_path_var.set(filepath); self.file_b_lines = content_lines; self.lexer_b = current_lexer
            self._display_single_file('b')
        if self.file_a_lines is not None and self.file_b_lines is not None:
            logger.info("Both files are loaded, showing diff.")
            self.after(50, self.show_diff_side_by_side)
        else: logger.info(f"File '{file_id}' loaded, waiting for the other file.")

    # --- CORRECTED _clear_pane ---
    def _clear_pane(self, pane_id):
        logger.debug(f"Clearing pane {pane_id}")
        if pane_id == 'a':
            widgets_to_clear = [self.content_a_widget, self.line_numbers_a_widget]
        elif pane_id == 'b':
            widgets_to_clear = [self.content_b_widget, self.line_numbers_b_widget]
        else: # 'all'
             widgets_to_clear = [self.content_a_widget, self.line_numbers_a_widget,
                                 self.content_b_widget, self.line_numbers_b_widget]

        for widget_wrapper in widgets_to_clear:
            if widget_wrapper and hasattr(widget_wrapper, 'configure'):
                try:
                    widget_wrapper.configure(state=ctk.NORMAL) # Enable to clear
                    tb = getattr(widget_wrapper, '_textbox', None)
                    if tb:
                        tb.delete("1.0", ctk.END)
                    # NOTE: We are NOT re-disabling here. The calling function
                    # (e.g., _display_single_file or show_diff_side_by_side)
                    # is responsible for disabling widgets *after* all content is populated.
                except Exception as e:
                    logger.error(f"Error during _clear_pane for widget {widget_wrapper}: {e}")
    # --- END OF CORRECTION ---


    def _display_single_file(self, pane_id):
        logger.info(f"Displaying single file content for pane: {pane_id}")
        if pane_id == 'a': target_content_widget, target_ln_widget, lines, lexer = self.content_a_widget, self.line_numbers_a_widget, self.file_a_lines, self.lexer_a
        elif pane_id == 'b': target_content_widget, target_ln_widget, lines, lexer = self.content_b_widget, self.line_numbers_b_widget, self.file_b_lines, self.lexer_b
        else: logger.error(f"Invalid pane_id for _display_single_file: {pane_id}"); return

        if lines is None: logger.debug(f"No lines available to display for pane {pane_id}"); self._clear_pane(pane_id); return

        self._clear_pane(pane_id) # Clears and leaves widgets NORMAL
        # Widgets are now NORMAL, ready for insert

        content_tb = getattr(target_content_widget, '_textbox', None); ln_tb = getattr(target_ln_widget, '_textbox', None)
        if not (content_tb and ln_tb): logger.error(f"Cannot display single file: _textbox missing for pane {pane_id}"); self._disable_text_widgets(); return # Disable all if error

        if not lines:
             logger.info(f"File for pane {pane_id} is empty."); ln_tb.insert("1.0", "1 \n", ("line_no",)); content_tb.insert("1.0", "<Empty File>\n", ("diff_common",))
        else:
            for i, line_content in enumerate(lines):
                line_num_str = str(i + 1)
                try: self._insert_line_into_pane(target_content_widget, target_ln_widget, line_num_str, line_content, content_tags=["diff_common"], ln_tags=("line_no",), lexer=lexer)
                except Exception as e: logger.error(f"Error displaying line {i+1} for single file {pane_id}: {e}", exc_info=True)
        
        # After populating this single pane, disable all text widgets
        # This is because the other pane might still be empty or showing its single content.
        # Full diff will re-enable and then disable all.
        self._disable_text_widgets()
        try: content_tb.yview_moveto(0.0); ln_tb.yview_moveto(0.0)
        except TclError: pass
        logger.debug(f"Single file display complete for pane {pane_id}")


    def _get_char_highlight_tags_for_pair(self, old_line_content, new_line_content): # Same
        old_tags, new_tags = [], []; s = difflib.SequenceMatcher(None, old_line_content, new_line_content, autojunk=False)
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == 'replace': old_tags.append(('char_highlight_del', i1, i2)); new_tags.append(('char_highlight_add', j1, j2))
            elif tag == 'delete': old_tags.append(('char_highlight_del', i1, i2))
            elif tag == 'insert': new_tags.append(('char_highlight_add', j1, j2))
        return old_tags, new_tags

    def _insert_line_into_pane(self, content_widget, ln_widget, line_num_str, line_content, content_tags=None, ln_tags=("line_no",), lexer=None, char_highlights=None, is_placeholder=False): # Same
        content_tb = getattr(content_widget, '_textbox', None); ln_tb = getattr(ln_widget, '_textbox', None)
        if not (content_tb and ln_tb): logger.error(f"Skipping insert: _textbox missing for {content_widget} or {ln_widget}."); return
        try:
            ln_tb.insert(ctk.END, f"{line_num_str.rjust(4)} \n", ln_tags)
            effective_content_tags = list(content_tags) if content_tags else []
            if is_placeholder:
                effective_content_tags.append("placeholder_bg"); content_tb.insert(ctk.END, "\n", tuple(effective_content_tags))
            else:
                if not line_content.endswith('\n'): line_content += '\n'
                highlight_line(content_tb, line_content, effective_content_tags, lexer, char_highlight_tags=char_highlights, content_start_offset=0)
        except TclError as e: logger.error(f"TclError inserting into {content_widget}/{ln_widget}: {e}. Line: '{line_content[:30]}'", exc_info=False)
        except Exception as e: logger.error(f"Error inserting into {content_widget}/{ln_widget}: {e}. Line: '{line_content[:30]}'", exc_info=True)

    def show_diff_side_by_side(self): # Same logic, ensure fixed _insert_line_into_pane is called
        logger.info("Showing diff (Side-by-Side)...")
        if self.file_a_lines is None or self.file_b_lines is None: logger.warning("show_diff_side_by_side called but files not ready."); return
        
        self._clear_pane('all') # Clears and leaves widgets NORMAL
        self._enable_text_widgets() # Explicitly enable all for the diff population process

        if not self.lexer_a: self.lexer_a = get_lexer(None, "")
        if not self.lexer_b: self.lexer_b = get_lexer(None, "")
        lines_a, lines_b = self.file_a_lines, self.file_b_lines
        s = difflib.SequenceMatcher(None, lines_a, lines_b, autojunk=False)
        opcodes = s.get_opcodes(); logger.debug(f"Generated {len(opcodes)} opcodes. A:{len(lines_a)}, B:{len(lines_b)}")

        if not opcodes:
            display_message_a, display_message_b = "", ""
            if not lines_a and not lines_b: display_message_a = "Both files are empty.\n"
            elif lines_a == lines_b: display_message_a = "Files are identical.\n"; display_message_b = "Files are identical.\n"
            elif not lines_a: display_message_a = "File A is empty.\n"; display_message_b = "\n"
            elif not lines_b: display_message_b = "File B is empty.\n"; display_message_a = "\n"
            else: display_message_a = "No programmatic differences found.\n"; display_message_b = "\n"
            logger.info(f"No opcodes. A: '{display_message_a.strip()}', B: '{display_message_b.strip()}'")
            max_len = max(len(lines_a), len(lines_b))
            if max_len == 0: max_len = 1
            for i in range(max_len):
                    line_a_c = lines_a[i] if i < len(lines_a) else (display_message_a if i == 0 and display_message_a else "\n")
                    num_a = str(i+1) if i < len(lines_a) else (" " if i < max_len else "")
                    is_ph_a = i >= len(lines_a)
                    line_b_c = lines_b[i] if i < len(lines_b) else (display_message_b if i == 0 and display_message_b else "\n")
                    num_b = str(i+1) if i < len(lines_b) else (" " if i < max_len else "")
                    is_ph_b = i >= len(lines_b)
                    self._insert_line_into_pane(self.content_a_widget, self.line_numbers_a_widget, num_a, line_a_c, lexer=self.lexer_a if not is_ph_a and i < len(lines_a) else None, is_placeholder=is_ph_a and not (i==0 and display_message_a and line_a_c.strip()))
                    self._insert_line_into_pane(self.content_b_widget, self.line_numbers_b_widget, num_b, line_b_c, lexer=self.lexer_b if not is_ph_b and i < len(lines_b) else None, is_placeholder=is_ph_b and not (i==0 and display_message_b and line_b_c.strip()))
            self._disable_text_widgets(); return

        line_num_a, line_num_b = 0, 0
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                for idx in range(i2 - i1):
                    line_num_a += 1; line_num_b += 1; line_content = lines_a[i1 + idx]
                    self._insert_line_into_pane(self.content_a_widget, self.line_numbers_a_widget, str(line_num_a), line_content, lexer=self.lexer_a)
                    self._insert_line_into_pane(self.content_b_widget, self.line_numbers_b_widget, str(line_num_b), line_content, lexer=self.lexer_b)
            elif tag == 'replace':
                len_a_chunk, len_b_chunk = i2 - i1, j2 - j1; max_chunk_len = max(len_a_chunk, len_b_chunk)
                for i in range(max_chunk_len):
                    char_highlights_a, char_highlights_b = None, None
                    line_a_content_for_char_diff = lines_a[i1 + i].rstrip('\n') if i < len_a_chunk else ""
                    line_b_content_for_char_diff = lines_b[j1 + i].rstrip('\n') if i < len_b_chunk else ""
                    if i < len_a_chunk and i < len_b_chunk : char_highlights_a, char_highlights_b = self._get_char_highlight_tags_for_pair(line_a_content_for_char_diff, line_b_content_for_char_diff)
                    if i < len_a_chunk:
                        line_num_a += 1; line_a_content = lines_a[i1 + i]; tags_a = ["line_changed_bg"] if i < len_b_chunk else ["line_del_bg"]; ln_tags_a = ("line_no_changed",) if i < len_b_chunk else ("line_no",)
                        self._insert_line_into_pane(self.content_a_widget, self.line_numbers_a_widget, str(line_num_a), line_a_content, tags_a, ln_tags_a, self.lexer_a, char_highlights_a)
                    else: self._insert_line_into_pane(self.content_a_widget, self.line_numbers_a_widget, "", "", ln_tags=("line_no_empty",), is_placeholder=True)
                    if i < len_b_chunk:
                        line_num_b += 1; line_b_content = lines_b[j1 + i]; tags_b = ["line_changed_bg"] if i < len_a_chunk else ["line_add_bg"]; ln_tags_b = ("line_no_changed",) if i < len_a_chunk else ("line_no",)
                        self._insert_line_into_pane(self.content_b_widget, self.line_numbers_b_widget, str(line_num_b), line_b_content, tags_b, ln_tags_b, self.lexer_b, char_highlights_b)
                    else: self._insert_line_into_pane(self.content_b_widget, self.line_numbers_b_widget, "", "", ln_tags=("line_no_empty",), is_placeholder=True)
            elif tag == 'delete':
                for idx in range(i2 - i1):
                    line_num_a += 1; line_a_content = lines_a[i1 + idx]
                    self._insert_line_into_pane(self.content_a_widget, self.line_numbers_a_widget, str(line_num_a), line_a_content, ["line_del_bg"], lexer=self.lexer_a)
                    self._insert_line_into_pane(self.content_b_widget, self.line_numbers_b_widget, "", "", ln_tags=("line_no_empty",), is_placeholder=True)
            elif tag == 'insert':
                for idx in range(j2 - j1):
                    line_num_b += 1; line_b_content = lines_b[j1 + idx]
                    self._insert_line_into_pane(self.content_a_widget, self.line_numbers_a_widget, "", "", ln_tags=("line_no_empty",), is_placeholder=True)
                    self._insert_line_into_pane(self.content_b_widget, self.line_numbers_b_widget, str(line_num_b), line_b_content, ["line_add_bg"], lexer=self.lexer_b)

        self._disable_text_widgets()
        for widget_wrapper in [self.content_a_widget, self.content_b_widget, self.line_numbers_a_widget, self.line_numbers_b_widget]:
            tb = getattr(widget_wrapper, '_textbox', None)
            if tb:
                try: tb.yview_moveto(0.0)
                except TclError: pass
        logger.info("Diff display complete (Side-by-Side).")

# Global Exception Hook and Main Execution
def global_excepthook(exctype, value, traceback_obj):
    logger.critical(f"Unhandled exception caught by global hook: {exctype.__name__}: {value}", exc_info=(exctype, value, traceback_obj))
    try:
        if not issubclass(exctype, (SystemExit, KeyboardInterrupt)):
             messagebox.showerror("Unhandled Application Error", f"An unexpected error occurred:\n{exctype.__name__}: {value}\n\nCheck logs.")
    except Exception as e: logger.error(f"Failed to show global error messagebox: {e}")
    sys.__excepthook__(exctype, value, traceback_obj)

if __name__ == "__main__":
    sys.excepthook = global_excepthook
    logger.info("================ Application Starting (Side-by-Side) ================")
    app = None
    try:
        app = DiffApp()
        app.mainloop()
        logger.info("================ Application Exited Normally (Side-by-Side) ================")
    except SystemExit:
        logger.info("Application exited via sys.exit().")
    except KeyboardInterrupt:
        logger.info("Application interrupted by user (KeyboardInterrupt).")
        if app and hasattr(app, 'destroy'): app.destroy()
    except Exception as e:
        logger.critical(f"CRITICAL ERROR during app instantiation or mainloop(): {e}", exc_info=True)
        if app and hasattr(app, 'destroy'): app.destroy()
        sys.exit(1)