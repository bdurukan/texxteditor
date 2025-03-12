"""
API Key configuration dialog for the TextEditor.
"""

import tkinter as tk
from tkinter import messagebox

class APIKeyDialog(tk.Toplevel):
    def __init__(self, parent, current_key="", save_callback=None):
        super().__init__(parent)
        self.title("API Key Configuration")
        self.geometry("400x200")
        self.configure(bg="#f8f9fa")
        self.resizable(False, False)
        
        self.parent = parent
        self.current_key = current_key
        self.save_callback = save_callback
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Create widgets
        self.create_widgets()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self, 
            text="OpenAI API Key Configuration", 
            font=("Helvetica", 12, "bold"),
            bg="#f8f9fa",
            fg="#212529"
        )
        title_label.pack(pady=(20, 10))
        
        # Description
        description = tk.Label(
            self,
            text="Enter your OpenAI API key to enable audio transcription",
            wraplength=360,
            justify="center",
            bg="#f8f9fa",
            fg="#212529"
        )
        description.pack(pady=(0, 20))
        
        # Key input frame
        key_frame = tk.Frame(self, bg="#f8f9fa")
        key_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # API Key entry
        self.api_key_var = tk.StringVar(value=self.current_key)
        self.api_key_entry = tk.Entry(
            key_frame, 
            textvariable=self.api_key_var, 
            width=40,
            show="*",
            bg="white",
            relief=tk.SOLID,
            bd=1
        )
        self.api_key_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Show/hide button
        self.show_var = tk.BooleanVar(value=False)
        self.show_button = tk.Button(
            key_frame, 
            text="Show", 
            command=self.toggle_show_hide,
            bg="#ffffff",
            fg="#4285f4",
            relief=tk.FLAT,
            padx=10,
            bd=0,
            highlightthickness=0
        )
        self.show_button.pack(side=tk.LEFT)
        
        # Button frame
        button_frame = tk.Frame(self, bg="#f8f9fa")
        button_frame.pack(fill=tk.X, pady=(20, 20), padx=20)
        
        # Save button
        save_button = tk.Button(
            button_frame, 
            text="Save", 
            command=self.save_api_key,
            bg="#4285f4",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            bd=0,
            highlightthickness=0
        )
        save_button.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.destroy,
            bg="#ffffff",
            fg="#4285f4",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            bd=0,
            highlightthickness=0
        )
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def toggle_show_hide(self):
        current_show = self.api_key_entry.cget("show")
        if current_show:
            self.api_key_entry.config(show="")
            self.show_button.config(text="Hide")
        else:
            self.api_key_entry.config(show="*")
            self.show_button.config(text="Show")
    
    def save_api_key(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "API key cannot be empty")
            return
        
        if self.save_callback:
            self.save_callback(api_key)
        self.destroy()