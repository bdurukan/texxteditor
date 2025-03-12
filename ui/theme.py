"""
Theme manager for the TextEditor.
Handles theme settings and switching between light and dark mode.
"""

class ThemeManager:
    def __init__(self):
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
        self.current_theme = "light"
        
    def get_theme(self, theme_name=None):
        """Get the specified theme or current theme if none specified."""
        if theme_name is None:
            theme_name = self.current_theme
            
        return self.themes.get(theme_name, self.themes["light"])
        
    def set_current_theme(self, theme_name):
        """Set the current theme."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
        
    def is_dark_mode(self):
        """Check if dark mode is enabled."""
        return self.current_theme == "dark"
        
    def get_theme_names(self):
        """Get a list of available theme names."""
        return list(self.themes.keys())