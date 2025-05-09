# main.py - FINAL THOROUGH SYNTAX CHECK
import customtkinter as ctk
from tkinter import filedialog, messagebox, TclError, font as tkfont, simpledialog
import difflib
import os
import re
import logging
import sys
import json

# --- Global Logging Setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
        # logging.FileHandler("diff_app_sbs.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

try:
    from syntax_highlighter import get_lexer, configure_tags, highlight_line, get_all_styles
except ImportError:
    logger.critical("Failed to import syntax_highlighter.py. Ensure it exists and has no syntax errors.")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Error during syntax_highlighter import: {e}", exc_info=True)
    sys.exit(1)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

MAX_HISTORY_ITEMS = 10
HISTORY_FILE = "diff_history.json"

class DiffApp(ctk.CTk):
    def __init__(self):
        logger.info("Initializing DiffApp (Split View)...")
        try:
            super().__init__()
            self.title("GitDiff Viewer - Split View Options")
            self.geometry("1750x950")

            self.file_a_path_var = ctk.StringVar(value="<File A>")
            self.file_b_path_var = ctk.StringVar(value="<File B>")
            self.file_a_full_path, self.file_b_full_path = None, None
            self.file_a_lines_orig, self.file_b_lines_orig = None, None
            self.file_a_lines_processed, self.file_b_lines_processed = None, None
            self.lexer_a, self.lexer_b = None, None
            self.current_font_family = ctk.StringVar(value="Consolas")
            self.current_font_size = ctk.IntVar(value=10)
            self.current_pygments_style = ctk.StringVar(value='monokai')
            self.word_wrap_var = ctk.BooleanVar(value=False)
            self.ignore_whitespace_var = ctk.BooleanVar(value=False)
            self.ignore_case_var = ctk.BooleanVar(value=False)
            self.ignore_line_endings_var = ctk.BooleanVar(value=False)
            self.fold_equal_blocks_var = ctk.BooleanVar(value=False)
            self.view_mode_var = ctk.StringVar(value="Side-by-Side")
            self.search_query_var = ctk.StringVar()
            self.all_search_results, self.current_search_highlight_idx = [], -1 # Combined from both panes
            self.search_tag_name = "search_highlight_tag"
            self.diff_block_tags, self.current_diff_block_idx = [], -1
            self.file_history = self._load_file_history()
            self.editing_enabled_var = ctk.BooleanVar(value=False)
            self.file_a_modified, self.file_b_modified = ctk.BooleanVar(value=False), ctk.BooleanVar(value=False)

            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=0); self.grid_rowconfigure(2, weight=0)
            self.grid_rowconfigure(3, weight=1); self.grid_rowconfigure(4, weight=0)

            self._create_widgets()
            self._re_grid_diff_panes()
            self._update_font_and_style_configuration()
            self._setup_scrolling_sync()
            self._disable_text_widgets()
            logger.info("DiffApp initialized successfully.")
        except Exception as e:
            logger.critical(f"CRITICAL ERROR during DiffApp __init__: {e}", exc_info=True)
            try: messagebox.showerror("Fatal Error", f"App failed to start:\n{e}\n\nCheck console.")
            except: pass
            if hasattr(self, 'destroy'): self.destroy()
            sys.exit(1)

    def _update_font_and_style_configuration(self, event=None):
        logger.info(f"Updating font/style/wrap/options...")
        new_content_font = (self.current_font_family.get(), self.current_font_size.get())
        new_ln_font = (self.current_font_family.get(), max(8, self.current_font_size.get() - 1))
        wrap_mode = ctk.WORD if self.word_wrap_var.get() else ctk.NONE
        widgets_cfg = {
            self.content_a_widget: {'font': new_content_font, 'wrap': wrap_mode},
            self.content_b_widget: {'font': new_content_font, 'wrap': wrap_mode},
            self.line_numbers_a_widget: {'font': new_ln_font},
            self.line_numbers_b_widget: {'font': new_ln_font}
        }
        for widget_wrapper, config in widgets_cfg.items():
            tb = getattr(widget_wrapper, '_textbox', None)
            if tb:
                try: tb.configure(**config)
                except Exception as e: logger.error(f"Error configuring {widget_wrapper}: {e}")
        self._configure_all_tags_for_pane(self.content_a_widget, self.line_numbers_a_widget)
        self._configure_all_tags_for_pane(self.content_b_widget, self.line_numbers_b_widget)
        if self.file_a_lines_orig is not None and self.file_b_lines_orig is not None:
            self.show_diff()
        elif self.file_a_lines_orig is not None: self._display_single_file('a')
        elif self.file_b_lines_orig is not None: self._display_single_file('b')

    def _manage_text_widget_state(self, state_to_set, manage_content_only=False):
        if manage_content_only: widgets_to_set = [self.content_a_widget, self.content_b_widget]
        else: widgets_to_set = [self.content_a_widget, self.line_numbers_a_widget, self.content_b_widget, self.line_numbers_b_widget]
        for widget in widgets_to_set:
            if widget and hasattr(widget, 'configure'):
                try: widget.configure(state=state_to_set)
                except Exception as e: logger.error(f"Error setting state {state_to_set} for {widget}: {e}")
    def _disable_text_widgets(self, content_only=False): self._manage_text_widget_state(ctk.DISABLED, content_only)
    def _enable_text_widgets(self, content_only=False): self._manage_text_widget_state(ctk.NORMAL, content_only)

    def _create_widgets(self):
        logger.debug("Creating widgets...")
        self.top_bar = ctk.CTkFrame(self, corner_radius=0); self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        ctk.CTkButton(self.top_bar, text="File A", width=80, command=lambda: self.load_file('a')).pack(side=ctk.LEFT, padx=(0,2), pady=5)
        self.file_a_label = ctk.CTkLabel(self.top_bar, textvariable=self.file_a_path_var, anchor="w"); self.file_a_label.pack(side=ctk.LEFT, padx=(0,5), pady=5, fill=ctk.X, expand=True)
        ctk.CTkButton(self.top_bar, text="Save A", width=70, command=lambda: self._save_file('a')).pack(side=ctk.LEFT, padx=(0,10), pady=5)
        ctk.CTkButton(self.top_bar, text="File B", width=80, command=lambda: self.load_file('b')).pack(side=ctk.LEFT, padx=(0,2), pady=5)
        self.file_b_label = ctk.CTkLabel(self.top_bar, textvariable=self.file_b_path_var, anchor="w"); self.file_b_label.pack(side=ctk.LEFT, padx=(0,5), pady=5, fill=ctk.X, expand=True)
        ctk.CTkButton(self.top_bar, text="Save B", width=70, command=lambda: self._save_file('b')).pack(side=ctk.LEFT, padx=(0,10), pady=5)
        initial_history_display = [f"{os.path.basename(a)} vs {os.path.basename(b)}" for a,b in self.file_history] or ["No History"]
        self.history_menu_button = ctk.CTkOptionMenu(self.top_bar, values=initial_history_display, width=150, command=self._handle_history_selection)
        self.history_menu_button.pack(side=ctk.LEFT, padx=(5,0), pady=5); self.history_menu_button.set(initial_history_display[0])

        self.appearance_bar = ctk.CTkFrame(self, corner_radius=0); self.appearance_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))
        ctk.CTkLabel(self.appearance_bar, text="View:").pack(side=ctk.LEFT, padx=(0,2), pady=5)
        ctk.CTkOptionMenu(self.appearance_bar, width=130, values=["Side-by-Side", "Top-Bottom"], variable=self.view_mode_var, command=self._toggle_view_mode).pack(side=ctk.LEFT, padx=(0,10), pady=5)
        ctk.CTkLabel(self.appearance_bar, text="Style:").pack(side=ctk.LEFT, padx=(0,2), pady=5)
        try: py_styles=sorted(list(get_all_styles())); d_stl='monokai'; self.current_pygments_style.set(d_stl if d_stl in py_styles else py_styles[0] if py_styles else d_stl)
        except: py_styles=['monokai','native']; self.current_pygments_style.set('monokai')
        ctk.CTkOptionMenu(self.appearance_bar,width=120,values=py_styles,variable=self.current_pygments_style,command=self._trigger_re_render).pack(side=ctk.LEFT,padx=(0,5),pady=5)
        ctk.CTkLabel(self.appearance_bar, text="Font:").pack(side=ctk.LEFT, padx=(5,2), pady=5)
        try: av_fonts=sorted([f for f in tkfont.families() if not f.startswith('@')]); d_fnt="Consolas"; self.current_font_family.set(d_fnt if d_fnt in av_fonts else av_fonts[0] if av_fonts else d_fnt)
        except: av_fonts=["Consolas","Courier New"]; self.current_font_family.set("Consolas")
        ctk.CTkOptionMenu(self.appearance_bar,width=150,values=av_fonts,variable=self.current_font_family,command=self._trigger_re_render,dynamic_resizing=False).pack(side=ctk.LEFT,padx=(0,5),pady=5)
        ctk.CTkLabel(self.appearance_bar, text="Size:").pack(side=ctk.LEFT, padx=(5,2), pady=5)
        f_sizes=[str(s) for s in range(8,25)]; self.font_size_var_menu=ctk.StringVar(value=str(self.current_font_size.get()))
        ctk.CTkOptionMenu(self.appearance_bar,width=60,values=f_sizes,variable=self.font_size_var_menu,command=lambda s:[self.current_font_size.set(int(s)),self.font_size_var_menu.set(s),self._trigger_re_render()]).pack(side=ctk.LEFT,padx=(0,5),pady=5)
        ctk.CTkCheckBox(self.appearance_bar,text="Wrap",variable=self.word_wrap_var,command=self._trigger_re_render).pack(side=ctk.LEFT,padx=5,pady=5)
        ctk.CTkCheckBox(self.appearance_bar, text="Ignore Whitespace", variable=self.ignore_whitespace_var, command=self._trigger_re_render).pack(side=ctk.LEFT, padx=5, pady=5)
        ctk.CTkCheckBox(self.appearance_bar, text="Ignore Case", variable=self.ignore_case_var, command=self._trigger_re_render).pack(side=ctk.LEFT, padx=5, pady=5)
        ctk.CTkCheckBox(self.appearance_bar, text="Ignore Line Endings", variable=self.ignore_line_endings_var, command=self._trigger_re_render).pack(side=ctk.LEFT, padx=5, pady=5)
        ctk.CTkCheckBox(self.appearance_bar, text="Fold Equal", variable=self.fold_equal_blocks_var, command=self._trigger_re_render).pack(side=ctk.LEFT, padx=(10,5), pady=5)
        ctk.CTkCheckBox(self.appearance_bar, text="Edit Mode", variable=self.editing_enabled_var, command=self._toggle_edit_mode).pack(side=ctk.LEFT, padx=(5,5), pady=5)
        self.recompare_button = ctk.CTkButton(self.appearance_bar, text="Re-Compare", width=100, command=self.show_diff, state=ctk.DISABLED)
        self.recompare_button.pack(side=ctk.LEFT, padx=5, pady=5)

        self.nav_search_bar = ctk.CTkFrame(self, corner_radius=0); self.nav_search_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,5))
        ctk.CTkButton(self.nav_search_bar, text="Prev Diff", width=70, command=self.navigate_to_prev_diff).pack(side=ctk.LEFT, padx=(0,5), pady=5)
        ctk.CTkButton(self.nav_search_bar, text="Next Diff", width=70, command=self.navigate_to_next_diff).pack(side=ctk.LEFT, padx=(0,5), pady=5)
        ctk.CTkButton(self.nav_search_bar, text="Go To Line", width=80, command=self._go_to_line).pack(side=ctk.LEFT, padx=(0,10), pady=5)
        self.search_entry=ctk.CTkEntry(self.nav_search_bar,placeholder_text="Search...",textvariable=self.search_query_var); self.search_entry.pack(side=ctk.LEFT,padx=(0,5),pady=5,fill=ctk.X,expand=True)
        self.search_entry.bind("<Return>", self.perform_search)
        ctk.CTkButton(self.nav_search_bar,text="Find",width=50,command=self.perform_search).pack(side=ctk.LEFT,padx=(0,5),pady=5)
        ctk.CTkButton(self.nav_search_bar,text="Clear",width=50,command=self.clear_search_highlights).pack(side=ctk.LEFT,padx=(0,0),pady=5)

        self.main_diff_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent"); self.main_diff_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
        # Panes created here but gridded by _re_grid_diff_panes
        self.pane_a = ctk.CTkFrame(self.main_diff_frame, corner_radius=3)
        self.pane_a.grid_rowconfigure(0, weight=1); self.pane_a.grid_columnconfigure(0, weight=0); self.pane_a.grid_columnconfigure(1, weight=1)
        self.line_numbers_a_widget = ctk.CTkTextbox(self.pane_a, width=50, activate_scrollbars=False); self.line_numbers_a_widget.grid(row=0, column=0, sticky="nsw")
        self.content_a_widget = ctk.CTkTextbox(self.pane_a, wrap=ctk.NONE, activate_scrollbars=True); self.content_a_widget.grid(row=0, column=1, sticky="nsew")
        self.content_a_widget._textbox.bind("<<Modified>>", lambda e, fid='a': self._on_text_modified(fid, e), add="+")
        self.pane_b = ctk.CTkFrame(self.main_diff_frame, corner_radius=3)
        self.pane_b.grid_rowconfigure(0, weight=1); self.pane_b.grid_columnconfigure(0, weight=0); self.pane_b.grid_columnconfigure(1, weight=1)
        self.line_numbers_b_widget = ctk.CTkTextbox(self.pane_b, width=50, activate_scrollbars=False); self.line_numbers_b_widget.grid(row=0, column=0, sticky="nsw")
        self.content_b_widget = ctk.CTkTextbox(self.pane_b, wrap=ctk.NONE, activate_scrollbars=True); self.content_b_widget.grid(row=0, column=1, sticky="nsew")
        self.content_b_widget._textbox.bind("<<Modified>>", lambda e, fid='b': self._on_text_modified(fid, e), add="+")
        
        self.status_bar = ctk.CTkFrame(self, corner_radius=0, height=25); self.status_bar.grid(row=4, column=0, sticky="ew", padx=10, pady=(5,10))
        self.diff_stats_label = ctk.CTkLabel(self.status_bar, text="Diff Stats: -"); self.diff_stats_label.pack(side=ctk.LEFT, padx=10)
        logger.debug("Widgets created.")

    def _re_grid_diff_panes(self):
        logger.debug(f"Re-gridding diff panes for mode: {self.view_mode_var.get()}")
        self.pane_a.grid_forget(); self.pane_b.grid_forget()
        if self.view_mode_var.get() == "Side-by-Side":
            self.main_diff_frame.grid_columnconfigure(0, weight=1); self.main_diff_frame.grid_columnconfigure(1, weight=1)
            self.main_diff_frame.grid_rowconfigure(0, weight=1); self.main_diff_frame.grid_rowconfigure(1, weight=0)
            self.pane_a.grid(row=0, column=0, sticky="nsew", padx=(0,2)); self.pane_b.grid(row=0, column=1, sticky="nsew", padx=(2,0))
        elif self.view_mode_var.get() == "Top-Bottom":
            self.main_diff_frame.grid_columnconfigure(0, weight=1); self.main_diff_frame.grid_columnconfigure(1, weight=0)
            self.main_diff_frame.grid_rowconfigure(0, weight=1); self.main_diff_frame.grid_rowconfigure(1, weight=1)
            self.pane_a.grid(row=0, column=0, sticky="nsew", pady=(0,2)); self.pane_b.grid(row=1, column=0, sticky="nsew", pady=(2,0))
        self.show_diff() # Re-render content with new layout

    def _toggle_view_mode(self, new_mode: str):
        logger.info(f"Toggling view mode to: {new_mode}")
        self.view_mode_var.set(new_mode)
        self._re_grid_diff_panes() # This will call show_diff

    def show_diff(self):
        # Currently only side-by-side is implemented, but this provides a hook for other views
        if self.file_a_lines_orig is not None and self.file_b_lines_orig is not None:
            self.show_diff_side_by_side()
        elif self.file_a_lines_orig is not None: self._display_single_file('a')
        elif self.file_b_lines_orig is not None: self._display_single_file('b')
        else: self._clear_pane('all') # Both are None

    def _configure_all_tags_for_pane(self, content_widget, line_numbers_widget):
        content_tb = getattr(content_widget, '_textbox', None); ln_tb = getattr(line_numbers_widget, '_textbox', None)
        font_fam = self.current_font_family.get(); font_sz = self.current_font_size.get()
        if content_tb:
            configure_tags(content_tb, style_name=self.current_pygments_style.get(), base_font_family=font_fam, base_font_size=font_sz)
            content_tb.tag_configure("line_del_bg", background="#401C1F"); content_tb.tag_configure("line_add_bg", background="#163B1F")
            content_tb.tag_configure("line_changed_bg", background="#443A1F"); content_tb.tag_configure(self.search_tag_name, background="#FFA500", foreground="black")
            try: p_bg = content_widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkTextbox"]["fg_color"])
            except: p_bg = "#2a2d30"
            content_tb.tag_configure("placeholder_bg", background=p_bg)
            content_tb.tag_configure("folded_block", foreground="#666666", font=(font_fam, max(8,font_sz-1), "italic"))
        if ln_tb:
            ln_font = (font_fam, max(8,font_sz-1))
            ln_tb.tag_configure("line_no", foreground="#586069", font=ln_font); ln_tb.tag_configure("line_no_changed", foreground="#B08827", font=ln_font)
            ln_tb.tag_configure("line_no_empty", foreground="#44474A", font=ln_font)

    def _setup_scrolling_sync(self):
        logger.debug("Setting up scrolling synchronization...")
        ca_tb, cb_tb = getattr(self.content_a_widget,'_textbox',None), getattr(self.content_b_widget,'_textbox',None)
        lna_tb, lnb_tb = getattr(self.line_numbers_a_widget,'_textbox',None), getattr(self.line_numbers_b_widget,'_textbox',None)
        if not all([ca_tb, cb_tb, lna_tb, lnb_tb]): logger.error("Scroll sync setup failed: textboxes missing."); return
        ca_scrl, cb_scrl = getattr(self.content_a_widget,'_y_scrollbar',None), getattr(self.content_b_widget,'_y_scrollbar',None)

        def make_proxy(src_tb, other_content_tb, own_ln_tb, other_ln_tb, src_scrollbar):
            def proxy(*args):
                if src_scrollbar and hasattr(src_scrollbar,'set'):
                    try: src_scrollbar.set(*args)
                    except Exception as e: logger.debug(f"Non-critical error setting scrollbar for {src_tb}: {e}")
                yview = src_tb.yview()
                if yview and len(yview) == 2:
                    y0 = yview[0]
                    if other_content_tb and other_content_tb != src_tb: self.after_idle(lambda tb=other_content_tb, y_pos=y0: tb.yview_moveto(y_pos) if tb and tb.winfo_exists() else None)
                    if own_ln_tb: self.after_idle(lambda tb=own_ln_tb, y_pos=y0: tb.yview_moveto(y_pos) if tb and tb.winfo_exists() else None)
                    if other_ln_tb: self.after_idle(lambda tb=other_ln_tb, y_pos=y0: tb.yview_moveto(y_pos) if tb and tb.winfo_exists() else None)
            return proxy

        if ca_tb: ca_tb.configure(yscrollcommand=make_proxy(ca_tb, cb_tb, lna_tb, lnb_tb, ca_scrl))
        if cb_tb: cb_tb.configure(yscrollcommand=make_proxy(cb_tb, ca_tb, lnb_tb, lna_tb, cb_scrl))

        all_tbs = [ca_tb, cb_tb, lna_tb, lnb_tb]
        def on_mousewheel(event, src_tb):
            delta = 0
            if event.num == 4: delta = -1
            elif event.num == 5: delta = 1
            elif event.delta: delta = -1 * (event.delta // 120)
            else: return
            if delta != 0: src_tb.yview_scroll(delta, "units")
            return "break"
        for tb in all_tbs:
            if tb:
                tb.bind("<MouseWheel>", lambda e, t=tb: on_mousewheel(e,t), add="+")
                tb.bind("<Button-4>", lambda e, t=tb: on_mousewheel(e,t), add="+")
                tb.bind("<Button-5>", lambda e, t=tb: on_mousewheel(e,t), add="+")
        logger.debug("Scrolling sync setup complete.")

    def _process_lines_for_diff(self, lines):
        if lines is None: return None
        processed_lines = list(lines) # Start with a copy of original lines (with their original endings)
        if self.ignore_line_endings_var.get():
            processed_lines = [line.rstrip('\r\n') + '\n' for line in processed_lines] # Normalize to \n
        if self.ignore_whitespace_var.get(): # Applied after line ending normalization if active
            # Strips all leading/trailing whitespace from the content of the line
            processed_lines = [line.strip() + ('\n' if line.endswith('\n') else '') for line in processed_lines]
        if self.ignore_case_var.get():
            processed_lines = [line.lower() for line in processed_lines]
        return processed_lines

    def _load_file_content(self, file_id_char, filepath):
        logger.debug(f"Loading content for pane {file_id_char} from: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f: lines_orig = f.readlines()
            logger.debug(f"File '{os.path.basename(filepath)}' loaded, {len(lines_orig)} lines.")
            lexer = get_lexer(filepath, "".join(lines_orig[:20]))
            if file_id_char == 'a':
                self.file_a_full_path = filepath
                self.file_a_path_var.set(os.path.basename(filepath)); self.file_a_lines_orig = lines_orig; self.lexer_a = lexer
                self.file_a_modified.set(False)
            elif file_id_char == 'b':
                self.file_b_full_path = filepath
                self.file_b_path_var.set(os.path.basename(filepath)); self.file_b_lines_orig = lines_orig; self.lexer_b = lexer
                self.file_b_modified.set(False)
            return True
        except Exception as e:
            logger.error(f"Error loading file content from {filepath}: {e}", exc_info=True)
            messagebox.showerror("Load Error", f"Could not load file:\n{filepath}\n\n{e}")
            path_var = self.file_a_path_var if file_id_char == 'a' else self.file_b_path_var; path_var.set(f"<Error>")
            if file_id_char == 'a': self.file_a_lines_orig,self.lexer_a,self.file_a_full_path = None,None,None; self._clear_pane('a'); self.file_a_modified.set(False)
            else: self.file_b_lines_orig,self.lexer_b,self.file_b_full_path = None,None,None; self._clear_pane('b'); self.file_b_modified.set(False)
            return False

    def load_file(self, file_id_char):
        logger.info(f"Initiating file load for pane: {file_id_char}")
        filepath = filedialog.askopenfilename(title=f"Select File {file_id_char.upper()}")
        if not filepath: logger.debug("File selection cancelled."); return

        if self._load_file_content(file_id_char, filepath):
            self._display_single_file(file_id_char)
            if self.file_a_lines_orig is not None and self.file_b_lines_orig is not None:
                logger.info("Both files are now loaded, queueing diff.")
                self.after(50, self.show_diff) # Use generic show_diff
                if self.file_a_full_path and self.file_b_full_path:
                    self._add_to_file_history(self.file_a_full_path, self.file_b_full_path)
            else: logger.info(f"File '{file_id_char}' loaded, waiting for the other file.")

    def _clear_pane(self, pane_id):
        logger.debug(f"Clearing pane {pane_id}")
        widgets_map = {
            'a': [self.content_a_widget, self.line_numbers_a_widget],
            'b': [self.content_b_widget, self.line_numbers_b_widget],
            'all': [self.content_a_widget, self.line_numbers_a_widget, self.content_b_widget, self.line_numbers_b_widget]
        }
        for widget_wrapper in widgets_map.get(pane_id, []):
            if widget_wrapper and hasattr(widget_wrapper, 'configure'):
                try:
                    widget_wrapper.configure(state=ctk.NORMAL)
                    tb = getattr(widget_wrapper, '_textbox', None)
                    if tb: tb.delete("1.0", ctk.END)
                except Exception as e: logger.error(f"Error clearing {widget_wrapper}: {e}")

    def _display_single_file(self, pane_id):
        logger.info(f"Displaying single file for pane: {pane_id}")
        is_editing = self.editing_enabled_var.get()
        if pane_id == 'a': content_w,ln_w,lines,lex,mod_var = self.content_a_widget,self.line_numbers_a_widget,self.file_a_lines_orig,self.lexer_a,self.file_a_modified
        elif pane_id == 'b': content_w,ln_w,lines,lex,mod_var = self.content_b_widget,self.line_numbers_b_widget,self.file_b_lines_orig,self.lexer_b,self.file_b_modified
        else: return
        
        self._clear_pane(pane_id) # Clears and leaves NORMAL
        
        content_tb, ln_tb = getattr(content_w,'_textbox',None), getattr(ln_w,'_textbox',None)
        if not (content_tb and ln_tb): self._manage_text_widget_state(ctk.DISABLED, content_only=is_editing); return

        if lines is None: content_tb.insert("1.0", f"<File {pane_id.upper()} not loaded>\n")
        elif not lines: ln_tb.insert("1.0", "1 \n",("line_no",)); content_tb.insert("1.0", "<Empty File>\n",("diff_common",))
        else:
            for i, line in enumerate(lines):
                self._insert_line_into_pane(content_w, ln_w, str(i+1), line, ["diff_common"],("line_no",), lex)
        
        mod_var.set(False); self._update_file_label_modified_state()
        content_w.configure(state=ctk.NORMAL if is_editing else ctk.DISABLED)
        ln_w.configure(state=ctk.DISABLED)
        try: 
            if content_tb: content_tb.yview_moveto(0.0)
            if ln_tb: ln_tb.yview_moveto(0.0)
        except TclError: pass
        logger.debug(f"Single file display complete for pane {pane_id}")

    def _get_char_highlight_tags_for_pair(self, old_line, new_line):
        old_t, new_t = [],[]; s=difflib.SequenceMatcher(None,old_line,new_line,autojunk=False)
        for tag,i1,i2,j1,j2 in s.get_opcodes():
            if tag=='replace': old_t.append(('char_highlight_del',i1,i2)); new_t.append(('char_highlight_add',j1,j2))
            elif tag=='delete': old_t.append(('char_highlight_del',i1,i2))
            elif tag=='insert': new_t.append(('char_highlight_add',j1,j2))
        return old_t, new_t

    def _insert_line_into_pane(self, content_widget, ln_widget, line_num_str, line_content,
                               content_tags=None, ln_tags=("line_no",), lexer=None,
                               char_highlights=None, is_placeholder=False, is_folded_summary=False):
        content_tb = getattr(content_widget, '_textbox', None); ln_tb = getattr(ln_widget, '_textbox', None)
        if not (content_tb and ln_tb): logger.error(f"Skipping insert: _textbox missing."); return
        try:
            ln_tb.insert(ctk.END, f"{line_num_str.rjust(4)} \n", ln_tags)
            eff_tags = list(content_tags) if content_tags else []
            if is_placeholder: eff_tags.append("placeholder_bg"); content_tb.insert(ctk.END, "\n", tuple(eff_tags))
            elif is_folded_summary: eff_tags.append("folded_block"); content_tb.insert(ctk.END, line_content, tuple(eff_tags))
            else:
                if not line_content.endswith('\n'): line_content += '\n'
                highlight_line(content_tb, line_content, eff_tags, lexer, char_highlights, 0)
        except Exception as e: logger.error(f"Error inserting line: {e}. Line: '{str(line_content)[:30]}'", exc_info=True)

    def show_diff_side_by_side(self):
        logger.info("Showing diff (Side-by-Side)...")
        if self.file_a_lines_orig is None or self.file_b_lines_orig is None:
            logger.warning("Diff attempt with one or both original files not loaded."); return
        
        self._clear_pane('all')
        self._manage_text_widget_state(ctk.NORMAL if self.editing_enabled_var.get() else ctk.DISABLED, content_only=True)
        self.line_numbers_a_widget.configure(state=ctk.NORMAL); self.line_numbers_b_widget.configure(state=ctk.NORMAL)

        self.file_a_lines_processed = self._process_lines_for_diff(self.file_a_lines_orig)
        self.file_b_lines_processed = self._process_lines_for_diff(self.file_b_lines_orig)
        lines_a_diff = self.file_a_lines_processed if self.file_a_lines_processed is not None else []
        lines_b_diff = self.file_b_lines_processed if self.file_b_lines_processed is not None else []
        lines_a_disp = self.file_a_lines_orig if self.file_a_lines_orig is not None else []
        lines_b_disp = self.file_b_lines_orig if self.file_b_lines_orig is not None else []

        if not self.lexer_a: self.lexer_a = get_lexer(None,"")
        if not self.lexer_b: self.lexer_b = get_lexer(None,"")
        s = difflib.SequenceMatcher(None, lines_a_diff, lines_b_diff, autojunk=False)
        opcodes = s.get_opcodes(); logger.debug(f"Opcodes: {len(opcodes)}. A_diff:{len(lines_a_diff)}, B_diff:{len(lines_b_diff)}")
        added, deleted, changed_blocks = 0,0,0; self.diff_block_tags = []

        if not opcodes:
            msg_a, msg_b = "","";
            if not lines_a_disp and not lines_b_disp: msg_a="Both files empty.\n"
            elif lines_a_disp==lines_b_disp: msg_a="Files identical.\n"; msg_b="Files identical.\n"
            else: msg_a="File A content (or no diffs).\n" if lines_a_disp else "File A empty.\n"; msg_b="File B content (or no diffs).\n" if lines_b_disp else "File B empty.\n"
            logger.info(f"No opcodes. A: '{msg_a.strip()}', B: '{msg_b.strip()}'")
            max_l = max(len(lines_a_disp), len(lines_b_disp))
            if max_l == 0 : max_l = 1
            for i in range(max_l):
                is_ph_a,is_ph_b=True,True; l_a_c,n_a_s="\n"," "; l_b_c,n_b_s="\n"," "
                if i<len(lines_a_disp):l_a_c,n_a_s,is_ph_a=lines_a_disp[i],str(i+1),False
                elif i==0 and msg_a.strip():l_a_c,is_ph_a=msg_a,False
                if i<len(lines_b_disp):l_b_c,n_b_s,is_ph_b=lines_b_disp[i],str(i+1),False
                elif i==0 and msg_b.strip():l_b_c,is_ph_b=msg_b,False
                self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,n_a_s,l_a_c,lexer=self.lexer_a if not is_ph_a else None,is_placeholder=is_ph_a)
                self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,n_b_s,l_b_c,lexer=self.lexer_b if not is_ph_b else None,is_placeholder=is_ph_b)
            self._manage_text_widget_state(ctk.NORMAL if self.editing_enabled_var.get() else ctk.DISABLED, content_only=True)
            self.line_numbers_a_widget.configure(state=ctk.DISABLED); self.line_numbers_b_widget.configure(state=ctk.DISABLED)
            self.diff_stats_label.configure(text=f"Stats: {msg_a.strip()}"); return

        ln_a, ln_b = 0,0; MIN_FOLD, CTX_FOLD = 5,1; final_opcodes=[]
        if self.fold_equal_blocks_var.get():
            for i,(tag,i1,i2,j1,j2) in enumerate(opcodes):
                if tag=='equal' and (i2-i1)>=MIN_FOLD and (i2-i1)>2*CTX_FOLD:
                    if CTX_FOLD>0: final_opcodes.append(('equal',i1,i1+CTX_FOLD,j1,j1+CTX_FOLD))
                    final_opcodes.append(('folded',i1+CTX_FOLD,i2-CTX_FOLD,j1+CTX_FOLD,j2-CTX_FOLD,(i2-i1)-2*CTX_FOLD))
                    if CTX_FOLD>0: final_opcodes.append(('equal',i2-CTX_FOLD,i2,j2-CTX_FOLD,j2))
                else: final_opcodes.append((tag,i1,i2,j1,j2))
            opcodes = final_opcodes
        ca_tb = getattr(self.content_a_widget,'_textbox',None)
        for op_data in opcodes:
            tag,i1,i2,j1,j2 = op_data[0],*op_data[1:5]
            if tag!='equal' and tag!='folded' and ca_tb:
                mk_tag=f"diff_blk_{len(self.diff_block_tags)}";ca_tb.mark_set(mk_tag,ctk.END+"-1c");ca_tb.mark_gravity(mk_tag,ctk.LEFT)
                self.diff_block_tags.append((mk_tag,ca_tb))
            if tag=='equal':
                for idx in range(i2-i1): ln_a+=1;ln_b+=1;l_a_d,l_b_d=lines_a_disp[i1+idx],lines_b_disp[j1+idx]; self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,str(ln_a),l_a_d,lexer=self.lexer_a); self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,str(ln_b),l_b_d,lexer=self.lexer_b)
            elif tag=='folded':
                f_count=op_data[5];f_sum=f"    ... {f_count} identical lines ...\n";ln_a+=f_count;ln_b+=f_count; self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,"...",f_sum,is_folded_summary=True); self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,"...",f_sum,is_folded_summary=True)
            elif tag=='replace':
                changed_blocks+=1;len_a_c,len_b_c=i2-i1,j2-j1;max_len=max(len_a_c,len_b_c)
                for i in range(max_len):
                    hl_a,hl_b=None,None;l_a_diff_s=lines_a_disp[i1+i].rstrip('\n') if i<len_a_c else "";l_b_diff_s=lines_b_disp[j1+i].rstrip('\n') if i<len_b_c else ""
                    if i<len_a_c and i<len_b_c: hl_a,hl_b=self._get_char_highlight_tags_for_pair(l_a_diff_s,l_b_diff_s)
                    if i<len_a_c:ln_a+=1;l_a_content=lines_a_disp[i1+i];t_a=["line_changed_bg"] if i<len_b_c else ["line_del_bg"];ln_t_a=("line_no_changed",) if i<len_b_c else ("line_no",);self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,str(ln_a),l_a_content,t_a,ln_t_a,self.lexer_a,hl_a)
                    else: self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,"","",ln_tags=("line_no_empty",),is_placeholder=True)
                    if i<len_b_c:ln_b+=1;l_b_content=lines_b_disp[j1+i];t_b=["line_changed_bg"] if i<len_a_c else ["line_add_bg"];ln_t_b=("line_no_changed",) if i<len_a_c else ("line_no",);self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,str(ln_b),l_b_content,t_b,ln_t_b,self.lexer_b,hl_b)
                    else: self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,"","",ln_tags=("line_no_empty",),is_placeholder=True)
            elif tag=='delete':
                deleted+=(i2-i1);
                for idx in range(i2-i1):ln_a+=1;l_a_content=lines_a_disp[i1+idx];self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,str(ln_a),l_a_content,["line_del_bg"],lexer=self.lexer_a);self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,"","",ln_tags=("line_no_empty",),is_placeholder=True)
            elif tag=='insert':
                added+=(j2-j1);
                for idx in range(j2-j1):ln_b+=1;l_b_content=lines_b_disp[j1+idx];self._insert_line_into_pane(self.content_a_widget,self.line_numbers_a_widget,"","",ln_tags=("line_no_empty",),is_placeholder=True);self._insert_line_into_pane(self.content_b_widget,self.line_numbers_b_widget,str(ln_b),l_b_content,["line_add_bg"],lexer=self.lexer_b)
        
        self._manage_text_widget_state(ctk.NORMAL if self.editing_enabled_var.get() else ctk.DISABLED, content_only=True)
        self.line_numbers_a_widget.configure(state=ctk.DISABLED)
        self.line_numbers_b_widget.configure(state=ctk.DISABLED)

        for w_wrapper in [self.content_a_widget,self.content_b_widget,self.line_numbers_a_widget,self.line_numbers_b_widget]:
            tb=getattr(w_wrapper,'_textbox',None)
            if tb:
                try:
                    tb.yview_moveto(0.0)
                except TclError: pass
                except Exception as e_scroll: logger.warning(f"Error scrolling widget to top: {e_scroll}")
        self.diff_stats_label.configure(text=f"Stats: +{added} lines, -{deleted} lines, ~{changed_blocks} changed blocks")
        self.current_diff_block_idx = -1
        logger.info("Diff display complete.")

    def perform_search(self, event=None):
        query=self.search_query_var.get();
        if not query: self.clear_search_highlights(); return
        self.clear_search_highlights(reset_indices=False); self.search_results_a,self.search_results_b,self.all_search_results,self.current_search_highlight_idx=[],[],[],-1
        for pane_results, widget_wrapper in [(self.search_results_a,self.content_a_widget),(self.search_results_b,self.content_b_widget)]:
            tb=getattr(widget_wrapper,'_textbox',None)
            if not tb: continue
            idx="1.0"
            while True:
                match_start=tb.search(query,idx,stopindex=ctk.END,nocase=True,regexp=False)
                if not match_start: break
                match_end=f"{match_start}+{len(query)}c"; tb.tag_add(self.search_tag_name,match_start,match_end)
                pane_results.append((match_start,match_end,tb)); idx=match_end
        self.all_search_results=sorted(self.search_results_a+self.search_results_b,key=lambda x:(x[2],x[0]))
        if self.all_search_results: self.current_search_highlight_idx=0; self._scroll_to_search_result(0); logger.info(f"Found {len(self.all_search_results)} of '{query}'.")
        else: logger.info(f"'{query}' not found."); messagebox.showinfo("Search",f"'{query}' not found.")

    def _scroll_to_search_result(self, idx):
        if self.all_search_results and 0<=idx<len(self.all_search_results):
            start_idx,_,tb_ref = self.all_search_results[idx]
            if tb_ref: tb_ref.see(start_idx)

    def clear_search_highlights(self, reset_indices=True):
        for w_w in [self.content_a_widget,self.content_b_widget]:
            tb=getattr(w_w,'_textbox',None)
            if tb:
                try:
                    tb.tag_remove(self.search_tag_name,"1.0",ctk.END)
                except TclError: pass
                except Exception as e: logger.warning(f"Error removing search tag from {w_w}: {e}")
        if reset_indices: self.search_results_a,self.search_results_b,self.all_search_results,self.current_search_highlight_idx=[],[],[],-1

    def navigate_to_diff(self, direction):
        if not self.diff_block_tags: logger.debug("No diff blocks."); return
        self.current_diff_block_idx += direction
        if self.current_diff_block_idx >= len(self.diff_block_tags): self.current_diff_block_idx=0
        elif self.current_diff_block_idx < 0: self.current_diff_block_idx=len(self.diff_block_tags)-1
        self._scroll_to_diff_block(self.current_diff_block_idx)
    def navigate_to_next_diff(self): self.navigate_to_diff(1)
    def navigate_to_prev_diff(self): self.navigate_to_diff(-1)

    def _scroll_to_diff_block(self, idx):
        if 0<=idx<len(self.diff_block_tags):
            mark,tb_ref=self.diff_block_tags[idx]
            if tb_ref:
                try: tb_ref.see(mark); logger.debug(f"Scrolled to diff block {idx}")
                except Exception as e: logger.error(f"Error scrolling to diff mark {mark}: {e}")

    def _toggle_edit_mode(self):
        is_editing = self.editing_enabled_var.get()
        new_state = ctk.NORMAL if is_editing else ctk.DISABLED
        logger.info(f"Toggling edit mode to: {'Enabled' if is_editing else 'Disabled'}")
        self.content_a_widget.configure(state=new_state); self.content_b_widget.configure(state=new_state)
        self.recompare_button.configure(state=ctk.NORMAL) # Always allow re-compare
        if not is_editing: # Turning OFF edit mode
            if self.file_a_lines_orig is not None and self.file_b_lines_orig is not None: self.show_diff()
            elif self.file_a_lines_orig is not None: self._display_single_file('a')
            elif self.file_b_lines_orig is not None: self._display_single_file('b')
        else: # Turning ON edit mode - refresh content from _orig arrays
            if self.file_a_lines_orig is not None: self._display_single_file_in_edit_mode('a')
            if self.file_b_lines_orig is not None: self._display_single_file_in_edit_mode('b')

    def _display_single_file_in_edit_mode(self, pane_id):
        logger.debug(f"Refreshing pane {pane_id} for edit mode.")
        if pane_id == 'a': content_w,ln_w,lines,lex = self.content_a_widget,self.line_numbers_a_widget,self.file_a_lines_orig,self.lexer_a
        elif pane_id == 'b': content_w,ln_w,lines,lex = self.content_b_widget,self.line_numbers_b_widget,self.file_b_lines_orig,self.lexer_b
        else: return
        if lines is None: return
        self._clear_pane(pane_id); content_w.configure(state=ctk.NORMAL); ln_w.configure(state=ctk.NORMAL)
        content_tb,ln_tb = getattr(content_w,'_textbox',None), getattr(ln_w,'_textbox',None)
        if not (content_tb and ln_tb): return
        if not lines: ln_tb.insert("1.0", "1 \n",("line_no",)); content_tb.insert("1.0", "<Empty File>\n")
        else:
            for i, line in enumerate(lines): self._insert_line_into_pane(content_w,ln_w,str(i+1),line,[],("line_no",),lex)
        content_w.configure(state=ctk.NORMAL); ln_w.configure(state=ctk.DISABLED)

    def _on_text_modified(self, file_id_char, event=None):
        text_widget = self.content_a_widget if file_id_char == 'a' else self.content_b_widget
        tb = getattr(text_widget, '_textbox', None)
        if tb:
            try:
                if tb.edit_modified(): 
                    if file_id_char == 'a': self.file_a_modified.set(True)
                    elif file_id_char == 'b': self.file_b_modified.set(True)
                    self._update_file_label_modified_state()
                    self.recompare_button.configure(state=ctk.NORMAL)
            except TclError: pass 
            except Exception as e: logger.error(f"Error in _on_text_modified for {file_id_char}: {e}")
        return "break" 

    def _update_file_label_modified_state(self):
        path_a = os.path.basename(self.file_a_full_path) if self.file_a_full_path else "<File A>"
        path_b = os.path.basename(self.file_b_full_path) if self.file_b_full_path else "<File B>"
        self.file_a_path_var.set(f"* {path_a}" if self.file_a_modified.get() else path_a)
        self.file_b_path_var.set(f"* {path_b}" if self.file_b_modified.get() else path_b)

    def _save_file(self, file_id_char):
        logger.info(f"Attempting to save file {file_id_char}")
        full_path, content_widget, modified_var, lines_orig_attr = None, None, None, None
        if file_id_char == 'a': full_path, content_widget, modified_var, lines_orig_attr = self.file_a_full_path, self.content_a_widget, self.file_a_modified, 'file_a_lines_orig'
        elif file_id_char == 'b': full_path, content_widget, modified_var, lines_orig_attr = self.file_b_full_path, self.content_b_widget, self.file_b_modified, 'file_b_lines_orig'
        if not full_path: messagebox.showerror("Save Error", f"No path for File {file_id_char.upper()}."); return
        tb = getattr(content_widget, '_textbox', None)
        if not tb: logger.error(f"Cannot save, textbox for {file_id_char} not found."); return
        content_to_save = tb.get("1.0", "end-1c")
        try:
            with open(full_path, 'w', encoding='utf-8', newline='') as f: # Use newline='' for universal line endings
                f.write(content_to_save)
            logger.info(f"File '{full_path}' saved."); modified_var.set(False); self._update_file_label_modified_state()
            
            # Update the internal _orig lines to reflect the saved content accurately for future diffs
            # Split by any newline, then add back '\n' to each line for consistency
            # This ensures self.file_x_lines_orig matches what was physically saved.
            saved_lines_list = []
            if content_to_save: # Only process if there's content
                temp_lines = content_to_save.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                for i, line in enumerate(temp_lines):
                    if i == len(temp_lines) - 1 and not line: # Last item is empty string due to trailing newline
                        if content_to_save.endswith('\n'): saved_lines_list.append('\n') # Original had trailing newline
                        # else, if no trailing newline, the last empty string is ignored
                    else:
                        saved_lines_list.append(line + '\n')
                # If the original content_to_save did not end with a newline, the last item in saved_lines_list will have an extra \n. Remove it.
                if content_to_save and not content_to_save.endswith(('\n', '\r')):
                    if saved_lines_list and saved_lines_list[-1] == '\n': # If it's just a newline from an empty line before it
                        pass
                    elif saved_lines_list and saved_lines_list[-1].endswith('\n'):
                         saved_lines_list[-1] = saved_lines_list[-1].rstrip('\n')


            setattr(self, lines_orig_attr, saved_lines_list)
            
            messagebox.showinfo("Save Successful", f"File {os.path.basename(full_path)} saved.")
            self.recompare_button.configure(state=ctk.NORMAL)
        except Exception as e: logger.error(f"Error saving file {full_path}: {e}", exc_info=True); messagebox.showerror("Save Error", f"Could not save {os.path.basename(full_path)}:\n{e}")

    def _trigger_re_render(self, event=None):
        self._update_font_and_style_configuration()

