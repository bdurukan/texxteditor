"""
Text editor functionality for the TextEditor.
Handles basic editing operations (cut, copy, paste, select all, etc).
"""

import tkinter as tk

class TextEditor:
    def __init__(self, text_widget, root=None, update_callback=None):
        self.text_widget = text_widget
        self.root = root
        self.update_callback = update_callback
        
    def select_all(self, event=None):
        """Select all text."""
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        return "break"  # Prevent default handling
    
    def cut(self):
        """Cut selected text."""
        if self.text_widget.tag_ranges(tk.SEL):
            self.copy()
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self._notify_update()
    
    def copy(self):
        """Copy selected text."""
        if self.text_widget.tag_ranges(tk.SEL):
            selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            if self.root:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
    
    def paste(self):
        """Paste text from clipboard."""
        if not self.root:
            return
            
        try:
            text = self.root.clipboard_get()
            if self.text_widget.tag_ranges(tk.SEL):
                self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_widget.insert(tk.INSERT, text)
            self._notify_update()
        except tk.TclError:
            pass  # Clipboard is empty
            
    def add_text(self, text, position=None):
        """
        Add text at the specified position or current cursor position.
        
        Args:
            text (str): Text to add
            position (str): Position to insert text (tkinter index)
            
        Returns:
            str: New cursor position
        """
        # Get the current index if position not specified
        if position is None:
            position = self.text_widget.index(tk.INSERT)
        
        # Insert the text
        self.text_widget.insert(position, text)
        
        # Calculate new cursor position
        new_position = self.text_widget.index(f"{position}+{len(text)}c")
        
        # Notify of update
        self._notify_update()
        
        return new_position
        
    def delete_selection(self):
        """Delete selected text."""
        if self.text_widget.tag_ranges(tk.SEL):
            self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self._notify_update()
            return True
        return False
        
    def get_all_text(self):
        """Get all text from editor."""
        return self.text_widget.get("1.0", "end-1c")
        
    def set_all_text(self, text):
        """Set all text in editor."""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)
        self._notify_update()
        
    def _notify_update(self):
        """Notify callback of text update."""
        if self.update_callback:
            self.update_callback()