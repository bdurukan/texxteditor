"""
Modern Text Editor - MS Word-like with A4 Page Format
Main Editor Class with A4 paper dimensions instead of free-form canvas
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font, ttk
import threading
import queue
import keyboard
import time
import os
import json

# Import our modules
from config import SettingsManager
from dialogs import APIKeyDialog, ShortcutEditor
from audio import AudioRecorder

class ModernTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Text Editor - Word Style")
        self.root.geometry("1200x800")
        
        # Initialize the settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize theme settings
        self.init_theme()
        
        # Configure the root window
        self.root.configure(bg=self.bg_color)
        
        # Create the main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        
        # Initialize the text queue for transcribed text
        self.text_queue = queue.Queue()
        
        # Initialize current file path
        self.current_file = None
        
        # Word count and other document statistics
        self.word_count = 0
        self.char_count = 0
        self.page_count = 1
        
        # First run - check if API key is configured
        if not self.settings_manager.get_api_key():
            self.show_api_key_setup()
        else:
            self.setup_main_interface()
        
    def init_theme(self):
        """Initialize theme colors and fonts."""
        # Define theme settings
        self.themes = {
            "light": {
                "bg_color": "#f8f9fa",
                "accent_color": "#4285f4",
                "text_color": "#212529",
                "button_bg": "#ffffff",
                "button_fg": "#4285f4",
                "document_bg": "#ffffff",
                "status_bg": "#f8f9fa",
                "page_border": "#d0d0d0",
                "ruler_bg": "#f0f0f0",
                "ruler_text": "#666666",
                "ruler_tick": "#999999",
                "selection_color": "#e8f0fe"
            },
            "dark": {
                "bg_color": "#212529",
                "accent_color": "#4285f4",
                "text_color": "#e9ecef",
                "button_bg": "#343a40",
                "button_fg": "#4dabf7",
                "document_bg": "#2b3035",
                "status_bg": "#212529",
                "page_border": "#495057",
                "ruler_bg": "#343a40",
                "ruler_text": "#adb5bd",
                "ruler_tick": "#6c757d",
                "selection_color": "#3b5bdb"
            }
        }
        
        # Set initial theme (light by default)
        theme_name = self.settings_manager.get_setting("theme", "light")
        self.theme = self.themes[theme_name]
        self.is_dark_mode = (theme_name == "dark")
        
        # Set theme variables on the instance for easy access
        for key, value in self.theme.items():
            setattr(self, key, value)
            
        # Define fonts
        self.default_font = ("Calibri", 11)
        self.header_font = ("Calibri", 11, "bold")
        self.title_font = ("Calibri", 16, "bold")
        self.status_font = ("Calibri", 9)
        
        # A4 page dimensions in pixels (assuming 96 DPI)
        # A4 is 210mm × 297mm ≈ 8.27in × 11.69in
        # At 96 DPI, that's approximately 794 × 1123 pixels
        self.page_width_px = 794
        self.page_height_px = 1123
        
        # Define margins in pixels (1 inch = 96 pixels at 96 DPI)
        self.margin_left_px = 96
        self.margin_right_px = 96
        self.margin_top_px = 96
        self.margin_bottom_px = 96
        
        # Calculate text area dimensions
        self.text_width_px = self.page_width_px - self.margin_left_px - self.margin_right_px
        self.text_height_px = self.page_height_px - self.margin_top_px - self.margin_bottom_px
        
    def show_api_key_setup(self):
        """Show initial API key setup screen before loading main interface."""
        # Clear any existing content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a centered setup container
        setup_frame = tk.Frame(self.main_frame, bg=self.bg_color, padx=40, pady=40)
        setup_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Add welcome message
        title_label = tk.Label(
            setup_frame,
            text="Welcome to Modern Text Editor",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(pady=(0, 20))
        
        # Add explanation text
        info_text = (
            "To use speech-to-text features, you'll need to configure your OpenAI API key.\n"
            "You can get an API key from https://platform.openai.com/api-keys"
        )
        info_label = tk.Label(
            setup_frame,
            text=info_text,
            font=self.default_font,
            bg=self.bg_color,
            fg=self.text_color,
            justify=tk.LEFT,
            wraplength=400
        )
        info_label.pack(pady=(0, 30))
        
        # API Key entry
        key_frame = tk.Frame(setup_frame, bg=self.bg_color)
        key_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.api_key_var = tk.StringVar()
        
        key_label = tk.Label(
            key_frame,
            text="OpenAI API Key:",
            bg=self.bg_color,
            fg=self.text_color,
            font=self.default_font
        )
        key_label.pack(anchor='w', pady=(0, 5))
        
        key_entry = tk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            width=40,
            font=self.default_font,
            show="*",
            bd=1,
            relief=tk.SOLID
        )
        key_entry.pack(fill=tk.X, ipady=5)
        key_entry.focus_set()  # Set focus on the entry
        
        # Show/hide toggle
        show_var = tk.BooleanVar(value=False)
        
        def toggle_show():
            if show_var.get():
                key_entry.config(show="")
            else:
                key_entry.config(show="*")
        
        show_check = tk.Checkbutton(
            key_frame,
            text="Show key",
            variable=show_var,
            command=toggle_show,
            bg=self.bg_color,
            fg=self.text_color,
            activebackground=self.bg_color,
            selectcolor=self.bg_color
        )
        show_check.pack(anchor='w', pady=(5, 0))
        
        # Skip option
        skip_info = tk.Label(
            setup_frame,
            text="You can skip this step, but speech-to-text features won't be available.",
            font=self.status_font,
            bg=self.bg_color,
            fg=self.text_color,
            justify=tk.LEFT,
            wraplength=400
        )
        skip_info.pack(pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(setup_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Style for buttons
        button_style = {
            "font": self.default_font,
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "borderwidth": 0,
            "highlightthickness": 0,
        }
        
        # Continue button with API key
        continue_btn = tk.Button(
            button_frame,
            text="Continue with API Key",
            command=self.save_initial_api_key,
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            **button_style
        )
        continue_btn.pack(side=tk.RIGHT)
        
        # Skip button
        skip_btn = tk.Button(
            button_frame,
            text="Skip for Now",
            command=self.skip_api_key,
            bg=self.button_bg,
            fg=self.accent_color,
            relief=tk.FLAT,
            **button_style
        )
        skip_btn.pack(side=tk.RIGHT, padx=10)
    
    def save_initial_api_key(self):
        """Save the API key and proceed to main interface."""
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.settings_manager.set_api_key(api_key)
        
        self.setup_main_interface()
    
    def skip_api_key(self):
        """Skip API key setup and proceed to main interface."""
        self.setup_main_interface()
        
    def setup_main_interface(self):
        """Set up the main editor interface."""
        # Clear the setup frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Main editor area with document and rulers
        self.editor_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal ruler
        self.h_ruler_frame = tk.Frame(self.editor_frame, bg=self.ruler_bg, height=20)
        self.h_ruler_frame.pack(fill=tk.X, padx=(30, 0))
        self.create_horizontal_ruler()
        
        # Document area with vertical ruler
        self.document_area = tk.Frame(self.editor_frame, bg=self.bg_color)
        self.document_area.pack(fill=tk.BOTH, expand=True)
        
        # Vertical ruler
        self.v_ruler_frame = tk.Frame(self.document_area, bg=self.ruler_bg, width=30)
        self.v_ruler_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.create_vertical_ruler()
        
        # Document frame (for scrolling)
        self.document_frame = tk.Frame(self.document_area, bg=self.bg_color)
        self.document_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        self.v_scrollbar = tk.Scrollbar(self.document_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = tk.Scrollbar(self.document_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for page (to enable scrolling)
        self.document_canvas = tk.Canvas(
            self.document_frame, 
            bg=self.bg_color,
            highlightthickness=0,
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.document_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        self.v_scrollbar.config(command=self.document_canvas.yview)
        self.h_scrollbar.config(command=self.document_canvas.xview)
        
        # Create frame for A4 page with margins
        self.page_frame = tk.Frame(
            self.document_canvas, 
            bg=self.document_bg,
            width=self.page_width_px,
            height=self.page_height_px,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=self.page_border,
            highlightthickness=1
        )
        
        # Add page to canvas
        self.page_window = self.document_canvas.create_window(
            50, 50,  # Position with some padding
            window=self.page_frame,
            anchor='nw'
        )
        
        # Create text widget for document content
        self.text_widget = tk.Text(
            self.page_frame,
            font=self.default_font,
            wrap=tk.WORD,
            width=1,  # Will be sized by place manager
            height=1,  # Will be sized by place manager
            padx=0,
            pady=0,
            bd=0,
            insertwidth=2,
            selectbackground=self.selection_color,
            highlightthickness=0,
            fg=self.text_color,
            bg=self.document_bg,
            undo=True  # Enable undo/redo
        )
        
        # Place text widget with margins
        self.text_widget.place(
            x=self.margin_left_px,
            y=self.margin_top_px,
            width=self.text_width_px,
            height=self.text_height_px
        )
        
        # Configure tag for search highlighting
        self.text_widget.tag_configure("search", background="yellow")
        
        # Set focus to text widget
        self.text_widget.focus_set()
        
        # Configure the canvas scroll region
        self.document_canvas.config(scrollregion=(0, 0, self.page_width_px + 100, self.page_height_px + 100))
        
        # Status bar
        self.create_status_bar()
        
        # Pack main frame
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize audio recorder with callbacks
        self.audio_recorder = AudioRecorder(
            self.settings_manager,
            status_callback=self.update_status,
            transcription_callback=self.add_transcribed_text
        )
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Start queue checking for transcribed text
        self.queue_check()
        
        # Add event bindings
        self.bind_events()
        
        # Update statistics
        self.update_statistics()
        
    def update_status(self, message):
        """Update the status bar message."""
        self.status_var.set(message)
        
    def create_menu_bar(self):
        """Create the main menu bar."""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_document)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: self.text_widget.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", command=lambda: self.text_widget.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all)
        edit_menu.add_command(label="Find", command=self.show_find_dialog)
        edit_menu.add_command(label="Replace", command=self.show_replace_dialog)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Format menu
        format_menu = tk.Menu(menu_bar, tearoff=0)
        format_menu.add_command(label="Font...", command=self.show_font_dialog)
        
        # Paragraph submenu
        paragraph_menu = tk.Menu(format_menu, tearoff=0)
        paragraph_menu.add_command(label="Left Align", command=lambda: self.set_alignment("left"))
        paragraph_menu.add_command(label="Center", command=lambda: self.set_alignment("center"))
        paragraph_menu.add_command(label="Right Align", command=lambda: self.set_alignment("right"))
        paragraph_menu.add_command(label="Justify", command=lambda: self.set_alignment("justify"))
        format_menu.add_cascade(label="Paragraph", menu=paragraph_menu)
        
        menu_bar.add_cascade(label="Format", menu=format_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Word Count", command=self.show_word_count)
        tools_menu.add_command(label="Spell Check", command=self.spell_check)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Configure API Key", command=self.configure_api_key)
        settings_menu.add_command(label="Edit Shortcuts", command=self.edit_shortcuts)
        settings_menu.add_command(label="System Audio Capture", command=self.configure_system_audio)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
    def create_toolbar(self):
        """Create the formatting toolbar."""
        # Main toolbar frame
        self.toolbar_frame = tk.Frame(self.main_frame, bg=self.bg_color, bd=1, relief=tk.SOLID)
        self.toolbar_frame.pack(fill=tk.X, padx=1, pady=(1, 5))
        
        # Font family combo box
        font_families = list(font.families())
        font_families.sort()
        
        self.font_family_var = tk.StringVar(value=self.default_font[0])
        self.font_family_combo = ttk.Combobox(
            self.toolbar_frame, 
            textvariable=self.font_family_var,
            width=15,
            values=font_families
        )
        self.font_family_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.font_family_combo.bind("<<ComboboxSelected>>", self.apply_font)
        
        # Font size combo box
        font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.font_size_var = tk.StringVar(value=self.default_font[1])
        self.font_size_combo = ttk.Combobox(
            self.toolbar_frame, 
            textvariable=self.font_size_var,
            width=5,
            values=font_sizes
        )
        self.font_size_combo.pack(side=tk.LEFT, padx=5, pady=5)
        self.font_size_combo.bind("<<ComboboxSelected>>", self.apply_font)
        
        # Add separator
        tk.Frame(self.toolbar_frame, width=1, bg="#d0d0d0").pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        # Style buttons
        button_style = {
            "bg": self.button_bg,
            "fg": self.button_fg,
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
        
    def create_horizontal_ruler(self):
        """Create the horizontal ruler."""
        self.h_ruler_canvas = tk.Canvas(
            self.h_ruler_frame, 
            bg=self.ruler_bg, 
            height=20, 
            highlightthickness=0
        )
        self.h_ruler_canvas.pack(fill=tk.X)
        
        # Draw ruler markings (assuming 96 DPI)
        for i in range(0, self.page_width_px + 100, 96):  # Every inch (96 pixels)
            # Draw major tick and label
            self.h_ruler_canvas.create_line(
                i, 18, i, 10, 
                fill=self.ruler_tick
            )
            self.h_ruler_canvas.create_text(
                i, 5, 
                text=str(i // 96), 
                fill=self.ruler_text,
                font=("Arial", 7)
            )
            
            # Draw minor ticks (1/4 inch)
            for j in range(1, 4):
                minor_tick = i + (j * 24)  # 96/4 = 24 pixels per 1/4 inch
                self.h_ruler_canvas.create_line(
                    minor_tick, 18, minor_tick, 14, 
                    fill=self.ruler_tick
                )
    
    def create_vertical_ruler(self):
        """Create the vertical ruler."""
        self.v_ruler_canvas = tk.Canvas(
            self.v_ruler_frame, 
            bg=self.ruler_bg, 
            width=30, 
            highlightthickness=0
        )
        self.v_ruler_canvas.pack(fill=tk.Y)
        
        # Draw ruler markings (assuming 96 DPI)
        for i in range(0, self.page_height_px + 100, 96):  # Every inch (96 pixels)
            # Draw major tick and label
            self.v_ruler_canvas.create_line(
                28, i, 20, i, 
                fill=self.ruler_tick
            )
            self.v_ruler_canvas.create_text(
                15, i, 
                text=str(i // 96), 
                fill=self.ruler_text,
                font=("Arial", 7)
            )
            
            # Draw minor ticks (1/4 inch)
            for j in range(1, 4):
                minor_tick = i + (j * 24)  # 96/4 = 24 pixels per 1/4 inch
                self.v_ruler_canvas.create_line(
                    28, minor_tick, 24, minor_tick, 
                    fill=self.ruler_tick
                )
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_frame = tk.Frame(self.main_frame, bg=self.status_bg, height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status message (left side)
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            bg=self.status_bg,
            fg=self.text_color,
            font=self.status_font,
            anchor=tk.W,
            padx=10
        )
        status_label.pack(side=tk.LEFT)
        
        # Document statistics (right side)
        self.stats_frame = tk.Frame(self.status_frame, bg=self.status_bg)
        self.stats_frame.pack(side=tk.RIGHT, padx=10)
        
        # Word count
        self.word_count_var = tk.StringVar(value="Words: 0")
        word_count_label = tk.Label(
            self.stats_frame,
            textvariable=self.word_count_var,
            bg=self.status_bg,
            fg=self.text_color,
            font=self.status_font,
            padx=5
        )
        word_count_label.pack(side=tk.LEFT)
        
        # Character count
        self.char_count_var = tk.StringVar(value="Characters: 0")
        char_count_label = tk.Label(
            self.stats_frame,
            textvariable=self.char_count_var,
            bg=self.status_bg,
            fg=self.text_color,
            font=self.status_font,
            padx=5
        )
        char_count_label.pack(side=tk.LEFT)
        
        # Page count
        self.page_count_var = tk.StringVar(value="Page: 1/1")
        page_count_label = tk.Label(
            self.stats_frame,
            textvariable=self.page_count_var,
            bg=self.status_bg,
            fg=self.text_color,
            font=self.status_font,
            padx=5
        )
        page_count_label.pack(side=tk.LEFT)
    
    def bind_events(self):
        """Set up event bindings."""
        # Text widget events
        self.text_widget.bind("<KeyRelease>", self.handle_key_release)
        self.text_widget.bind("<Control-a>", self.select_all)
        self.text_widget.bind("<Control-f>", lambda event: self.show_find_dialog())
        self.text_widget.bind("<Control-h>", lambda event: self.show_replace_dialog())
        
        # Canvas events
        self.document_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Window events
        self.root.bind("<FocusIn>", lambda event: self.text_widget.focus_set())
    
    def handle_key_release(self, event):
        """Handle key release events in the text widget."""
        # Update word and character count
        self.update_statistics()
    
    def on_canvas_configure(self, event):
        """Handle canvas resize events."""
        # Update the scroll region
        self.document_canvas.config(scrollregion=self.document_canvas.bbox("all"))
        
        # Center the page in the canvas
        canvas_width = event.width
        canvas_height = event.height
        
        # Only center if the canvas is larger than the page
        if canvas_width > self.page_width_px + 100:
            x = (canvas_width - self.page_width_px) / 2
            self.document_canvas.coords(self.page_window, x, 50)
    
    def update_statistics(self):
        """Update document statistics."""
        # Get text content
        text = self.text_widget.get("1.0", "end-1c")
        
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
    
    def queue_check(self):
        """Check the text queue for transcribed text."""
        try:
            while True:
                text = self.text_queue.get_nowait()
                self.add_text(text)
        except queue.Empty:
            pass
        self.root.after(100, self.queue_check)
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        if theme_name in self.themes:
            self.theme = self.themes[theme_name]
            self.is_dark_mode = (theme_name == "dark")
            
            # Update theme variables on instance
            for key, value in self.theme.items():
                setattr(self, key, value)
            
            # Update UI components
            self.update_ui_theme()
            
            # Save theme setting
            self.settings_manager.update_setting("theme", theme_name)
            
            # Update status
            self.status_var.set(f"{theme_name.capitalize()} theme applied")
    
    def update_ui_theme(self):
        """Update UI components with current theme."""
        # Update root and frames
        self.root.configure(bg=self.bg_color)
        self.main_frame.configure(bg=self.bg_color)
        self.toolbar_frame.configure(bg=self.bg_color)
        self.editor_frame.configure(bg=self.bg_color)
        self.document_area.configure(bg=self.bg_color)
        self.document_frame.configure(bg=self.bg_color)
        
        # Update rulers
        self.h_ruler_frame.configure(bg=self.ruler_bg)
        self.v_ruler_frame.configure(bg=self.ruler_bg)
        self.h_ruler_canvas.configure(bg=self.ruler_bg)
        self.v_ruler_canvas.configure(bg=self.ruler_bg)
        
        # Update document canvas and page
        self.document_canvas.configure(bg=self.bg_color)
        self.page_frame.configure(
            bg=self.document_bg,
            highlightbackground=self.page_border
        )
        
        # Update text widget
        self.text_widget.configure(
            fg=self.text_color,
            bg=self.document_bg,
            selectbackground=self.selection_color
        )
        
        # Update toolbar buttons
        button_config = {
            "bg": self.button_bg,
            "fg": self.button_fg
        }
        self.bold_button.configure(**button_config)
        self.italic_button.configure(**button_config)
        self.underline_button.configure(**button_config)
        self.align_left_button.configure(**button_config)
        self.align_center_button.configure(**button_config)
        self.align_right_button.configure(**button_config)
        self.mic_button.configure(**button_config)
        
        # Update status bar
        self.status_frame.configure(bg=self.status_bg)
        self.stats_frame.configure(bg=self.status_bg)
        
        for widget in self.status_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.status_bg, fg=self.text_color)
                
        for widget in self.stats_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.status_bg, fg=self.text_color)
    
    def apply_font(self, event=None):
        """Apply selected font to text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            # No selection, show error message
            self.status_var.set("Please select text first")
            return
            
        # Get font settings
        family = self.font_family_var.get()
        size = int(self.font_size_var.get())
        
        # Apply to selected text
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        # Check for existing font tags and remove them
        for tag in current_tags:
            if tag.startswith("font-"):
                self.text_widget.tag_remove(tag, tk.SEL_FIRST, tk.SEL_LAST)
        
        # Create new font tag
        tag_name = f"font-{family}-{size}"
        self.text_widget.tag_configure(tag_name, font=(family, size))
        self.text_widget.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
        
        self.status_var.set(f"Font applied: {family}, {size}pt")
    
    def toggle_bold(self):
        """Toggle bold formatting on selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.status_var.set("Please select text first")
            return
            
        # Check if selection already has bold tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "bold" in current_tags:
            # Remove bold
            self.text_widget.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Bold removed")
        else:
            # Apply bold
            self.text_widget.tag_configure("bold", font=(None, None, "bold"))
            self.text_widget.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Bold applied")
    
    def toggle_italic(self):
        """Toggle italic formatting on selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.status_var.set("Please select text first")
            return
            
        # Check if selection already has italic tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "italic" in current_tags:
            # Remove italic
            self.text_widget.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Italic removed")
        else:
            # Apply italic
            self.text_widget.tag_configure("italic", font=(None, None, "italic"))
            self.text_widget.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Italic applied")
    
    def toggle_underline(self):
        """Toggle underline formatting on selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.status_var.set("Please select text first")
            return
            
        # Check if selection already has underline tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "underline" in current_tags:
            # Remove underline
            self.text_widget.tag_remove("underline", tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Underline removed")
        else:
            # Apply underline
            self.text_widget.tag_configure("underline", underline=True)
            self.text_widget.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
            self.status_var.set("Underline applied")
    
    def set_alignment(self, alignment):
        """Set text alignment for the paragraph."""
        if alignment == "left":
            self.text_widget.tag_configure("align", justify=tk.LEFT)
        elif alignment == "center":
            self.text_widget.tag_configure("align", justify=tk.CENTER)
        elif alignment == "right":
            self.text_widget.tag_configure("align", justify=tk.RIGHT)
        else:  # justify
            self.text_widget.tag_configure("align", justify=tk.LEFT)  # Default justify in tkinter
            
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
            
        self.status_var.set(f"{alignment.capitalize()} alignment applied")
    
    def show_font_dialog(self):
        """Show font selection dialog."""
        # A simple font dialog (could be replaced with ttk.Notebook for a more complete dialog)
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("Font")
        font_dialog.geometry("400x300")
        font_dialog.transient(self.root)
        font_dialog.grab_set()
        
        # Center the dialog
        font_dialog.update_idletasks()
        width = font_dialog.winfo_width()
        height = font_dialog.winfo_height()
        x = (font_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (font_dialog.winfo_screenheight() // 2) - (height // 2)
        font_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Font family list
        family_frame = tk.Frame(font_dialog)
        family_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(family_frame, text="Font:").pack(anchor=tk.W)
        
        family_listbox = tk.Listbox(family_frame, exportselection=0)
        family_listbox.pack(fill=tk.BOTH, expand=True)
        
        for family in sorted(font.families()):
            family_listbox.insert(tk.END, family)
            
        # Set selection to current font
        try:
            current_index = sorted(font.families()).index(self.font_family_var.get())
            family_listbox.selection_set(current_index)
            family_listbox.see(current_index)
        except ValueError:
            pass
        
        # Font style and size frame
        style_frame = tk.Frame(font_dialog)
        style_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Style
        tk.Label(style_frame, text="Font style:").pack(anchor=tk.W)
        
        styles = ["Regular", "Bold", "Italic", "Bold Italic"]
        style_listbox = tk.Listbox(style_frame, height=4)
        style_listbox.pack(fill=tk.X)
        
        for style in styles:
            style_listbox.insert(tk.END, style)
        
        # Size
        tk.Label(style_frame, text="Size:").pack(anchor=tk.W, pady=(10, 0))
        
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        size_listbox = tk.Listbox(style_frame)
        size_listbox.pack(fill=tk.BOTH, expand=True)
        
        for size in sizes:
            size_listbox.insert(tk.END, size)
            
        # Set selection to current size
        try:
            current_size_index = sizes.index(int(self.font_size_var.get()))
            size_listbox.selection_set(current_size_index)
            size_listbox.see(current_size_index)
        except (ValueError, TypeError):
            pass
        
        # Preview frame
        preview_frame = tk.Frame(font_dialog, relief=tk.GROOVE, bd=2)
        preview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        preview_label = tk.Label(preview_frame, text="AaBbYyZz", height=3)
        preview_label.pack()
        
        # Button frame
        button_frame = tk.Frame(font_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Update preview when selection changes
        def update_preview(event=None):
            # Get selected font family
            if family_listbox.curselection():
                family = family_listbox.get(family_listbox.curselection()[0])
            else:
                family = self.font_family_var.get()
                
            # Get selected style
            if style_listbox.curselection():
                style_index = style_listbox.curselection()[0]
                style = styles[style_index]
            else:
                style = "Regular"
                
            # Map style to font options
            if style == "Bold":
                font_style = "bold"
            elif style == "Italic":
                font_style = "italic"
            elif style == "Bold Italic":
                font_style = "bold italic"
            else:
                font_style = "normal"
                
            # Get selected size
            if size_listbox.curselection():
                size = size_listbox.get(size_listbox.curselection()[0])
            else:
                size = self.font_size_var.get()
                
            # Update preview
            preview_label.config(font=(family, size, font_style))
            
        family_listbox.bind("<<ListboxSelect>>", update_preview)
        style_listbox.bind("<<ListboxSelect>>", update_preview)
        size_listbox.bind("<<ListboxSelect>>", update_preview)
        
        # Initial preview update
        update_preview()
        
        # OK button
        def apply_font_and_close():
            # Get selected values
            if family_listbox.curselection():
                family = family_listbox.get(family_listbox.curselection()[0])
                self.font_family_var.set(family)
                
            if size_listbox.curselection():
                size = size_listbox.get(size_listbox.curselection()[0])
                self.font_size_var.set(size)
                
            # Apply to selection
            self.apply_font()
            
            # Close dialog
            font_dialog.destroy()
            
        ok_button = tk.Button(
            button_frame, 
            text="OK", 
            command=apply_font_and_close,
            width=10
        )
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=font_dialog.destroy,
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def show_find_dialog(self):
        """Show find dialog."""
        find_dialog = tk.Toplevel(self.root)
        find_dialog.title("Find")
        find_dialog.geometry("300x100")
        find_dialog.transient(self.root)
        find_dialog.grab_set()
        
        # Center the dialog
        find_dialog.update_idletasks()
        width = find_dialog.winfo_width()
        height = find_dialog.winfo_height()
        x = (find_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (find_dialog.winfo_screenheight() // 2) - (height // 2)
        find_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Find frame
        find_frame = tk.Frame(find_dialog, padx=10, pady=10)
        find_frame.pack(fill=tk.X)
        
        tk.Label(find_frame, text="Find what:").pack(side=tk.LEFT)
        
        find_var = tk.StringVar()
        find_entry = tk.Entry(find_frame, textvariable=find_var, width=25)
        find_entry.pack(side=tk.LEFT, padx=5)
        find_entry.focus_set()
        
        # Case sensitivity
        case_var = tk.BooleanVar(value=False)
        case_check = tk.Checkbutton(find_dialog, text="Match case", variable=case_var)
        case_check.pack(anchor=tk.W, padx=10)
        
        # Button frame
        button_frame = tk.Frame(find_dialog, padx=10, pady=(0, 10))
        button_frame.pack(fill=tk.X)
        
        # Find next function
        def find_text():
            # Remove existing highlights
            self.text_widget.tag_remove("search", "1.0", tk.END)
            
            search_text = find_var.get()
            if not search_text:
                return
                
            # Start search from current cursor position
            current_pos = self.text_widget.index(tk.INSERT)
            
            # Configure case sensitivity
            if case_var.get():
                start_pos = self.text_widget.search(
                    search_text, current_pos, stopindex=tk.END, exact=True
                )
            else:
                start_pos = self.text_widget.search(
                    search_text, current_pos, stopindex=tk.END, nocase=True
                )
                
            if start_pos:
                # Calculate end position based on search string length
                end_pos = f"{start_pos}+{len(search_text)}c"
                
                # Select and highlight the text
                self.text_widget.tag_add("search", start_pos, end_pos)
                self.text_widget.mark_set(tk.INSERT, end_pos)
                self.text_widget.see(start_pos)
                
                # Update status
                self.status_var.set(f"Found: '{search_text}'")
            else:
                # Start from beginning if not found
                if case_var.get():
                    start_pos = self.text_widget.search(
                        search_text, "1.0", stopindex=current_pos, exact=True
                    )
                else:
                    start_pos = self.text_widget.search(
                        search_text, "1.0", stopindex=current_pos, nocase=True
                    )
                    
                if start_pos:
                    # Calculate end position
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    
                    # Select and highlight the text
                    self.text_widget.tag_add("search", start_pos, end_pos)
                    self.text_widget.mark_set(tk.INSERT, end_pos)
                    self.text_widget.see(start_pos)
                    
                    # Update status
                    self.status_var.set(f"Found: '{search_text}' (search wrapped)")
                else:
                    self.status_var.set(f"Cannot find: '{search_text}'")
        
        # Find button
        find_button = tk.Button(
            button_frame, 
            text="Find Next", 
            command=find_text,
            width=10
        )
        find_button.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=find_dialog.destroy,
            width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to find button
        find_entry.bind("<Return>", lambda event: find_text())
        
    def show_replace_dialog(self):
        """Show find and replace dialog."""
        replace_dialog = tk.Toplevel(self.root)
        replace_dialog.title("Replace")
        replace_dialog.geometry("350x150")
        replace_dialog.transient(self.root)
        replace_dialog.grab_set()
        
        # Center the dialog
        replace_dialog.update_idletasks()
        width = replace_dialog.winfo_width()
        height = replace_dialog.winfo_height()
        x = (replace_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (replace_dialog.winfo_screenheight() // 2) - (height // 2)
        replace_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Find frame
        find_frame = tk.Frame(replace_dialog, padx=10, pady=(10, 5))
        find_frame.pack(fill=tk.X)
        
        tk.Label(find_frame, text="Find what:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        
        find_var = tk.StringVar()
        find_entry = tk.Entry(find_frame, textvariable=find_var, width=30)
        find_entry.pack(side=tk.LEFT, padx=5)
        find_entry.focus_set()
        
        # Replace frame
        replace_frame = tk.Frame(replace_dialog, padx=10, pady=5)
        replace_frame.pack(fill=tk.X)
        
        tk.Label(replace_frame, text="Replace with:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        
        replace_var = tk.StringVar()
        replace_entry = tk.Entry(replace_frame, textvariable=replace_var, width=30)
        replace_entry.pack(side=tk.LEFT, padx=5)
        
        # Case sensitivity
        options_frame = tk.Frame(replace_dialog, padx=10)
        options_frame.pack(fill=tk.X, pady=5)
        
        case_var = tk.BooleanVar(value=False)
        case_check = tk.Checkbutton(options_frame, text="Match case", variable=case_var)
        case_check.pack(anchor=tk.W)
        
        # Button frame
        button_frame = tk.Frame(replace_dialog, padx=10, pady=(5, 10))
        button_frame.pack(fill=tk.X)
        
        # Find text function
        def find_text():
            # Remove existing highlights
            self.text_widget.tag_remove("search", "1.0", tk.END)
            
            search_text = find_var.get()
            if not search_text:
                return
                
            # Start search from current cursor position
            current_pos = self.text_widget.index(tk.INSERT)
            
            # Configure case sensitivity
            if case_var.get():
                start_pos = self.text_widget.search(
                    search_text, current_pos, stopindex=tk.END, exact=True
                )
            else:
                start_pos = self.text_widget.search(
                    search_text, current_pos, stopindex=tk.END, nocase=True
                )
                
            if start_pos:
                # Calculate end position based on search string length
                end_pos = f"{start_pos}+{len(search_text)}c"
                
                # Select and highlight the text
                self.text_widget.tag_add("search", start_pos, end_pos)
                self.text_widget.mark_set(tk.INSERT, end_pos)
                self.text_widget.see(start_pos)
                
                # Update status
                self.status_var.set(f"Found: '{search_text}'")
                return True
            else:
                # Start from beginning if not found
                if case_var.get():
                    start_pos = self.text_widget.search(
                        search_text, "1.0", stopindex=current_pos, exact=True
                    )
                else:
                    start_pos = self.text_widget.search(
                        search_text, "1.0", stopindex=current_pos, nocase=True
                    )
                    
                if start_pos:
                    # Calculate end position
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    
                    # Select and highlight the text
                    self.text_widget.tag_add("search", start_pos, end_pos)
                    self.text_widget.mark_set(tk.INSERT, end_pos)
                    self.text_widget.see(start_pos)
                    
                    # Update status
                    self.status_var.set(f"Found: '{search_text}' (search wrapped)")
                    return True
                else:
                    self.status_var.set(f"Cannot find: '{search_text}'")
                    return False
        
        # Replace function
        def replace_text():
            # Check if we have a selection
            try:
                start_pos = self.text_widget.index("search.first")
                end_pos = self.text_widget.index("search.last")
                
                # Replace the selected text
                self.text_widget.delete(start_pos, end_pos)
                self.text_widget.insert(start_pos, replace_var.get())
                self.text_widget.mark_set(tk.INSERT, f"{start_pos}+{len(replace_var.get())}c")
                
                # Find next occurrence
                find_text()
                
                # Update status
                self.status_var.set("Replaced")
            except tk.TclError:
                # No selection, find first
                find_text()
        
        # Replace all function
        def replace_all():
            # Start from the beginning
            self.text_widget.mark_set(tk.INSERT, "1.0")
            
            count = 0
            while True:
                # Find next occurrence
                if not find_text():
                    break
                    
                # Replace it
                start_pos = self.text_widget.index("search.first")
                end_pos = self.text_widget.index("search.last")
                
                self.text_widget.delete(start_pos, end_pos)
                self.text_widget.insert(start_pos, replace_var.get())
                self.text_widget.mark_set(tk.INSERT, f"{start_pos}+{len(replace_var.get())}c")
                
                count += 1
                
            # Update status
            self.status_var.set(f"Replaced {count} occurrences")
        
        # Buttons
        find_button = tk.Button(
            button_frame, 
            text="Find Next", 
            command=find_text,
            width=10
        )
        find_button.pack(side=tk.LEFT)
        
        replace_button = tk.Button(
            button_frame, 
            text="Replace", 
            command=replace_text,
            width=10
        )
        replace_button.pack(side=tk.LEFT, padx=5)
        
        replace_all_button = tk.Button(
            button_frame, 
            text="Replace All", 
            command=replace_all,
            width=10
        )
        replace_all_button.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=replace_dialog.destroy,
            width=10
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def show_word_count(self):
        """Show detailed word count dialog."""
        # Update statistics
        self.update_statistics()
        
        # Create dialog
        stats_dialog = tk.Toplevel(self.root)
        stats_dialog.title("Word Count")
        stats_dialog.geometry("300x200")
        stats_dialog.transient(self.root)
        stats_dialog.grab_set()
        
        # Center the dialog
        stats_dialog.update_idletasks()
        width = stats_dialog.winfo_width()
        height = stats_dialog.winfo_height()
        x = (stats_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (stats_dialog.winfo_screenheight() // 2) - (height // 2)
        stats_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Get more detailed statistics
        text = self.text_widget.get("1.0", "end-1c")
        
        # Count pages (estimate)
        pages = max(1, (self.word_count + 499) // 500)
        
        # Count paragraphs
        paragraphs = max(1, len([p for p in text.split('\n\n') if p.strip()]))
        
        # Count sentences (rough estimate)
        sentences = max(1, len([s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]))
        
        # Count lines
        lines = max(1, text.count('\n') + 1)
        
        # Create statistics display
        frame = tk.Frame(stats_dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Grid layout for statistics
        tk.Label(frame, text="Statistics:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Labels
        tk.Label(frame, text="Pages:").grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Label(frame, text="Words:").grid(row=2, column=0, sticky=tk.W, pady=2)
        tk.Label(frame, text="Characters (with spaces):").grid(row=3, column=0, sticky=tk.W, pady=2)
        tk.Label(frame, text="Characters (no spaces):").grid(row=4, column=0, sticky=tk.W, pady=2)
        tk.Label(frame, text="Paragraphs:").grid(row=5, column=0, sticky=tk.W, pady=2)
        tk.Label(frame, text="Lines:").grid(row=6, column=0, sticky=tk.W, pady=2)
        tk.Label(frame, text="Sentences:").grid(row=7, column=0, sticky=tk.W, pady=2)
        
        # Values
        tk.Label(frame, text=str(pages)).grid(row=1, column=1, sticky=tk.E, pady=2)
        tk.Label(frame, text=str(self.word_count)).grid(row=2, column=1, sticky=tk.E, pady=2)
        tk.Label(frame, text=str(len(text))).grid(row=3, column=1, sticky=tk.E, pady=2)
        tk.Label(frame, text=str(len(text.replace(" ", "")))).grid(row=4, column=1, sticky=tk.E, pady=2)
        tk.Label(frame, text=str(paragraphs)).grid(row=5, column=1, sticky=tk.E, pady=2)
        tk.Label(frame, text=str(lines)).grid(row=6, column=1, sticky=tk.E, pady=2)
        tk.Label(frame, text=str(sentences)).grid(row=7, column=1, sticky=tk.E, pady=2)
        
        # Close button
        tk.Button(
            frame, 
            text="Close", 
            command=stats_dialog.destroy,
            width=10
        ).grid(row=8, column=0, columnspan=2, pady=(15, 0))
    
    def spell_check(self):
        """Basic spell check functionality (placeholder)."""
        messagebox.showinfo("Spell Check", "Spell check feature is not implemented in this version.")
        
    def print_document(self):
        """Print document functionality (placeholder)."""
        messagebox.showinfo("Print", "Print feature is not implemented in this version.")
        
    def show_about(self):
        """Show about dialog."""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About Modern Text Editor")
        about_dialog.geometry("400x200")
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        
        # Center the dialog
        about_dialog.update_idletasks()
        width = about_dialog.winfo_width()
        height = about_dialog.winfo_height()
        x = (about_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (height // 2)
        about_dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Content frame
        frame = tk.Frame(about_dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # App info
        tk.Label(
            frame, 
            text="Modern Text Editor",
            font=("Helvetica", 16, "bold")
        ).pack()
        
        tk.Label(
            frame, 
            text="Version 1.0.0",
            font=("Helvetica", 10)
        ).pack()
        
        # Description
        description = (
            "A Microsoft Word-like text editor with A4 paper format.\n"
            "Includes speech-to-text capabilities and basic text formatting."
        )
        
        tk.Label(
            frame, 
            text=description,
            justify=tk.CENTER,
            wraplength=350,
            pady=10
        ).pack()
        
        # Copyright
        tk.Label(
            frame, 
            text="© 2025 Text Editor Team",
            font=("Helvetica", 8)
        ).pack(pady=(10, 0))
        
        # Close button
        tk.Button(
            frame, 
            text="Close", 
            command=about_dialog.destroy,
            width=10
        ).pack(pady=(10, 0))
    
    def configure_api_key(self):
        """Configure the OpenAI API key."""
        dialog = APIKeyDialog(
            self.root, 
            current_key=self.settings_manager.get_api_key(),
            save_callback=self.save_api_key
        )
        self.root.wait_window(dialog)
    
    def save_api_key(self, api_key):
        """Save the API key."""
        self.settings_manager.set_api_key(api_key)
        self.status_var.set("API key saved successfully")
    
    def edit_shortcuts(self):
        """Edit keyboard shortcuts."""
        dialog = ShortcutEditor(
            self.root,
            self.settings_manager.get_shortcuts(),
            self.save_shortcuts
        )
        self.root.wait_window(dialog)
    
    def save_shortcuts(self, new_shortcuts):
        """Save keyboard shortcuts."""
        for action, key_combo in new_shortcuts.items():
            self.settings_manager.update_shortcut(action, key_combo)
        self.setup_shortcuts()
        self.status_var.set("Shortcuts saved successfully")
        
    def configure_system_audio(self):
        """Configure system audio capture settings."""
        system_audio = self.settings_manager.get_setting("system_audio", False)
        
        # Create a dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("System Audio Capture")
        dialog.geometry("400x250")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create content
        content_frame = tk.Frame(dialog, bg=self.bg_color, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="System Audio Capture",
            font=self.header_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Description
        description = tk.Label(
            content_frame,
            text=(
                "Enable system audio capture to transcribe audio from\n"
                "your computer (e.g. from videos or music).\n\n"
                "When enabled, the microphone will be excluded during system audio capture.\n\n"
                "Default shortcut: F10"
            ),
            justify=tk.LEFT,
            bg=self.bg_color,
            fg=self.text_color
        )
        description.pack(anchor='w', pady=(0, 20))
        
        # Enable/disable toggle
        system_audio_var = tk.BooleanVar(value=system_audio)
        toggle = tk.Checkbutton(
            content_frame,
            text="Enable system audio capture",
            variable=system_audio_var,
            bg=self.bg_color,
            fg=self.text_color,
            selectcolor=self.document_bg,
            activebackground=self.bg_color
        )
        toggle.pack(anchor='w', pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X)
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self.save_system_audio_settings(system_audio_var.get(), dialog),
            bg=self.accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            bd=0
        )
        save_btn.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg=self.button_bg,
            fg=self.button_fg,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            bd=0
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
    def save_system_audio_settings(self, enabled, dialog):
        """Save system audio capture settings."""
        self.settings_manager.update_setting("system_audio", enabled)
        dialog.destroy()
        
        status = "enabled" if enabled else "disabled"
        self.status_var.set(f"System audio capture {status}")
        
    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        shortcuts = self.settings_manager.get_shortcuts()
        
        # Clear existing shortcuts
        for shortcut in shortcuts.values():
            try:
                keyboard.remove_hotkey(shortcut)
            except:
                pass
        
        # Set up new shortcuts
        try:
            keyboard.add_hotkey(shortcuts["transcribe"], self.start_transcription, trigger_on_release=False)
            keyboard.add_hotkey(shortcuts["system_audio"], self.start_system_audio_capture, trigger_on_release=False)
            keyboard.add_hotkey(shortcuts["cut"], self.cut)
            keyboard.add_hotkey(shortcuts["copy"], self.copy)
            keyboard.add_hotkey(shortcuts["paste"], self.paste)
            keyboard.add_hotkey(shortcuts["save"], self.save_file)
            keyboard.add_hotkey(shortcuts["open"], self.open_file)
            keyboard.add_hotkey(shortcuts["new"], self.new_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup shortcuts: {e}")
    
    def start_transcription(self):
        """Start recording from the microphone for transcription."""
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            messagebox.showerror("Error", "Please configure your OpenAI API key first")
            self.configure_api_key()
            return
            
        if hasattr(self, 'audio_recorder'):
            # Update the mic button appearance
            self.mic_button.configure(relief=tk.SUNKEN, bg=self.accent_color, fg="white")
            
            # Start recording
            self.status_var.set("Recording... (Hold the transcription key)")
            if self.audio_recorder.start_microphone_transcription():
                # Start monitoring
                self.root.after(100, self.check_transcription_status)
            else:
                # Reset button if failed
                self.mic_button.configure(relief=tk.FLAT, bg=self.button_bg, fg=self.button_fg)
                
    def check_transcription_status(self):
        """Check if transcription is still active."""
        if not hasattr(self, 'audio_recorder') or not self.audio_recorder.is_recording:
            # Recording stopped, reset the button
            self.mic_button.configure(relief=tk.FLAT, bg=self.button_bg, fg=self.button_fg)
        else:
            # Still recording, check again later
            self.root.after(100, self.check_transcription_status)
            
    def start_system_audio_capture(self):
        """Start capturing system audio."""
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            messagebox.showerror("Error", "Please configure your OpenAI API key first")
            self.configure_api_key()
            return
            
        if hasattr(self, 'audio_recorder'):
            # Update the status
            self.status_var.set("Recording system audio... (Release the key to stop)")
            
            # Start recording
            self.audio_recorder.start_system_audio_capture()
    
    def add_transcribed_text(self, text):
        """Add transcribed text to the queue."""
        self.text_queue.put(text)
    
    def add_text(self, text):
        """Add text at the current cursor position."""
        # Get the current index
        current_index = self.text_widget.index(tk.INSERT)
        
        # Insert the text
        self.text_widget.insert(current_index, text)
        
        # Update statistics
        self.update_statistics()
    
    def select_all(self, event=None):
        """Select all text."""
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        return "break"  # Prevent default handling
    
    def cut(self):
        """Cut selected text."""
        if self.text_widget.tag_ranges(tk.SEL):
            self.copy()
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.update_statistics()
    
    def copy(self):
        """Copy selected text."""
        if self.text_widget.tag_ranges(tk.SEL):
            selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
    
    def paste(self):
        """Paste text from clipboard."""
        try:
            text = self.root.clipboard_get()
            if self.text_widget.tag_ranges(tk.SEL):
                self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_widget.insert(tk.INSERT, text)
            self.update_statistics()
        except tk.TclError:
            pass  # Clipboard is empty
    
    def new_file(self):
        """Create a new file."""
        if self.text_widget.get("1.0", "end-1c") and messagebox.askyesno("Save?", "Do you want to save your current work?"):
            self.save_file()
            
        self.text_widget.delete("1.0", tk.END)
        self.current_file = None
        self.update_statistics()
        self.root.title("Modern Text Editor - Word Style")
        self.status_var.set("New file created")
    
    def open_file(self):
        """Open a file."""
        if self.text_widget.get("1.0", "end-1c") and messagebox.askyesno("Save?", "Do you want to save your current work?"):
            self.save_file()
        
        file_path = filedialog.askopenfilename(
            defaultextension=".txt", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    
                # Clear current content and insert new content
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", content)
                
                # Update current file and UI
                self.current_file = file_path
                self.root.title(f"Modern Text Editor - {os.path.basename(file_path)}")
                self.update_statistics()
                self.status_var.set(f"Opened: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            return self.save_file_as()
            
        try:
            content = self.text_widget.get("1.0", "end-1c")
            with open(self.current_file, 'w') as file:
                file.write(content)
                
            self.status_var.set(f"Saved: {self.current_file}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return False
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return False
            
        self.current_file = file_path
        self.root.title(f"Modern Text Editor - {os.path.basename(file_path)}")
        return self.save_file()
    
    def exit_app(self):
        """Exit the application."""
        if self.text_widget.get("1.0", "end-1c") and messagebox.askyesno("Save?", "Do you want to save your current work?"):
            self.save_file()
        self.root.quit()