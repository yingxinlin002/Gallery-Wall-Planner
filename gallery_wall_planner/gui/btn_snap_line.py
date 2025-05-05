import tkinter as tk

from typing import override
from gallery_wall_planner.gui.btn_base import BTNBase
from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.gui.popup_snap_lines import PopupSnapLines

class BTNSnapLine(BTNBase):
    def __init__(self, parent_frame : tk.Frame, snap_line : SingleLine, AppMain : AppMain, parent_ui: 'ScreenEditorUI', *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.snap_line: SingleLine = snap_line 
        self.AppMain: AppMain = AppMain
        self.parent_ui: 'ScreenEditorUI' = parent_ui
        self.item_text: str = str(snap_line)

    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.snap_line.id}")

    @override
    def on_edit_clicked(self):
        PopupSnapLines(self.AppMain, self.parent_ui, self.snap_line)