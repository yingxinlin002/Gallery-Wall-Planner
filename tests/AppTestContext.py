import tkinter as tk
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gallery_wall_planner.gui.AppMain import AppMain
from gallery_wall_planner.models.gallery import Gallery


class AppTestContext:
    """Context manager for setting up and tearing down an AppMain instance for tests"""
    
    def __init__(self):
        self.root = None
        self.app = None
    
    def __enter__(self):
        """Set up the Tkinter root and AppMain instance for the test context"""
        self.root = tk.Tk()
        self.root.geometry("1x1+0+0")
        self.app = AppMain(self.root)
        self.root.update_idletasks()
        self.root.update()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Teardown: Destroy the root window
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass  # Ignore errors if window is already gone
    
    def update(self):
        """Process Tkinter events"""
        self.root.update_idletasks()
        self.root.update()
    
    def find_button(self, parent_widget, button_text):
        """Find a button with the given text in the parent widget"""
        for widget in parent_widget.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == button_text:
                return widget
        return None
