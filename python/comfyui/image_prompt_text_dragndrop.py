import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import pyperclip
import re
import json
from tkinter import filedialog, messagebox

# Constants
THUMBNAIL_SIZE = (300, 200)
WINDOW_SIZE = '786x786'
BACKGROUND_COLOR = "#111111"
WIDGET_BG = "#222222"
WIDGET_FG = "#FFFFFF"
FONT_STYLE = ("Helvetica", 12)

def extract_text_from_png(filepath):
    """
    Extracts text from ComfyUI PNG metadata.
    Tries multiple extraction methods for robustness.
    """
    try:
        with open(filepath, "rb") as file:
            image_data = file.read()
        
        # Method 1: Try to find and parse complete JSON structure
        try:
            # Look for workflow or prompt JSON blocks
            json_patterns = [
                (b'"prompt":', b'}'),
                (b'"text":', b'",'),
                (b'{"text":', b'"}'),
            ]
            
            for start_pattern, end_pattern in json_patterns:
                json_start = image_data.find(start_pattern)
                if json_start != -1:
                    # Find the closing of JSON structure
                    json_end = image_data.find(end_pattern, json_start)
                    if json_end != -1:
                        json_end += len(end_pattern)
                        try:
                            # Extract and parse JSON
                            json_str = image_data[json_start:json_end].decode('utf-8')
                            # Try to parse as JSON
                            parsed = json.loads('{' + json_str + '}')
                            if 'text' in parsed:
                                return parsed['text']
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
        except Exception as e:
            pass
        
        # Method 2: Original pattern matching (fallback)
        json_start = image_data.find(b'"text": "')
        if json_start != -1:
            json_start += len(b'"text": "')
            # Look for end marker, but be careful with escaped quotes
            json_end = json_start
            while json_end < len(image_data):
                if image_data[json_end:json_end+2] == b'",':
                    break
                json_end += 1
            
            if json_end < len(image_data):
                extracted_text = image_data[json_start:json_end].decode('utf-8', errors='ignore').strip('"')
                return extracted_text
        
        # Method 3: Look for tEXt chunks (PNG metadata)
        text_chunk_start = image_data.find(b'tEXt')
        if text_chunk_start != -1:
            # PNG tEXt chunk format: keyword\0text
            chunk_data_start = text_chunk_start + 4
            null_pos = image_data.find(b'\x00', chunk_data_start)
            if null_pos != -1:
                # Extract text after null terminator
                text_start = null_pos + 1
                # Find next chunk or end
                text_end = image_data.find(b'IEND', text_start)
                if text_end == -1:
                    text_end = len(image_data)
                text_data = image_data[text_start:text_end]
                try:
                    decoded = text_data.decode('utf-8', errors='ignore')
                    if len(decoded) > 10:  # Sanity check
                        return decoded
                except:
                    pass
        
        return None
        
    except Exception as e:
        raise Exception(f"Failed to extract text: {e}")

def drop_file(event):
    """Handles the dropped file path."""
    file_path = event.data.strip('{}')  # Remove braces if present
    open_file(file_path)

def open_file(filepath=None):
    """Opens and processes a ComfyUI PNG file."""
    try:
        if not filepath:
            filepath = filedialog.askopenfilename(
                title="Select ComfyUI PNG Image",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
        if not filepath:
            return
        
        # Validate file type
        if not filepath.lower().endswith('.png'):
            messagebox.showwarning("Invalid File", "Please select a PNG file.")
            return
        
        # Load and display image
        img = Image.open(filepath)
        img.thumbnail(THUMBNAIL_SIZE)
        tk_img = ImageTk.PhotoImage(img)
        image_label.config(image=tk_img)
        image_label.image = tk_img
        
        # Extract text from image metadata
        extracted_text = extract_text_from_png(filepath)
        
        if extracted_text:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, extracted_text)
            text_widget.config(state=tk.DISABLED)
            status_label.config(text=f"✓ Loaded: {filepath.split('/')[-1]}")
        else:
            messagebox.showerror("Error", "Text not found in image metadata.\n\nThis may not be a ComfyUI generated image.")
            status_label.config(text="✗ No text found in image")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image:\n{e}")
        status_label.config(text="✗ Error loading file")

