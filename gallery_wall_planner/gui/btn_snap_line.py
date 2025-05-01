import tkinter as tk

from typing import override
from gallery_wall_planner.gui.btn_base import BTNBase
from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.gui.app_main import AppMain

class BTNSnapLine(BTNBase):
    def __init__(self, parent_frame : tk.Frame, snap_line_id : str, AppMain : AppMain, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.snap_line_id: str = snap_line_id 
        self.AppMain: AppMain = AppMain

    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.snap_line_id}")

    @override
    def on_edit_clicked(self):
        print(f"Edit clicked on {self.snap_line_id}")
        