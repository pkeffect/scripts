# VERSION: 0.0.3
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import re
from threading import Thread

class FuturisticUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Model Unloader")
        
        # Theme configuration - refined dark grays
        self.colors = {
            "bg": "#1A1A1A",
            "card_bg": "#252525",
            "text": "#E0E0E0",
            "text_secondary": "#9E9E9E",
            "accent": "#00B0FF",
            "button": "#2D2D2D",
            "button_hover": "#3A3A3A",
            "input_bg": "#0D0D0D",
            "border": "#3A3A3A",
            "success": "#4CAF50",
            "warning": "#FFA726",
            "error": "#EF5350"
        }
        
        # Configure window
        self.root.configure(bg=self.colors["bg"])
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Create UI components
        self.setup_ui()
        
        # Auto-run ollama ps on startup
        self.root.after(100, self.refresh_models)
    
    def setup_ui(self):
        """Set up all UI components"""
        # Main container with padding
        self.main_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        self.header_frame = tk.Frame(self.main_container, bg=self.colors["bg"])
        self.header_frame.pack(fill=tk.X, pady=(0, 25))
        
        self.title_label = tk.Label(
            self.header_frame,
            text="OLLAMA MODEL MANAGER",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"]
        )
        self.title_label.pack()
        
        self.subtitle_label = tk.Label(
            self.header_frame,
            text="Monitor and manage running models",
            font=("Segoe UI", 10),
            bg=self.colors["bg"],
            fg=self.colors["text_secondary"]
        )
        self.subtitle_label.pack(pady=(5, 0))
        
        # Button container - centered
        self.button_container = tk.Frame(self.main_container, bg=self.colors["bg"])
        self.button_container.pack(pady=(0, 20))
        
        # Refresh button
        self.refresh_button = self.create_button(
            self.button_container,
            "↻  REFRESH MODELS",
            self.refresh_models
        )
        self.refresh_button.pack(side=tk.LEFT, padx=8)
        
        # Stop button
        self.action_button = self.create_button(
            self.button_container,
            "■  STOP ALL MODELS",
            self.run_stop_command,
            accent=True
        )
        self.action_button.pack(side=tk.LEFT, padx=8)
        
        # Console card
        self.console_card = tk.Frame(
            self.main_container,
            bg=self.colors["card_bg"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        self.console_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Console header
        self.console_header = tk.Label(
            self.console_card,
            text="Console Output",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["card_bg"],
            fg=self.colors["text"],
            anchor=tk.W
        )
        self.console_header.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        # Console output area with padding
        self.console_frame = tk.Frame(self.console_card, bg=self.colors["card_bg"])
        self.console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.console = scrolledtext.ScrolledText(
            self.console_frame,
            bg=self.colors["input_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            font=("Consolas", 10),
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15,
            wrap=tk.WORD
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        self.console.config(state=tk.DISABLED)
        
        # Status bar
        self.status_frame = tk.Frame(
            self.main_container,
            bg=self.colors["card_bg"],
            highlightbackground=self.colors["border"],
            highlightthickness=1
        )
        self.status_frame.pack(fill=tk.X)
        
        self.status_bar = tk.Label(
            self.status_frame,
            text="● Ready",
            bg=self.colors["card_bg"],
            fg=self.colors["text_secondary"],
            font=("Segoe UI", 9),
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, padx=20, pady=12)
    
    def create_button(self, parent, text, command, accent=False):
        """Factory method to create buttons with consistent styling"""
        button = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent"] if accent else self.colors["button"],
            fg="#FFFFFF" if accent else self.colors["text"],
            activebackground=self.colors["button_hover"],
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            borderwidth=0,
            padx=24,
            pady=12,
            cursor="hand2",
            command=command
        )
        
        # Hover effects
        def on_enter(e):
            button['background'] = self.colors["button_hover"] if not accent else "#0099DD"
        
        def on_leave(e):
            button['background'] = self.colors["accent"] if accent else self.colors["button"]
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
        
    def update_status(self, text, status_type="info"):
        """Update status bar text with indicator"""
        indicators = {
            "info": "●",
            "loading": "◌",
            "success": "✓",
            "warning": "⚠",
            "error": "✕"
        }
        
        colors = {
            "info": self.colors["text_secondary"],
            "loading": self.colors["accent"],
            "success": self.colors["success"],
            "warning": self.colors["warning"],
            "error": self.colors["error"]
        }
        
        indicator = indicators.get(status_type, "●")
        color = colors.get(status_type, self.colors["text_secondary"])
        
        self.status_bar.config(text=f"{indicator} {text}", fg=color)
        
    def append_to_console(self, text, color_key=None):
        """Add text to the console with optional color"""
        self.console.config(state=tk.NORMAL)
        
        color = self.colors.get(color_key) if color_key else None
        if color:
            tag_name = f"tag_{color.replace('#', '')}"
            self.console.tag_configure(tag_name, foreground=color)
            self.console.insert(tk.END, text, tag_name)
        else:
            self.console.insert(tk.END, text)
            
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
    
    def refresh_models(self):
        """Refresh the list of running models"""
        self.append_to_console("═" * 80 + "\n", "border")
        self.append_to_console("Fetching running models...\n", "accent")
        self.update_status("Scanning for running models...", "loading")
        
        Thread(target=self.fetch_running_models, daemon=True).start()
    
    def fetch_running_models(self):
        """Fetch and display running models"""
        try:
            result = subprocess.run(
                'ollama ps', 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Command failed"
                self.append_to_console(f"✕ Error: {error_msg}\n\n", "error")
                self.update_status("Failed to retrieve models", "error")
                return
                
            # Display the output
            self.append_to_console(result.stdout + "\n")
            
            # Count running models
            lines = result.stdout.strip().split('\n')
            model_count = len(lines) - 1 if len(lines) > 1 else 0
            
            if model_count == 0:
                self.append_to_console("⚠ No running models found.\n\n", "warning")
                self.update_status("No running models detected", "warning")
            else:
                self.append_to_console(f"✓ Found {model_count} running model(s)\n\n", "success")
                self.update_status(f"Found {model_count} running model(s)", "success")
                
        except subprocess.TimeoutExpired:
            self.append_to_console("✕ Command timed out\n\n", "error")
            self.update_status("Command timed out", "error")
        except Exception as e:
            self.append_to_console(f"✕ Error: {str(e)}\n\n", "error")
            self.update_status("Error occurred", "error")
        
    def run_stop_command(self):
        """Run the ollama ps command, extract model names, and stop them"""
        self.append_to_console("═" * 80 + "\n", "border")
        self.append_to_console("Initiating model shutdown sequence...\n", "accent")
        self.update_status("Stopping models...", "loading")
        
        Thread(target=self.process_ollama_command, daemon=True).start()
        
    def process_ollama_command(self):
        """Process the ollama ps command and stop running models"""
        try:
            # Get the list of running models
            result = subprocess.run(
                'ollama ps', 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Command failed"
                self.append_to_console(f"✕ Error: {error_msg}\n\n", "error")
                self.update_status("Failed to retrieve models", "error")
                return
                
            # Display the output
            self.append_to_console(result.stdout + "\n")
            
            # Extract model names, skipping the header line
            model_names = []
            lines = result.stdout.strip().split('\n')
            
            if len(lines) <= 1:  # Only header or empty
                self.append_to_console("⚠ No running models found.\n\n", "warning")
                self.update_status("No running models detected", "warning")
                return
                
            for line in lines[1:]:  # Skip header
                columns = re.split(r'\s+', line.strip())
                if columns and len(columns) >= 1:
                    model_names.append(columns[0])
            
            if not model_names:
                self.append_to_console("⚠ No running models found.\n\n", "warning")
                self.update_status("No running models detected", "warning")
                return
                
            # Stop each model
            success_count = 0
            for model in model_names:
                self.append_to_console(f"→ Stopping: {model}\n", "warning")
                
                try:
                    stop_result = subprocess.run(
                        f'ollama stop {model}', 
                        shell=True, 
                        capture_output=True, 
                        text=True,
                        timeout=10
                    )
                    
                    if stop_result.returncode == 0:
                        self.append_to_console(f"  ✓ Successfully stopped: {model}\n", "success")
                        success_count += 1
                    else:
                        error_msg = stop_result.stderr.strip() if stop_result.stderr else "Unknown error"
                        self.append_to_console(f"  ✕ Failed to stop {model}: {error_msg}\n", "error")
                except Exception as e:
                    self.append_to_console(f"  ✕ Error stopping {model}: {str(e)}\n", "error")
            
            self.append_to_console(f"\n{'═' * 80}\n", "border")
            if success_count == len(model_names):
                self.update_status(f"Successfully stopped all {success_count} model(s)", "success")
            else:
                self.update_status(f"Stopped {success_count} of {len(model_names)} model(s)", "warning")
            
        except subprocess.TimeoutExpired:
            self.append_to_console("✕ Command timed out\n\n", "error")
            self.update_status("Command timed out", "error")
        except Exception as e:
            self.append_to_console(f"✕ Error: {str(e)}\n\n", "error")
            self.update_status("Error occurred", "error")

if __name__ == "__main__":
    root = tk.Tk()
    app = FuturisticUI(root)
    root.mainloop()