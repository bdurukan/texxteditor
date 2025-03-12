"""
File operations for the Word-Style TextEditor.
Handles file save, open, and new document operations.
"""

import os
import json
from tkinter import filedialog, messagebox

class FileOperations:
    def __init__(self, text_widget, update_title_callback=None, update_status_callback=None):
        self.text_widget = text_widget
        self.current_file = None
        self.update_title = update_title_callback
        self.update_status = update_status_callback
        
    def new_file(self, confirm_save=True):
        """Create a new empty file."""
        if confirm_save and self.has_content() and messagebox.askyesno("Save?", "Do you want to save your current work?"):
            self.save_file()
            
        self.text_widget.delete("1.0", "end")
        self.current_file = None
        
        if self.update_title:
            self.update_title("Modern Text Editor - Word Style")
            
        if self.update_status:
            self.update_status("New file created")
            
        return True
    
    def open_file(self):
        """Open a file."""
        if self.has_content() and messagebox.askyesno("Save?", "Do you want to save your current work?"):
            self.save_file()
        
        file_path = filedialog.askopenfilename(
            defaultextension=".txt", 
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Clear current content and insert new content
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", content)
            
            # Update current file
            self.current_file = file_path
            
            # Update UI
            if self.update_title:
                self.update_title(f"Modern Text Editor - {os.path.basename(file_path)}")
                
            if self.update_status:
                self.update_status(f"Opened: {file_path}")
                
            return True
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            return False
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            return self.save_file_as()
            
        try:
            content = self.text_widget.get("1.0", "end-1c")
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
                
            if self.update_status:
                self.update_status(f"Saved: {self.current_file}")
                
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
        
        if self.update_title:
            self.update_title(f"Modern Text Editor - {os.path.basename(file_path)}")
            
        return self.save_file()
    
    def has_content(self):
        """Check if the document has any content."""
        return len(self.text_widget.get("1.0", "end-1c").strip()) > 0
    
    def get_current_file(self):
        """Get the current file path."""
        return self.current_file
        
    def export_as_html(self):
        """Export the document as HTML."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html", 
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return False
            
        try:
            # Get text content
            content = self.text_widget.get("1.0", "end-1c")
            
            # Apply simple HTML conversion
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(file_path)}</title>
    <style>
        body {{
            font-family: Calibri, Arial, sans-serif;
            line-height: 1.5;
            margin: 1in;
            max-width: 8.27in;
        }}
    </style>
</head>
<body>
    {content.replace('\n', '<br>\n')}
</body>
</html>"""
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
                
            if self.update_status:
                self.update_status(f"Exported as HTML: {file_path}")
                
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not export as HTML: {e}")
            return False