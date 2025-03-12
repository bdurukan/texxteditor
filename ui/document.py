"""
Document UI manager for the TextEditor.
Handles document layout, rulers, and page formatting.
"""

import tkinter as tk

class DocumentManager:
    def __init__(self, parent_frame, theme):
        self.parent_frame = parent_frame
        self.theme = theme
        
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
        
        # Initialize components
        self.editor_frame = None
        self.h_ruler_frame = None
        self.h_ruler_canvas = None
        self.document_area = None
        self.v_ruler_frame = None
        self.v_ruler_canvas = None
        self.document_frame = None
        self.v_scrollbar = None
        self.h_scrollbar = None
        self.document_canvas = None
        self.page_frame = None
        self.page_window = None
        self.text_widget = None
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the document UI components."""
        # Main editor area with document and rulers
        self.editor_frame = tk.Frame(self.parent_frame, bg=self.theme["bg_color"])
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal ruler
        self.h_ruler_frame = tk.Frame(self.editor_frame, bg=self.theme["ruler_bg"], height=20)
        self.h_ruler_frame.pack(fill=tk.X, padx=(30, 0))
        self.create_horizontal_ruler()
        
        # Document area with vertical ruler
        self.document_area = tk.Frame(self.editor_frame, bg=self.theme["bg_color"])
        self.document_area.pack(fill=tk.BOTH, expand=True)
        
        # Vertical ruler
        self.v_ruler_frame = tk.Frame(self.document_area, bg=self.theme["ruler_bg"], width=30)
        self.v_ruler_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.create_vertical_ruler()
        
        # Document frame (for scrolling)
        self.document_frame = tk.Frame(self.document_area, bg=self.theme["bg_color"])
        self.document_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        self.v_scrollbar = tk.Scrollbar(self.document_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.h_scrollbar = tk.Scrollbar(self.document_frame, orient=tk.HORIZONTAL)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create canvas for page (to enable scrolling)
        self.document_canvas = tk.Canvas(
            self.document_frame, 
            bg=self.theme["bg_color"],
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
            bg=self.theme["document_bg"],
            width=self.page_width_px,
            height=self.page_height_px,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=self.theme["page_border"],
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
            font=("Calibri", 11),
            wrap=tk.WORD,
            width=1,  # Will be sized by place manager
            height=1,  # Will be sized by place manager
            padx=0,
            pady=0,
            bd=0,
            insertwidth=2,
            selectbackground=self.theme["selection_color"],
            highlightthickness=0,
            fg=self.theme["text_color"],
            bg=self.theme["document_bg"],
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
        
    def create_horizontal_ruler(self):
        """Create the horizontal ruler."""
        self.h_ruler_canvas = tk.Canvas(
            self.h_ruler_frame, 
            bg=self.theme["ruler_bg"], 
            height=20, 
            highlightthickness=0
        )
        self.h_ruler_canvas.pack(fill=tk.X)
        
        # Draw ruler markings (assuming 96 DPI)
        for i in range(0, self.page_width_px + 100, 96):  # Every inch (96 pixels)
            # Draw major tick and label
            self.h_ruler_canvas.create_line(
                i, 18, i, 10, 
                fill=self.theme["ruler_tick"]
            )
            self.h_ruler_canvas.create_text(
                i, 5, 
                text=str(i // 96), 
                fill=self.theme["ruler_text"],
                font=("Arial", 7)
            )
            
            # Draw minor ticks (1/4 inch)
            for j in range(1, 4):
                minor_tick = i + (j * 24)  # 96/4 = 24 pixels per 1/4 inch
                self.h_ruler_canvas.create_line(
                    minor_tick, 18, minor_tick, 14, 
                    fill=self.theme["ruler_tick"]
                )
    
    def create_vertical_ruler(self):
        """Create the vertical ruler."""
        self.v_ruler_canvas = tk.Canvas(
            self.v_ruler_frame, 
            bg=self.theme["ruler_bg"], 
            width=30, 
            highlightthickness=0
        )
        self.v_ruler_canvas.pack(fill=tk.Y)
        
        # Draw ruler markings (assuming 96 DPI)
        for i in range(0, self.page_height_px + 100, 96):  # Every inch (96 pixels)
            # Draw major tick and label
            self.v_ruler_canvas.create_line(
                28, i, 20, i, 
                fill=self.theme["ruler_tick"]
            )
            self.v_ruler_canvas.create_text(
                15, i, 
                text=str(i // 96), 
                fill=self.theme["ruler_text"],
                font=("Arial", 7)
            )
            
            # Draw minor ticks (1/4 inch)
            for j in range(1, 4):
                minor_tick = i + (j * 24)  # 96/4 = 24 pixels per 1/4 inch
                self.v_ruler_canvas.create_line(
                    28, minor_tick, 24, minor_tick, 
                    fill=self.theme["ruler_tick"]
                )
                
    def update_theme(self, theme):
        """Update the theme of all document components."""
        self.theme = theme
        
        # Update frames
        self.editor_frame.configure(bg=theme["bg_color"])
        self.document_area.configure(bg=theme["bg_color"])
        self.document_frame.configure(bg=theme["bg_color"])
        
        # Update rulers
        self.h_ruler_frame.configure(bg=theme["ruler_bg"])
        self.v_ruler_frame.configure(bg=theme["ruler_bg"])
        self.h_ruler_canvas.configure(bg=theme["ruler_bg"])
        self.v_ruler_canvas.configure(bg=theme["ruler_bg"])
        
        # Update document canvas and page
        self.document_canvas.configure(bg=theme["bg_color"])
        self.page_frame.configure(
            bg=theme["document_bg"],
            highlightbackground=theme["page_border"]
        )
        
        # Update text widget
        self.text_widget.configure(
            fg=theme["text_color"],
            bg=theme["document_bg"],
            selectbackground=theme["selection_color"]
        )
        
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