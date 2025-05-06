


import tkinter as tk
from tkinter import ttk, messagebox
from typing import override

from gallery_wall_planner.gui.wall_item_draggable import WallItemDraggable
from gallery_wall_planner.gui.ui_styles import get_ui_styles, apply_primary_button_style
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.gui.popup_edit_wall_item import PopupEditWallItem
from gallery_wall_planner.gui.btn_base import BTNBase
from gallery_wall_planner.gui.app_main import AppMain, ScreenType


class BTNNewWallItem(BTNBase):
    def __init__(self, 
                 app_main : AppMain,
                 parent_frame : tk.Frame, 
                 screen_type : ScreenType,
                 is_artwork : bool,
                 *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.app_main: AppMain = app_main
        self.screen_type: ScreenType = screen_type
        if is_artwork:
            self.item_text = "New Artwork"
        else:
            self.item_text = "New Permanent Object"
        self.is_artwork: bool = is_artwork

    @override
    def load_content(self):
        self.label = tk.Label(self,
               text=self.item_text,
               font=self.styles["label_font"],
               bg="#fff",
               justify="left",
               anchor="w",
                )
        self.label.pack(side="left", fill="both", padx=5, expand=True)
        self.label.bind("<Button-1>", self.on_clicked)
        
    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.item_text}")
        PopupEditWallItem(self.app_main, None, self.screen_type, self.is_artwork)
    
    @override
    def on_edit_clicked(self):
        print(f"Edit clicked on {self.item_text}")


