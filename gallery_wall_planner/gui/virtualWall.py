### Based on Shanes's OrganizeArt code 
# Details changed to work with editorUI.py
# ###
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.gui.snap_line_popup import open_snap_line_popup
from gallery_wall_planner.models.wall_line import Orientation, HorizontalAlignment, VerticalAlignment

class VirtualWall:
    def __init__(self, parent_frame, selected_wall):
        self.parent = parent_frame
        self.selected_wall = selected_wall
        self.artworks = []
        self.draggable_items = []
        self.snap_lines = []
        self.popup_windows = {}
        
        # Canvas setup
        self.canvas_width = 800
        self.canvas_height = 600
        self.margin = 50
        self.snap_threshold = 8  # pixels
        self.grid_spacing = 50    # pixels between grid lines
        
        # Initialize grid attributes
        self.grid_visible = True
        self.horizontal_lines = []
        self.vertical_lines = []
        
        self.create_ui()
        self.setup_default_snap_lines()
    
    def create_ui(self):
        """Create the main UI components"""
        self.calculate_scale()
        
        # Main canvas
        self.canvas = tk.Canvas(self.parent, bg="white", 
                              width=self.canvas_width, 
                              height=self.canvas_height)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Draw the wall
        self.draw_wall()
        
        # Draw the grid (starts empty except for default snap line)
        self.draw_grid()
        
        # Snap line controls frame
        self.snap_button_frame = ttk.Frame(self.parent)
        self.snap_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Grid controls
        self.toggle_grid_btn = ttk.Button(
            self.snap_button_frame, 
            text="Toggle Grid", 
            command=self.toggle_grid
        )
        self.toggle_grid_btn.pack(side="left", padx=5)
        
        # Add snap line button
        self.add_line_btn = ttk.Button(
            self.snap_button_frame, 
            text="Add Snap Line", 
            command=self.add_new_snap_line
        )
        self.add_line_btn.pack(side="left", padx=5)
        
        # Edit snap lines button
        self.edit_lines_btn = ttk.Button(
            self.snap_button_frame,
            text="Edit Snap Lines",
            command=self.open_manage_lines_popup
        )
        self.edit_lines_btn.pack(side="left", padx=5)
        
        # Save layout button
        self.save_btn = ttk.Button(
            self.snap_button_frame,
            text="Save Layout",
            command=self.save_layout
        )
        self.save_btn.pack(side="right", padx=5)

    def toggle_grid(self):
        """Toggle grid visibility"""
        self.grid_visible = not self.grid_visible
        self.draw_grid()
    
    def calculate_scale(self):
        """Calculate the scaling factor for the wall"""
        self.scale = min(
            (self.canvas_width - 2*self.margin) / self.selected_wall.width,
            (self.canvas_height - 2*self.margin) / self.selected_wall.height
        )
    
    def draw_wall(self):
        """Draw the wall representation on canvas"""
        wall_left = self.margin
        wall_bottom = self.margin
        wall_right = wall_left + self.selected_wall.width * self.scale
        wall_top = wall_bottom + self.selected_wall.height * self.scale
        
        self.canvas.create_rectangle(
            wall_left, self.canvas_height - wall_top,
            wall_right, self.canvas_height - wall_bottom,
            fill="#f5f5f5", outline="black", width=2
        )
    
    def draw_grid(self):
        """Draw grid lines on canvas - starts empty except for default snap line"""
        # Clear existing grid
        self.canvas.delete("grid_line")
        
        if not self.grid_visible:
            return
            
        wall_left = self.margin
        wall_bottom = self.margin
        wall_right = wall_left + self.selected_wall.width * self.scale
        wall_top = wall_bottom + self.selected_wall.height * self.scale
        
        # Only draw the default horizontal line at 60 inches (converted to canvas coordinates)
        default_y = self.canvas_height - (wall_bottom + 60 * self.scale)
        self.canvas.create_line(
            wall_left, default_y,
            wall_right, default_y,
            fill="lightgray", dash=(2, 2), tags="grid_line"
        )
    
    def setup_default_snap_lines(self):
        """Create default snap line at 60 inches"""
        default_line = SingleLine(
            orientation=Orientation.HORIZONTAL,  # Use the enum value here
            alignment=HorizontalAlignment.CENTER,  # Use the enum value here
            distance=60.0,  # Changed from 62 to 60 inches
            snap_to=True,
            moveable=True
        )
        self.snap_lines.append(default_line)
        self.draw_snap_lines()

    def draw_snap_lines(self):
        """Draw all snap lines on canvas"""
        self.canvas.delete("snap_line")
        wall_left = self.margin
        wall_bottom = self.margin

        for line in self.snap_lines:
            if line.orientation == "horizontal":
                if line.alignment == HorizontalAlignment.TOP:
                    # Draw the top snap line
                    y = self.canvas_height - (wall_bottom + line.distance * self.scale)
                    self.canvas.create_line(
                        wall_left, y,
                        wall_left + self.selected_wall.width * self.scale, y,
                        fill="blue", dash=(4, 2), width=4, tags="snap_line"
                    )
                elif line.alignment == HorizontalAlignment.CENTER:
                    # Draw the center snap line
                    y = self.canvas_height - (wall_bottom + (line.distance * self.scale))
                    self.canvas.create_line(
                        wall_left, y,
                        wall_left + self.selected_wall.width * self.scale, y,
                        fill="blue", dash=(4, 2), width=4, tags="snap_line"
                    )
                elif line.alignment == HorizontalAlignment.BOTTOM:
                    # Draw the bottom snap line
                    y = self.canvas_height - (wall_bottom + self.selected_wall.height * self.scale - line.distance * self.scale)
                    self.canvas.create_line(
                        wall_left, y,
                        wall_left + self.selected_wall.width * self.scale, y,
                        fill="blue", dash=(4, 2), width=4, tags="snap_line"
                    )
            else:  # vertical
                if line.alignment == VerticalAlignment.LEFT:
                    # Draw the left snap line
                    x = wall_left + line.distance * self.scale
                    self.canvas.create_line(
                        x, self.canvas_height - (wall_bottom + self.selected_wall.height * self.scale),
                        x, self.canvas_height - wall_bottom,
                        fill="blue", dash=(4, 2), width=4, tags="snap_line"
                    )
                elif line.alignment == VerticalAlignment.CENTER:
                    # Draw the center snap line
                    x = wall_left + line.distance * self.scale
                    self.canvas.create_line(
                        x, self.canvas_height - (wall_bottom + self.selected_wall.height * self.scale / 2),
                        x, self.canvas_height - wall_bottom,
                        fill="blue", dash=(4, 2), width=4, tags="snap_line"
                    )
                elif line.alignment == VerticalAlignment.RIGHT:
                    # Draw the right snap line
                    x = wall_left + line.distance * self.scale
                    self.canvas.create_line(
                        x, self.canvas_height - (wall_bottom + self.selected_wall.height * self.scale),
                        x, self.canvas_height - wall_bottom,
                        fill="blue", dash=(4, 2), width=4, tags="snap_line"
                    )
                    self.canvas.tag_raise("snap_line")  # Bring snap lines to the front
    
    def add_new_snap_line(self):
        """Add a new snap line to the wall"""
        def handle_save(new_line):
            # Check for duplicate lines
            for existing in self.snap_lines:
                if (existing.orientation == new_line.orientation and 
                    abs(existing.distance - new_line.distance) < 0.05):
                    self.show_duplicate_line_popup(new_line)
                    return
            
            self.snap_lines.append(new_line)
            self.draw_snap_lines()
            self.draw_grid()  # Redraw grid to include new line
        
        open_snap_line_popup(
            self.parent,
            handle_save,
            wall_width=self.selected_wall.width,
            wall_height=self.selected_wall.height
        )

    def show_duplicate_line_popup(self, new_line):
        """Show popup when duplicate line is detected"""
        popup = Toplevel(self.parent)
        popup.title("Line Already Exists")
        
        msg = "A snap line at this location already exists.\nWould you like to add it anyway?"
        ttk.Label(popup, text=msg).pack(padx=20, pady=(15, 10))
        
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Cancel", 
            command=popup.destroy
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Add Anyway",
            command=lambda: [self.snap_lines.append(new_line), 
                            self.draw_snap_lines(), 
                            self.draw_grid(),
                            popup.destroy()]
        ).pack(side="left", padx=5)
    
    def open_manage_lines_popup(self):
        """Open popup to manage existing snap lines"""
        popup = Toplevel(self.parent)
        popup.title("Manage Snap Lines")
        popup.geometry("400x300")
        
        if not self.snap_lines:
            ttk.Label(popup, text="No snap lines to manage.").pack(padx=10, pady=10)
            return
            
        canvas = tk.Canvas(popup)
        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        frame.bind("<Configure>", on_configure)
        
        for idx, line in enumerate(self.snap_lines):
            self.create_snap_line_control(frame, idx, line)
    
    def create_snap_line_control(self, parent, index, line):
        """Create controls for a single snap line"""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5, padx=10)

        label_text = f"{line.orientation.name.capitalize()} - {line.alignment.name.capitalize()} - {line.distance:.2f}\""
        ttk.Label(frame, text=label_text).pack(side="left")

        ttk.Button(
            frame,
            text="Edit",
            command=lambda i=index: self.edit_snap_line(i)
        ).pack(side="right", padx=5)

        ttk.Button(
            frame,
            text="Delete",
            command=lambda i=index: self.delete_snap_line(i)
        ).pack(side="right", padx=5)
    
    def edit_snap_line(self, index):
        """Edit an existing snap line"""
        def handle_save(updated_line):
            self.snap_lines[index] = updated_line
            self.draw_snap_lines()
            self.draw_grid()  # Redraw grid to reflect changes
        
        open_snap_line_popup(
            self.parent,
            handle_save,
            existing_line=self.snap_lines[index],
            wall_width=self.selected_wall.width,
            wall_height=self.selected_wall.height
        )
    
    def delete_snap_line(self, index):
        """Delete a snap line"""
        del self.snap_lines[index]
        self.draw_snap_lines()
        self.draw_grid()  # Redraw grid to reflect changes
    
    def add_artwork(self, artwork):
        """Add artwork to the virtual wall"""
        self.artworks.append(artwork)
        self.create_draggable_artwork(artwork)
    
    def create_draggable_artwork(self, artwork):
        """Create a draggable artwork item"""
        wall_left = self.margin
        wall_bottom = self.margin
        
        # Default position (top-left corner)
        x = wall_left + 10 * self.scale
        y = self.canvas_height - (wall_bottom + 10 * self.scale + artwork.height * self.scale)
        
        # Create artwork rectangle
        item_id = self.canvas.create_rectangle(
            x, y,
            x + artwork.width * self.scale,
            y + artwork.height * self.scale,
            fill="lightblue", outline="black", width=2,
            tags="artwork"
        )
        
        # Add text label
        text_id = self.canvas.create_text(
            x + artwork.width * self.scale / 2,
            y + artwork.height * self.scale / 2,
            text=artwork.name,
            font=("Arial", 10),
            tags="artwork"
        )
        
        # Store draggable item
        draggable = {
            'id': item_id,
            'text_id': text_id,
            'artwork': artwork,
            'x': 10,  # Default x position in inches
            'y': 10   # Default y position in inches
        }
        self.draggable_items.append(draggable)
        
        # Bind drag events
        self.canvas.tag_bind(item_id, "<ButtonPress-1>", lambda e, i=item_id: self.on_drag_start(e, i))
        self.canvas.tag_bind(item_id, "<B1-Motion>", lambda e, i=item_id: self.on_drag(e, i))
        self.canvas.tag_bind(item_id, "<ButtonRelease-1>", lambda e, i=item_id: self.on_drop(e, i))
        self.canvas.tag_bind(text_id, "<ButtonPress-1>", lambda e, i=item_id: self.on_drag_start(e, i))
        self.canvas.tag_bind(text_id, "<B1-Motion>", lambda e, i=item_id: self.on_drag(e, i))
        self.canvas.tag_bind(text_id, "<ButtonRelease-1>", lambda e, i=item_id: self.on_drop(e, i))

    def on_drag_start(self, event, item_id):
        """Handle drag start event"""
        self.drag_data = {
            'item': item_id,
            'x': event.x,
            'y': event.y,
            'initial_coords': self.canvas.coords(item_id)
        }

    def on_drag(self, event, item_id):
        """Handle dragging event with boundary checking, real-time snapping, and visual feedback"""
        dx = event.x - self.drag_data['x']
        dy = event.y - self.drag_data['y']
        
        # Get initial coordinates
        x1, y1, x2, y2 = self.drag_data['initial_coords']
        new_x1 = x1 + dx
        new_y1 = y1 + dy
        width = x2 - x1
        height = y2 - y1
        
        # Check wall boundaries
        wall_left = self.margin
        wall_right = wall_left + self.selected_wall.width * self.scale
        wall_top = self.margin
        wall_bottom = self.canvas_height - (self.margin + self.selected_wall.height * self.scale)
        
        # Prevent dragging outside the wall
        if new_x1 < wall_left:
            new_x1 = wall_left
        if new_x1 + width > wall_right:
            new_x1 = wall_right - width
        if new_y1 < wall_bottom:
            new_y1 = wall_bottom
        if new_y1 + height > self.canvas_height - wall_top:
            new_y1 = self.canvas_height - wall_top - height
        
        # Get the artwork dimensions
        artwork = None
        for item in self.draggable_items:
            if item['id'] == item_id:
                artwork = item['artwork']
                break
        
        # Track if we snapped to any line
        snapped = False
        
        if artwork:
            # Store original position before snapping
            original_x, original_y = new_x1, new_y1
            
            # Check for snap lines in pixel coordinates
            for line in self.snap_lines:
                if not line.snap_to:
                    continue
                
                if line.orientation == Orientation.HORIZONTAL:  # Use the enum comparison for orientation
                    line_y = self.canvas_height - (self.margin + line.distance * self.scale)
                    
                    # Check top edge (8 pixel threshold)
                    if abs((new_y1 + height) - line_y) < 8:
                        new_y1 = line_y - height
                        snapped = True
                    # Check center (8 pixel threshold)
                    elif abs((new_y1 + height/2) - line_y) < 8:
                        new_y1 = line_y - height/2
                        snapped = True
                    # Check bottom edge (8 pixel threshold)
                    elif abs(new_y1 - line_y) < 8:
                        new_y1 = line_y
                        snapped = True
                    
                else:  # vertical
                    line_x = self.margin + line.distance * self.scale
                    
                    # Check left edge (8 pixel threshold)
                    if abs(new_x1 - line_x) < 8:
                        new_x1 = line_x
                        snapped = True
                    # Check center (8 pixel threshold)
                    elif abs((new_x1 + width/2) - line_x) < 8:
                        new_x1 = line_x - width/2
                        snapped = True
                    # Check right edge (8 pixel threshold)
                    elif abs((new_x1 + width) - line_x) < 8:
                        new_x1 = line_x - width
                        snapped = True
        
        # Visual feedback for snapping
        if snapped:
            # Highlight artwork when snapped (thicker green outline)
            self.canvas.itemconfig(item_id, outline="green", width=3)
            
            # Find and highlight the snap line we're snapping to
            self.canvas.itemconfig("snap_line", width=1)  # Reset all snap lines first
            for line in self.snap_lines:
                if line.orientation == Orientation.HORIZONTAL:  # Use the enum comparison
                    line_y = self.canvas_height - (self.margin + line.distance * self.scale)
                    if abs(new_y1 - line_y) < 8 or abs(new_y1 + height - line_y) < 8 or abs(new_y1 + height/2 - line_y) < 8:
                        # Find the canvas line item for this snap line
                        items = self.canvas.find_withtag("snap_line")
                        for item in items:
                            coords = self.canvas.coords(item)
                            if len(coords) == 4 and abs(coords[1] - line_y) < 1:  # Check y-coordinate matches
                                self.canvas.itemconfig(item, width=3, fill="green")
                                break
                else:  # vertical
                    line_x = self.margin + line.distance * self.scale
                    if abs(new_x1 - line_x) < 8 or abs(new_x1 + width - line_x) < 8 or abs(new_x1 + width/2 - line_x) < 8:
                        items = self.canvas.find_withtag("snap_line")
                        for item in items:
                            coords = self.canvas.coords(item)
                            if len(coords) == 4 and abs(coords[0] - line_x) < 1:  # Check x-coordinate matches
                                self.canvas.itemconfig(item, width=3, fill="green")
                                break
        else:
            # Normal appearance when not snapped
            self.canvas.itemconfig(item_id, outline="black", width=2)
            self.canvas.itemconfig("snap_line", width=1, fill="blue")  # Reset snap lines
        
        # Move the artwork
        self.canvas.coords(item_id, new_x1, new_y1, new_x1 + width, new_y1 + height)
        
        # Move associated text
        for item in self.draggable_items:
            if item['id'] == item_id:
                self.canvas.coords(
                    item['text_id'],
                    new_x1 + width/2,
                    new_y1 + height/2
                )
                break

    
    def on_drop(self, event, item_id):
        """Handle drop event with snapping to lines"""
        # Find the draggable item
        for item in self.draggable_items:
            if item['id'] == item_id:
                # Calculate new position in inches
                coords = self.canvas.coords(item_id)
                wall_left = self.margin
                wall_bottom = self.margin
                
                item['x'] = (coords[0] - wall_left) / self.scale
                item['y'] = (self.canvas_height - coords[3] - wall_bottom) / self.scale
                
                # Snap to nearby lines
                item['x'], item['y'] = self.snap_to_lines(
                    item['x'], item['y'],
                    item['artwork'].width,
                    item['artwork'].height
                )
                
                # Enforce boundaries
                item['x'], item['y'] = self.enforce_boundaries(
                    item['x'], item['y'],
                    item['artwork'].width,
                    item['artwork'].height
                )
                
                # Update position
                self.move_item_to_position(item)
                break
    
    def enforce_boundaries(self, x, y, width, height):
        """Ensure artwork stays within wall boundaries"""
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + width > self.selected_wall.width:
            x = self.selected_wall.width - width
        if y + height > self.selected_wall.height:
            y = self.selected_wall.height - height
        return x, y
    
    def snap_to_lines(self, x, y, width, height, threshold_pixels=8):
        """Snap artwork to nearby snap lines with pixel-based threshold"""
        # Convert artwork position and dimensions to canvas pixels
        x_px = x * self.scale
        y_px = y * self.scale
        width_px = width * self.scale
        height_px = height * self.scale

        for line in self.snap_lines:
            if not line.snap_to:
                continue

            if line.orientation == Orientation.HORIZONTAL:  # Enum comparison
                target_y_px = line.distance * self.scale

                if line.alignment == HorizontalAlignment.TOP:  # Enum comparison
                    candidate_y_px = target_y_px - height_px
                    if abs(y_px + height_px - target_y_px) < threshold_pixels:
                        y = (candidate_y_px) / self.scale
                elif line.alignment == HorizontalAlignment.CENTER:  # Enum comparison
                    candidate_y_px = target_y_px - height_px / 2
                    if abs(y_px + height_px / 2 - target_y_px) < threshold_pixels:
                        y = (candidate_y_px) / self.scale
                elif line.alignment == HorizontalAlignment.BOTTOM:  # Enum comparison
                    candidate_y_px = target_y_px
                    if abs(y_px - target_y_px) < threshold_pixels:
                        y = (candidate_y_px) / self.scale

            else:  # vertical
                target_x_px = line.distance * self.scale

                if line.alignment == VerticalAlignment.LEFT:  # Enum comparison
                    candidate_x_px = target_x_px
                    if abs(x_px - target_x_px) < threshold_pixels:
                        x = (candidate_x_px) / self.scale
                elif line.alignment == VerticalAlignment.CENTER:  # Enum comparison
                    candidate_x_px = target_x_px - width_px / 2
                    if abs(x_px + width_px / 2 - target_x_px) < threshold_pixels:
                        x = (candidate_x_px) / self.scale
                elif line.alignment == VerticalAlignment.RIGHT:  # Enum comparison
                    candidate_x_px = target_x_px - width_px
                    if abs(x_px + width_px - target_x_px) < threshold_pixels:
                        x = (candidate_x_px) / self.scale

        return x, y

    
    def move_item_to_position(self, item):
        """Move artwork to its current position"""
        wall_left = self.margin
        wall_bottom = self.margin
        
        x1 = wall_left + item['x'] * self.scale
        y1 = self.canvas_height - (wall_bottom + (item['y'] + item['artwork'].height) * self.scale)
        x2 = wall_left + (item['x'] + item['artwork'].width) * self.scale
        y2 = self.canvas_height - (wall_bottom + item['y'] * self.scale)
        
        self.canvas.coords(item['id'], x1, y1, x2, y2)
        self.canvas.coords(
            item['text_id'],
            x1 + item['artwork'].width * self.scale / 2,
            y1 + item['artwork'].height * self.scale / 2
        )
    
    def check_collisions(self):
        """Check for collisions between artworks"""
        colliding = set()
        
        for i in range(len(self.draggable_items)):
            for j in range(i + 1, len(self.draggable_items)):
                if self.rectangles_overlap(
                    self.draggable_items[i],
                    self.draggable_items[j]
                ):
                    colliding.add(i)
                    colliding.add(j)
        
        # Update visual indication
        for i, item in enumerate(self.draggable_items):
            self.canvas.itemconfig(
                item['id'], 
                outline="red" if i in colliding else "black"
            )
        
        return len(colliding) > 0
    
    def rectangles_overlap(self, item1, item2):
        """Check if two artworks overlap"""
        ax1, ay1 = item1['x'], item1['y']
        ax2, ay2 = ax1 + item1['artwork'].width, ay1 + item1['artwork'].height
        bx1, by1 = item2['x'], item2['y']
        bx2, by2 = bx1 + item2['artwork'].width, by1 + item2['artwork'].height
        
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
    
    def save_layout(self):
        """Save the current layout to a file"""
        if self.check_collisions():
            self.show_collision_warning()
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            title="Save Layout",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        with open(filename, "w") as f:
            f.write(f"Wall Name: {self.selected_wall.name}\n")
            f.write(f"Wall Width: {self.selected_wall.width}\"\n")
            f.write(f"Wall Height: {self.selected_wall.height}\"\n\n")
            
            for item in self.draggable_items:
                artwork = item['artwork']
                center_x = item['x'] + artwork.width / 2
                center_y = item['y'] + artwork.height / 2
                
                f.write(
                    f"Artwork: {artwork.name}, "
                    f"Size: {artwork.width}\" x {artwork.height}\", "
                    f"Position: ({item['x']:.1f}, {item['y']:.1f}), "
                    f"Center: ({center_x:.1f}, {center_y:.1f})\n"
                )
        
        messagebox.showinfo("Saved", f"Layout saved to {filename}")
    
    def show_collision_warning(self):
        """Show warning when collisions are detected"""
        popup = Toplevel(self.parent)
        popup.title("Collision Detected")
        
        ttk.Label(
            popup, 
            text="Some artworks are overlapping.\nWould you like to save anyway?"
        ).pack(padx=20, pady=10)
        
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="Continue Editing",
            command=popup.destroy
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Save Anyway",
            command=lambda: [popup.destroy(), self.save_layout()]
        ).pack(side="left", padx=5)
