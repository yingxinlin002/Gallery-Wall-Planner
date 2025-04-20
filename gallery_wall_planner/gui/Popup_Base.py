import tkinter as tk
from gallery_wall_planner.gui.AppMain import AppMain

class Popup_Base(tk.Toplevel):
    def __init__(self, AppMain : AppMain, Title : str, Width : int, Height : int, *args, **kwargs):
        super().__init__(AppMain.root, *args, **kwargs)
        self.AppMain = AppMain
        self.geometry(f"{Width}x{Height}")
        self.title(Title)
    
    def load_content(self):
        pass