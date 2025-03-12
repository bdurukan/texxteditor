"""
Selection handling for the TextEditor.
"""

import tkinter.font as tkFont

class SelectionHandler:
    def __init__(self, canvas, text_handler, theme_manager):
        self.canvas = canvas
        self.text_handler = text_handler
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme()
        
        # Text selection variables
        self.selection_start_index = None
        self.selection_end_index = None
        self.selection_rect = None
        
        # Multiple selection tracking
        self.selected_blocks = []
        self.selection_outlines = {}
        self.window_selection_rect = None
        self.is_window_selecting = False
        self.is_moving_blocks = False
        
        # Drag tracking
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.move_start_x = 0
        self.move_start_y = 0
        
    def update_theme(self, theme_name):
        """Update the theme."""
        self.theme = self.theme_manager.get_theme(theme_name)
        
        # Update selection outlines
        for block_id, outline_id in self.selection_outlines.items():
            self.canvas.itemconfig(outline_id, outline=self.theme["selected_block_outline"])
            
        # Update selection rectangles
        if self.selection_rect:
            if isinstance(self.selection_rect, list):
                for rect in self.selection_rect:
                    self.canvas.itemconfig(rect, fill=self.theme["selection_color"])
            else:
                self.canvas.itemconfig(self.selection_rect, fill=self.theme["selection_color"])
                
        # Update window selection
        if self.window_selection_rect:
            self.canvas.itemconfig(
                self.window_selection_rect, 
                outline=self.theme["accent_color"], 
                fill=self.theme["selection_color"]
            )
    
    def clear_selection(self):
        """Clear text selection."""
        self.selection_start_index = None
        self.selection_end_index = None
        if self.selection_rect:
            if isinstance(self.selection_rect, list):
                for rect in self.selection_rect:
                    self.canvas.delete(rect)
            else:
                self.canvas.delete(self.selection_rect)
            self.selection_rect = None
    
    def draw_selection(self, current_text_item, current_text, block_start_x, block_start_y):
        """Draw text selection highlighting with support for wrapped text."""
        # Clear any existing selection highlight
        if self.selection_rect:
            if isinstance(self.selection_rect, list):
                for rect in self.selection_rect:
                    self.canvas.delete(rect)
            else:
                self.canvas.delete(self.selection_rect)
            self.selection_rect = None
            
        if self.selection_start_index is None or self.selection_end_index is None:
            return
            
        # Ensure correct order of selection indices
        start_idx = min(self.selection_start_index, self.selection_end_index)
        end_idx = max(self.selection_start_index, self.selection_end_index)
        
        # No selection if they're equal
        if start_idx == end_idx:
            return
            
        font_obj = tkFont.Font(font=("Helvetica", 12))
        block_width = self.text_handler.block_width
        
        # Get wrapped lines for proper highlighting
        wrapped_lines = self.text_handler.wrap_text_to_width(current_text, block_width, font_obj)
        line_height = font_obj.metrics("linespace")
        
        # Find which wrapped lines contain our selection
        selection_rects = []
        current_idx = 0
        
        for line_num, line in enumerate(wrapped_lines):
            line_start_idx = current_idx
            line_end_idx = current_idx + len(line)
            
            # Check if this line contains any selected text
            if start_idx < line_end_idx and end_idx > line_start_idx:
                # Calculate selection start and end within this line
                sel_start_in_line = max(0, start_idx - line_start_idx)
                sel_end_in_line = min(len(line), end_idx - line_start_idx)
                
                # Calculate positions
                x0 = block_start_x + font_obj.measure(line[:sel_start_in_line])
                x1 = block_start_x + font_obj.measure(line[:sel_end_in_line])
                y0 = block_start_y + line_num * line_height
                y1 = y0 + line_height
                
                # Create highlight rectangle
                rect = self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=self.theme["selection_color"],
                    outline=""
                )
                selection_rects.append(rect)
                self.canvas.tag_lower(rect, current_text_item)
                
            # Move to next line, +1 for newline if not the last line
            if line_num < len(wrapped_lines) - 1:
                current_idx = line_end_idx + 1
            else:
                current_idx = line_end_idx
                
        self.selection_rect = selection_rects
        
    def clear_all_selections(self):
        """Clear all text and block selections."""
        # Clear text selection
        self.clear_selection()
        
        # Clear block selections
        for outline_id in self.selection_outlines.values():
            self.canvas.delete(outline_id)
            
        self.selected_blocks = []
        self.selection_outlines = {}
        
    def add_block_to_selection(self, block):
        """Add a block to the multi-selection."""
        if block['id'] not in self.selected_blocks:
            self.selected_blocks.append(block['id'])
            
            # Create highlight rectangle around block
            font_obj = tkFont.Font(font=("Helvetica", 12))
            lines = self.text_handler.wrap_text_to_width(block['text'], self.text_handler.block_width, font_obj)
            line_height = font_obj.metrics("linespace")
            max_width = min(max((font_obj.measure(line) for line in lines), default=0), self.text_handler.block_width)
            total_height = len(lines) * line_height
            
            outline = self.canvas.create_rectangle(
                block['x'] - 2, 
                block['y'] - 2, 
                block['x'] + max_width + 4, 
                block['y'] + total_height + 2,
                outline=self.theme["selected_block_outline"],
                width=2,
                dash=(2, 2)
            )
            self.selection_outlines[block['id']] = outline
            
            # Ensure the outline is behind the text
            self.canvas.tag_lower(outline, block['id'])
            
    def start_window_selection(self, x, y):
        """Start a window selection at the given coordinates."""
        self.is_window_selecting = True
        self.drag_start_x = x
        self.drag_start_y = y
        self.window_selection_rect = self.canvas.create_rectangle(
            x, y, x, y,
            outline=self.theme["accent_color"],
            fill=self.theme["selection_color"],
            stipple="gray25"
        )
        
    def update_window_selection(self, x, y):
        """Update the window selection rectangle."""
        if self.is_window_selecting and self.window_selection_rect:
            self.canvas.coords(
                self.window_selection_rect,
                self.drag_start_x, self.drag_start_y, x, y
            )
            
    def end_window_selection(self):
        """End the window selection and select blocks inside the rectangle."""
        if not self.is_window_selecting:
            return
            
        self.is_window_selecting = False
        
        if self.window_selection_rect:
            # Get the selection rectangle coordinates
            x1, y1, x2, y2 = self.canvas.coords(self.window_selection_rect)
            
            # Normalize coordinates (ensure x1,y1 is top-left and x2,y2 is bottom-right)
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            
            # Find all blocks within the selection rectangle
            for block in self.text_handler.get_all_blocks():
                # Skip empty blocks for selection
                if not block['text'].strip():
                    continue
                    
                font_obj = tkFont.Font(font=("Helvetica", 12))
                lines = self.text_handler.wrap_text_to_width(block['text'], self.text_handler.block_width, font_obj)
                line_height = font_obj.metrics("linespace")
                max_width = min(max((font_obj.measure(line) for line in lines), default=0), self.text_handler.block_width)
                total_height = len(lines) * line_height
                
                # Check if block is inside selection rectangle
                if (x1 <= block['x'] <= x2 or x1 <= block['x'] + max_width <= x2 or
                   (block['x'] <= x1 and block['x'] + max_width >= x2)) and \
                   (y1 <= block['y'] <= y2 or y1 <= block['y'] + total_height <= y2 or
                   (block['y'] <= y1 and block['y'] + total_height >= y2)):
                    self.add_block_to_selection(block)
            
            # Delete the selection rectangle
            self.canvas.delete(self.window_selection_rect)
            self.window_selection_rect = None
            
    def start_block_movement(self, x, y):
        """Start moving selected blocks."""
        self.is_moving_blocks = True
        self.move_start_x = x
        self.move_start_y = y
        
    def update_block_movement(self, x, y):
        """Update the position of selected blocks during movement."""
        if self.is_moving_blocks and self.selected_blocks:
            dx = x - self.move_start_x
            dy = y - self.move_start_y
            
            # Move all selected blocks
            for block_id in self.selected_blocks:
                # Update the text block position
                for block in self.text_handler.get_all_blocks():
                    if block['id'] == block_id:
                        new_x = block['x'] + dx
                        new_y = block['y'] + dy
                        
                        # Move the text item
                        self.canvas.coords(block_id, new_x, new_y)
                        
                        # Update the block data
                        block['x'] = new_x
                        block['y'] = new_y
                        
                        # Update the selection outline
                        if block_id in self.selection_outlines:
                            font_obj = tkFont.Font(font=("Helvetica", 12))
                            lines = self.text_handler.wrap_text_to_width(block['text'], self.text_handler.block_width, font_obj)
                            line_height = font_obj.metrics("linespace")
                            max_width = min(max((font_obj.measure(line) for line in lines), default=0), self.text_handler.block_width)
                            total_height = len(lines) * line_height
                            
                            self.canvas.coords(
                                self.selection_outlines[block_id],
                                new_x - 2, 
                                new_y - 2, 
                                new_x + max_width + 4, 
                                new_y + total_height + 2
                            )
            
            # Update the move start position
            self.move_start_x = x
            self.move_start_y = y
            
    def end_block_movement(self, ctrl_pressed=False):
        """End moving selected blocks."""
        self.is_moving_blocks = False
        # If not control, we would typically clear other selections
        if not ctrl_pressed:
            selected_blocks = self.selected_blocks.copy()
            self.clear_all_selections()
            for block_id in selected_blocks:
                for block in self.text_handler.get_all_blocks():
                    if block['id'] == block_id:
                        self.add_block_to_selection(block)
                        break
                        
    def select_all_blocks(self):
        """Select all text blocks."""
        self.clear_all_selections()
        for block in self.text_handler.get_all_blocks():
            self.add_block_to_selection(block)
            
    def get_selected_blocks(self):
        """Get the list of selected block IDs."""
        return self.selected_blocks