import tkinter as tk

from gallery_wall_planner.gui.btn_base import BTNBase
from gallery_wall_planner.models.wall import Wall


class BTNWall(BTNBase):
    def __init__(self, parent_frame : tk.Frame, wall : Wall, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.wall: Wall = wall
        self.item_text: str = self.wall.name
        self.edit_button_text: str = "Edit"
        

    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.wall.name}")
        self.AppMain.set_current_screen(ScreenType.WALL)
        self.AppMain.set_current_wall(self.wall)

    @override
    def on_edit_clicked(self):
        print(f"Edit clicked on {self.wall.name}")
        Popup_EditWall(self.AppMain, self)
