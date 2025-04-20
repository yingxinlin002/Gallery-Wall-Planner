from __future__ import annotations
from gallery_wall_planner.gui import WallCanvas
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.gui.WallCanvas import WallCanvas

class WallItem:

    def __init__(self, index, wall_object: WallObject, parent_ui: WallCanvas, name: str):
        self.index = index
        self.wall_object = wall_object
        self.parent_ui = parent_ui
        # self.name = parent_ui.obstacle_names[index]
        self.name = name

        self.id = None
        self.update_popup_fields = None

    def create_canvas_item(self):
        # Convert from bottom-left origin to canvas coordinates
        x1 = self.parent_ui.wall_position.wall_left + self.wall_object.position.x * self.parent_ui.screen_scale
        y1 = self.parent_ui.canvas_dimensions.height - (
                    self.parent_ui.wall_position.wall_bottom + self.wall_object.position.y * self.parent_ui.screen_scale)  # Changed from (y + height)
        x2 = self.parent_ui.wall_position.wall_left + (
                    self.wall_object.position.x + self.wall_object.width) * self.parent_ui.screen_scale
        y2 = self.parent_ui.canvas_dimensions.height - (self.parent_ui.wall_position.wall_bottom + (
                    self.wall_object.position.y + self.wall_object.height) * self.parent_ui.screen_scale)  # Changed from just y
        self.id = self.parent_ui.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=2)

    def rectangles_overlap(self, item2: WallItem):
        """Check if two draggable items overlap"""
        ax1, ay1 = self.wall_object.position.x, self.wall_object.position.y
        ax2, ay2 = ax1 + self.wall_object.width, ay1 + self.wall_object.height
        bx1, by1 = item2.wall_object.position.x, item2.wall_object.position.y
        bx2, by2 = bx1 + item2.wall_object.width, by1 + item2.wall_object.height
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