# File History Methods
    def _load_file_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE,'r') as f: history=json.load(f)
                if isinstance(history,list) and all(isinstance(i,(list,tuple)) and len(i)==2 for i in history): return history
                logger.warning(f"History file '{HISTORY_FILE}' invalid. Ignoring."); return []
            return []
        except Exception as e: logger.error(f"Error loading file history: {e}",exc_info=True); return []
    def _save_file_history(self):
        try:
            with open(HISTORY_FILE,'w') as f: json.dump(self.file_history,f,indent=2)
            logger.info("File history saved.")
        except Exception as e: logger.error(f"Error saving file history: {e}",exc_info=True)
    def _add_to_file_history(self, path_a, path_b):
        if not (path_a and path_b and os.path.exists(path_a) and os.path.exists(path_b)): logger.debug("Skipping add to history: invalid paths."); return
        pair=(path_a,path_b)
        if pair in self.file_history: self.file_history.remove(pair)
        self.file_history.insert(0,pair); self.file_history=self.file_history[:MAX_HISTORY_ITEMS]
        self._save_file_history(); self._update_history_menu()
    def _update_history_menu(self):
        if hasattr(self,'history_menu_button') and self.history_menu_button:
            hist_disp=[f"{os.path.basename(a)} vs {os.path.basename(b)}" for a,b in self.file_history] or ["No History"]
            self.history_menu_button.configure(values=hist_disp)
            self.history_menu_button.set(hist_disp[0])
            logger.debug("History menu values updated.")
    def _handle_history_selection(self,selection_str:str):
        if selection_str=="No History" or not self.file_history: return
        sel_pair=next(((pa,pb) for pa,pb in self.file_history if f"{os.path.basename(pa)} vs {os.path.basename(pb)}"==selection_str),None)
        if sel_pair: self._load_from_history(sel_pair[0],sel_pair[1])
        else: logger.warning(f"Could not find history entry for: {selection_str}")
    def _load_from_history(self,path_a,path_b):
        logger.info(f"Loading from history: A='{path_a}', B='{path_b}'")
        loaded_a,loaded_b=False,False
        if os.path.exists(path_a): loaded_a=self._load_file_content('a',path_a)
        else: messagebox.showerror("History Error",f"File A not found: {path_a}");self.file_a_lines_orig=None;self.file_a_path_var.set("<Not Found>")
        if os.path.exists(path_b): loaded_b=self._load_file_content('b',path_b)
        else: messagebox.showerror("History Error",f"File B not found: {path_b}");self.file_b_lines_orig=None;self.file_b_path_var.set("<Not Found>")
        if loaded_a: self._display_single_file('a')
        if loaded_b: self._display_single_file('b')
        if self.file_a_lines_orig is not None and self.file_b_lines_orig is not None:
            self.after(50,self.show_diff);self._add_to_file_history(path_a,path_b)

