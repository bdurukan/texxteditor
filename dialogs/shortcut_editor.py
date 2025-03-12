"""
Shortcut editor dialog for the TextEditor.
"""

import tkinter as tk

class ShortcutEditor(tk.Toplevel):
    def __init__(self, parent, shortcuts, save_callback):
        super().__init__(parent)
        self.title("Shortcut Editor")
        self.geometry("500x450")  # Increased height to show all shortcuts
        self.resizable(False, False)
        
        # Get parent theme colors
        if hasattr(parent, 'bg_color'):
            self.bg_color = parent.bg_color
            self.text_color = parent.text_color
            self.button_bg = parent.button_bg
            self.button_fg = parent.button_fg
            self.accent_color = parent.accent_color
            self.canvas_bg = parent.canvas_bg
        else:
            # Default light theme
            self.bg_color = "#f8f9fa"
            self.text_color = "#212529"
            self.button_bg = "#ffffff"
            self.button_fg = "#4285f4"
            self.accent_color = "#4285f4"
            self.canvas_bg = "#ffffff"
        
        self.parent = parent
        self.shortcuts = shortcuts
        self.save_callback = save_callback
        
        # Configure the window
        self.configure(bg=self.bg_color)
        self.transient(parent)
        self.grab_set()
        
        # Create UI elements
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
            text="Keyboard Shortcuts", 
            font=("Helvetica", 14, "bold"),
            bg=self.bg_color, 
            fg=self.text_color
        )
        title_label.pack(pady=(15, 10))
        
        # Shortcuts container with scrollbar for many shortcuts
        container_frame = tk.Frame(self, bg=self.bg_color)
        container_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(container_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for scrolling
        canvas = tk.Canvas(
            container_frame, 
            bg=self.bg_color,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=canvas.yview)
        
        # Frame inside canvas for shortcuts
        shortcuts_frame = tk.Frame(canvas, bg=self.bg_color)
        shortcuts_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=shortcuts_frame, anchor="nw")
        
        # Headers
        header_frame = tk.Frame(shortcuts_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header_frame, 
            text="Action", 
            font=("Helvetica", 10, "bold"),
            width=20, 
            anchor="w",
            bg=self.bg_color, 
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            header_frame, 
            text="Shortcut", 
            font=("Helvetica", 10, "bold"),
            width=15, 
            anchor="w",
            bg=self.bg_color, 
            fg=self.text_color
        ).pack(side=tk.LEFT)
        
        # Separator
        separator = tk.Frame(shortcuts_frame, height=1, bg="#dee2e6")
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Shortcut entries
        self.shortcut_entries = {}
        
        # Human-readable names for actions
        action_names = {
            "transcribe": "Microphone Transcription",
            "system_audio": "System Audio Capture",
            "cut": "Cut",
            "copy": "Copy",
            "paste": "Paste",
            "save": "Save",
            "open": "Open",
            "new": "New"
        }
        
        for action, key in self.shortcuts.items():
            row = tk.Frame(shortcuts_frame, bg=self.bg_color)
            row.pack(fill=tk.X, pady=5)
            
            # Use human-readable name or capitalize action name
            display_name = action_names.get(action, action.replace("_", " ").title())
            
            action_label = tk.Label(
                row, 
                text=display_name, 
                width=20, 
                anchor="w",
                bg=self.bg_color, 
                fg=self.text_color
            )
            action_label.pack(side=tk.LEFT, padx=(0, 10))
            
            shortcut_var = tk.StringVar(value=key)
            self.shortcut_entries[action] = shortcut_var
            
            shortcut_entry = tk.Entry(
                row, 
                textvariable=shortcut_var, 
                width=15,
                bg=self.canvas_bg if hasattr(self, 'canvas_bg') else "white",
                relief=tk.SOLID,
                bd=1
            )
            shortcut_entry.pack(side=tk.LEFT)
            
            # Add a button to record the key press
            record_button = tk.Button(
                row, 
                text="Record", 
                command=lambda a=action, e=shortcut_entry: self.record_shortcut(a, e),
                bg=self.button_bg,
                fg=self.button_fg,
                relief=tk.FLAT,
                padx=10,
                bd=0,
                highlightthickness=0
            )
            record_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Button frame
        button_frame = tk.Frame(self, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(15, 20), padx=20)
        
        # Save button
        save_button = tk.Button(
            button_frame, 
            text="Save", 
            command=self.save_shortcuts,
            bg=self.accent_color,
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
            bg=self.button_bg,
            fg=self.button_fg,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            bd=0,
            highlightthickness=0
        )
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def record_shortcut(self, action, entry):
        entry.delete(0, tk.END)
        entry.insert(0, "Press a key...")
        
        def on_key_press(event):
            key_name = event.keysym
            if key_name in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
                return
            
            modifiers = []
            if event.state & 0x4:  # Control
                modifiers.append("ctrl")
            if event.state & 0x1:  # Shift
                modifiers.append("shift")
            if event.state & 0x8:  # Alt
                modifiers.append("alt")
            
            shortcut = "+".join(modifiers + [key_name.lower()])
            self.shortcut_entries[action].set(shortcut)
            self.focus_set()  # Remove focus from the entry
            
            # Unbind the key press event
            entry.unbind("<Key>")
        
        entry.focus_set()
        entry.bind("<Key>", on_key_press)
    
    def save_shortcuts(self):
        new_shortcuts = {action: shortcut_var.get() for action, shortcut_var in self.shortcut_entries.items()}
        self.save_callback(new_shortcuts)
        self.destroy()