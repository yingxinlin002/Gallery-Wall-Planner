from __future__ import annotations
from gallery_wall_planner.models.wall_object import WallObject
from PIL import Image, ImageTk
import os

from gallery_wall_planner.models.structures import Position
class WallItem:

    def __init__(self, wall_object: WallObject, parent_ui):
        self.wall_object = wall_object
        from gallery_wall_planner.gui.WallCanvas import WallCanvas
        self.parent_ui: WallCanvas = parent_ui
        self.id = None
        self.update_popup_fields = None
        self.image_obj : ImageTk = None
        self.label_id: int = None

    def create_canvas_item(self, fill_color:str = "lightblue"):
        # Convert from bottom-left origin to canvas coordinates
        x1 = self.parent_ui.wall_position.wall_left + self.wall_object.position.x * self.parent_ui.screen_scale
        y1 = self.parent_ui.canvas_dimensions.height - (
                    self.parent_ui.wall_position.wall_bottom + self.wall_object.position.y * self.parent_ui.screen_scale)  # Changed from (y + height)
        x2 = self.parent_ui.wall_position.wall_left + (
                    self.wall_object.position.x + self.wall_object.width) * self.parent_ui.screen_scale
        y2 = self.parent_ui.canvas_dimensions.height - (self.parent_ui.wall_position.wall_bottom + (
                    self.wall_object.position.y + self.wall_object.height) * self.parent_ui.screen_scale)  # Changed from just y

        if self.wall_object.image_path and os.path.isfile(self.wall_object.image_path):
            img = Image.open(self.wall_object.image_path)
            img = img.resize((int(x2 - x1), int(y2 - y1)), Image.ANTIALIAS)
            self.image_obj = ImageTk.PhotoImage(img)
            self.id = self.parent_ui.canvas.create_image(x1, y1, anchor="nw", image=self.image_obj)
        else:
            self.id = self.parent_ui.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black", width=2)
            label_position = self.get_label_location(x1, x2, y1, y2)
            self.label_id = self.parent_ui.canvas.create_text(label_position.x,label_position.y, text=self.wall_object.name, fill="black",
                                                             font=("Arial", 10))

    def update(self, wall_object: WallObject):
        self.wall_object = wall_object
        self.parent_ui.canvas.delete(self.id)
        self.parent_ui.canvas.delete(self.label_id)
        self.create_canvas_item()

    def get_label_location(self, x1: int, x2:int, y1:int, y2:int) -> Position:
        return Position((x1 + x2) / 2, (y1 + y2) / 2)

    def rectangles_overlap(self, item2: WallItem):
        """Check if two draggable items overlap"""
        ax1, ay1 = self.wall_object.position.x, self.wall_object.position.y
        ax2, ay2 = ax1 + self.wall_object.width, ay1 + self.wall_object.height
        bx1, by1 = item2.wall_object.position.x, item2.wall_object.position.y
        bx2, by2 = bx1 + item2.wall_object.width, by1 + item2.wall_object.height
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

    def redraw(self, screen_scale, wall_position):
        """Redraw the wall item based on the current screen scale and wall position."""
        x1 = wall_position.wall_left + self.wall_object.x * screen_scale
        y1 = wall_position.wall_bottom - (self.wall_object.y + self.wall_object.height) * screen_scale
        x2 = x1 + self.wall_object.width * screen_scale
        y2 = y1 + self.wall_object.height * screen_scale
        self.parent_ui.canvas.coords(self.id, x1, y1, x2, y2)