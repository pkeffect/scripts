import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import pyperclip
import re
from tkinter import filedialog, messagebox

def drop_file(event):
    """Handles the dropped file path."""
    file_path = event.data  # File path as a string
    open_file(file_path)

def open_file(filepath=None):
    try:
        if not filepath:
            filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not filepath:
            return
        
        img = Image.open(filepath)
        img.thumbnail((300, 200))
        tk_img = ImageTk.PhotoImage(img)
        image_label.config(image=tk_img)
        image_label.image = tk_img

        with open(filepath, "rb") as file:
            image_data = file.read()
        
        json_start = image_data.find(b'"text": "') + len(b'"text": "')
        json_end = image_data.find(b'",', json_start)

        if json_start != -1 and json_end != -1:
            extracted_text = image_data[json_start:json_end].decode('utf-8').strip('"')
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, extracted_text)
            text_widget.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "Text not found in image.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")

def copy_text():
    try:
        if text_widget.get(1.0, tk.END).strip() == "":
            raise ValueError("No text to copy.")
        
        cleaned_text = re.sub(r'\s+', ' ', text_widget.get(1.0, tk.END))
        pyperclip.copy(cleaned_text)
        messagebox.showinfo("Success", "Text copied to clipboard!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = TkinterDnD.Tk()
root.title("ComfyUI PNG Image Text Extractor")
root.geometry('786x786')
root.configure(bg="#111111")

# Styling
style = {
    "background": "#222222",
    "foreground": "#FFFFFF",
    "font": ("Helvetica", 12),
}

open_button = tk.Button(root, text="Select a ComfyUI Generated PNG File", command=open_file, bg=style["background"], fg=style["foreground"])
open_button.pack(pady=20)

label = tk.Label(root, text="Drag & Drop an image on this text", bg=style["background"], fg=style["foreground"])
label.pack(pady=20)

image_label = tk.Label(root, bg=style["background"])
image_label.pack()

text_widget = tk.Text(root, height=15, width=80, wrap=tk.WORD, bg=style["background"], fg=style["foreground"])
text_widget.config(state=tk.DISABLED)
text_widget.pack(pady=20)

copy_button = tk.Button(root, text="Copy Text", command=copy_text, bg=style["background"], fg=style["foreground"])
copy_button.pack(pady=5)

# Enable drop events
label.drop_target_register(DND_FILES)
label.dnd_bind("<<Drop>>", drop_file)

root.mainloop()
