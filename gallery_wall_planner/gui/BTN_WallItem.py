
import tkinter as tk

from gallery_wall_planner.gui.WallItem_Draggable import WallItem_Draggable
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.permanentObject import PermanentObject
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.gui.Popup_EditWallItem import Popup_EditWallItem

class BTN_WallItem(tk.Frame):
    
    def __init__(self, parent_frame : tk.Frame, draggable_item : WallItem_Draggable, *args, **kwargs):
        super().__init__(parent_frame, *args, **kwargs)
        self.draggable_item: WallItem_Draggable = draggable_item
        self.styles = get_ui_styles()
        self.label: tk.Label = None

        
    def load_content(self):
        self.label = tk.Label(self,
               text=self.draggable_item.wall_object.name,
               font=self.styles["label_font"],
               bg="#fff",
               justify="left",
               anchor="w")
        self.label.pack(side="left", fill="both", padx=5, expand=True)
        self.edit_button = tk.Button(self, text="Edit", command=self.on_edit_clicked)
        self.edit_button.pack(side="right", padx=5)
        self.label.bind("<Button-1>", self.on_clicked)


    def on_clicked(self, event):
        print(f"Clicked on {self.draggable_item.wall_object.name}")
        if isinstance(self.draggable_item.wall_object, PermanentObject):
            print("Permanent Object")
        elif isinstance(self.draggable_item.wall_object, Artwork):
            print("Artwork")

    def on_edit_clicked(self):
        print(f"Edit clicked on {self.draggable_item.wall_object.name}")
        Popup_EditWallItem(self.draggable_item.parent_ui.AppMain, self)

    def update_wall_object(self, wall_object: WallObject):
        self.draggable_item.update(wall_object)
        self.label.configure(text=wall_object.name)
        
        