def copy_text():
    """Copies the extracted text to clipboard."""
    try:
        text_content = text_widget.get(1.0, tk.END).strip()
        if not text_content:
            raise ValueError("No text to copy.")
        
        # Normalize whitespace for cleaner clipboard content
        cleaned_text = re.sub(r'\s+', ' ', text_content)
        pyperclip.copy(cleaned_text)
        messagebox.showinfo("Success", "Text copied to clipboard!")
        status_label.config(text="✓ Text copied to clipboard")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="✗ Copy failed")

def clear_text():
    """Clears the text widget and image preview."""
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    text_widget.config(state=tk.DISABLED)
    image_label.config(image='')
    image_label.image = None
    status_label.config(text="Ready")

# Create the main window
root = TkinterDnD.Tk()
root.title("ComfyUI PNG Image Text Extractor")
root.geometry(WINDOW_SIZE)
root.configure(bg=BACKGROUND_COLOR)

# Header frame
header_frame = tk.Frame(root, bg=WIDGET_BG)
header_frame.pack(fill=tk.X, padx=10, pady=10)

title_label = tk.Label(
    header_frame, 
    text="ComfyUI PNG Text Extractor", 
    bg=WIDGET_BG, 
    fg=WIDGET_FG,
    font=("Helvetica", 16, "bold")
)
title_label.pack(pady=5)

# Button frame
button_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
button_frame.pack(pady=10)

open_button = tk.Button(
    button_frame, 
    text="📂 Select PNG File", 
    command=open_file, 
    bg=WIDGET_BG, 
    fg=WIDGET_FG,
    font=FONT_STYLE,
    padx=20,
    pady=5
)
open_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(
    button_frame, 
    text="🗑️ Clear", 
    command=clear_text, 
    bg=WIDGET_BG, 
    fg=WIDGET_FG,
    font=FONT_STYLE,
    padx=20,
    pady=5
)
clear_button.pack(side=tk.LEFT, padx=5)

# Drag and drop label
drop_label = tk.Label(
    root, 
    text="⬇️ Drag & Drop PNG Image Here ⬇️", 
    bg=WIDGET_BG, 
    fg=WIDGET_FG,
    font=FONT_STYLE,
    pady=15
)
drop_label.pack(pady=10, padx=10, fill=tk.X)

# Image preview
image_label = tk.Label(root, bg=WIDGET_BG)
image_label.pack(pady=10)

# Text display frame
text_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

text_label = tk.Label(
    text_frame,
    text="Extracted Text:",
    bg=BACKGROUND_COLOR,
    fg=WIDGET_FG,
    font=FONT_STYLE
)
text_label.pack(anchor=tk.W)

# Scrollbar for text widget
scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_widget = tk.Text(
    text_frame, 
    height=15, 
    width=80, 
    wrap=tk.WORD, 
    bg=WIDGET_BG, 
    fg=WIDGET_FG,
    font=FONT_STYLE,
    yscrollcommand=scrollbar.set
)
text_widget.config(state=tk.DISABLED)
text_widget.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=text_widget.yview)

# Copy button
copy_button = tk.Button(
    root, 
    text="📋 Copy Text to Clipboard", 
    command=copy_text, 
    bg=WIDGET_BG, 
    fg=WIDGET_FG,
    font=FONT_STYLE,
    padx=20,
    pady=5
)
copy_button.pack(pady=10)

# Status bar
status_label = tk.Label(
    root,
    text="Ready",
    bg=WIDGET_BG,
    fg=WIDGET_FG,
    font=("Helvetica", 10),
    anchor=tk.W,
    padx=10,
    pady=5
)
status_label.pack(fill=tk.X, side=tk.BOTTOM)

# Enable drop events
drop_label.drop_target_register(DND_FILES)
drop_label.dnd_bind("<<Drop>>", drop_file)

root.mainloop()