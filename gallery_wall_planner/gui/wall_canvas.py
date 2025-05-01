import tkinter as tk
from tkinter import ttk

from typing import List, Dict

# from gallery_wall_planner.gui.DraggableItem import DraggableItem
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.wall_item import WallItem
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.structures import CanvasDimensions, WallPosition
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.gui.ui_styles import (
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from gallery_wall_planner.models.wall_line import Orientation

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
        from gallery_wall_planner.gui.wall_item_draggable import WallItemDraggable
        self.draggable_items : Dict[str,WallItemDraggable] = {}
        from gallery_wall_planner.gui.wall_item import WallItem
        self.fixed_items : Dict[str,WallItem] = {}
        self.snap_lines : List[int] = []

    def add_draggables(self, wall_objects: Dict[str, WallObject]):
        for _, wall_object in wall_objects.items():
            self.add_draggable(wall_object)

    def add_draggable(self, wall_object : WallObject):
        from gallery_wall_planner.gui.wall_item_draggable import WallItemDraggable
        di: WallItemDraggable = WallItemDraggable(
            wall_object=wall_object,
            parent_ui=self
            )
        di.create_canvas_item()
        self.draggable_items[wall_object.id] = di

    def add_fixed_items(self, wall_objects : Dict[str,WallObject]):
        for _,obj in wall_objects.items():
            fixed_item = WallItem(obj,self)
            fixed_item.create_canvas_item("#999999")
            self.fixed_items[obj.id] = fixed_item
            # pos = obj.position
            # x1 = self.wall_position.wall_left + pos.x * self.screen_scale
            # y1 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + (pos.y + obj.height) * self.screen_scale)
            # x2 = self.wall_position.wall_left + (pos.x + obj.width) * self.screen_scale
            # y2 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + pos.y * self.screen_scale)
            # self.canvas.create_rectangle(x1, y1, x2, y2, fill="#999999", outline="black", width=2)

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

    def move_item_to_canvas(self, artwork):
        """Move the specified artwork to the canvas."""
        print(f"[DEBUG] Moving artwork: {artwork}")
        print(f"[DEBUG] Available keys in draggable_items: {list(self.draggable_items.keys())}")

        try:
            item = self.draggable_items[artwork.id]  # Use artwork.id as the key
            # Update the item's position on the canvas
            x1 = self.wall_position.wall_left + artwork.x * self.screen_scale
            y1 = self.canvas_dimensions.height - (self.wall_position.wall_bottom + artwork.y * self.screen_scale)
            x2 = x1 + artwork.width * self.screen_scale
            y2 = y1 - artwork.height * self.screen_scale
            self.canvas.coords(item.id, x1, y1, x2, y2)
        except KeyError:
            print(f"[ERROR] Artwork not found in draggable_items: {artwork}")
            raise

    def check_all_collisions(self):
        n = len(self.draggable_items)
        keys = list(self.draggable_items.keys())
        colliding = set()
        for i in range(n):
            for j in range(i+1, n):
                if self.draggable_items[keys[i]].rectangles_overlap(self.draggable_items[keys[j]]):
                    colliding.add(keys[i])
                    colliding.add(keys[j])
            for fixed in self.fixed_items:
                if self.draggable_items[keys[i]].rectangles_overlap(fixed):
                    colliding.add(keys[i])

        for key in keys:
            self.canvas.itemconfig(self.draggable_items[key].id, outline="red" if key in colliding else "black")
        return len(colliding) > 0

    def refresh_artworks(self):
        """Clear and redraw all artworks with their current positions"""
        self.clear_artworks()  # You may need to implement this
        for artwork in self.selected_wall.artwork:
            self.add_draggable(artwork)

    def draw_snap_lines(self):
        for line in self.snap_lines:
            self.canvas.delete(line)
        self.snap_lines.clear()
        line_number = 0
        for line in self.AppMain.gallery.current_wall.wall_lines:
            if line.orientation == Orientation.HORIZONTAL:
                y = self.wall_position.wall_top + line.distance * self.screen_scale
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

