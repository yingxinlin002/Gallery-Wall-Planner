
import tkinter as tk

from typing import override

from gallery_wall_planner.gui.WallItem_Draggable import WallItem_Draggable
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.permanentObject import PermanentObject
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.gui.Popup_EditWallItem import Popup_EditWallItem
from gallery_wall_planner.gui.BTN_Base import BTN_Base

class BTN_WallItem(BTN_Base):
    
    def __init__(self, parent_frame : tk.Frame, draggable_item : WallItem_Draggable, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.draggable_item: WallItem_Draggable = draggable_item
        self.styles = get_ui_styles()
        self.label: tk.Label = None
        self.edit_button: tk.Button = None
        self.edit_button_text: str = "Edit"
        self.item_text: str = self.draggable_item.wall_object.name
        
    @override
    def on_clicked(self, event):
        print(f"Clicked on {self.draggable_item.wall_object.name}")
        if isinstance(self.draggable_item.wall_object, PermanentObject):
            print("Permanent Object")
        elif isinstance(self.draggable_item.wall_object, Artwork):
            print("Artwork")

    @override
    def on_edit_clicked(self):
        print(f"Edit clicked on {self.draggable_item.wall_object.name}")
        Popup_EditWallItem(self.draggable_item.parent_ui.AppMain, self)

    def update_wall_object(self, wall_object: WallObject):
        self.draggable_item.parent_ui.AppMain.gallery.current_wall.update_wall_item(self.draggable_item.wall_object.id, wall_object)
        self.draggable_item.update(wall_object)
        self.label.configure(text=wall_object.name)
        
        
