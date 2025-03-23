# launcher.py
import os
import sys

# Get the absolute path of the script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to Python path
sys.path.insert(0, current_dir)

# Import and run the main function
if __name__ == "__main__":
    # Import main function here to avoid module not found errors
    from main import main
    main()