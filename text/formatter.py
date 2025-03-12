"""
Text formatting functionality for the Word-Style TextEditor.
"""

import tkinter as tk
from tkinter import messagebox, font

class TextFormatter:
    def __init__(self, text_widget, update_status_callback=None):
        self.text_widget = text_widget
        self.update_status = update_status_callback
        
        # Configure tags for formatting
        self.configure_tags()
    
    def configure_tags(self):
        """Configure text formatting tags."""
        # Base formatting tags
        self.text_widget.tag_configure("bold", font=(None, None, "bold"))
        self.text_widget.tag_configure("italic", font=(None, None, "italic"))
        self.text_widget.tag_configure("underline", underline=True)
        
        # Alignment tags
        self.text_widget.tag_configure("left", justify=tk.LEFT)
        self.text_widget.tag_configure("center", justify=tk.CENTER)
        self.text_widget.tag_configure("right", justify=tk.RIGHT)
        
        # Search highlighting
        self.text_widget.tag_configure("search", background="yellow")
    
    def update_status_message(self, message):
        """Update status message if callback is available."""
        if self.update_status:
            self.update_status(message)
    
    def apply_font(self, family, size):
        """Apply selected font to text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.update_status_message("Please select text first")
            return False
            
        # Create new font tag
        tag_name = f"font-{family}-{size}"
        
        # Check if this tag already exists
        try:
            existing_font = self.text_widget.tag_cget(tag_name, "font")
            if not existing_font:
                self.text_widget.tag_configure(tag_name, font=(family, size))
        except tk.TclError:
            # Tag doesn't exist yet, create it
            self.text_widget.tag_configure(tag_name, font=(family, size))
        
        # Apply to selected text
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        # Remove any existing font tags
        for tag in current_tags:
            if tag.startswith("font-"):
                self.text_widget.tag_remove(tag, tk.SEL_FIRST, tk.SEL_LAST)
        
        # Add the new font tag
        self.text_widget.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
        
        self.update_status_message(f"Font applied: {family}, {size}pt")
        return True
    
    def toggle_bold(self):
        """Toggle bold formatting on selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.update_status_message("Please select text first")
            return False
            
        # Check if selection already has bold tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "bold" in current_tags:
            # Remove bold
            self.text_widget.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
            self.update_status_message("Bold removed")
        else:
            # Apply bold
            self.text_widget.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
            self.update_status_message("Bold applied")
            
        return True
    
    def toggle_italic(self):
        """Toggle italic formatting on selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.update_status_message("Please select text first")
            return False
            
        # Check if selection already has italic tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "italic" in current_tags:
            # Remove italic
            self.text_widget.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
            self.update_status_message("Italic removed")
        else:
            # Apply italic
            self.text_widget.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
            self.update_status_message("Italic applied")
            
        return True
    
    def toggle_underline(self):
        """Toggle underline formatting on selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.update_status_message("Please select text first")
            return False
            
        # Check if selection already has underline tag
        current_tags = self.text_widget.tag_names(tk.SEL_FIRST)
        
        if "underline" in current_tags:
            # Remove underline
            self.text_widget.tag_remove("underline", tk.SEL_FIRST, tk.SEL_LAST)
            self.update_status_message("Underline removed")
        else:
            # Apply underline
            self.text_widget.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
            self.update_status_message("Underline applied")
            
        return True
    
    def set_alignment(self, alignment):
        """Set text alignment for the paragraph."""
        # First remove any existing alignment tags from the selected text
        for tag in ["left", "center", "right"]:
            if self.text_widget.tag_ranges(tk.SEL):
                self.text_widget.tag_remove(tag, tk.SEL_FIRST, tk.SEL_LAST)
            else:
                # Get the current paragraph if no selection
                current_line = self.text_widget.index(tk.INSERT).split('.')[0]
                start = f"{current_line}.0"
                end = f"{current_line}.end"
                self.text_widget.tag_remove(tag, start, end)
        
        # Apply the requested alignment
        if self.text_widget.tag_ranges(tk.SEL):
            # Apply to selected text
            self.text_widget.tag_add(alignment, tk.SEL_FIRST, tk.SEL_LAST)
        else:
            # Apply to current paragraph
            current_line = self.text_widget.index(tk.INSERT).split('.')[0]
            start = f"{current_line}.0"
            end = f"{current_line}.end"
            self.text_widget.tag_add(alignment, start, end)
            
        self.update_status_message(f"{alignment.capitalize()} alignment applied")
        return True
    
    def find_text(self, search_text, case_sensitive=False, start_position=None):
        """Find text in the document."""
        # Remove existing search highlights
        self.text_widget.tag_remove("search", "1.0", tk.END)
        
        if not search_text:
            return False
            
        # Start search from the given position or current cursor
        if start_position is None:
            start_position = self.text_widget.index(tk.INSERT)
            
        # Configure search options
        search_options = {}
        if not case_sensitive:
            search_options["nocase"] = True
            
        # Perform the search
        position = self.text_widget.search(
            search_text, start_position, stopindex=tk.END, **search_options
        )
        
        if position:
            # Calculate end position
            end_position = f"{position}+{len(search_text)}c"
            
            # Highlight the found text
            self.text_widget.tag_add("search", position, end_position)
            
            # Move cursor and ensure visibility
            self.text_widget.mark_set(tk.INSERT, end_position)
            self.text_widget.see(position)
            
            self.update_status_message(f"Found: '{search_text}'")
            return position
        else:
            # Try wrapping the search from the beginning
            position = self.text_widget.search(
                search_text, "1.0", stopindex=start_position, **search_options
            )
            
            if position:
                # Calculate end position
                end_position = f"{position}+{len(search_text)}c"
                
                # Highlight the found text
                self.text_widget.tag_add("search", position, end_position)
                
                # Move cursor and ensure visibility
                self.text_widget.mark_set(tk.INSERT, end_position)
                self.text_widget.see(position)
                
                self.update_status_message(f"Found: '{search_text}' (search wrapped)")
                return position
            else:
                self.update_status_message(f"Cannot find: '{search_text}'")
                return False
    
    def replace_text(self, search_text, replace_text, case_sensitive=False):
        """Replace the currently highlighted (searched) text."""
        try:
            # Check if we have a highlighted search
            start_pos = self.text_widget.index("search.first")
            end_pos = self.text_widget.index("search.last")
            
            # Replace the selected text
            self.text_widget.delete(start_pos, end_pos)
            self.text_widget.insert(start_pos, replace_text)
            
            # Update cursor position
            self.text_widget.mark_set(tk.INSERT, f"{start_pos}+{len(replace_text)}c")
            
            # Find next occurrence
            next_pos = self.find_text(search_text, case_sensitive)
            
            # Update status
            self.update_status_message("Replaced")
            return True
            
        except tk.TclError:
            # No selection, find first
            next_pos = self.find_text(search_text, case_sensitive)
            return next_pos is not False
    
    def replace_all(self, search_text, replace_text, case_sensitive=False):
        """Replace all occurrences of the search text."""
        if not search_text:
            return 0
            
        # Start from the beginning
        self.text_widget.mark_set(tk.INSERT, "1.0")
        
        count = 0
        while True:
            # Find next occurrence
            position = self.find_text(search_text, case_sensitive)
            if not position:
                break
                
            # Replace it
            try:
                start_pos = self.text_widget.index("search.first")
                end_pos = self.text_widget.index("search.last")
                
                self.text_widget.delete(start_pos, end_pos)
                self.text_widget.insert(start_pos, replace_text)
                
                # Update cursor position
                self.text_widget.mark_set(tk.INSERT, f"{start_pos}+{len(replace_text)}c")
                
                count += 1
            except tk.TclError:
                break
                
        # Update status
        self.update_status_message(f"Replaced {count} occurrences")
        return count
    
    def get_font_metrics(self):
        """Get metrics for the current font."""
        current_index = self.text_widget.index(tk.INSERT)
        tags = self.text_widget.tag_names(current_index)
        
        # Find the font tag if it exists
        font_family = None
        font_size = None
        
        for tag in tags:
            if tag.startswith("font-"):
                parts = tag.split("-")
                if len(parts) >= 3:
                    font_family = parts[1]
                    font_size = int(parts[2])
                    break
        
        # Use default font if no specific font tag is applied
        if not font_family:
            font_family = "Calibri"
        if not font_size:
            font_size = 11
            
        # Check bold, italic, underline
        is_bold = "bold" in tags
        is_italic = "italic" in tags
        is_underline = "underline" in tags
        
        # Check alignment
        alignment = "left"  # Default
        if "center" in tags:
            alignment = "center"
        elif "right" in tags:
            alignment = "right"
            
        return {
            "family": font_family,
            "size": font_size,
            "bold": is_bold,
            "italic": is_italic,
            "underline": is_underline,
            "alignment": alignment
        }
    
    def clear_formatting(self):
        """Clear all formatting from selected text."""
        if not self.text_widget.tag_ranges(tk.SEL):
            self.update_status_message("Please select text first")
            return False
            
        # Get the selected text
        selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        
        # Remove all tags from the selection
        for tag in self.text_widget.tag_names():
            if tag != tk.SEL:  # Keep the selection itself
                self.text_widget.tag_remove(tag, tk.SEL_FIRST, tk.SEL_LAST)
                
        self.update_status_message("Formatting cleared")
        return True