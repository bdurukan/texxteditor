"""
Canvas management for the TextEditor.
This version manages A4 paper display and scrolling.
"""

import tkinter as tk

class CanvasManager:
    def __init__(self, document_canvas, page_frame, theme_manager, page_dimensions):
        self.document_canvas = document_canvas
        self.page_frame = page_frame
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme()
        
        # Store A4 dimensions
        self.page_width = page_dimensions["width"]
        self.page_height = page_dimensions["height"]
        
        # Initialize window ID (from canvas.create_window)
        self.page_window_id = None
        
        # Add the page to the canvas with some padding
        self.page_window_id = self.document_canvas.create_window(
            50, 50,  # Position with some padding
            window=self.page_frame,
            anchor='nw'
        )
        
        # Configure the canvas scroll region
        self.document_canvas.config(scrollregion=(0, 0, self.page_width + 100, self.page_height + 100))
    
    def update_theme(self, theme_name):
        """Update the theme."""
        self.theme = self.theme_manager.get_theme(theme_name)
        
        # Update document canvas
        self.document_canvas.configure(bg=self.theme["bg_color"])
        
        # Update page frame
        self.page_frame.configure(
            bg=self.theme["document_bg"],
            highlightbackground=self.theme["page_border"]
        )
    
    def center_page(self, canvas_width):
        """Center the page horizontally in the canvas."""
        if canvas_width > self.page_width + 100:
            x = (canvas_width - self.page_width) / 2
            self.document_canvas.coords(self.page_window_id, x, 50)
            
    def update_scroll_region(self):
        """Update the scroll region to encompass all content."""
        self.document_canvas.config(scrollregion=self.document_canvas.bbox("all"))
        
    def scroll_to_position(self, x, y):
        """Scroll the canvas to make the specified position visible."""
        canvas_width = self.document_canvas.winfo_width()
        canvas_height = self.document_canvas.winfo_height()
        
        # Get the current visible area
        x_view_min = self.document_canvas.canvasx(0)
        y_view_min = self.document_canvas.canvasy(0)
        x_view_max = x_view_min + canvas_width
        y_view_max = y_view_min + canvas_height
        
        # Determine if we need to scroll
        scroll_x = None
        scroll_y = None
        
        if x < x_view_min or x > x_view_max:
            # Scroll horizontally to center the x coordinate
            scroll_x = (x - canvas_width/2) / (self.page_width + 100)
            
        if y < y_view_min or y > y_view_max:
            # Scroll vertically to center the y coordinate
            scroll_y = (y - canvas_height/2) / (self.page_height + 100)
            
        # Apply scrolling
        if scroll_x is not None:
            self.document_canvas.xview_moveto(max(0, min(1, scroll_x)))
            
        if scroll_y is not None:
            self.document_canvas.yview_moveto(max(0, min(1, scroll_y)))
            
    def get_canvas_dimensions(self):
        """Get the current canvas dimensions."""
        return {
            "width": self.document_canvas.winfo_width(),
            "height": self.document_canvas.winfo_height()
        }