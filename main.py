#!/usr/bin/env python3
"""
TextEditor - A Microsoft Word-like text editor with A4 paper format
Main entry point for the application
"""

import tkinter as tk
import sys

# Check for required packages
try:
    import requests
    import keyboard
    import sounddevice
    import pyaudio
    import numpy as np
    import pydub
except ImportError:
    print("Please install the required packages with:")
    print("pip install requests keyboard pyaudio pydub sounddevice numpy")
    sys.exit(1)

# Import our main editor class
from editor import ModernTextEditor

def main():
    root = tk.Tk()
    
    # Set window icon (placeholder)
    # root.iconbitmap('path/to/icon.ico')  # Uncomment and add icon if available
    
    # Set min window size to fit A4 page
    root.minsize(900, 700)
    
    # Create editor instance
    app = ModernTextEditor(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()