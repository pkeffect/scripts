import tkinter as tk
from tkinter import filedialog, messagebox
import torchocr
from PIL import Image, ImageTk

class ComfyUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ComfyUI PNG Image Text Extractor")
        self.root.geometry('786x786')
        self.root.configure(bg="#111111")

        # Styling
        style = {
            "background": "#222222",
            "foreground": "#FFFFFF",
            "font": ("Helvetica", 12),
        }

        # Layout elements
        self.create_widgets(style)

    def create_widgets(self, style):
        # Button for selecting a file
        open_button = tk.Button(
            self.root,
            text="Select a ComfyUI Generated PNG File",
            command=self.open_file,
            bg=style["background"],
            fg=style["foreground"]
        )
        open_button.pack(pady=20)

        # Label to drag and drop an image
        label = tk.Label(
            self.root,
            text="Drag & Drop an image on this text",
            bg=style["background"],
            fg=style["foreground"],
            font=("Helvetica", 14)
        )
        label.pack(pady=20)

        # Label to display the image
        self.image_label = tk.Label(self.root, bg=style["background"])
        self.image_label.pack()

        # Text widget for displaying extracted text
        self.text_widget = tk.Text(
            self.root,
            height=15,
            width=80,
            wrap=tk.WORD,
            bg=style["background"],
            fg=style["foreground"]
        )
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.pack(pady=20)

        # Button to copy the text
        copy_button = tk.Button(
            self.root,
            text="Copy Text",
            command=self.copy_text,
            bg=style["background"],
            fg=style["foreground"]
        )
        copy_button.pack(pady=20)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if file_path:
            self.display_image(file_path)
            extracted_text = self.extract_text_from_image(file_path)
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, extracted_text)
            self.text_widget.config(state=tk.DISABLED)

    def display_image(self, file_path):
        image = Image.open(file_path)
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo

    def extract_text_from_image(self, file_path):
        # Load the model
        model = torchocr.Recognizer("path/to/your/model.pth")

        # Read the image
        image = Image.open(file_path)

        # Perform OCR
        result = model.rec(image)
        extracted_text = "\n".join([text for text, score in result])
        
        return extracted_text

    def copy_text(self):
        text = self.text_widget.get(1.0, tk.END)
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("Success", "Text copied to clipboard!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComfyUIApp(root)
    root.mainloop()
