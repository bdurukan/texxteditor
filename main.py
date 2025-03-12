#!/usr/bin/env python3
"""
TextEditor - A Microsoft Word-like text editor with A4 paper format
Main entry point for the application
"""

import tkinter as tk
import sys

# Check for required packages
try:
    import requests
    import keyboard
    import sounddevice
    import pyaudio
    import numpy as np
    import pydub
except ImportError:
    print("Please install the required packages with:")
    print("pip install requests keyboard pyaudio pydub sounddevice numpy")
    sys.exit(1)

# Import modular components
from config import SettingsManager
from ui.theme import ThemeManager
from ui.document import DocumentManager
from ui.toolbar import ToolbarManager
from ui.statusbar import StatusBarManager
from text.formatter import TextFormatter
from text.search import TextSearcher
from text.statistics import DocumentStatistics
from file.operations import FileOperations
from dialogs import APIKeyDialog, ShortcutEditor
from audio.recorder import AudioRecorder
from dialogs.system_audio_dialog import SystemAudioDialog
from audio.system_capture import SystemAudioCapture

class TextEditorApp:
    """Modern text editor application with A4 paper formatting."""
    
    def __init__(self, root):
        """Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Modern Text Editor - Word Style")
        self.root.geometry("1200x800")
        
        # Initialize settings
        self.settings_manager = SettingsManager()
        
        # Initialize theme
        self.theme_manager = ThemeManager()
        theme_name = self.settings_manager.get_setting("theme", "light")
        self.theme_manager.set_current_theme(theme_name)
        self.theme = self.theme_manager.get_theme()
        
        # For easy access, set theme variables on the instance
        for key, value in self.theme.items():
            setattr(self, key, value)
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        # Main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize text queue for transcribed text
        self.text_queue = tk.StringVar()
        
        # Initialize current file path
        self.current_file = None
        
        # First run - check if API key is configured
        if not self.settings_manager.get_api_key():
            self.show_api_key_setup()
        else:
            self.setup_main_interface()
    
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
            font=("Calibri", 16, "bold"),
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
            font=("Calibri", 11),
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
            font=("Calibri", 11)
        )
        key_label.pack(anchor='w', pady=(0, 5))
        
        key_entry = tk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            width=40,
            font=("Calibri", 11),
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
            font=("Calibri", 9),
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
            "font": ("Calibri", 11),
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
        # Clear any existing content
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar with formatting options
        format_callbacks = {
            'apply_font': self.apply_font,
            'toggle_bold': self.toggle_bold,
            'toggle_italic': self.toggle_italic,
            'toggle_underline': self.toggle_underline,
            'set_alignment': self.set_alignment,
            'start_transcription': self.start_transcription
        }
        self.toolbar_manager = ToolbarManager(
            self.main_frame, 
            self.theme, 
            None,  # Will set text_widget later
            format_callbacks
        )
        
        # Create document area (page, text widget, rulers)
        self.document_manager = DocumentManager(self.main_frame, self.theme)
        
        # Now we can set the text widget for the toolbar
        self.toolbar_manager.text_widget = self.document_manager.text_widget
        
        # Create status bar
        self.statusbar_manager = StatusBarManager(self.main_frame, self.theme)
        
        # Create text formatter
        self.text_formatter = TextFormatter(
            self.document_manager.text_widget,
            self.update_status
        )
        
        # Create text searcher
        self.text_searcher = TextSearcher(
            self.document_manager.text_widget,
            self.update_status
        )
        
        # Create document statistics
        self.document_statistics = DocumentStatistics(self.document_manager.text_widget)
        
        # Create file operations
        self.file_operations = FileOperations(
            self.document_manager.text_widget,
            self.update_title,
            self.update_status
        )
        
        # Initialize audio recorder with callbacks
        self.audio_recorder = AudioRecorder(
            self.settings_manager,
            status_callback=self.update_status,
            transcription_callback=self.add_transcribed_text
        )

        # Initialize system audio capture
        self.system_audio_capture = SystemAudioCapture(
            self.settings_manager,
            self.audio_recorder.transcription_service,
            status_callback=self.update_status,
            text_callback=self.add_transcribed_text,
            continuous_mode=self.settings_manager.get_setting("continuous_transcription", False)
        )
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
        
        # Bind events
        self.bind_events()
        
        # Update statistics
        self.update_statistics()
        
        # Set focus to text widget
        self.document_manager.text_widget.focus_set()
    
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
        edit_menu.add_command(label="Undo", command=lambda: self.document_manager.text_widget.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", command=lambda: self.document_manager.text_widget.event_generate("<<Redo>>"))
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
    
    def bind_events(self):
        """Set up event bindings."""
        # Text widget events
        self.document_manager.text_widget.bind("<KeyRelease>", self.handle_key_release)
        self.document_manager.text_widget.bind("<Control-a>", self.select_all)
        self.document_manager.text_widget.bind("<Control-f>", lambda event: self.show_find_dialog())
        self.document_manager.text_widget.bind("<Control-h>", lambda event: self.show_replace_dialog())
        
        # Canvas events
        self.document_manager.document_canvas.bind("<Configure>", self.document_manager.on_canvas_configure)
        
        # Window events
        self.root.bind("<FocusIn>", lambda event: self.document_manager.text_widget.focus_set())
    
    def handle_key_release(self, event):
        """Handle key release events in the text widget."""
        # Update word and character count
        self.update_statistics()
    
    def update_statistics(self):
        """Update document statistics."""
        # Get text content
        text = self.document_manager.text_widget.get("1.0", "end-1c")
        
        # Update status bar 
        self.statusbar_manager.update_statistics(text)
    
    def update_status(self, message):
        """Update the status bar message."""
        self.statusbar_manager.update_status(message)
        
    def update_title(self, title):
        """Update the window title."""
        self.root.title(title)
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        if self.theme_manager.set_current_theme(theme_name):
            self.theme = self.theme_manager.get_theme()
            
            # Update theme variables on instance
            for key, value in self.theme.items():
                setattr(self, key, value)
            
            # Update UI components
            self.document_manager.update_theme(self.theme)
            self.toolbar_manager.update_theme(self.theme)
            self.statusbar_manager.update_theme(self.theme)
            
            # Update root and main frame
            self.root.configure(bg=self.bg_color)
            self.main_frame.configure(bg=self.bg_color)
            
            # Save theme setting
            self.settings_manager.update_setting("theme", theme_name)
            
            # Update status
            self.statusbar_manager.update_status(f"{theme_name.capitalize()} theme applied")
    
    # Formatting methods
    def apply_font(self, family, size):
        """Apply font to selected text."""
        self.text_formatter.apply_font(family, size)
        
    def toggle_bold(self):
        """Toggle bold formatting on selected text."""
        self.text_formatter.toggle_bold()
        
    def toggle_italic(self):
        """Toggle italic formatting on selected text."""
        self.text_formatter.toggle_italic()
        
    def toggle_underline(self):
        """Toggle underline formatting on selected text."""
        self.text_formatter.toggle_underline()
        
    def set_alignment(self, alignment):
        """Set text alignment for the paragraph."""
        self.text_formatter.set_alignment(alignment)
    
    # File operations
    def new_file(self):
        """Create a new file."""
        self.file_operations.new_file()
        self.update_statistics()
    
    def open_file(self):
        """Open a file."""
        self.file_operations.open_file()
        self.update_statistics()
    
    def save_file(self):
        """Save the current file."""
        self.file_operations.save_file()
    
    def save_file_as(self):
        """Save the current file with a new name."""
        self.file_operations.save_file_as()
    
    def print_document(self):
        """Print document functionality (placeholder)."""
        self.update_status("Print feature is not implemented in this version")
    
    def exit_app(self):
        """Exit the application."""
        if self.file_operations.has_content() and tk.messagebox.askyesno("Save?", "Do you want to save your current work?"):
            self.file_operations.save_file()
        self.root.quit()
    
    # Edit operations
    def cut(self):
        """Cut selected text."""
        if self.document_manager.text_widget.tag_ranges(tk.SEL):
            self.copy()
            self.document_manager.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.update_statistics()
    
    def copy(self):
        """Copy selected text."""
        if self.document_manager.text_widget.tag_ranges(tk.SEL):
            selected_text = self.document_manager.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
    
    def paste(self):
        """Paste text from clipboard."""
        try:
            text = self.root.clipboard_get()
            if self.document_manager.text_widget.tag_ranges(tk.SEL):
                self.document_manager.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.document_manager.text_widget.insert(tk.INSERT, text)
            self.update_statistics()
        except tk.TclError:
            pass  # Clipboard is empty
    
    def select_all(self, event=None):
        """Select all text."""
        self.document_manager.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        return "break"  # Prevent default handling
    
    # Dialog methods
    def show_find_dialog(self):
        """Show find dialog."""
        # This would be implemented with a custom dialog, using the TextSearcher
        self.update_status("Find dialog will be implemented in the dialogs package")
    
    def show_replace_dialog(self):
        """Show replace dialog."""
        # This would be implemented with a custom dialog, using the TextSearcher
        self.update_status("Replace dialog will be implemented in the dialogs package")
    
    def show_font_dialog(self):
        """Show font selection dialog."""
        # This would be implemented with a custom dialog
        self.update_status("Font dialog will be implemented in the dialogs package")
    
    def show_word_count(self):
        """Show detailed word count dialog."""
        # Get statistics
        stats = self.document_statistics.get_all_statistics()
        
        # Format and display in a dialog (placeholder)
        message = f"Words: {stats['word_count']}\n" \
                  f"Characters (with spaces): {stats['character_count']}\n" \
                  f"Characters (no spaces): {stats['character_count_no_spaces']}\n" \
                  f"Lines: {stats['line_count']}\n" \
                  f"Paragraphs: {stats['paragraph_count']}\n" \
                  f"Pages: {stats['page_count']}"
        
        tk.messagebox.showinfo("Word Count", message)
    
    def spell_check(self):
        """Basic spell check functionality (placeholder)."""
        tk.messagebox.showinfo("Spell Check", "Spell check feature is not implemented in this version.")
    
    def show_about(self):
        """Show about dialog."""
        about_text = (
            "Modern Text Editor\n\n"
            "Version 1.0.0\n\n"
            "A Microsoft Word-like text editor with A4 paper format.\n"
            "Includes speech-to-text capabilities and basic text formatting."
        )
        tk.messagebox.showinfo("About", about_text)
    
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
        self.update_status("API key saved successfully")
    
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
        self.update_status("Shortcuts saved successfully")
    
    def configure_system_audio(self):
        """Open the system audio configuration dialog."""
        dialog = SystemAudioDialog(
            self.root,
            self.system_audio_capture,
            self.settings_manager,
            save_callback=self.update_system_audio_settings
        )
        self.root.wait_window(dialog)
    
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
            keyboard.add_hotkey(shortcuts.get("transcribe", "f9"), self.start_transcription, trigger_on_release=False)
            keyboard.add_hotkey(shortcuts.get("system_audio", "f10"), self.start_system_audio_capture, trigger_on_release=False)
            keyboard.add_hotkey(shortcuts.get("cut", "ctrl+x"), self.cut)
            keyboard.add_hotkey(shortcuts.get("copy", "ctrl+c"), self.copy)
            keyboard.add_hotkey(shortcuts.get("paste", "ctrl+v"), self.paste)
            keyboard.add_hotkey(shortcuts.get("save", "ctrl+s"), self.save_file)
            keyboard.add_hotkey(shortcuts.get("open", "ctrl+o"), self.open_file)
            keyboard.add_hotkey(shortcuts.get("new", "ctrl+n"), self.new_file)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to setup shortcuts: {e}")
    
    def start_transcription(self, reset_callback=None):
        """Start recording from the microphone for transcription."""
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            tk.messagebox.showerror("Error", "Please configure your OpenAI API key first")
            self.configure_api_key()
            return
            
        # Update status
        self.update_status("Recording... (Hold the transcription key)")
        
        # Start recording
        self.audio_recorder.start_microphone_transcription()
    
    def start_system_audio_capture(self):
        """Start capturing system audio."""
        api_key = self.settings_manager.get_api_key()
        if not api_key:
            tk.messagebox.showerror("Error", "Please configure your OpenAI API key first")
            self.configure_api_key()
            return
        
        # Check if system audio is enabled in settings
        if not self.settings_manager.get_setting("system_audio", False):
            tk.messagebox.showinfo(
                "System Audio Disabled",
                "System audio capture is currently disabled.\n" +
                "Enable it in Settings > System Audio Capture."
            )
            return
        # Get the keyboard shortcut for reference
        shortcut = self.settings_manager.get_shortcuts().get("system_audio", "F10")
        # Start the capture
        self.system_audio_capture.start_capture(shortcut_key=shortcut)

            
        # Update status
        self.update_status("Recording system audio... (Release the key to stop)")
        
        # Start recording
        self.audio_recorder.start_system_audio_capture()
    
    def add_transcribed_text(self, text):
        """Add transcribed text at the current cursor position."""
        self.document_manager.text_widget.insert(tk.INSERT, text)
        self.update_statistics()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    
    # Set min window size to fit A4 page
    root.minsize(900, 700)
    
    # Create editor instance
    app = TextEditorApp(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()