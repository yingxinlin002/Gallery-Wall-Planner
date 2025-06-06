import tkinter as tk
from tkinter import ttk

from typing import List, Dict

# from gallery_wall_planner.gui.DraggableItem import DraggableItem
from gallery.gui.app_main import AppMain, ScreenType
from gallery.gui.wall_item import WallItem
from gallery.models.wall import Wall
from gallery.models.structures import CanvasDimensions, WallPosition
from gallery.models.wall_object import WallObject
from gallery.gui.ui_styles import (
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from gallery.models.wall_line import Orientation

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
        from gallery.gui.wall_item_draggable import WallItemDraggable
        self.draggable_items : Dict[str,WallItemDraggable] = {}
        from gallery.gui.wall_item import WallItem
        self.fixed_items : Dict[str,WallItem] = {}
        self.snap_lines : List[int] = []
        self.snap_draggables: bool = True

    def create_draggables(self, wall_objects: Dict[str, WallObject]):
        for _, wall_object in wall_objects.items():
            self.create_draggable(wall_object)

    def create_draggable(self, wall_object : WallObject):
        from gallery.gui.wall_item_draggable import WallItemDraggable
        di: WallItemDraggable = WallItemDraggable(
            wall_object=wall_object,
            parent_ui=self
            )
        di.create_canvas_item()
        self.draggable_items[wall_object.id] = di

    def add_draggable(self, draggable_item : 'WallItemDraggable'):
        draggable_item.create_canvas_item()
        self.draggable_items[draggable_item.wall_object.id] = draggable_item

    def add_fixed_items(self, wall_objects : Dict[str,WallObject]):
        for _,obj in wall_objects.items():
            fixed_item = WallItem(obj,self)
            fixed_item.create_canvas_item("#999999")
            self.fixed_items[obj.id] = fixed_item

    def update_wall_object(self, old_id : str, wall_object : WallObject):
        if old_id in self.draggable_items:
            temp_draggable = self.draggable_items.pop(old_id)
            temp_draggable.update(wall_object)
            self.draggable_items[wall_object.id] = temp_draggable
        elif old_id in self.fixed_items:
            temp_fixed = self.fixed_items.pop(old_id)
            temp_fixed.update(wall_object)
            self.fixed_items[wall_object.id] = temp_fixed

    def load_content(self):
        self.canvas = tk.Canvas(self.parent_frame, width=self.canvas_dimensions.width, height=self.canvas_dimensions.height)
        apply_canvas_style(self.canvas)
        self.canvas.pack(padx=self.canvas_dimensions.padding.left, pady=self.canvas_dimensions.padding.top)
        c_width = self.canvas_dimensions.width - self.canvas_dimensions.padding.left - self.canvas_dimensions.padding.right - ( 2 * self.canvas_dimensions.margin)
        c_height = self.canvas_dimensions.height - self.canvas_dimensions.padding.top - self.canvas_dimensions.padding.bottom - ( 2 * self.canvas_dimensions.margin)
        self.screen_scale = min(
            c_width / self.wall.width, 
            c_height / self.wall.height)
        self.wall_position = WallPosition(
            self.canvas_dimensions.margin, 
            self.canvas_dimensions.margin, 
            self.canvas_dimensions.margin + self.wall.width * self.screen_scale, 
            self.canvas_dimensions.margin + self.wall.height * self.screen_scale
        )

        # Draw wall background
        self.canvas.create_rectangle(self.wall_position.wall_left, 
                                    self.wall_position.wall_top,
                                    self.wall_position.wall_right, 
                                    self.wall_position.wall_bottom,
                                    fill=self.wall.color, outline="black", width=2)

        # Add coordinate indicators
        self.canvas.create_text(self.wall_position.wall_left - 10, self.wall_position.wall_bottom - 5, text="0", anchor="e")
        self.canvas.create_text(self.wall_position.wall_left - 10, self.wall_position.wall_top - 5,
                        text=f"{self.wall.height}\"", anchor="e")
        self.canvas.create_text(self.wall_position.wall_left + 5, self.wall_position.wall_bottom + 5, text="0", anchor="n")
        self.canvas.create_text(self.wall_position.wall_right + 10, self.wall_position.wall_top - 5, text=f"{self.wall.width}\"", anchor="w")

        # Add snap lines
        self.draw_snap_lines()

    def enforce_boundaries_even_spacing(self, x, y, width, height):
        """Ensure the item stays within wall boundaries when centered at Y position"""
        min_x = 0
        max_x = self.wall.width - width
        
        # Calculate min/max Y based on keeping center within bounds
        min_y = height/2  # Can't go so high that center would be above wall
        max_y = self.wall.height - height/2  # Can't go so low that center would be below floor
        
        x = max(min_x, min(x, max_x))
        y = max(min_y, min(y, max_y))
        
        return x, y
    
    def enforce_boundaries(self, x, y, width, height):
        return self.AppMain.gallery.current_wall.enforce_boundaries(x, y, width, height)

    def check_all_collisions(self):
        colliding_ids = self.AppMain.gallery.current_wall.check_collisions()
        for key in self.draggable_items:
            if key in colliding_ids:    
                self.canvas.itemconfig(self.draggable_items[key].id, outline="red")
            else:
                self.canvas.itemconfig(self.draggable_items[key].id, outline="black")
        return len(colliding_ids) > 0

    def draw_snap_lines(self):
        for line in self.snap_lines:
            self.canvas.delete(line)
        self.snap_lines.clear()
        line_number = 0
        for line in self.AppMain.gallery.current_wall.wall_lines:
            if line.orientation == Orientation.HORIZONTAL:
                y = self.wall_position.wall_bottom - line.distance * self.screen_scale
                line_number = self.canvas.create_line(
                    self.wall_position.wall_left, y,
                    self.wall_position.wall_right, y,
                    fill="blue", dash=(4, 2), width=2, tags="snap_line"
                )
            elif line.orientation == Orientation.VERTICAL:
                x = self.wall_position.wall_left + line.distance * self.screen_scale
                line_number = self.canvas.create_line(
                    x, self.wall_position.wall_top,
                    x, self.wall_position.wall_bottom,
                    fill="blue", dash=(4, 2), width=2, tags="snap_line"
                )
            self.snap_lines.append(line_number)

