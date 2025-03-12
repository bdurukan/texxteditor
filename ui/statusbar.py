"""
Status bar UI manager for the TextEditor.
Handles status messages and document statistics.
"""

import tkinter as tk

class StatusBarManager:
    def __init__(self, parent_frame, theme):
        self.parent_frame = parent_frame
        self.theme = theme
        
        # Document statistics
        self.word_count = 0
        self.char_count = 0
        self.page_count = 1
        
        # Status bar components
        self.status_frame = None
        self.status_var = None
        self.stats_frame = None
        self.word_count_var = None
        self.char_count_var = None
        self.page_count_var = None
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the status bar UI."""
        self.status_frame = tk.Frame(self.parent_frame, bg=self.theme["status_bg"], height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message (left side)
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            bg=self.theme["status_bg"],
            fg=self.theme["text_color"],
            font=("Calibri", 9),
            anchor=tk.W,
            padx=10
        )
        status_label.pack(side=tk.LEFT)
        
        # Document statistics (right side)
        self.stats_frame = tk.Frame(self.status_frame, bg=self.theme["status_bg"])
        self.stats_frame.pack(side=tk.RIGHT, padx=10)
        
        # Word count
        self.word_count_var = tk.StringVar(value="Words: 0")
        word_count_label = tk.Label(
            self.stats_frame,
            textvariable=self.word_count_var,
            bg=self.theme["status_bg"],
            fg=self.theme["text_color"],
            font=("Calibri", 9),
            padx=5
        )
        word_count_label.pack(side=tk.LEFT)
        
        # Character count
        self.char_count_var = tk.StringVar(value="Characters: 0")
        char_count_label = tk.Label(
            self.stats_frame,
            textvariable=self.char_count_var,
            bg=self.theme["status_bg"],
            fg=self.theme["text_color"],
            font=("Calibri", 9),
            padx=5
        )
        char_count_label.pack(side=tk.LEFT)
        
        # Page count
        self.page_count_var = tk.StringVar(value="Page: 1/1")
        page_count_label = tk.Label(
            self.stats_frame,
            textvariable=self.page_count_var,
            bg=self.theme["status_bg"],
            fg=self.theme["text_color"],
            font=("Calibri", 9),
            padx=5
        )
        page_count_label.pack(side=tk.LEFT)
        
    def update_theme(self, theme):
        """Update the theme of status bar components."""
        self.theme = theme
        
        # Update status bar frame
        self.status_frame.configure(bg=theme["status_bg"])
        self.stats_frame.configure(bg=theme["status_bg"])
        
        # Update labels
        for widget in self.status_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["status_bg"], fg=theme["text_color"])
                
        for widget in self.stats_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["status_bg"], fg=theme["text_color"])
                
    def update_status(self, message):
        """Update the status message."""
        self.status_var.set(message)
        
    def update_statistics(self, text):
        """Update document statistics based on the text content."""
        # Count words
        if text.strip():
            words = text.split()
            self.word_count = len(words)
        else:
            self.word_count = 0
            
        # Count characters
        self.char_count = len(text)
        
        # Estimated page count (approximate)
        # A typical page has about 500 words
        self.page_count = max(1, (self.word_count + 499) // 500)
        
        # Update status bar
        self.word_count_var.set(f"Words: {self.word_count}")
        self.char_count_var.set(f"Characters: {self.char_count}")
        self.page_count_var.set(f"Page: 1/{self.page_count}")
        
        return {
            "word_count": self.word_count,
            "char_count": self.char_count,
            "page_count": self.page_count
        }