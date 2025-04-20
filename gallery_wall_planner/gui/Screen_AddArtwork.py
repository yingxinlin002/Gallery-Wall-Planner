import tkinter as tk
from gallery_wall_planner.models.wall import Wall  
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.gui.Screen_Base import Screen_Base


class Screen_AddArtworkUI(Screen_Base):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.selected_wall = AppMain.gallery.current_wall

        