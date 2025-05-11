import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
import os
from gallery_wall_planner.models.wall_line import SingleLine, Orientation, HorizontalAlignment, VerticalAlignment
from gallery_wall_planner.gui.popup_editor import open_popup_editor
from gallery_wall_planner.gui.ui_styles import (
    init_styles,
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from gallery_wall_planner.gui.snap_line_popup import open_snap_line_popup
from gallery_wall_planner.utils.measurement_lines import MeasurementLinesManager

class VirtualWall:
    def __init__(self, parent_frame, selected_wall, artworks=None, on_drag_callback=None):
        self.parent = parent_frame
        self.selected_wall = selected_wall
        self.artworks = artworks if artworks else []
        self.items = []
        self.on_drag_callback = on_drag_callback
        
        self.wall_name = selected_wall.name
        self.wall_width = selected_wall.width
        self.wall_height = selected_wall.height
        self.wall_color = getattr(selected_wall, "color", "#f5f5f5")
        self.snap_lines = []
        self.measurement_lines = []
        self.measurement_texts = []
        for line in getattr(selected_wall, 'wall_lines', []):
            if isinstance(line.alignment, str):
                if line.orientation == Orientation.HORIZONTAL:
                    line.alignment = HorizontalAlignment[line.alignment.upper()]
                else:
                    line.alignment = VerticalAlignment[line.alignment.upper()]
            elif line.alignment is None:
                line.alignment = (
                    HorizontalAlignment.CENTER if line.orientation == Orientation.HORIZONTAL
                    else VerticalAlignment.CENTER
                )

        self.layout_items = {}
        self.popup_windows = {}
        self.items = []

        self.margin = 50
        self.canvas_width = 800
        self.canvas_height = 600
        self.scale = min(
            (self.canvas_width - 2*self.margin) / self.wall_width,
            (self.canvas_height - 2*self.margin) / self.wall_height
        )

        self.wall_left = self.margin
        self.wall_bottom = self.margin
        self.wall_right = self.wall_left + self.wall_width * self.scale
        self.wall_top = self.wall_bottom + self.wall_height * self.scale

        self.build_ui()

    def get_alignment_string(self, line):
        print(f"[DEBUG] line.orientation={line.orientation}, line.alignment={line.alignment}, type={type(line.alignment)}")
        if line.orientation == Orientation.HORIZONTAL:
            return line.alignment.value.capitalize() if isinstance(line.alignment, HorizontalAlignment) else "Unknown"
        elif line.orientation == Orientation.VERTICAL:
            return line.alignment.value.capitalize() if isinstance(line.alignment, VerticalAlignment) else "Unknown"
        return "Unknown"

    def check_collision_with_permanent_objects(self, x, y, width, height):
        """Check if artwork would collide with permanent objects"""
        if not hasattr(self.selected_wall, 'permanent_objects'):
            return False

        for obj in self.selected_wall.permanent_objects:
            pos = obj.position
            obj_x1 = pos['x']
            obj_y1 = pos['y']
            obj_x2 = obj_x1 + obj.width
            obj_y2 = obj_y1 + obj.height

            if not (x + width <= obj_x1 or obj_x2 <= x or y + height <= obj_y1 or obj_y2 <= y):
                return True

        return False

    def build_ui(self):
        init_styles(self.parent)
        for widget in self.parent.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)

        title_label = ttk.Label(header_frame, text="Organize Art")
        apply_header_label_style(title_label)
        title_label.pack(side="left")

        self.buttons_frame = ttk.Frame(header_frame)
        self.buttons_frame.pack(side="left", padx=20)
        self.item_buttons = {}

        self.canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height)
        apply_canvas_style(self.canvas)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        snap_button_frame = ttk.Frame(main_frame)
        snap_button_frame.pack(fill="x", padx=10, pady=(0, 10))

        add_line_btn = ttk.Button(snap_button_frame, text="Add Snap Line", command=self.add_new_snap_line)
        apply_primary_button_style(add_line_btn)
        add_line_btn.pack(side="left", padx=5)

        edit_line_btn = ttk.Button(snap_button_frame, text="Move/Delete Line", command=self.open_manage_lines_popup)
        apply_primary_button_style(edit_line_btn)
        edit_line_btn.pack(side="left", padx=5)

        self.canvas.create_rectangle(
            self.wall_left, self.canvas_height - self.wall_top,
            self.wall_right, self.canvas_height - self.wall_bottom,
            fill=self.wall_color, outline="black", width=2
        )

        if not self.snap_lines:
            default_snap_line = SingleLine(
                orientation=Orientation.HORIZONTAL,
                alignment=HorizontalAlignment.CENTER,
                distance=60.0,
                snap_to=True,
                moveable=True
            )
            self.snap_lines.append(default_snap_line)

        self.draw_snap_lines()

        if hasattr(self.selected_wall, 'permanent_objects'):
            for obj in self.selected_wall.permanent_objects:
                self.create_fixed_item(obj, obj.position)

        if hasattr(self.selected_wall, 'artwork'):
            for artwork in self.selected_wall.artwork:
                key = artwork.name if artwork.name else f"Art{len(self.items)+1}"
                if key in self.layout_items:
                    continue  # Skip if already added

                index = len(self.items)
                x = getattr(artwork, "x", 0.0)
                y = getattr(artwork, "y", 0.0)
                self.layout_items[key] = {"x": x, "y": y}
                art_data = {
                    "Name": artwork.name,
                    "Width": artwork.width,
                    "Height": artwork.height,
                    "Image": False,
                    "Hang": getattr(artwork, "hang_height", 0.0)
                }
                draggable = self.DraggableArt(index, art_data, self)
                self.snap_to_lines(draggable)
                self.items.append(draggable)
                self.move_item_to_canvas(index)

                # Create button for each loaded artwork
                btn = ttk.Button(self.buttons_frame, text=key, command=lambda idx=index: self.show_item_popup(idx))
                apply_primary_button_style(btn)
                btn.pack(side="left", padx=3)
                self.item_buttons[index] = btn


    def create_fixed_item(self, obj, pos):
        x1 = self.wall_left + pos.x * self.scale
        y1 = self.canvas_height - (self.wall_bottom + (pos.y + obj.height) * self.scale)
        x2 = self.wall_left + (pos.x + obj.width) * self.scale
        y2 = self.canvas_height - (self.wall_bottom + pos.y * self.scale)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#999999", outline="black", width=2)

    def enforce_boundaries(self, x, y, width, height):
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + width > self.wall_width:
            x = self.wall_width - width
        if y + height > self.wall_height:
            y = self.wall_height - height
        return x, y

    def draw_snap_lines(self):
        self.canvas.delete("snap_line")
        for line in self.snap_lines:
            if line.orientation == Orientation.HORIZONTAL:
                y = self.canvas_height - (self.wall_bottom + line.distance * self.scale)
                self.canvas.create_line(
                    self.wall_left, y,
                    self.wall_right, y,
                    fill="blue", dash=(4, 2), width=2, tags="snap_line"
                )
            elif line.orientation == Orientation.VERTICAL:
                x = self.wall_left + line.distance * self.scale
                self.canvas.create_line(
                    x, self.canvas_height - self.wall_top,
                    x, self.canvas_height - self.wall_bottom,
                    fill="blue", dash=(4, 2), width=2, tags="snap_line"
                )

    def redraw_snap_lines(self):
        self.draw_snap_lines()

    def add_new_snap_line(self):
        def handle_save(new_line):
            print(f"[DEBUG] Saving Snap Line line.orientation={new_line.orientation}, line.alignment={new_line.alignment}, type={type(new_line.alignment)}")
            for existing in self.snap_lines:
                if (existing.orientation == new_line.orientation and abs(existing.distance - new_line.distance) < 0.05):
                    self.show_duplicate_line_popup(new_line)
                    return
            self.snap_lines.append(new_line)
            self.selected_wall.wall_lines = self.snap_lines
            self.draw_snap_lines()

        open_snap_line_popup(
            self.parent,
            handle_save,
            wall_width=self.wall_width,
            wall_height=self.wall_height
        )

    def show_duplicate_line_popup(self, new_line):
        popup = Toplevel(self.parent)
        popup.title("Line Already Exists")

        ttk.Label(
            popup,
            text="A snap line at this location already exists.\nWould you like to add it anyway?"
        ).pack(padx=20, pady=(15, 10))

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)
        ttk.Button(
            btn_frame,
            text="Add Anyway",
            command=lambda: [self.snap_lines.append(new_line), self.draw_snap_lines(), popup.destroy()]
        ).pack(side="left", padx=5)

    def open_manage_lines_popup(self):
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
            line_frame = ttk.Frame(frame)
            line_frame.pack(fill="x", pady=5, padx=10)

            orientation_str = line.orientation.value.capitalize() if isinstance(line.orientation, Orientation) else "Unknown"
            alignment_str = self.get_alignment_string(line)
            label_text = f"{orientation_str} - {alignment_str} - {line.distance:.3f}\""
            ttk.Label(line_frame, text=label_text).pack(side="left")

            ttk.Button(
                line_frame,
                text="Edit",
                command=lambda i=idx: self.edit_snap_line(i, popup)
            ).pack(side="right", padx=5)

            ttk.Button(
                line_frame,
                text="Delete",
                command=lambda i=idx: self.delete_snap_line(i, popup)
            ).pack(side="right", padx=5)

    def edit_snap_line(self, index, popup):
        def handle_save(updated_line):
            self.snap_lines[index] = updated_line
            self.draw_snap_lines()
            popup.destroy()

        existing_line = self.snap_lines[index]

        # Fallback defaults if fields are missing
        if existing_line.orientation is None:
            existing_line.orientation = Orientation.HORIZONTAL
        if existing_line.alignment is None:
            if existing_line.orientation == Orientation.HORIZONTAL:
                existing_line.alignment = HorizontalAlignment.CENTER
            else:
                existing_line.alignment = VerticalAlignment.CENTER

        open_snap_line_popup(
            self.parent,
            handle_save,
            existing_line=existing_line,
            wall_width=self.wall_width,
            wall_height=self.wall_height
        )

    def delete_snap_line(self, index, popup):
        del self.snap_lines[index]
        self.draw_snap_lines()
        popup.destroy()
            
    def add_artwork(self, artwork):
        """
        Add an artwork object to the canvas with highlighting support.
        Handles both the standard Artwork model and maintains backward compatibility.
        """
        # Add to artworks list if it exists (from first version)
        if hasattr(self, 'artworks'):
            self.artworks.append(artwork)
        
        # Create the draggable artwork item (combining both approaches)
        index = len(self.items)
        name = artwork.name or f"Art{index+1}"
        
        # Prevent double-add if already exists
        if name in self.layout_items:
            return
        
        # Create art data structure
        art_data = {
            "Name": name,
            "Width": artwork.width,
            "Height": artwork.height,
            "Image": False,
            "Hang": getattr(artwork, "hang_height", 0.0)
        }
        
        # Create draggable artwork
        draggable = self.DraggableArt(index, art_data, self)
        self.items.append(draggable)

        # Initialize UI elements if they don't exist
        if not hasattr(self, 'item_buttons'):
            self.item_buttons = {}

        if not hasattr(self, 'buttons_frame') or not self.buttons_frame.winfo_exists():
            for child in self.parent.winfo_children():
                if isinstance(child, ttk.Frame) and 'buttons' in str(child).lower():
                    self.buttons_frame = child
                    break
            else:
                self.buttons_frame = ttk.Frame(self.parent)
                self.buttons_frame.pack(side="top", padx=20, pady=5)

        # Add control button for the artwork
        btn = ttk.Button(self.buttons_frame, text=name, command=lambda idx=index: self.show_item_popup(idx))
        apply_primary_button_style(btn)
        btn.pack(side="left", padx=3)
        self.item_buttons[index] = btn

        # Check for highlighting if this is the selected artwork
        if hasattr(self.parent.master, 'editor_artwork_selected'):
            if artwork == self.parent.master.editor_artwork_selected:
                self.canvas.itemconfig(draggable.id, outline="#800080", width=4)

        # Position and validate the artwork
        self.snap_to_lines(draggable)
        self.move_item_to_canvas(index)
        self.check_all_collisions()
        
        # Update layout items
        self.layout_items[name] = {"x": draggable.x, "y": draggable.y}

    def rectangles_overlap(self, item1, item2):
        ax1, ay1 = item1.x, item1.y
        ax2, ay2 = ax1 + item1.width, ay1 + item1.height
        bx1, by1 = item2.x, item2.y
        bx2, by2 = bx1 + item2.width, by1 + item2.height
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

    def check_all_collisions(self):
        n = len(self.items)
        colliding = set()
        for i in range(n):
            for j in range(i + 1, n):
                if self.rectangles_overlap(self.items[i], self.items[j]):
                    colliding.add(i)
                    colliding.add(j)

            # Check against permanent objects
            x_in = self.items[i].x
            y_in = self.items[i].y
            w = self.items[i].width
            h = self.items[i].height
            if self.check_collision_with_permanent_objects(x_in, y_in, w, h):
                colliding.add(i)

        for i, item in enumerate(self.items):
            self.canvas.itemconfig(item.id, outline="red" if i in colliding else "black")
        return len(colliding) > 0

    def move_item_to_canvas(self, item_index):
        item = self.items[item_index]
        x1 = self.wall_left + item.x * self.scale
        y1 = self.canvas_height - (self.wall_bottom + (item.y + item.height) * self.scale)
        x2 = self.wall_left + (item.x + item.width) * self.scale
        y2 = self.canvas_height - (self.wall_bottom + item.y * self.scale)
        self.canvas.coords(item.id, x1, y1, x2, y2)

    def snap_to_lines(self, art, threshold=8):
        print("Evaluating snapping...")
        print(f"Art position BEFORE snapping: x={art.x:.3f}, y={art.y:.3f}")

        for line in self.snap_lines:
            if not line.snap_to:
                continue

            alignment_str = self.get_alignment_string(line)

            if line.orientation == Orientation.HORIZONTAL:
                target_y = line.distance
                if isinstance(line.alignment, HorizontalAlignment):
                    if line.alignment == HorizontalAlignment.TOP:
                        candidate_y = target_y - art.height
                    elif line.alignment == HorizontalAlignment.CENTER:
                        candidate_y = target_y - art.height / 2
                    elif line.alignment == HorizontalAlignment.BOTTOM:
                        candidate_y = target_y
                    else:
                        continue

                    print(f"Checking snap to HORIZONTAL-{alignment_str} at target_y={target_y}")
                    if abs(art.y + art.height - target_y) < threshold or abs(art.y - candidate_y) < threshold:
                        print(f"Snap check: Art y={art.y:.3f}, candidate_y={candidate_y:.3f}, threshold={threshold}")
                        art.y = candidate_y

            elif line.orientation == Orientation.VERTICAL:
                target_x = line.distance
                if isinstance(line.alignment, VerticalAlignment):
                    if line.alignment == VerticalAlignment.LEFT:
                        candidate_x = target_x
                    elif line.alignment == VerticalAlignment.CENTER:
                        candidate_x = target_x - art.width / 2
                    elif line.alignment == VerticalAlignment.RIGHT:
                        candidate_x = target_x - art.width
                    else:
                        continue

                    print(f"Checking snap to VERTICAL-{alignment_str} at target_x={target_x}")
                    if abs(art.x - candidate_x) < threshold or abs(art.x + art.width - target_x) < threshold:
                        print(f"Snap check: Art x={art.x:.3f}, candidate_x={candidate_x:.3f}, threshold={threshold}")
                        art.x = candidate_x



    def show_item_popup(self, item_index):
        item = self.items[item_index]
        item_data = {
            "Name": item.name,
            "x": item.x,
            "y": item.y,
            "Width": item.width,
            "Height": item.height
        }

        open_popup_editor(
            root=self.parent,
            item_index=item_index,
            item_data=item_data,
            obstacles=[],
            obstacle_names=[],
            layout_items=self.layout_items,
            items=self.items,
            item_buttons=self.item_buttons,
            canvas=self.canvas,
            scale=self.scale,
            wall_left=self.wall_left,
            wall_bottom=self.wall_bottom,
            canvas_height=self.canvas_height,
            move_item_to_canvas=self.move_item_to_canvas,
            check_all_collisions=self.check_all_collisions,
            enforce_boundaries=self.enforce_boundaries,
            popup_windows=self.popup_windows,
        )

    class DraggableArt:
        def __init__(self, index, art_data, wall_ref):
            self.index = index
            self.art_data = art_data
            self.name = art_data.get("Name", f"Art{index+1}")

            pos = wall_ref.layout_items.get(self.name, {"x": 0.0, "y": 0.0})
            self.x = float(pos.get("x", 0.0))  # Ensure float conversion
            self.y = float(pos.get("y", 0.0))  # Ensure float conversion
            
            self.width = art_data.get("Width", 0.0)  # Default to 0.0 if missing
            self.height = art_data.get("Height", 0.0)  # Default to 0.0 if missing
            self.id = None
            self.update_popup_fields = None
            self.wall_ref = wall_ref

            # Initialize measurement lines manager
            self.measurement_manager = MeasurementLinesManager(wall_ref.canvas, wall_ref)

            self.create_canvas_item()

        def create_canvas_item(self):
            x1 = self.wall_ref.wall_left + self.x * self.wall_ref.scale
            y1 = self.wall_ref.canvas_height - (self.wall_ref.wall_bottom + (self.y + self.height) * self.wall_ref.scale)
            x2 = self.wall_ref.wall_left + (self.x + self.width) * self.wall_ref.scale
            y2 = self.wall_ref.canvas_height - (self.wall_ref.wall_bottom + self.y * self.wall_ref.scale)
            self.id = self.wall_ref.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=2)
            self.wall_ref.canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_start)
            self.wall_ref.canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
            self.wall_ref.canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_drop)

        def on_start(self, event):
            self._drag_data = {"x": event.x, "y": event.y}

        def on_drag(self, event):
            """Handle dragging event with measurement lines."""
            # Calculate movement delta
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]

            # Move the canvas item
            self.wall_ref.canvas.move(self.id, dx, dy)

            # Update drag reference point
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

            # Get current coordinates and dimensions
            coords = self.wall_ref.canvas.coords(self.id)
            x1 = (coords[0] - self.wall_ref.wall_left) / self.wall_ref.scale
            y1 = (self.wall_ref.canvas_height - coords[3] - self.wall_ref.wall_bottom) / self.wall_ref.scale
            x2 = (coords[2] - self.wall_ref.wall_left) / self.wall_ref.scale
            y2 = (self.wall_ref.canvas_height - coords[1] - self.wall_ref.wall_bottom) / self.wall_ref.scale

            # Draw new measurement lines and distances
            self.measurement_manager.draw_measurement_lines(x1, y1, x2, y2)

            # Temporary boundary check during drag
            if x1 < 0 or x2 > self.wall_ref.wall_width or y1 < 0 or y2 > self.wall_ref.wall_height:
                self.wall_ref.canvas.itemconfig(self.id, outline="orange")
            else:
                self.wall_ref.canvas.itemconfig(self.id, outline="black")

        def on_drop(self, event):
            # Clear measurement lines on drop
            self.measurement_manager.clear_measurement_lines()
            coords = self.wall_ref.canvas.coords(self.id)
            new_x = (coords[0] - self.wall_ref.wall_left) / self.wall_ref.scale  # Use self.wall_ref.scale
            new_y = (self.wall_ref.canvas_height - coords[3] - self.wall_ref.wall_bottom) / self.wall_ref.scale  # Use self.wall_ref.scale
            # Initial boundary enforcement
            new_x, new_y = self.wall_ref.enforce_boundaries(new_x, new_y, self.width, self.height)
            self.x = new_x
            self.y = new_y
            # Snap to nearby lines
            self.wall_ref.snap_to_lines(self)
            # Enforce boundaries again after snapping
            self.x, self.y = self.wall_ref.enforce_boundaries(self.x, self.y, self.width, self.height)
            # Update canvas BEFORE layout_items
            self.wall_ref.move_item_to_canvas(self.index)
            # Update layout memory and collision check
            self.wall_ref.layout_items[self.name] = {"x": self.x, "y": self.y}

            # Also write back to the original artwork object if it exists
            for art in getattr(self.wall_ref.selected_wall, "artwork", []):
                if art.name == self.name:
                    art.x = self.x
                    art.y = self.y
                    break

            self.wall_ref.check_all_collisions()
            if self.update_popup_fields and self.index in self.wall_ref.popup_windows and self.wall_ref.popup_windows[self.index].winfo_exists():
                self.update_popup_fields()