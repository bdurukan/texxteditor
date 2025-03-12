"""
Search and replace functionality for the TextEditor.
"""

import tkinter as tk

class TextSearcher:
    def __init__(self, text_widget, status_callback=None):
        self.text_widget = text_widget
        self.status_callback = status_callback
        
        # Configure search highlight tag
        self.text_widget.tag_configure("search", background="yellow")
        
    def update_status(self, message):
        """Update status bar message if callback provided."""
        if self.status_callback:
            self.status_callback(message)
            
    def find_text(self, search_text, case_sensitive=False, start_pos=None):
        """
        Find text in the document.
        
        Args:
            search_text (str): Text to search for
            case_sensitive (bool): Whether to match case
            start_pos (str): Starting position for search (tkinter index)
            
        Returns:
            bool: True if found, False otherwise
        """
        # Remove existing highlights
        self.text_widget.tag_remove("search", "1.0", tk.END)
        
        if not search_text:
            return False
            
        # Start search from current cursor position if not specified
        if start_pos is None:
            start_pos = self.text_widget.index(tk.INSERT)
            
        # Configure case sensitivity
        search_kwargs = {"stopindex": tk.END}
        if case_sensitive:
            search_kwargs["exact"] = True
        else:
            search_kwargs["nocase"] = True
            
        # Search for text
        found_pos = self.text_widget.search(search_text, start_pos, **search_kwargs)
                
        if found_pos:
            # Calculate end position based on search string length
            end_pos = f"{found_pos}+{len(search_text)}c"
            
            # Select and highlight the text
            self.text_widget.tag_add("search", found_pos, end_pos)
            self.text_widget.mark_set(tk.INSERT, end_pos)
            self.text_widget.see(found_pos)
            
            # Update status
            self.update_status(f"Found: '{search_text}'")
            return True
        else:
            # Try searching from beginning if not found
            if start_pos != "1.0":
                # We've already searched from the current position to the end,
                # now search from beginning to current position
                search_kwargs["stopindex"] = start_pos
                found_pos = self.text_widget.search(search_text, "1.0", **search_kwargs)
                
                if found_pos:
                    # Calculate end position
                    end_pos = f"{found_pos}+{len(search_text)}c"
                    
                    # Select and highlight the text
                    self.text_widget.tag_add("search", found_pos, end_pos)
                    self.text_widget.mark_set(tk.INSERT, end_pos)
                    self.text_widget.see(found_pos)
                    
                    # Update status
                    self.update_status(f"Found: '{search_text}' (search wrapped)")
                    return True
                    
            # Not found anywhere
            self.update_status(f"Cannot find: '{search_text}'")
            return False
            
    def replace_current(self, replace_text):
        """
        Replace currently highlighted text.
        
        Args:
            replace_text (str): Text to replace with
            
        Returns:
            bool: True if replaced, False otherwise
        """
        try:
            # Check if we have a search selection
            start_pos = self.text_widget.index("search.first")
            end_pos = self.text_widget.index("search.last")
            
            # Replace the selected text
            self.text_widget.delete(start_pos, end_pos)
            self.text_widget.insert(start_pos, replace_text)
            self.text_widget.mark_set(tk.INSERT, f"{start_pos}+{len(replace_text)}c")
            
            # Update status
            self.update_status("Replaced")
            return True
            
        except tk.TclError:
            # No selection
            return False
            
    def replace_all(self, search_text, replace_text, case_sensitive=False):
        """
        Replace all occurrences of search_text with replace_text.
        
        Args:
            search_text (str): Text to search for
            replace_text (str): Text to replace with
            case_sensitive (bool): Whether to match case
            
        Returns:
            int: Number of replacements made
        """
        # Start from the beginning
        self.text_widget.mark_set(tk.INSERT, "1.0")
        
        count = 0
        while True:
            # Find next occurrence
            if not self.find_text(search_text, case_sensitive):
                break
                
            # Replace it
            if not self.replace_current(replace_text):
                break
                
            count += 1
            
        # Update status
        self.update_status(f"Replaced {count} occurrences")
        return count