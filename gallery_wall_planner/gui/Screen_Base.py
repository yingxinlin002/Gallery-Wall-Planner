import tkinter as tk

from gallery_wall_planner.gui.app_main import AppMain

class ScreenBase(tk.Canvas):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain.frame_main, *args, **kwargs)
        self.AppMain = AppMain
        self.pack(fill="both", expand=True)

    def load_content(self):
        """This method should be overridden by child classes to load their specific content.
        It will be called when the screen is switched to this UI component.
        """
        pass