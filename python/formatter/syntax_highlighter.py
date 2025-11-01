import logging
import os
from pygments import highlight 
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename, guess_lexer
from pygments.styles import get_style_by_name, get_all_styles
from pygments.token import Token 
import tkinter as tk

logger = logging.getLogger(__name__)

TOKEN_CONFIG = {}
CURRENT_PYGMENTS_STYLE_NAME = 'monokai'

MANUAL_OVERRIDES = { 
    Token.Keyword: {'foreground': '#FF79C6'},
    Token.Name.Class: {'font_style_override': 'bold'}, 
    Token.Name.Function: {'foreground': '#50FA7B'},
    Token.Name.Builtin: {'foreground': '#8BE9FD', 'font_style_override': 'italic'},
    Token.Literal.String: {'foreground': '#F1FA8C'},
    Token.Literal.Number: {'foreground': '#BD93F9'},
    Token.Operator: {'foreground': '#FF79C6'},
    Token.Comment: {'foreground': '#6272A4', 'font_style_override': 'italic'},
}

def _get_font_tuple(base_font_family, base_font_size, style_parts_str="normal"):
    """Helper to create Tkinter font tuples."""
    return (base_font_family, base_font_size, style_parts_str)

def initialize_style(style_name='monokai', base_font_family="Consolas", base_font_size=11):
    """Initializes TOKEN_CONFIG based on a Pygments style and applies overrides."""
    global TOKEN_CONFIG, CURRENT_PYGMENTS_STYLE_NAME
    TOKEN_CONFIG = {}
    CURRENT_PYGMENTS_STYLE_NAME = style_name
    logger.debug(f"Initializing Pygments style: {style_name} with base font: {base_font_family} {base_font_size}pt")

    try:
        style = get_style_by_name(style_name)
    except Exception as e:
        logger.warning(f"Pygments style '{style_name}' not found. Falling back to 'default'. Error: {e}")
        style = get_style_by_name('default')
        CURRENT_PYGMENTS_STYLE_NAME = 'default'

    default_fg = f"#{style.style_for_token(Token.Text)['color'] or 'F8F8F2'}"
    TOKEN_CONFIG[Token.Text] = {'foreground': default_fg}

    for token_type, style_info in style:
        config = {}
        font_style_parts = []
        if style_info['color']: config['foreground'] = f"#{style_info['color']}"
        if style_info['bgcolor']: config['background'] = f"#{style_info['bgcolor']}" 
        if style_info['bold']: font_style_parts.append('bold')
        if style_info['italic']: font_style_parts.append('italic')
        if style_info['underline']: config['underline'] = True 
        
        manual_font_style = MANUAL_OVERRIDES.get(token_type, {}).get('font_style_override')
        if manual_font_style:
            config['font'] = _get_font_tuple(base_font_family, base_font_size, manual_font_style)
        elif font_style_parts:
            config['font'] = _get_font_tuple(base_font_family, base_font_size, " ".join(font_style_parts))
        if config: TOKEN_CONFIG[token_type] = config
    
    for token_type, override_config in MANUAL_OVERRIDES.items():
        if token_type not in TOKEN_CONFIG: TOKEN_CONFIG[token_type] = {} 
        for k,v in override_config.items():
            if k != 'font_style_override': TOKEN_CONFIG[token_type][k] = v
    logger.debug(f"Token config after style '{style_name}': {len(TOKEN_CONFIG)} rules loaded.")

def get_lexer(filename, code):
    """Gets the appropriate Pygments lexer for a filename or code snippet."""
    lexer = None
    try:
        log_filename = os.path.basename(filename) if filename else 'code snippet'
        if filename: 
            lexer = guess_lexer_for_filename(filename, code)
            logger.debug(f"Guessed lexer for filename '{log_filename}': {type(lexer).__name__}")
        elif code.strip(): 
            lexer = guess_lexer(code) 
            logger.debug(f"Guessed lexer from code: {type(lexer).__name__}")
        else: 
             lexer = get_lexer_by_name("text")
             logger.debug("No filename or code, defaulting to text lexer.")
        return lexer
    except Exception as e: 
        log_filename_on_error = os.path.basename(filename) if filename else 'code snippet'
        logger.warning(f"Could not guess lexer for '{log_filename_on_error}'. Falling back to text. Error: {e}")
        try: return get_lexer_by_name("text") 
        except Exception: logger.error("CRITICAL: Could not get 'text' lexer from Pygments."); return None

def get_tkinter_tag_for_token(token_type):
    """Generates a unique tag name for a Pygments token type for Tkinter."""
    return f"pygments_{CURRENT_PYGMENTS_STYLE_NAME}_{str(token_type).replace('.', '_')}"

