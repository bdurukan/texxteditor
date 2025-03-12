"""
Toolbar UI manager for the TextEditor.
Handles formatting toolbar and formatting functions.
"""

import tkinter as tk
from tkinter import font, ttk

class ToolbarManager:
    def __init__(self, parent_frame, theme, text_widget, format_callbacks=None):
        self.parent_frame = parent_frame
        self.theme = theme
        self.text_widget = text_widget
        self.callbacks = format_callbacks or {}
        
        # Default font settings
        self.default_font = ("Calibri", 11)
        
        # Variables for font controls
        self.font_family_var = tk.StringVar(value=self.default_font[0])
        self.font_size_var = tk.StringVar(value=self.default_font[1])
        
        # Toolbar frame and controls
        self.toolbar_frame = None
        self.font_family_combo = None
        self.font_size_combo = None
        self.bold_button = None
        self.italic_button = None
        self.underline_button = None
        self.align_left_button = None
        self.align_center_button = None
        self.align_right_button = None
        self.mic_button = None
        
        # Initialize UI
        self.setup_toolbar()
        
    def setup_toolbar(self):
        """Create the formatting toolbar."""
        # Main toolbar frame
        self.toolbar_frame = tk.Frame(self.parent_frame, bg=self.theme["bg_color"], bd=1, relief=tk.SOLID)
        self.toolbar_frame.pack(fill=tk.X, padx=1, pady=(1, 5))
        
        # Font family combo box
        font_families = list(font.families())
        font_families.sort()
        
        self.font_family_combo = ttk.Combobox(
            self.toolbar_frame, 
            textvariable=self.font_family_var,
            width=15,
            values=font_families
        )
        self.font_family_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.font_family_combo.bind("<<ComboboxSelected>>", self.on_font_change)
        
        # Font size combo box
        font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.font_size_combo = ttk.Combobox(
            self.toolbar_frame, 
            textvariable=self.font_size_var,
            width=5,
            values=font_sizes
        )
        self.font_size_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.font_size_combo.bind("<<ComboboxSelected>>", self.on_font_change)
        
        # Add separator
        tk.Frame(self.toolbar_frame, width=1, bg="#d0d0d0").pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        # Style buttons
        button_style = {
            "bg": self.theme["button_bg"],
            "fg": self.theme["button_fg"],
            "relief": tk.FLAT,
            "padx": 5,
            "pady": 2,
            "font": self.default_font,
            "width": 3,
            "height": 1,
            "borderwidth": 0
        }
        
        # Bold button
        self.bold_button = tk.Button(
            self.toolbar_frame, 
            text="B", 
            command=self.toggle_bold,
            **button_style
        )
        self.bold_button.pack(side=tk.LEFT, padx=2)
        
        # Italic button
        self.italic_button = tk.Button(
            self.toolbar_frame, 
            text="I", 
            command=self.toggle_italic,
            **button_style
        )
        self.italic_button.pack(side=tk.LEFT, padx=2)
        
        # Underline button
        self.underline_button = tk.Button(
            self.toolbar_frame, 
            text="U", 
            command=self.toggle_underline,
            **button_style
        )
        self.underline_button.pack(side=tk.LEFT, padx=2)
        
        # Add separator
        tk.Frame(self.toolbar_frame, width=1, bg="#d0d0d0").pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        # Alignment buttons
        self.align_left_button = tk.Button(
            self.toolbar_frame, 
            text="←", 
            command=lambda: self.set_alignment("left"),
            **button_style
        )
        self.align_left_button.pack(side=tk.LEFT, padx=2)
        
        self.align_center_button = tk.Button(
            self.toolbar_frame, 
            text="↔", 
            command=lambda: self.set_alignment("center"),
            **button_style
        )
        self.align_center_button.pack(side=tk.LEFT, padx=2)
        
        self.align_right_button = tk.Button(
            self.toolbar_frame, 
            text="→", 
            command=lambda: self.set_alignment("right"),
            **button_style
        )
        self.align_right_button.pack(side=tk.LEFT, padx=2)
        
        # Add separator
        tk.Frame(self.toolbar_frame, width=1, bg="#d0d0d0").pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        # Microphone button for speech-to-text
        self.mic_button = tk.Button(
            self.toolbar_frame, 
            text="🎤", 
            command=self.start_transcription,
            **button_style
        )
        self.mic_button.pack(side=tk.LEFT, padx=2)
        
    def update_theme(self, theme):
        """Update the theme of toolbar components."""
        self.theme = theme
        
        # Update toolbar frame
        self.toolbar_frame.configure(bg=theme["bg_color"])
        
        # Update buttons
        button_config = {
            "bg": theme["button_bg"],
            "fg": theme["button_fg"]
        }
        self.bold_button.configure(**button_config)
        self.italic_button.configure(**button_config)
        self.underline_button.configure(**button_config)
        self.align_left_button.configure(**button_config)
        self.align_center_button.configure(**button_config)
        self.align_right_button.configure(**button_config)
        self.mic_button.configure(**button_config)
        
    def on_font_change(self, event=None):
        """Handle font selection changes."""
        if 'apply_font' in self.callbacks:
            self.callbacks['apply_font'](
                self.font_family_var.get(),
                int(self.font_size_var.get())
            )
            
    def toggle_bold(self):
        """Toggle bold formatting on selected text."""
        if 'toggle_bold' in self.callbacks:
            self.callbacks['toggle_bold']()
        else:
            self._default_toggle_bold()
            
    def _default_toggle_bold(self):
        """Default bold toggle implementation."""
        if not self.text_widget.tag_ranges(tk.SEL):
            return
            
        # Check if selection already has bold tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "bold" in current_tags:
            # Remove bold
            self.text_widget.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
        else:
            # Apply bold
            self.text_widget.tag_configure("bold", font=(None, None, "bold"))
            self.text_widget.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
            
    def toggle_italic(self):
        """Toggle italic formatting on selected text."""
        if 'toggle_italic' in self.callbacks:
            self.callbacks['toggle_italic']()
        else:
            self._default_toggle_italic()
            
    def _default_toggle_italic(self):
        """Default italic toggle implementation."""
        if not self.text_widget.tag_ranges(tk.SEL):
            return
            
        # Check if selection already has italic tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "italic" in current_tags:
            # Remove italic
            self.text_widget.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
        else:
            # Apply italic
            self.text_widget.tag_configure("italic", font=(None, None, "italic"))
            self.text_widget.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
            
    def toggle_underline(self):
        """Toggle underline formatting on selected text."""
        if 'toggle_underline' in self.callbacks:
            self.callbacks['toggle_underline']()
        else:
            self._default_toggle_underline()
            
    def _default_toggle_underline(self):
        """Default underline toggle implementation."""
        if not self.text_widget.tag_ranges(tk.SEL):
            return
            
        # Check if selection already has underline tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "underline" in current_tags:
            # Remove underline
            self.text_widget.tag_remove("underline", tk.SEL_FIRST, tk.SEL_LAST)
        else:
            # Apply underline
            self.text_widget.tag_configure("underline", underline=True)
            self.text_widget.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
            
    def set_alignment(self, alignment):
        """Set text alignment for the paragraph."""
        if 'set_alignment' in self.callbacks:
            self.callbacks['set_alignment'](alignment)
        else:
            self._default_set_alignment(alignment)
            
    def _default_set_alignment(self, alignment):
        """Default alignment implementation."""
        if alignment == "left":
            self.text_widget.tag_configure("align", justify=tk.LEFT)
        elif alignment == "center":
            self.text_widget.tag_configure("align", justify=tk.CENTER)
        elif alignment == "right":
            self.text_widget.tag_configure("align", justify=tk.RIGHT)
        else:  # justify
            self.text_widget.tag_configure("align", justify=tk.LEFT)
            
        # Apply to entire paragraph if no selection
        if not self.text_widget.tag_ranges(tk.SEL):
            # Get the paragraph (current line)
            current_line = self.text_widget.index(tk.INSERT).split('.')[0]
            start = f"{current_line}.0"
            end = f"{current_line}.end"
            
            # Apply alignment
            self.text_widget.tag_add("align", start, end)
        else:
            # Apply to selected text
            self.text_widget.tag_add("align", tk.SEL_FIRST, tk.SEL_LAST)
            
    def start_transcription(self):
        """Start speech-to-text transcription."""
        if 'start_transcription' in self.callbacks:
            # Update button appearance
            self.mic_button.configure(relief=tk.SUNKEN, bg=self.theme["accent_color"], fg="white")
            self.callbacks['start_transcription'](self.reset_mic_button)
            
    def reset_mic_button(self):
        """Reset the microphone button appearance."""
        self.mic_button.configure(relief=tk.FLAT, bg=self.theme["button_bg"], fg=self.theme["button_fg"])