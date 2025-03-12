"""
System audio configuration dialog for the TextEditor.
Allows users to configure system audio capture settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class SystemAudioDialog(tk.Toplevel):
    def __init__(self, parent, system_audio_capture, settings_manager, save_callback=None):
        super().__init__(parent)
        self.title("System Audio Configuration")
        self.geometry("550x450")
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
        self.system_audio_capture = system_audio_capture
        self.settings_manager = settings_manager
        self.save_callback = save_callback
        
        # Get current settings
        self.system_audio_enabled = self.settings_manager.get_setting("system_audio", False)
        self.continuous_mode = self.settings_manager.get_setting("continuous_transcription", False)
        self.chunk_duration = self.settings_manager.get_setting("chunk_duration", 10)
        self.selected_device_id = self.settings_manager.get_setting("audio_device_id", None)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Configure the window
        self.configure(bg=self.bg_color)
        
        # Create UI elements
        self.create_widgets()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Scan for audio devices
        self.scan_devices()
        
    def create_widgets(self):
        """Create the dialog widgets."""
        # Main frame with padding
        main_frame = tk.Frame(self, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="System Audio Capture Settings",
            font=("Helvetica", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Description
        description = tk.Label(
            main_frame,
            text=(
                "Capture system audio from sources like YouTube videos, Zoom meetings, "
                "and other media for transcription. This requires a system audio loopback device."
            ),
            wraplength=510,
            justify=tk.LEFT,
            bg=self.bg_color,
            fg=self.text_color
        )
        description.pack(anchor=tk.W, pady=(0, 15))
        
        # Device selection frame
        device_frame = tk.LabelFrame(
            main_frame,
            text="Audio Device Selection",
            bg=self.bg_color,
            fg=self.text_color,
            padx=15,
            pady=15
        )
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Device selection instructions
        device_desc = tk.Label(
            device_frame,
            text="Select the audio device that can capture system audio:",
            bg=self.bg_color,
            fg=self.text_color,
            justify=tk.LEFT
        )
        device_desc.pack(anchor=tk.W, pady=(0, 10))
        
        # Device listbox frame with scrollbar
        listbox_frame = tk.Frame(device_frame, bg=self.bg_color)
        listbox_frame.pack(fill=tk.X)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create listbox for devices
        self.device_listbox = tk.Listbox(
            listbox_frame,
            height=6,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            exportselection=0
        )
        self.device_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.device_listbox.yview)
        
        # Button frame for device operations
        device_button_frame = tk.Frame(device_frame, bg=self.bg_color)
        device_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Refresh devices button
        refresh_btn = tk.Button(
            device_button_frame,
            text="Refresh Devices",
            command=self.scan_devices,
            bg=self.button_bg,
            fg=self.button_fg,
            padx=10
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Options frame
        options_frame = tk.LabelFrame(
            main_frame,
            text="Transcription Options",
            bg=self.bg_color,
            fg=self.text_color,
            padx=15,
            pady=15
        )
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Enable system audio capture
        self.system_audio_var = tk.BooleanVar(value=self.system_audio_enabled)
        system_audio_check = tk.Checkbutton(
            options_frame,
            text="Enable system audio capture",
            variable=self.system_audio_var,
            bg=self.bg_color,
            fg=self.text_color,
            selectcolor=self.canvas_bg if hasattr(self, 'canvas_bg') else "white"
        )
        system_audio_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Continuous transcription mode
        self.continuous_var = tk.BooleanVar(value=self.continuous_mode)
        continuous_check = tk.Checkbutton(
            options_frame,
            text="Enable continuous transcription (process in chunks)",
            variable=self.continuous_var,
            bg=self.bg_color,
            fg=self.text_color,
            selectcolor=self.canvas_bg if hasattr(self, 'canvas_bg') else "white",
            command=self.toggle_continuous_options
        )
        continuous_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Chunk duration frame
        self.chunk_frame = tk.Frame(options_frame, bg=self.bg_color)
        self.chunk_frame.pack(fill=tk.X, padx=(20, 0), pady=(0, 10))
        
        tk.Label(
            self.chunk_frame,
            text="Chunk duration (seconds):",
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Chunk duration spinbox
        self.chunk_var = tk.IntVar(value=self.chunk_duration)
        chunk_spin = tk.Spinbox(
            self.chunk_frame,
            from_=5,
            to=60,
            increment=5,
            textvariable=self.chunk_var,
            width=5
        )
        chunk_spin.pack(side=tk.LEFT)
        
        # Set initial state of chunk frame based on continuous mode
        if not self.continuous_mode:
            self.chunk_frame.pack_forget()
        
        # Shortcut configuration frame
        shortcut_frame = tk.LabelFrame(
            main_frame,
            text="Keyboard Shortcut",
            bg=self.bg_color,
            fg=self.text_color,
            padx=15,
            pady=15
        )
        shortcut_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Current shortcut display
        current_shortcut = self.settings_manager.get_shortcuts().get("system_audio", "F10")
        tk.Label(
            shortcut_frame,
            text=f"Current shortcut: {current_shortcut.upper()}",
            bg=self.bg_color,
            fg=self.text_color
        ).pack(anchor=tk.W)
        
        # Info about changing shortcuts
        tk.Label(
            shortcut_frame,
            text="To change this shortcut, use the Shortcut Editor in the Settings menu.",
            bg=self.bg_color,
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            bg=self.accent_color,
            fg="white",
            padx=15,
            pady=5
        )
        save_button.pack(side=tk.RIGHT)
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            bg=self.button_bg,
            fg=self.button_fg,
            padx=15,
            pady=5
        )
        cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Test button
        test_button = tk.Button(
            button_frame,
            text="Test Capture",
            command=self.test_audio_capture,
            bg=self.button_bg,
            fg=self.button_fg,
            padx=15,
            pady=5
        )
        test_button.pack(side=tk.LEFT)
        
    def toggle_continuous_options(self):
        """Show or hide continuous mode options based on checkbox state."""
        if self.continuous_var.get():
            self.chunk_frame.pack(fill=tk.X, padx=(20, 0), pady=(0, 10))
        else:
            self.chunk_frame.pack_forget()
            
    def scan_devices(self):
        """Scan for audio devices and populate the listbox."""
        # Clear the listbox
        self.device_listbox.delete(0, tk.END)
        
        try:
            # Get device information from the system audio capture module
            device_info = self.system_audio_capture.detect_audio_sources()
            
            # First add loopback devices (most likely to work for system audio)
            for device in device_info.get('loopback_devices', []):
                self.device_listbox.insert(tk.END, f"🔄 {device['name']} ({device['channels']} ch)")
                
            # Then add other input devices
            for device in device_info.get('input_devices', []):
                # Skip devices already added as loopback
                if device not in device_info.get('loopback_devices', []):
                    prefix = "🎤" if device['default'] else "  "
                    self.device_listbox.insert(tk.END, f"{prefix} {device['name']} ({device['channels']} ch)")
                    
            # Store the device IDs for reference
            self.device_ids = []
            loopback_ids = [d['id'] for d in device_info.get('loopback_devices', [])]
            self.device_ids.extend(loopback_ids)
            
            input_ids = [d['id'] for d in device_info.get('input_devices', []) 
                         if d['id'] not in loopback_ids]
            self.device_ids.extend(input_ids)
            
            # Select the currently configured device if available
            if self.selected_device_id is not None:
                try:
                    index = self.device_ids.index(self.selected_device_id)
                    self.device_listbox.selection_set(index)
                    self.device_listbox.see(index)
                except ValueError:
                    # Device not found in list
                    pass
                    
        except Exception as e:
            self.device_listbox.insert(tk.END, f"Error scanning devices: {str(e)}")
            messagebox.showerror("Device Scan Error", f"Could not scan audio devices: {str(e)}")
            
    def test_audio_capture(self):
        """Test the selected audio device with a short capture."""
        # Get the selected device
        selection = self.device_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Device Selected", "Please select an audio device to test.")
            return
            
        device_id = self.device_ids[selection[0]]
        
        # Configure the device
        self.system_audio_capture.configure_device(device_id)
        
        # Start a short capture test
        messagebox.showinfo(
            "Test Capture", 
            "System will record 5 seconds of audio. Please play some audio on your system."
        )
        
        # Set up a placeholder for test results
        result_window = tk.Toplevel(self)
        result_window.title("Test In Progress")
        result_window.geometry("300x100")
        result_window.transient(self)
        result_window.resizable(False, False)
        
        # Center the window
        result_window.update_idletasks()
        width = result_window.winfo_width()
        height = result_window.winfo_height()
        x = (result_window.winfo_screenwidth() // 2) - (width // 2)
        y = (result_window.winfo_screenheight() // 2) - (height // 2)
        result_window.geometry(f"{width}x{height}+{x}+{y}")
        
        result_label = tk.Label(
            result_window, 
            text="Recording system audio...\nPlease wait...",
            padx=20,
            pady=20
        )
        result_label.pack(expand=True, fill=tk.BOTH)
        
        # Function to capture and process test audio
        def test_capture():
            # Create a temporary callback for this test
            test_transcript = []
            
            def test_callback(text):
                test_transcript.append(text)
                
            # Store the original callback and set our test callback
            original_callback = self.system_audio_capture.text_callback
            self.system_audio_capture.text_callback = test_callback
            
            try:
                # Start capture for 5 seconds
                self.system_audio_capture.start_capture(duration=5)
                
                # Wait for capture to complete (6 seconds to allow processing)
                self.after(6000, lambda: complete_test(test_transcript, original_callback))
                
            except Exception as e:
                messagebox.showerror("Test Error", f"Error during test: {str(e)}")
                # Restore original callback
                self.system_audio_capture.text_callback = original_callback
                result_window.destroy()
                
        def complete_test(transcript, original_callback):
            # Restore original callback
            self.system_audio_capture.text_callback = original_callback
            
            # Show results
            if transcript:
                result_text = "Success! Transcript detected:\n\n" + "".join(transcript)
                result_label.configure(text=result_text)
                result_window.title("Test Successful")
                result_window.geometry("400x200")
            else:
                result_label.configure(text="No speech detected in the audio.\nThe device may not be capturing system audio.")
                result_window.title("Test Complete")
                
            # Add a close button
            tk.Button(
                result_window,
                text="Close",
                command=result_window.destroy
            ).pack(pady=(0, 10))
            
        # Start test in a separate thread
        self.after(100, test_capture)
        
    def save_settings(self):
        """Save the system audio settings."""
        # Get the selected device
        selection = self.device_listbox.curselection()
        if selection:
            device_id = self.device_ids[selection[0]]
            self.settings_manager.update_setting("audio_device_id", device_id)
            
            # Update the system audio capture module
            self.system_audio_capture.configure_device(device_id)
        
        # Save other settings
        self.settings_manager.update_setting("system_audio", self.system_audio_var.get())
        self.settings_manager.update_setting("continuous_transcription", self.continuous_var.get())
        self.settings_manager.update_setting("chunk_duration", self.chunk_var.get())
        
        # Update continuous mode in the capture module
        if hasattr(self.system_audio_capture, 'set_continuous_mode'):
            self.system_audio_capture.set_continuous_mode(
                self.continuous_var.get(),
                self.chunk_var.get()
            )
        
        # Call the save callback if provided
        if self.save_callback:
            self.save_callback({
                "system_audio": self.system_audio_var.get(),
                "audio_device_id": device_id if selection else None,
                "continuous_transcription": self.continuous_var.get(),
                "chunk_duration": self.chunk_var.get()
            })
            
        # Close the dialog
        self.destroy()