def configure_tags(text_widget, style_name='monokai', base_font_family="Consolas", base_font_size=11):
    """Configures Tkinter Text widget tags based on the chosen Pygments style."""
    logger.info(f"Configuring tags for style '{style_name}' on widget: {text_widget}")
    initialize_style(style_name, base_font_family, base_font_size)
    
    for tag in text_widget.tag_names():
        if tag.startswith("pygments_"): 
            try: text_widget.tag_delete(tag)
            except tk.TclError: pass 

    base_font_tuple = _get_font_tuple(base_font_family, base_font_size)

    for token_type, config in TOKEN_CONFIG.items():
        tag_name = get_tkinter_tag_for_token(token_type)
        final_config = config.copy()
        if 'font' not in final_config: 
            final_config['font'] = base_font_tuple
        try:
            text_widget.tag_configure(tag_name, **final_config)
        except tk.TclError as e: 
            logger.error(f"TclError configuring Pygments tag '{tag_name}' with {final_config}: {e}")
        except Exception as e: 
             logger.error(f"Unexpected error configuring Pygments tag '{tag_name}': {e}", exc_info=True)

    try:
        default_bg = text_widget.cget("bg") 
        text_widget.tag_configure("diff_add", background="#163B1F", font=base_font_tuple) 
        text_widget.tag_configure("diff_del", background="#401C1F", font=base_font_tuple) 
        text_widget.tag_configure("diff_header", foreground="#888888", font=_get_font_tuple(base_font_family, base_font_size, "bold"))
        text_widget.tag_configure("diff_common", background=default_bg, font=base_font_tuple) 
        text_widget.tag_configure("line_no", foreground="#586069", font=_get_font_tuple(base_font_family, base_font_size -1)) 
        text_widget.tag_configure("char_highlight_add", background="#1F542A", font=base_font_tuple) 
        text_widget.tag_configure("char_highlight_del", background="#6B2028", font=base_font_tuple) 
        text_widget.tag_configure("no_newline_marker", foreground="#C87A23", font=_get_font_tuple(base_font_family, base_font_size - 1, "italic"))
        text_widget.tag_configure("line_del_bg", background="#401C1F", font=base_font_tuple) 
        text_widget.tag_configure("line_add_bg", background="#163B1F", font=base_font_tuple) 
        text_widget.tag_configure("line_changed_bg", background="#443A1F", font=base_font_tuple) 
    except tk.TclError as e:
        logger.error(f"TclError configuring diff utility tags: {e}")
    except Exception as e:
        logger.error(f"Unexpected error configuring diff utility tags: {e}", exc_info=True)
    logger.debug("Diff and utility tags configuration attempt complete.")


def highlight_line(text_widget, line_content_with_marker, base_line_tags, lexer,
                   char_highlight_tags=None, content_start_offset=0):
    """
    Highlights a single line of code/text and inserts it into the text_widget.
    Uses the robust Pygments token loop.
    """
    try:
        start_index_line = text_widget.index(tk.END + "-1c") 
        text_widget.insert(tk.END, line_content_with_marker)
        end_index_line = text_widget.index(tk.END + "-1c") 

        if base_line_tags:
            for tag in base_line_tags:
                text_widget.tag_add(tag, start_index_line, end_index_line)

        content_for_syntax = line_content_with_marker[content_start_offset:].rstrip('\n')

        if lexer and content_for_syntax: 
            current_char_pos_in_syntax_content = 0
            try:
                tokens_iterator = lexer.get_tokens_unprocessed(content_for_syntax)
                for token_tuple in tokens_iterator: 
                    token_type, token_text = None, None 
                    if len(token_tuple) == 3:
                        _index, token_type, token_text = token_tuple
                    elif len(token_tuple) == 2: 
                        logger.warning(f"Lexer {type(lexer).__name__} yielded 2 items from get_tokens_unprocessed. Content: '{content_for_syntax[:30]}...' Token: {token_tuple}")
                        token_type, token_text = token_tuple 
                    else:
                        logger.error(f"Lexer {type(lexer).__name__} yielded unexpected items ({len(token_tuple)}) from get_tokens_unprocessed. Token: {token_tuple}. Skipping.")
                        continue 
                    if token_type is None or token_text is None: 
                        logger.error(f"Token type or text is None after unpacking: {token_tuple}. Skipping.")
                        continue
                        
                    token_start_widget_idx = f"{start_index_line}+{content_start_offset + current_char_pos_in_syntax_content}c"
                    token_end_widget_idx = f"{start_index_line}+{content_start_offset + current_char_pos_in_syntax_content + len(token_text)}c"
                    current_token_type_iter = token_type
                    while current_token_type_iter is not None: 
                        pygments_tag_name = get_tkinter_tag_for_token(current_token_type_iter)
                        if pygments_tag_name in text_widget.tag_names(): 
                            text_widget.tag_add(pygments_tag_name, token_start_widget_idx, token_end_widget_idx)
                        current_token_type_iter = current_token_type_iter.parent
                    current_char_pos_in_syntax_content += len(token_text)
            except ValueError as e: 
                logger.error(f"ValueError during Pygments token processing for content '{content_for_syntax[:30].strip()}...': {e}", exc_info=True)
            except Exception as e: 
                logger.error(f"Unexpected error during Pygments token processing for content '{content_for_syntax[:30].strip()}...': {e}", exc_info=True)

        if char_highlight_tags:
            for tag_name, start_char, end_char in char_highlight_tags:
                char_tag_start_idx = f"{start_index_line}+{content_start_offset + start_char}c"
                char_tag_end_idx = f"{start_index_line}+{content_start_offset + end_char}c"
                text_widget.tag_add(tag_name, char_tag_start_idx, char_tag_end_idx)
    except tk.TclError as e:
        logger.error(f"TclError in highlight_line for content '{line_content_with_marker[:30].strip()}...': {e}", exc_info=False)
    except Exception as e:
        logger.error(f"Unexpected error in highlight_line (outer try-except) for content '{line_content_with_marker[:30].strip()}...': {e}", exc_info=True)