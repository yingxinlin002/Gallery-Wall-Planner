import tkinter as tk
from tkinter import ttk

from gallery_wall_planner.gui.Popup_Base import Popup_Base
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanentObject import PermanentObject
from gallery_wall_planner.gui.AppMain import AppMain
from gallery_wall_planner.gui.ui_styles import get_ui_styles

class Popup_EditWallItem(Popup_Base):
    def __init__(self, AppMain : AppMain, parent_button, *args, **kwargs):
        super().__init__(AppMain, "Edit Wall Item", 300, 400, *args, **kwargs)
        from gallery_wall_planner.gui.BTN_WallItem import BTN_WallItem
        self.parent_button: BTN_WallItem = parent_button
        self.styles = get_ui_styles()

        self.load_content()
        
    @property
    def draggable_item(self):
        return self.parent_button.draggable_item

    def load_content(self):
        self.title_label = ttk.Label(self, text="Edit Wall Item", font=self.styles["title_font"])
        self.title_label.pack(pady=10)
        
        self.name_label = ttk.Label(self, text="Name:")
        self.name_label.pack(pady=5)
        
        self.name_var = tk.StringVar(value=self.draggable_item.wall_object.name)
        self.name_entry = ttk.Entry(self, textvariable=self.name_var)
        self.name_entry.pack(pady=5)
        
        self.width_label = ttk.Label(self, text="Width:")
        self.width_label.pack(pady=5)
        
        self.width_var = tk.StringVar(value=self.draggable_item.wall_object.width)
        self.width_entry = ttk.Entry(self, textvariable=self.width_var)
        self.width_entry.pack(pady=5)
        
        self.height_label = ttk.Label(self, text="Height:")
        self.height_label.pack(pady=5)
        
        self.height_var = tk.StringVar(value=self.draggable_item.wall_object.height)
        self.height_entry = ttk.Entry(self, textvariable=self.height_var)
        self.height_entry.pack(pady=5)

        if isinstance(self.draggable_item.wall_object, Artwork):
            self.artwork_label = ttk.Label(self, text="Hanging Point:")
            self.artwork_label.pack(pady=5)
            
            self.artwork_hanging_point_var = tk.StringVar(value=self.draggable_item.wall_object.hanging_point)
            self.artwork_hanging_point_entry = ttk.Entry(self, textvariable=self.artwork_hanging_point_var)
            self.artwork_hanging_point_entry.pack(pady=5)
        
        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.save_button.pack(pady=10)
        
    def save(self):
        if isinstance(self.draggable_item.wall_object, Artwork):
            wall_object = Artwork(
                name=self.name_var.get(),
                width=float(self.width_var.get()),
                height=float(self.height_var.get()),
                image_path=self.draggable_item.wall_object.image_path,
                price=self.draggable_item.wall_object.price,
                hanging_point=float(self.artwork_hanging_point_var.get())
            )
        else:
            wall_object = PermanentObject(
                name=self.name_var.get(),
                width=float(self.width_var.get()),
                height=float(self.height_var.get()),
                image_path=self.draggable_item.wall_object.image_path
            )
        wall_object.position = self.draggable_item.wall_object.position
        self.parent_button.update_wall_object(wall_object)
        self.destroy()