# Go To Line Method
    def _go_to_line(self):
        try:
            line_num_str = simpledialog.askstring("Go to Line", "Enter line number:", parent=self)
            if line_num_str is None: return
            line_num = int(line_num_str)
            if line_num < 1: messagebox.showwarning("Invalid Line", "Line number must be >= 1."); return
        except ValueError: messagebox.showwarning("Invalid Input", "Please enter a valid number."); return
        except Exception as e: logger.error(f"Go to line dialog error: {e}"); return
        logger.info(f"Attempting to go to line: {line_num}"); tk_index = f"{line_num}.0"
        scrolled_any = False
        for widget_wrapper in [self.content_a_widget, self.content_b_widget]:
            tb = getattr(widget_wrapper, '_textbox', None)
            if tb:
                try: tb.see(tk_index); scrolled_any = True
                except TclError: logger.debug(f"Line {line_num} not in {widget_wrapper}")
                except Exception as e: logger.error(f"Error scrolling {widget_wrapper}: {e}")
        if scrolled_any:
            self.after_idle(lambda: self.content_a_widget._textbox.event_generate("<<Scroll>>") if hasattr(self.content_a_widget,'_textbox') and self.content_a_widget._textbox.winfo_exists() else None)

# Global Exception Hook & Main Execution
def global_excepthook(exctype, value, tb_obj):
    logger.critical(f"UNHANDLED EXCEPTION: {exctype.__name__}: {value}", exc_info=(exctype,value,tb_obj))
    if not issubclass(exctype,(SystemExit,KeyboardInterrupt)):
        try: messagebox.showerror("Application Error",f"Unexpected error:\n{exctype.__name__}: {value}\n\nLogs may have details.")
        except: pass
    sys.__excepthook__(exctype,value,tb_obj)

if __name__ == "__main__":
    sys.excepthook = global_excepthook
    logger.info(f"================ App Start (SBS - Final Syntax Check) {ctk.get_appearance_mode()} ================")
    app = None
    try:
        app = DiffApp()
        app.mainloop()
    except SystemExit: logger.info("App exited via SystemExit.")
    except KeyboardInterrupt: logger.info("App interrupted by user.");
    except Exception as e: logger.critical(f"FATAL ERROR in main execution: {e}", exc_info=True)
    finally: logger.info("================ App Exit ================ ");