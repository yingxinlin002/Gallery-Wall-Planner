
import tkinter as tk

from typing import override, Callable, Optional

from gallery_wall_planner.gui.wall_item_draggable import WallItemDraggable
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.gui.popup_edit_wall_item import PopupEditWallItem
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.btn_base import BTNBase
from enum import Enum

class WallItemState(Enum):
    ACTIVE = 1
    PLACED = 2
    INACTIVE = 3

class BTNWallItem(BTNBase):
    """Button class for wall items (artwork, permanent objects)"""
    def __init__(self, 
                 app_main : AppMain,
                 parent_frame : tk.Frame, 
                 wall_object : WallObject,
                 screen_type : ScreenType,
                 state : WallItemState = WallItemState.PLACED, 
                 *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.app_main: AppMain = app_main
        self.wall_object: WallObject = wall_object
        self.item_text: str = self.wall_object.name
        self.state: WallItemState = state
        self.screen_type: ScreenType = screen_type    
    
    @override
    def load_content(self):
        """Load the content of the button wall item"""
        if self.state == WallItemState.ACTIVE or self.state == WallItemState.PLACED:
            if self.state == WallItemState.ACTIVE:
                self.edit_button_text = "Add to Wall"
            super().load_content()
        else:
            self.label = tk.Label(self,
               text=self.item_text,
               font=self.styles["label_font"],
               bg="#e0e0e0",
               justify="left",
               anchor="w",
                )
            self.label.pack(side="left", fill="both", padx=5, expand=True)
        
    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.wall_object.name}")
        if isinstance(self.wall_object, PermanentObject):
            print("Permanent Object")
        elif isinstance(self.wall_object, Artwork):
            print("Artwork")

    @override
    def on_edit_clicked(self):
        print(f"Edit clicked on {self.wall_object.name}")
        if self.state == WallItemState.ACTIVE:
            if isinstance(self.wall_object, Artwork):
                self.app_main.gallery.place_art(self.wall_object.name, self.app_main.gallery.current_wall.name)
            # elif isinstance(self.wall_object, PermanentObject):
            #     self.app_main.gallery.current_wall.place_permanent_object(self.wall_object.name, self.app_main.gallery.current_wall.name)
            self.app_main.switch_screen(self.screen_type)
        else:
            PopupEditWallItem(self.app_main, self.wall_object, self.screen_type)

