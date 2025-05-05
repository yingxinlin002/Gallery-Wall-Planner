import tkinter as tk
from gallery_wall_planner.gui.app_main import AppMain

class PopupBase(tk.Toplevel):
    def __init__(self, AppMain : AppMain, Title : str, Width : int, Height : int, *args, **kwargs):
        super().__init__(AppMain.root, *args, **kwargs)
        self.AppMain = AppMain
        self.geometry(f"{Width}x{Height}")
        self.title(Title)

        self.attributes("-topmost", True)

        self.transient(AppMain.root)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_content(self):
        pass

    def on_close(self):
        self.grab_release()
        self.destroy()
        self.AppMain.root.focus_set()