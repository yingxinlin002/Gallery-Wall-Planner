import tkinter as tk
from gallery_wall_planner.gui.app_main import AppMain

class PopupBase(tk.Toplevel):
    def __init__(self, AppMain : AppMain, Title : str, Width : int, Height : int, *args, **kwargs):
        super().__init__(AppMain.root, *args, **kwargs)
        self.AppMain = AppMain
        self.geometry(f"{Width}x{Height}")
        self.title(Title)
        
        # Set window properties
        self.attributes("-topmost", True)
        self.transient(self.AppMain.root)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configure the window to be ready for content
        self.update_idletasks()
        
        # We'll set grab_set() after the window is fully loaded with content
        # This happens at the end of the load_content method in child classes

    def load_content(self):
        # This method should be overridden by child classes
        # After all content is loaded, we can safely grab focus
        self.update_idletasks()
        self.grab_set()

    def on_close(self):
        # Release grab before destroying to avoid errors
        try:
            self.grab_release()
        except tk.TclError:
            # If the window is already destroyed or grab isn't set
            pass
        self.destroy()
        self.AppMain.root.focus_set()