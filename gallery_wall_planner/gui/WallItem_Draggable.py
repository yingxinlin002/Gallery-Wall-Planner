from __future__ import annotations
from gallery_wall_planner.gui import WallCanvas
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.gui.Screen_LockObjectsUI import Screen_LockObjectsUI
from gallery_wall_planner.models.structures import Position
from gallery_wall_planner.gui.WallCanvas import WallCanvas
from gallery_wall_planner.gui.WallItem import WallItem

class WallItem_Draggable(WallItem):
    def __init__(self, index, wall_object: WallObject, parent_ui: WallCanvas, name: str):
        super().__init__(index, wall_object, parent_ui, name)
        self.reference_lines = []  # Stores line IDs
        self.distance_labels = []  # Stores label IDs
        self._drag_data : Position = Position(0, 0)
        self.update_popup_fields = None

    def create_canvas_item(self):
        # Convert from bottom-left origin to canvas coordinates
        super().create_canvas_item()
        self.parent_ui.canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_start)
        self.parent_ui.canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        self.parent_ui.canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_drop)

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
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", state='hidden'),  # Left
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", state='hidden'),  # Right
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", angle=90, state='hidden'),  # Top
            self.parent_ui.canvas.create_text(0, 0, text="", fill="blue", angle=90, state='hidden')   # Bottom
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

        # Check boundaries in canvas coordinates
        if new_x1 < self.parent_ui.wall_position.wall_left:
            dx = self.parent_ui.wall_position.wall_left - coords[0]
        if new_x2 > self.parent_ui.wall_position.wall_right:
            dx = self.parent_ui.wall_position.wall_right - coords[2]
        if new_y1 < self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom - self.parent_ui.wall.height*self.parent_ui.screen_scale:
            dy = (self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom - self.parent_ui.wall.height*self.parent_ui.screen_scale) - coords[1]
        if new_y2 > self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom:
            dy = (self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom) - coords[3]

        # Apply constrained movement
        self.parent_ui.canvas.move(self.id, dx, dy)
        self._drag_data.x += dx
        self._drag_data.y += dy
        self.update_reference_lines()

    def on_drop(self, event):
        coords = self.parent_ui.canvas.coords(self.id)
        # Convert from canvas coordinates back to bottom-left origin
        new_x = (coords[0] - self.parent_ui.wall_position.wall_left) / self.parent_ui.screen_scale
        new_y = (self.parent_ui.canvas_dimensions.height - coords[3] - self.parent_ui.wall_position.wall_bottom) / self.parent_ui.screen_scale  # Using bottom coordinate (y2)
        new_x, new_y = self.parent_ui.enforce_boundaries(new_x, new_y, self.wall_object.width, self.wall_object.height)

        self.wall_object.position = Position(new_x, new_y)
        #self.parent_ui.layout_items[self.name] = {"x": new_x, "y": new_y}

        self.clear_reference_lines()
        self.parent_ui.move_item_to_canvas(self.index)
        self.parent_ui.check_all_collisions()

        if self.update_popup_fields and self.index in popup_windows and popup_windows[self.index].winfo_exists():
            self.update_popup_fields()

    def update_reference_lines(self):
        """Update existing reference lines instead of creating new ones"""
        coords = self.parent_ui.canvas.coords(self.id)

        # Left distance (from left wall edge)
        left_dist = (coords[0] - self.parent_ui.wall_position.wall_left) / self.parent_ui.screen_scale
        self.parent_ui.canvas.coords(self.reference_lines[0],
                    self.parent_ui.wall_position.wall_left, self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom,
                    coords[0], self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom)

        # Right distance (from right wall edge)
        right_dist = (self.parent_ui.wall_position.wall_right - coords[2]) / self.parent_ui.screen_scale
        self.parent_ui.canvas.coords(self.reference_lines[1],
                    coords[2], self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom,
                    self.parent_ui.wall_position.wall_right, self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom)

        # Top distance (from top wall edge)
        top_dist = (self.parent_ui.AppMain.gallery.current_wall.height - ((self.parent_ui.canvas_dimensions.height - coords[1] - self.parent_ui.wall_position.wall_bottom)/self.parent_ui.screen_scale))  # Changed calculation
        self.parent_ui.canvas.coords(self.reference_lines[2],
                    self.parent_ui.wall_position.wall_left, coords[1],
                    self.parent_ui.wall_position.wall_left, self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom)

        # Bottom distance (from bottom wall edge)
        bottom_dist = ((self.parent_ui.canvas_dimensions.height - coords[3] - self.parent_ui.wall_position.wall_bottom)/self.parent_ui.screen_scale)  # Changed calculation
        self.parent_ui.canvas.coords(self.reference_lines[3],
                    self.parent_ui.wall_position.wall_left, coords[3],
                    self.parent_ui.wall_position.wall_left, self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom)

        # Update all lines and labels
        for line in self.reference_lines:
            self.parent_ui.canvas.itemconfig(line, state='normal')

        # Update distance labels
        self.parent_ui.canvas.coords(self.distance_labels[0],
                    (self.parent_ui.wall_position.wall_left + coords[0])/2,
                    self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom + 15)
        self.parent_ui.canvas.itemconfig(self.distance_labels[0],
                        text=f"{left_dist:.1f}\"", state='normal')

        self.parent_ui.canvas.coords(self.distance_labels[1],
                    (coords[2] + self.parent_ui.wall_position.wall_right)/2,
                    self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom + 15)
        self.parent_ui.canvas.itemconfig(self.distance_labels[1],
                        text=f"{right_dist:.1f}\"", state='normal')

        self.parent_ui.canvas.coords(self.distance_labels[2],
                    self.parent_ui.wall_position.wall_left-15,
                    (coords[1] + self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom - self.parent_ui.wall.height*self.parent_ui.screen_scale)/2)
        self.parent_ui.canvas.itemconfig(self.distance_labels[2],
                        text=f"{top_dist:.1f}\"", state='normal')

        self.parent_ui.canvas.coords(self.distance_labels[3],
                    self.parent_ui.wall_position.wall_left-15,
                    (coords[3] + self.parent_ui.canvas_dimensions.height - self.parent_ui.wall_position.wall_bottom)/2)
        self.parent_ui.canvas.itemconfig(self.distance_labels[3],
                        text=f"{bottom_dist:.1f}\"", state='normal')

    def clear_reference_lines(self):
        """Hide all measurement lines"""
        for line in self.reference_lines:
            self.parent_ui.canvas.itemconfig(line, state='hidden')
        for label in self.distance_labels:
            self.parent_ui.canvas.itemconfig(label, state='hidden')
            
