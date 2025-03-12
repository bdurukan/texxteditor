"""
Document statistics calculations for the Word-Style TextEditor.
"""

class DocumentStatistics:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def get_word_count(self):
        """Get the number of words in the document."""
        text = self.text_widget.get("1.0", "end-1c")
        if not text.strip():
            return 0
        return len(text.split())
    
    def get_character_count(self, include_spaces=True):
        """Get the number of characters in the document."""
        text = self.text_widget.get("1.0", "end-1c")
        if not include_spaces:
            text = text.replace(" ", "")
        return len(text)
    
    def get_line_count(self):
        """Get the number of lines in the document."""
        text = self.text_widget.get("1.0", "end-1c")
        return text.count('\n') + 1
    
    def get_paragraph_count(self):
        """Get the number of paragraphs in the document."""
        text = self.text_widget.get("1.0", "end-1c")
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        return max(1, len(paragraphs))
    
    def get_sentence_count(self):
        """Get the approximate number of sentences in the document."""
        text = self.text_widget.get("1.0", "end-1c")
        # This is a simple approximation that counts periods, exclamation points, and question marks
        sentences = [s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        return max(1, len(sentences))
    
    def estimate_page_count(self, words_per_page=500):
        """
        Estimate the number of pages in the document.
        
        Args:
            words_per_page: The average number of words per page (defaults to 500)
            
        Returns:
            int: Estimated number of pages
        """
        word_count = self.get_word_count()
        return max(1, (word_count + words_per_page - 1) // words_per_page)
    
    def get_reading_time(self, words_per_minute=200):
        """
        Calculate the estimated reading time in minutes.
        
        Args:
            words_per_minute: Average reading speed (defaults to 200 wpm)
            
        Returns:
            float: Estimated reading time in minutes
        """
        word_count = self.get_word_count()
        return word_count / words_per_minute
    
    def get_all_statistics(self):
        """Get all document statistics in a dictionary."""
        return {
            "word_count": self.get_word_count(),
            "character_count": self.get_character_count(),
            "character_count_no_spaces": self.get_character_count(include_spaces=False),
            "line_count": self.get_line_count(),
            "paragraph_count": self.get_paragraph_count(),
            "sentence_count": self.get_sentence_count(),
            "page_count": self.estimate_page_count(),
            "reading_time_minutes": self.get_reading_time()
        }
    
    def format_reading_time(self, reading_time_minutes):
        """Format reading time in a human-readable string."""
        if reading_time_minutes < 1:
            seconds = int(reading_time_minutes * 60)
            return f"{seconds} seconds"
        elif reading_time_minutes < 60:
            minutes = int(reading_time_minutes)
            seconds = int((reading_time_minutes - minutes) * 60)
            if seconds > 0:
                return f"{minutes} minutes, {seconds} seconds"
            else:
                return f"{minutes} minutes"
        else:
            hours = int(reading_time_minutes / 60)
            minutes = int(reading_time_minutes % 60)
            if minutes > 0:
                return f"{hours} hours, {minutes} minutes"
            else:
                return f"{hours} hours"