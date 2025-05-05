


import tkinter as tk
from tkinter import ttk

from typing import override

from gallery_wall_planner.gui.wall_item_draggable import WallItemDraggable
from gallery_wall_planner.gui.ui_styles import get_ui_styles, apply_primary_button_style
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.gui.popup_edit_wall_item import PopupEditWallItem
from gallery_wall_planner.gui.btn_base import BTNBase
from gallery_wall_planner.gui.wall_canvas import WallCanvas


class BTNNewWallItem(BTNBase):
    def __init__(self, parent_frame : tk.Frame, parent_ui : 'ScreenLockObjectsUI' , is_artwork : bool, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        if is_artwork:
            self.item_text = "New Artwork"
        else:
            self.item_text = "New Permanent Object"
        self.is_artwork: bool = is_artwork
        self.draggable_item: WallItemDraggable = None
        self.wall_object: WallObject = None
        from gallery_wall_planner.gui.screen_lock_objects_ui import ScreenLockObjectsUI
        self.parent_ui: ScreenLockObjectsUI = parent_ui

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
        if self.is_artwork:
            self.wall_object = Artwork(name="New Artwork", width=30.0, height=20.0)
        else:
            self.wall_object = PermanentObject(name="New Permanent Object", width=30.0, height=20.0)

        self.draggable_item = WallItemDraggable(self.wall_object, self.parent_ui.wall_canvas)
        PopupEditWallItem(self.parent_ui.AppMain, self)
    
    @override
    def on_edit_clicked(self):
        print(f"Edit clicked on {self.item_text}")


    def update_wall_object(self, wall_object: WallObject):
        self.wall_object = wall_object
        self.draggable_item = WallItemDraggable(self.wall_object, self.parent_ui.wall_canvas)
        self.parent_ui.new_wall_item_button(self.draggable_item)
