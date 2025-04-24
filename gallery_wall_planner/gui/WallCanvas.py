import tkinter as tk
from tkinter import ttk

from typing import List

# from gallery_wall_planner.gui.DraggableItem import DraggableItem
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.structures import CanvasDimensions, WallPosition
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.gui.ui_styles import (
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)


class WallCanvas():
    
    def __init__(self, AppMain : AppMain, parent_frame : tk.Frame, canvas_dimensions : CanvasDimensions, *args, **kwargs):
        self.AppMain = AppMain
        self.obstacle_names = [f"Obstacle{i+1}" for i in range(len(self.AppMain.gallery.current_wall.permanent_objects))]
        self.parent_frame = parent_frame
        self.canvas_dimensions = canvas_dimensions
        self.wall : Wall = self.AppMain.gallery.current_wall
        self.canvas: tk.Canvas = None
        self.screen_scale = None
        self.wall_position = None
        from gallery_wall_planner.gui.WallItem_Draggable import WallItem_Draggable
        self.draggable_items : list[WallItem_Draggable] = []
        from gallery_wall_planner.gui.WallItem import WallItem
        self.fixed_items : list[WallItem] = []

    def add_draggables(self, wall_objects : List[WallObject]):
        for i, wall_object in enumerate(wall_objects):
            self.add_draggable(wall_object,i)

    def add_draggable(self, wall_object : WallObject, index: int):
        from gallery_wall_planner.gui.WallItem_Draggable import WallItem_Draggable
        di: WallItem_Draggable = WallItem_Draggable(
            index=index,
            wall_object=wall_object,
                parent_ui=self,
                name=wall_object.name
            )
        di.create_canvas_item()
        self.draggable_items.append(di)

    def add_fixed_item(self, wall_objects : List[WallObject]):
        for obj in wall_objects:
            pos = obj.position
            x1 = self.wall_position.wall_left + pos.x * self.screen_scale
            y1 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + (pos.y + obj.height) * self.screen_scale)
            x2 = self.wall_position.wall_left + (pos.x + obj.width) * self.screen_scale
            y2 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + pos.y * self.screen_scale)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#999999", outline="black", width=2)

    def load_content(self):
        self.canvas = tk.Canvas(self.parent_frame, width=self.canvas_dimensions.width, height=self.canvas_dimensions.height)
        apply_canvas_style(self.canvas)
        self.canvas.pack(padx=self.canvas_dimensions.padding.left, pady=self.canvas_dimensions.padding.top)
        self.screen_scale = min((self.canvas_dimensions.width - 2 * self.canvas_dimensions.padding.left) / self.wall.width, (self.canvas_dimensions.height - 2 * self.canvas_dimensions.padding.top) / self.wall.height)
        self.wall_position = WallPosition(
            self.canvas_dimensions.margin, 
            self.canvas_dimensions.margin, 
            self.canvas_dimensions.margin + self.wall.width * self.screen_scale, 
            self.canvas_dimensions.margin + self.wall.height * self.screen_scale
        )

        # Draw wall background
        self.canvas.create_rectangle(self.wall_position.wall_left, self.canvas_dimensions.height - self.wall_position.wall_bottom - self.wall.height*self.screen_scale,
                          self.wall_position.wall_right, self.canvas_dimensions.height - self.wall_position.wall_bottom,
                          fill=self.wall.color, outline="black", width=2)

        # Add coordinate indicators
        self.canvas.create_text(self.wall_position.wall_left - 10, self.canvas_dimensions.height - self.wall_position.wall_bottom + 5, text="0", anchor="e")
        self.canvas.create_text(self.wall_position.wall_left - 10, self.canvas_dimensions.height - self.wall_position.wall_bottom - self.wall.height*self.screen_scale - 5,
                        text=f"{self.wall.height}\"", anchor="e")
        self.canvas.create_text(self.wall_position.wall_left + 5, self.canvas_dimensions.height - self.wall_position.wall_bottom + 15, text="0", anchor="n")
        self.canvas.create_text(self.wall_position.wall_right - 5, self.canvas_dimensions.height - self.wall_position.wall_bottom + 15, text=f"{self.wall.width}\"", anchor="n")

    def enforce_boundaries(self, x, y, width, height):
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + width > self.wall.width:
            x = self.wall.width - width
        if y + height > self.wall.height:
            y = self.wall.height - height
        return x, y

    def move_item_to_canvas(self,item_index):
        from gallery_wall_planner.gui.WallItem_Draggable import WallItem_Draggable
        item : WallItem_Draggable = self.draggable_items[item_index]
        x1 = self.wall_position.wall_left + item.wall_object.position.x * self.screen_scale
        y1 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + item.wall_object.position.y * self.screen_scale)  # Changed from (y + height)
        x2 = self.wall_position.wall_left + (item.wall_object.position.x + item.wall_object.width) * self.screen_scale
        y2 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + (item.wall_object.position.y + item.wall_object.height) * self.screen_scale)  # Changed from just y
        self.canvas.coords(item.id, x1, y1, x2, y2)

    def check_all_collisions(self):
        n = len(self.draggable_items)
        colliding = set()
        for i in range(n):
            for j in range(i+1, n):
                if self.draggable_items[i].rectangles_overlap(self.draggable_items[j]):
                    colliding.add(i)
                    colliding.add(j)
            for fixed in self.fixed_items:
                if self.draggable_items[i].rectangles_overlap(fixed):
                    colliding.add(i)

        for i, item in enumerate(self.draggable_items):
            self.canvas.itemconfig(item.id, outline="red" if i in colliding else "black")
        return len(colliding) > 0
