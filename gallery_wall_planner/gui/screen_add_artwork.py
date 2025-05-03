import tkinter as tk
from gallery_wall_planner.models.wall import Wall  
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.screen_base import ScreenBase


class ScreenAddArtworkUI(ScreenBase):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.selected_wall = AppMain.gallery.current_wall

        