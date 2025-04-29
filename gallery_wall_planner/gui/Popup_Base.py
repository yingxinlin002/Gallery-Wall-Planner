import tkinter as tk
from gallery_wall_planner.gui.app_main import AppMain

class PopupBase(tk.Toplevel):
    def __init__(self, AppMain : AppMain, Title : str, Width : int, Height : int, *args, **kwargs):
        super().__init__(AppMain.root, *args, **kwargs)
        self.AppMain = AppMain
        self.geometry(f"{Width}x{Height}")
        self.title(Title)
    
    def load_content(self):
        pass