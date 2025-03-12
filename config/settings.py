"""
Settings management module for the TextEditor.
Handles loading, saving, and default settings.
"""

import os
import json
from tkinter import messagebox

class SettingsManager:
    def __init__(self):
        # Setup config directory
        self.config_dir = os.path.join(os.path.expanduser("~"), ".texxteditor")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.settings = self.load_settings()

    def load_settings(self):
        """Load settings from config file or return defaults if file doesn't exist."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_settings()
        else:
            return self.get_default_settings()

    def save_settings(self):
        """Save current settings to config file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False

    def get_default_settings(self):
        """Return default settings."""
        return {
            "api_key": "",
            "shortcuts": {
                "transcribe": "f9",
                "system_audio": "f10",
                "cut": "ctrl+x",
                "copy": "ctrl+c",
                "paste": "ctrl+v",
                "save": "ctrl+s",
                "open": "ctrl+o",
                "new": "ctrl+n"
            },
            "system_audio": False,
            "theme": "light"
        }

    def update_setting(self, key, value):
        """Update a specific setting."""
        self.settings[key] = value
        return self.save_settings()

    def get_setting(self, key, default=None):
        """Get a specific setting with an optional default value."""
        return self.settings.get(key, default)

    def update_shortcut(self, action, key_combo):
        """Update a specific keyboard shortcut."""
        if "shortcuts" not in self.settings:
            self.settings["shortcuts"] = {}
        self.settings["shortcuts"][action] = key_combo
        return self.save_settings()

    def get_shortcuts(self):
        """Get all keyboard shortcuts."""
        return self.settings.get("shortcuts", {})

    def get_api_key(self):
        """Get the API key."""
        return self.settings.get("api_key", "")

    def set_api_key(self, api_key):
        """Set the API key."""
        self.settings["api_key"] = api_key
        return self.save_settings()