import tkinter as tk
from typing import override
from gallery.gui.btn_base import BTNBase
from gallery.models.wall import Wall
from gallery.gui.app_main import AppMain
from tkinter import messagebox

class BTNWall(BTNBase):
    def __init__(self, parent_frame : tk.Frame, wall : Wall, app_main : AppMain, parent_ui : 'ScreenSelectWallSpaceUI', *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.app_main: AppMain = app_main
        self.wall: Wall = wall
        self.item_text: str = self.wall.name
        self.edit_button_text: str = "Edit"
        from gallery.gui.screen_select_wall_space_ui import ScreenSelectWallSpaceUI
        self.parent_ui: ScreenSelectWallSpaceUI = parent_ui
        

    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.wall.name}")
        self.app_main.gallery.current_wall = self.wall
        self.parent_ui.update_wall_preview()
        

    @override
    def on_edit_clicked(self):
        from gallery.gui.popup_edit_wall import PopupEditWall
        print(f"Edit clicked on {self.wall.name}")
        popup = PopupEditWall(self.app_main, self)
        popup.load_content()


    def update_wall(self, wall : Wall):
        if self.app_main.gallery.update_wall(self.wall.id, wall):
            self.wall = wall
            self.label.configure(text=self.wall.name)
            self.parent_ui.update_wall_preview()
        else:
            messagebox.showerror("Error", "Failed to update wall")

    def delete_wall(self):
        self.app_main.gallery.remove_wall(self.wall)
        self.parent_ui.remove_wall_btn(self.wall.id)
        self.parent_ui.update_wall_preview()
