import tkinter as tk
from tkinter import messagebox, filedialog
from gallery_wall_planner.gui.app_main import AppMain

class PopupBase(tk.Toplevel):
    def __init__(self, app_main : AppMain, Title : str, Width : int, Height : int, *args, **kwargs):
        super().__init__(app_main.root, *args, **kwargs)
        self.app_main: AppMain = app_main
        self.geometry(f"{Width}x{Height}")
        self.title(Title)
        
        # Set window properties
        self.attributes("-topmost", True)
        self.transient(self.app_main.root)
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
        self.app_main.root.focus_set()

    def set_to_top(self):
        self.attributes("-topmost", True)
        self.grab_set()

    def release_top(self):
        self.attributes("-topmost", False)
        self.grab_release()
        
    def messagebox_showinfo(self, title : str, message : str):
        self.release_top()
        messagebox.showinfo(title, message)
        self.set_to_top()

    def messagebox_showerror(self, title : str, message : str):
        self.release_top()
        messagebox.showerror(title, message)
        self.set_to_top()

    def messagebox_askyesno(self, title : str, message : str) -> bool:
        self.release_top()
        result = messagebox.askyesno(title, message)
        self.set_to_top()
        return result

    def messagebox_askokcancel(self, title : str, message : str) -> bool:
        self.release_top()
        result = messagebox.askokcancel(title, message)
        self.set_to_top()
        return result

    def filedialog_askopenfilename(self, *args, **kwargs) -> str:
        self.release_top()
        result = filedialog.askopenfilename(*args, **kwargs)
        self.set_to_top()
        return result