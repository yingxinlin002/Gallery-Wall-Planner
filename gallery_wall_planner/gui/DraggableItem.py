



class DraggableItem:
    def __init__(self, index, permanent_object, move_item_to_canvas, check_all_collisions):
        self.index = index
        self.permanent_object = permanent_object[0]  # Get the PermanentObject instance
        self.name = obstacle_names[index]
        self.width = self.permanent_object.width
        self.height = self.permanent_object.height

        # Initialize position from wall or default to (0,0)
        pos = permanent_object[1] if permanent_object[1] else {"x": 0.0, "y": 0.0}
        self.x = pos["x"]
        self.y = pos["y"]

        self.id = None
        self.reference_lines = []  # Stores line IDs
        self.distance_labels = []  # Stores label IDs
        self.create_canvas_item()
        self._drag_data = {"x": 0, "y": 0}
        self.update_popup_fields = None
        self.move_item_to_canvas = move_item_to_canvas
        self.check_all_collisions = check_all_collisions

    def create_canvas_item(self):
        # Convert from bottom-left origin to canvas coordinates
        x1 = wall_left + self.x * scale
        y1 = canvas_height - (wall_bottom + self.y * scale)  # Changed from (y + height)
        x2 = wall_left + (self.x + self.width) * scale
        y2 = canvas_height - (wall_bottom + (self.y + self.height) * scale)  # Changed from just y
        self.id = canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=2)
        canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_start)
        canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_drop)

    def on_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        # Initialize reference lines (but don't show yet)
        self.reference_lines = [
            canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden'),  # Left
            canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden'),  # Right
            canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden'),  # Top
            canvas.create_line(0, 0, 0, 0, dash=(2,2), fill="blue", state='hidden')   # Bottom
        ]
        self.distance_labels = [
            canvas.create_text(0, 0, text="", fill="blue", state='hidden'),  # Left
            canvas.create_text(0, 0, text="", fill="blue", state='hidden'),  # Right
            canvas.create_text(0, 0, text="", fill="blue", angle=90, state='hidden'),  # Top
            canvas.create_text(0, 0, text="", fill="blue", angle=90, state='hidden')   # Bottom
        ]

    def on_drag(self, event):
        # Calculate proposed movement
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]

        # Get current canvas coordinates
        coords = canvas.coords(self.id)

        # Calculate new position in canvas coordinates
        new_x1 = coords[0] + dx
        new_y1 = coords[1] + dy
        new_x2 = coords[2] + dx
        new_y2 = coords[3] + dy

        # Check boundaries in canvas coordinates
        if new_x1 < wall_left:
            dx = wall_left - coords[0]
        if new_x2 > wall_right:
            dx = wall_right - coords[2]
        if new_y1 < canvas_height - wall_bottom - wall_height*scale:
            dy = (canvas_height - wall_bottom - wall_height*scale) - coords[1]
        if new_y2 > canvas_height - wall_bottom:
            dy = (canvas_height - wall_bottom) - coords[3]

        # Apply constrained movement
        canvas.move(self.id, dx, dy)
        self._drag_data["x"] += dx
        self._drag_data["y"] += dy
        self.update_reference_lines()

    def on_drop(self, event):
        coords = canvas.coords(self.id)
        # Convert from canvas coordinates back to bottom-left origin
        new_x = (coords[0] - wall_left) / scale
        new_y = (canvas_height - coords[3] - wall_bottom) / scale  # Using bottom coordinate (y2)
        new_x, new_y = enforce_boundaries(new_x, new_y, self.width, self.height, wall_width, wall_height)

        self.x = new_x
        self.y = new_y
        # Update position directly in the permanent object
        self.permanent_object.position = {"x": self.x, "y": self.y}
        layout_items[self.name] = {"x": self.x, "y": self.y}

        self.clear_reference_lines()
        self.move_item_to_canvas(self.index)
        self.check_all_collisions()

        if self.update_popup_fields and self.index in popup_windows and popup_windows[self.index].winfo_exists():
            self.update_popup_fields()

    def update_reference_lines(self):
        """Update existing reference lines instead of creating new ones"""
        coords = canvas.coords(self.id)

        # Left distance (from left wall edge)
        left_dist = (coords[0] - wall_left) / scale
        canvas.coords(self.reference_lines[0],
                    wall_left, canvas_height-wall_bottom,
                    coords[0], canvas_height-wall_bottom)

        # Right distance (from right wall edge)
        right_dist = (wall_right - coords[2]) / scale
        canvas.coords(self.reference_lines[1],
                    coords[2], canvas_height-wall_bottom,
                    wall_right, canvas_height-wall_bottom)

        # Top distance (from top wall edge)
        top_dist = (wall_height - ((canvas_height - coords[1] - wall_bottom)/scale))  # Changed calculation
        canvas.coords(self.reference_lines[2],
                    wall_left, coords[1],
                    wall_left, canvas_height-wall_bottom-wall_height*scale)

        # Bottom distance (from bottom wall edge)
        bottom_dist = ((canvas_height - coords[3] - wall_bottom)/scale)  # Changed calculation
        canvas.coords(self.reference_lines[3],
                    wall_left, coords[3],
                    wall_left, canvas_height-wall_bottom)

        # Update all lines and labels
        for line in self.reference_lines:
            canvas.itemconfig(line, state='normal')

        # Update distance labels
        canvas.coords(self.distance_labels[0],
                    (wall_left + coords[0])/2,
                    canvas_height-wall_bottom+15)
        canvas.itemconfig(self.distance_labels[0],
                        text=f"{left_dist:.1f}\"", state='normal')

        canvas.coords(self.distance_labels[1],
                    (coords[2] + wall_right)/2,
                    canvas_height-wall_bottom+15)
        canvas.itemconfig(self.distance_labels[1],
                        text=f"{right_dist:.1f}\"", state='normal')

        canvas.coords(self.distance_labels[2],
                    wall_left-15,
                    (coords[1] + canvas_height-wall_bottom-wall_height*scale)/2)
        canvas.itemconfig(self.distance_labels[2],
                        text=f"{top_dist:.1f}\"", state='normal')

        canvas.coords(self.distance_labels[3],
                    wall_left-15,
                    (coords[3] + canvas_height-wall_bottom)/2)
        canvas.itemconfig(self.distance_labels[3],
                        text=f"{bottom_dist:.1f}\"", state='normal')

    def clear_reference_lines(self):
        """Hide all measurement lines"""
        for line in self.reference_lines:
            canvas.itemconfig(line, state='hidden')
        for label in self.distance_labels:
            canvas.itemconfig(label, state='hidden')
