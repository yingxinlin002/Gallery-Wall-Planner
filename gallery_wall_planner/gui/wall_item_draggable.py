from __future__ import annotations

from typing import Union

from gallery_wall_planner.gui import wall_canvas
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.structures import Position
from gallery_wall_planner.gui.wall_canvas import WallCanvas
from gallery_wall_planner.gui.wall_item import WallItem, ItemLocation
from gallery_wall_planner.models.wall_line import Orientation, HorizontalAlignment, VerticalAlignment, SingleLine

class SnapAction():
    def __init__(self, orientation: Orientation):
        self.orientation: Orientation = orientation
        self.distance: int = None
        self.alignment: Union[HorizontalAlignment, VerticalAlignment] = None


class WallItemDraggable(WallItem):

    SNAP_TOLERANCE = 1.5
    def __init__(self, wall_object: WallObject, parent_ui: wall_canvas):
        super().__init__(wall_object, parent_ui)
        self.reference_lines = []  # Stores line IDs
        self.distance_labels = []  # Stores label IDs
        self._drag_data : Position = Position(0, 0)

    def create_canvas_item(self):
        # Convert from bottom-left origin to canvas coordinates
        super().create_canvas_item()
        self.parent_ui.canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_start)
        self.parent_ui.canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        self.parent_ui.canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_drop)
        if self.image_id is not None:
            self.parent_ui.canvas.tag_bind(self.image_id, "<ButtonPress-1>", self.on_start)
            self.parent_ui.canvas.tag_bind(self.image_id, "<B1-Motion>", self.on_drag)
            self.parent_ui.canvas.tag_bind(self.image_id, "<ButtonRelease-1>", self.on_drop)
        if self.label_id is not None:
            self.parent_ui.canvas.tag_bind(self.label_id, "<ButtonPress-1>", self.on_start)
            self.parent_ui.canvas.tag_bind(self.label_id, "<B1-Motion>", self.on_drag)
            self.parent_ui.canvas.tag_bind(self.label_id, "<ButtonRelease-1>", self.on_drop)


    def on_start(self, event):
        self._drag_data.x = event.x
        self._drag_data.y = event.y
        # Initialize reference lines (but don't show yet)
        self.reference_lines = [
            self.parent_ui.canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden'),  # Left
            self.parent_ui.canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden'),  # Right
            self.parent_ui.canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden'),  # Top
            self.parent_ui.canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden')   # Bottom
        ]
        self.distance_labels = [
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", state='hidden',anchor="e"),  # Left
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", state='hidden',anchor="w"),  # Right
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", state='hidden',anchor="s"),  # Top
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", state='hidden',anchor="n")   # Bottom
        ]

    def on_drag(self, event):
        # Calculate proposed movement
        dx = event.x - self._drag_data.x
        dy = event.y - self._drag_data.y

        # Get current canvas coordinates
        coords = self.parent_ui.canvas.coords(self.id)

        # Calculate new position in canvas coordinates
        new_x1 = coords[0] + dx
        new_y1 = coords[1] + dy
        new_x2 = coords[2] + dx
        new_y2 = coords[3] + dy

        snap_action_x: SnapAction = SnapAction(Orientation.HORIZONTAL)
        snap_action_y: SnapAction = SnapAction(Orientation.VERTICAL)
        center_x = (new_x1 + new_x2) / 2
        center_y = (new_y1 + new_y2) / 2
        snap_points_x = [new_x1, new_x2, center_x]
        snap_points_y = [new_y1, new_y2, center_y]
        for snap_line in self.parent_ui.wall.wall_lines:
            if snap_line.orientation == Orientation.VERTICAL:
                for snap_point in snap_points_x:
                    check_distance = self.parent_ui.wall_position.wall_left + snap_line.distance * self.parent_ui.screen_scale
                    if abs(check_distance - snap_point) < (self.SNAP_TOLERANCE * self.parent_ui.screen_scale) and (snap_action_x.distance is None or
                        abs(check_distance - snap_point) < snap_action_x.distance):
                        snap_action_x.distance = check_distance - snap_point
            if snap_line.orientation == Orientation.HORIZONTAL:
                for snap_point in snap_points_y:
                    check_distance = self.parent_ui.wall_position.wall_bottom - snap_line.distance * self.parent_ui.screen_scale
                    if abs(check_distance - snap_point) < (self.SNAP_TOLERANCE * self.parent_ui.screen_scale) and (snap_action_y.distance is None or
                        abs(check_distance - snap_point) < snap_action_y.distance):
                        snap_action_y.distance = check_distance - snap_point

        if snap_action_x.distance is not None:
            new_x1 = new_x1 + snap_action_x.distance
            new_x2 = new_x1 + self.wall_object.width * self.parent_ui.screen_scale
        if snap_action_y.distance is not None:
            new_y1 = new_y1 + snap_action_y.distance
            new_y2 = new_y1 + self.wall_object.height * self.parent_ui.screen_scale

        # Check boundaries in canvas coordinates
        if new_x1 < self.parent_ui.wall_position.wall_left:
            new_x1 = self.parent_ui.wall_position.wall_left 
            new_x2 = new_x1 + self.wall_object.width * self.parent_ui.screen_scale
        if new_x2 > self.parent_ui.wall_position.wall_right:
            new_x2 = self.parent_ui.wall_position.wall_right 
            new_x1 = new_x2 - self.wall_object.width * self.parent_ui.screen_scale
        if new_y1 < self.parent_ui.wall_position.wall_top:
            new_y1 = self.parent_ui.wall_position.wall_top 
            new_y2 = new_y1 + self.wall_object.height * self.parent_ui.screen_scale
        if new_y2 > self.parent_ui.wall_position.wall_bottom:
            new_y2 = self.parent_ui.wall_position.wall_bottom 
            new_y1 = new_y2 - self.wall_object.height * self.parent_ui.screen_scale



        # Apply constrained movement
        # self.parent_ui.canvas.move(self.id, dx, dy)
        self.parent_ui.canvas.coords(self.id, new_x1, new_y1, new_x2, new_y2)
        current_location = ItemLocation(new_x1, new_y1, new_x2, new_y2)
        new_position_x = (new_x1 - self.parent_ui.wall_position.wall_left) / self.parent_ui.screen_scale
        new_position_y = (new_y1 - self.parent_ui.wall_position.wall_top) / self.parent_ui.screen_scale
        self.wall_object.position = Position(new_position_x, new_position_y)

        if self.image_id is not None:
            image_location = self.get_item_location()
            self.parent_ui.canvas.coords(self.image_id, new_x1, new_y1)
        elif self.label_id is not None:
            label_position = self.get_label_location(current_location)
            self.parent_ui.canvas.coords(self.label_id, label_position.x, label_position.y)
        self._drag_data.x += dx
        self._drag_data.y += dy
        self.update_reference_lines()
        self.parent_ui.check_all_collisions()

    def on_drop(self, event):
        coords = self.parent_ui.canvas.coords(self.id)
        # Convert from canvas coordinates back to bottom-left origin
        new_x = (coords[0] - self.parent_ui.wall_position.wall_left) / self.parent_ui.screen_scale
        new_y = (coords[1] - self.parent_ui.wall_position.wall_top) / self.parent_ui.screen_scale
        new_x, new_y = self.parent_ui.enforce_boundaries(new_x, new_y, self.wall_object.width, self.wall_object.height)

        self.wall_object.position = Position(new_x, new_y)
        #self.parent_ui.layout_items[self.name] = {"x": new_x, "y": new_y}

        self.clear_reference_lines()
        # self.parent_ui.move_item_to_canvas(self.index)
        # self.parent_ui.check_all_collisions()
        #
        # if self.update_popup_fields and self.index in popup_windows and popup_windows[self.index].winfo_exists():
        #     self.update_popup_fields()

    def update_reference_lines(self):
        """Update existing reference lines instead of creating new ones"""
        coords = self.parent_ui.canvas.coords(self.id)
        # print(f"Wall left {self.parent_ui.wall_position.wall_left}, "
        #       f"Height {self.parent_ui.canvas_dimensions.height}, "
        #       f"Bottom {self.parent_ui.wall_position.wall_bottom}, "
        #       f"Coord {coords[0]}, ")

        # Left distance (from left wall edge)
        self.parent_ui.canvas.coords(self.reference_lines[0],
                    coords[0], self.parent_ui.wall_position.wall_top,
                    coords[0], self.parent_ui.wall_position.wall_bottom)

        # Right distance (from right wall edge)
        self.parent_ui.canvas.coords(self.reference_lines[1],
                    coords[2], self.parent_ui.wall_position.wall_top,
                    coords[2], self.parent_ui.wall_position.wall_bottom)

        # Top distance (from top wall edge)
        self.parent_ui.canvas.coords(self.reference_lines[2],
                    self.parent_ui.wall_position.wall_left,coords[1],
                    self.parent_ui.wall_position.wall_right, coords[1])

        # Bottom distance (from bottom wall edge)
        self.parent_ui.canvas.coords(self.reference_lines[3],
                    self.parent_ui.wall_position.wall_left,coords[3],
                    self.parent_ui.wall_position.wall_right, coords[3])

        # Update all lines and labels
        for line in self.reference_lines:
            self.parent_ui.canvas.itemconfig(line, state='normal')

        # Update distance labels
        left_dist = (coords[0] - self.parent_ui.wall_position.wall_left) / self.parent_ui.screen_scale
        right_dist = (self.parent_ui.wall_position.wall_right - coords[2]) / self.parent_ui.screen_scale
        top_dist = (coords[1] - self.parent_ui.wall_position.wall_top) / self.parent_ui.screen_scale
        bottom_dist = (self.parent_ui.wall_position.wall_bottom - coords[3]) / self.parent_ui.screen_scale
        self.parent_ui.canvas.coords(self.distance_labels[0],
                    coords[0],
                    (coords[1] + coords[3])/2)
        self.parent_ui.canvas.itemconfig(self.distance_labels[0],
                        text=f"{left_dist:.1f}\"", state='normal')

        self.parent_ui.canvas.coords(self.distance_labels[1],
                    coords[2],
                    (coords[1] + coords[3])/2)
        self.parent_ui.canvas.itemconfig(self.distance_labels[1],
                        text=f"{right_dist:.1f}\"", state='normal')

        self.parent_ui.canvas.coords(self.distance_labels[2],
                    (coords[0] + coords[2])/2,
                    coords[1])
        self.parent_ui.canvas.itemconfig(self.distance_labels[2],
                        text=f"{top_dist:.1f}\"", state='normal')

        self.parent_ui.canvas.coords(self.distance_labels[3],
                    (coords[0] + coords[2])/2,
                    coords[3])
        self.parent_ui.canvas.itemconfig(self.distance_labels[3],
                        text=f"{bottom_dist:.1f}\"", state='normal')

    def clear_reference_lines(self):
        """Hide all measurement lines"""
        for line in self.reference_lines:
            self.parent_ui.canvas.itemconfig(line, state='hidden')
        for label in self.distance_labels:
            self.parent_ui.canvas.itemconfig(label, state='hidden')
            
    def update_position(self):
        """Update the position of the draggable item and its label on the canvas."""
        # Update artwork position
        x1 = self.parent_ui.wall_position.wall_left + self.wall_object.x * self.parent_ui.screen_scale
        y1 = self.parent_ui.wall_position.wall_bottom - self.wall_object.y * self.parent_ui.screen_scale
        x2 = x1 + self.wall_object.width * self.parent_ui.screen_scale
        y2 = y1 - self.wall_object.height * self.parent_ui.screen_scale
        self.parent_ui.canvas.coords(self.id, x1, y1, x2, y2)
        
        # Update label position if it exists
        if hasattr(self, 'label_id') and self.label_id:
            current_location = ItemLocation(x1, y1, x2, y2)
            label_position = self.get_label_location(current_location)
            self.parent_ui.canvas.coords(self.label_id, label_position.x, label_position.y)
            self.parent_ui.canvas.itemconfig(self.label_id, text=self.wall_object.name)