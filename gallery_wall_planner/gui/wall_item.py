from __future__ import annotations
from gallery_wall_planner.models.wall_object import WallObject
from PIL import Image, ImageTk
import os

from gallery_wall_planner.models.structures import Position

class ItemLocation:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        return f"ItemLocation(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})"

class WallItem:
    def __init__(self, wall_object: WallObject, parent_ui):
        self.wall_object: WallObject = wall_object
        from gallery_wall_planner.gui.wall_canvas import WallCanvas
        self.parent_ui: WallCanvas = parent_ui
        self.id: int = None
        self.update_popup_fields = None
        self.image_obj : ImageTk = None
        self.label_id: int = None
        self.image_id: int = None

    def create_canvas_item(self, fill_color:str = "lightblue"):
        # Convert from bottom-left origin to canvas coordinates
        # x1 = self.parent_ui.wall_position.wall_left + self.wall_object.position.x * self.parent_ui.screen_scale
        # y1 = (
        #             self.parent_ui.wall_position.wall_bottom + self.wall_object.position.y * self.parent_ui.screen_scale)  # Changed from (y + height)
        # x2 = self.parent_ui.wall_position.wall_left + (
        #             self.wall_object.position.x + self.wall_object.width) * self.parent_ui.screen_scale
        # y2 = (
        #             self.parent_ui.wall_position.wall_bottom + (
        #             self.wall_object.position.y + self.wall_object.height) * self.parent_ui.screen_scale)  # Changed from just y

        item_location = self.get_item_location()
        self.id = self.parent_ui.canvas.create_rectangle(item_location.x1, item_location.y1, item_location.x2,
                                                         item_location.y2, fill=fill_color, outline="black", width=2)
        if self.wall_object.image_path and os.path.isfile(self.wall_object.image_path):
            img = Image.open(self.wall_object.image_path)
            img = img.resize((int(item_location.x2 - item_location.x1), int(item_location.y2 - item_location.y1)), Image.ANTIALIAS)
            self.image_obj = ImageTk.PhotoImage(img)
            image_location = self.get_image_location(item_location)
            self.image_id = self.parent_ui.canvas.create_image(image_location.x, image_location.y, anchor="nw", image=self.image_obj)
        else:
            label_position = self.get_label_location(item_location)
            self.label_id = self.parent_ui.canvas.create_text(label_position.x,label_position.y, text=self.wall_object.name, fill="black",
                                                             font=("Arial", 10))

    def get_item_location(self) -> ItemLocation:
        x1 = self.parent_ui.wall_position.wall_left + self.wall_object.position.x * self.parent_ui.screen_scale
        y1 = self.parent_ui.wall_position.wall_top + self.wall_object.position.y * self.parent_ui.screen_scale
        x2 = self.parent_ui.wall_position.wall_left + (self.wall_object.position.x + self.wall_object.width) * self.parent_ui.screen_scale
        y2 = self.parent_ui.wall_position.wall_top + (self.wall_object.position.y + self.wall_object.height) * self.parent_ui.screen_scale
        return ItemLocation(x1, y1, x2, y2)

    def update(self, wall_object: WallObject):
        self.wall_object = wall_object
        self.parent_ui.canvas.delete(self.id)
        self.parent_ui.canvas.delete(self.label_id)
        self.create_canvas_item()

    def get_label_location(self, item_location: ItemLocation) -> Position:
        return Position((item_location.x1 + item_location.x2) / 2, (item_location.y1 + item_location.y2) / 2)

    def get_image_location(self, item_location: ItemLocation) -> Position:
        return Position(item_location.x1, item_location.y1)

    def rectangles_overlap(self, item2: WallItem):
        """Check if two draggable items overlap"""
        ax1, ay1 = self.wall_object.position.x, self.wall_object.position.y
        ax2, ay2 = ax1 + self.wall_object.width, ay1 + self.wall_object.height
        bx1, by1 = item2.wall_object.position.x, item2.wall_object.position.y
        bx2, by2 = bx1 + item2.wall_object.width, by1 + item2.wall_object.height
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
