"""
Text handling functionality for the TextEditor.
"""

import tkinter.font as tkFont

class TextHandler:
    def __init__(self, canvas, theme_manager):
        self.canvas = canvas
        self.theme_manager = theme_manager
        self.theme = theme_manager.get_theme()
        
        # Text block settings
        self.block_width = 300  # Default width for text blocks
        self.line_wrap = True   # Enable line wrapping by default
        
        # Text blocks storage
        self.text_blocks = []
        
        # Active block information
        self.current_text_item = None
        self.current_text = ""
        self.current_block_start_x = 20
        self.current_block_start_y = 20
        self.current_line_y = 20
        self.insertion_index = 0
        
        # Selection variables (will be managed by SelectionHandler)
        self.selection_start_index = None
        self.selection_end_index = None
        
        # Cursor position
        self.cursor_x = 20
        self.cursor_y = 20
    
    def update_theme(self, theme_name):
        """Update the theme."""
        self.theme = self.theme_manager.get_theme(theme_name)
        
        # Update text color for all text blocks
        for block in self.text_blocks:
            self.canvas.itemconfig(block['id'], fill=self.theme["text_color"])
    
    def set_block_width(self, width):
        """Set the width for text blocks."""
        self.block_width = width
        
        # Update all existing blocks if line wrap is enabled
        if self.line_wrap:
            for block in self.text_blocks:
                self.canvas.itemconfig(block['id'], width=width)
    
    def toggle_line_wrap(self, enabled):
        """Toggle line wrapping for text blocks."""
        self.line_wrap = enabled
        
        # Update all existing blocks
        for block in self.text_blocks:
            if self.line_wrap:
                self.canvas.itemconfig(block['id'], width=self.block_width)
            else:
                self.canvas.itemconfig(block['id'], width=0)
    
    def create_new_text_block(self, x, y):
        """Create a new text block at the specified position."""
        self.current_block_start_x = x
        self.current_block_start_y = y
        self.current_line_y = y
        self.current_text = ""
        self.insertion_index = 0
        self.selection_start_index = None
        self.selection_end_index = None
        
        self.current_text_item = self.canvas.create_text(
            x, y, 
            text="", 
            anchor='nw', 
            font=("Helvetica", 12), 
            fill=self.theme["text_color"],
            width=self.block_width if self.line_wrap else 0  # Set width for wrapping
        )
        self.text_blocks.append({'id': self.current_text_item, 'x': x, 'y': y, 'text': ""})
        
        # Return the cursor position to update in the main application
        return x, y
    
    def add_character(self, char):
        """Add a character at the current insertion point."""
        if self.current_text_item is None:
            # Create a new text block if none is active
            self.create_new_text_block(self.cursor_x, self.cursor_y)
            
        font_obj = tkFont.Font(font=("Helvetica", 12))
        
        # Insert character at current insertion point
        self.current_text = self.current_text[:self.insertion_index] + char + self.current_text[self.insertion_index:]
        self.insertion_index += len(char)
        
        # Update the text display with proper wrapping
        self.canvas.itemconfig(
            self.current_text_item, 
            text=self.current_text,
            width=self.block_width if self.line_wrap else 0
        )
        
        # Update cursor position based on wrapped text
        wrapped_lines = self.wrap_text_to_width(self.current_text[:self.insertion_index], self.block_width, font_obj)
        line_number = len(wrapped_lines) - 1
        last_line = wrapped_lines[-1]
        
        # Position cursor at the end of the wrapped line
        new_x = self.current_block_start_x + font_obj.measure(last_line)
        new_y = self.current_block_start_y + line_number * font_obj.metrics("linespace")
        self.current_line_y = new_y
        
        # Update the block text in storage
        for block in self.text_blocks:
            if block['id'] == self.current_text_item:
                block['text'] = self.current_text
                break
                
        # Return the new cursor position
        return new_x, new_y
    
    def add_text(self, text):
        """Add a string of text at the current insertion point."""
        new_x, new_y = self.cursor_x, self.cursor_y
        for char in text:
            new_x, new_y = self.add_character(char)
        return new_x, new_y
    
    def handle_backspace(self):
        """Handle backspace key press."""
        # If there's a selection, the selection handler will handle it
        if self.selection_start_index is not None and self.selection_end_index is not None:
            return None, None
            
        if self.insertion_index <= 0 or self.current_text_item is None:
            return None, None
            
        font_obj = tkFont.Font(font=("Helvetica", 12))
        
        # Remove the character before cursor
        self.current_text = self.current_text[:self.insertion_index - 1] + self.current_text[self.insertion_index:]
        self.insertion_index -= 1
        
        # Update text with wrapping
        self.canvas.itemconfig(
            self.current_text_item, 
            text=self.current_text,
            width=self.block_width if self.line_wrap else 0
        )
        
        # Update cursor position based on wrapped text
        wrapped_text = self.current_text[:self.insertion_index]
        wrapped_lines = self.wrap_text_to_width(wrapped_text, self.block_width, font_obj)
        line_number = len(wrapped_lines) - 1
        last_line = wrapped_lines[-1] if wrapped_lines else ""
        
        # Position cursor
        new_x = self.current_block_start_x + font_obj.measure(last_line)
        new_y = self.current_block_start_y + line_number * font_obj.metrics("linespace")
        self.current_line_y = new_y
        
        # Update block in storage
        for block in self.text_blocks:
            if block['id'] == self.current_text_item:
                block['text'] = self.current_text
                break
                
        # Return the new cursor position
        return new_x, new_y
    
    def delete_selection(self, start_idx, end_idx):
        """Delete the selected text."""
        if start_idx is None or end_idx is None or self.current_text_item is None:
            return None, None
            
        start = min(start_idx, end_idx)
        end = max(start_idx, end_idx)
        self.current_text = self.current_text[:start] + self.current_text[end:]
        self.insertion_index = start
        
        self.canvas.itemconfig(self.current_text_item, text=self.current_text)
        for block in self.text_blocks:
            if block['id'] == self.current_text_item:
                block['text'] = self.current_text
                break
                
        # Update cursor position
        return self.update_cursor_after_text_change()
    
    def update_cursor_after_text_change(self):
        """Update cursor position after text has changed."""
        font_obj = tkFont.Font(font=("Helvetica", 12))
        lines = self.current_text[:self.insertion_index].split("\n")
        line_number = len(lines) - 1
        last_line = lines[-1] if lines else ""
        new_x = self.current_block_start_x + font_obj.measure(last_line)
        new_y = self.current_block_start_y + line_number * font_obj.metrics("linespace")
        self.current_line_y = new_y
        return new_x, new_y
    
    def move_cursor(self, direction, shift_pressed=False):
        """Move cursor in the specified direction with selection support."""
        if self.current_text_item is None:
            return None, None, None, None
            
        font_obj = tkFont.Font(font=("Helvetica", 12))
        wrapped_lines = self.wrap_text_to_width(self.current_text, self.block_width, font_obj)
        
        # Find current cursor position in wrapped text
        current_pos = self.find_wrapped_position(wrapped_lines, self.insertion_index)
        line_num, char_pos = current_pos
        
        # Start selection if shift is pressed
        selection_start = self.selection_start_index
        selection_end = self.selection_end_index
        
        if shift_pressed and selection_start is None:
            selection_start = self.insertion_index
            
        # Move the cursor based on direction
        if direction == "Left":
            if self.insertion_index > 0:
                self.insertion_index -= 1
        elif direction == "Right":
            if self.insertion_index < len(self.current_text):
                self.insertion_index += 1
        elif direction == "Up":
            if line_num > 0:
                # Move to same horizontal position in previous line
                prev_line = wrapped_lines[line_num - 1]
                char_pos = min(char_pos, len(prev_line))
                self.insertion_index = self.find_actual_index(wrapped_lines, line_num - 1, char_pos)
        elif direction == "Down":
            if line_num < len(wrapped_lines) - 1:
                # Move to same horizontal position in next line
                next_line = wrapped_lines[line_num + 1]
                char_pos = min(char_pos, len(next_line))
                self.insertion_index = self.find_actual_index(wrapped_lines, line_num + 1, char_pos)
        
        # Update selection if shift is pressed
        if shift_pressed:
            selection_end = self.insertion_index
        elif selection_start is not None:
            # Clear selection if shift is not pressed
            selection_start = None
            selection_end = None
            
        # Update cursor position
        new_x, new_y = self.update_cursor_after_text_change()
        
        return new_x, new_y, selection_start, selection_end
    
    def wrap_text_to_width(self, text, width, font_obj):
        """Wrap text to fit within specified width."""
        if not text:
            return [""]
            
        wrapped_lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                wrapped_lines.append("")
                continue
                
            words = paragraph.split(' ')
            current_line = words[0]
            
            for word in words[1:]:
                test_line = current_line + ' ' + word
                if font_obj.measure(test_line) <= width:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word
                    
            wrapped_lines.append(current_line)
            
        return wrapped_lines
    
    def find_wrapped_position(self, wrapped_lines, global_index):
        """Find (line, char) position in wrapped text from global index."""
        current_idx = 0
        for line_num, line in enumerate(wrapped_lines):
            line_end_idx = current_idx + len(line)
            if global_index <= line_end_idx:
                return (line_num, global_index - current_idx)
            # Move to next line, +1 for newline if not the last line
            if line_num < len(wrapped_lines) - 1:
                current_idx = line_end_idx + 1
            else:
                current_idx = line_end_idx
        # If we're at the end of text
        return (len(wrapped_lines) - 1, len(wrapped_lines[-1]) if wrapped_lines else 0)
    
    def find_actual_index(self, wrapped_lines, line_index, char_index):
        """Convert wrapped text position to position in original text."""
        # Count characters up to the requested line
        char_count = 0
        for i in range(line_index):
            char_count += len(wrapped_lines[i])
            # Account for space or newline that might have been at the end
            if i < line_index - 1:
                char_count += 1
                
        # Add the character index within the line
        char_count += char_index
        return char_count
    
    def get_clicked_block_and_position(self, canvas_x, canvas_y):
        """
        Get the block and cursor position when clicked.
        
        Args:
            canvas_x: X coordinate of click
            canvas_y: Y coordinate of click
            
        Returns:
            tuple: (block, insertion_index, cursor_x, cursor_y)
        """
        font_obj = tkFont.Font(font=("Helvetica", 12))
        clicked_block = None
        
        # Calculate actual areas of existing blocks
        for block in self.text_blocks:
            # Skip empty blocks for selection
            if not block['text'].strip():
                continue
                
            lines = self.wrap_text_to_width(block['text'], self.block_width, font_obj)
            line_height = font_obj.metrics("linespace")
            max_width = min(max((font_obj.measure(line) for line in lines), default=0), self.block_width)
            total_height = len(lines) * line_height
            
            if block['x'] <= canvas_x <= block['x'] + max_width and block['y'] <= canvas_y <= block['y'] + total_height:
                clicked_block = block
                break
        
        # If no block was clicked, return None
        if not clicked_block:
            return None, 0, canvas_x, canvas_y
                
        # Handle text editing within a block
        x0 = clicked_block['x']
        y0 = clicked_block['y']
        
        # Process wrapped text for proper cursor positioning
        wrapped_lines = self.wrap_text_to_width(clicked_block['text'], self.block_width, font_obj)
        line_height = font_obj.metrics("linespace")
        
        # Find which line was clicked
        line_index = int((canvas_y - y0) // line_height)
        if line_index >= len(wrapped_lines):
            line_index = len(wrapped_lines) - 1
            
        # Find character position in the wrapped text
        relative_x = canvas_x - x0
        current_line = wrapped_lines[line_index]
        char_index_in_line = 0
        
        for i in range(len(current_line) + 1):
            if font_obj.measure(current_line[:i]) > relative_x:
                char_index_in_line = i - 1
                break
            else:
                char_index_in_line = i
                
        # Convert wrapped line position to actual text index
        if line_index == 0:
            insertion_index = char_index_in_line
        else:
            # Calculate the actual character position in the original text
            insertion_index = self.find_actual_index(wrapped_lines, line_index, char_index_in_line)
            
        # Calculate cursor position
        cursor_x = x0 + font_obj.measure(current_line[:char_index_in_line])
        cursor_y = y0 + line_index * line_height
        
        return clicked_block, insertion_index, cursor_x, cursor_y
    
    def delete_blocks(self, block_ids):
        """Delete blocks by their IDs."""
        for block_id in block_ids:
            # Remove block from canvas
            self.canvas.delete(block_id)
            
            # Remove block from data
            self.text_blocks = [b for b in self.text_blocks if b['id'] != block_id]
            
        # Reset current item if it was deleted
        if self.current_text_item in block_ids:
            self.current_text_item = None
            self.current_text = ""
            
    def get_all_blocks(self):
        """Get all text blocks."""
        return self.text_blocks
    
    def update_block_position(self, block_id, new_x, new_y):
        """Update the position of a text block."""
        for block in self.text_blocks:
            if block['id'] == block_id:
                # Update coordinates in data
                block['x'] = new_x
                block['y'] = new_y
                
                # Update canvas position
                self.canvas.coords(block_id, new_x, new_y)
                break