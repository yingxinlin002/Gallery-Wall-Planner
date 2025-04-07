import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
import os
from gallery_wall_planner.gui.popup_editor import open_popup_editor
from gallery_wall_planner.gui.ui_styles import (
    init_styles,
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from gallery_wall_planner.gui.OrganizeArt import launch_organize_art_ui
from gallery_wall_planner.models.project_exporter import export_project
from gallery_wall_planner.gui.SelectWallSpaceUI import SelectWallSpaceUI

# -------------------------
# Function: Enforce Boundaries
# -------------------------
def enforce_boundaries(x, y, width, height, wall_width, wall_height):
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + width > wall_width:
        x = wall_width - width
    if y + height > wall_height:
        y = wall_height - height
    return x, y

# -------------------------
# Main Entry Point for Embedding
# -------------------------
def launch_lock_objects_ui(root, wall):
    init_styles(root)
    root.title("Place fixtures")

    global wall_name, wall_width, wall_height, wall_color
    global obstacle_names, layout_items, popup_windows, items

    wall_name = wall.name
    wall_width = wall.width
    wall_height = wall.height
    wall_color = wall.color

    # Get permanent objects from wall
    permanent_objects = wall.get_permanent_objects()
    obstacle_names = [f"Obstacle{i+1}" for i in range(len(permanent_objects))]
    layout_items = {}
    popup_windows = {}
    items = []

    for widget in root.winfo_children():
        widget.destroy()

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(main_frame)
    header_frame.pack(side="top", fill="x", padx=10, pady=10)

    title_label = ttk.Label(header_frame, text="Place fixtures")
    apply_header_label_style(title_label)
    title_label.pack(side="left")

    buttons_frame = ttk.Frame(header_frame)
    buttons_frame.pack(side="left", padx=20)
    item_buttons = {}

    # Make canvas non-expanding to free space below
    canvas_frame = ttk.Frame(main_frame)
    canvas_frame.pack(side="top", fill="both", expand=True)

    canvas_width = 800
    canvas_height = 350
    canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height)
    apply_canvas_style(canvas)
    canvas.pack(padx=10, pady=10)

    margin = 50
    scale = min((canvas_width - 2*margin) / wall_width, (canvas_height - 2*margin) / wall_height)
    wall_left = margin
    wall_bottom = margin
    wall_right = wall_left + wall_width * scale
    wall_top = wall_bottom + wall_height * scale

    # Draw wall background
    canvas.create_rectangle(wall_left, canvas_height - wall_bottom - wall_height*scale,
                      wall_right, canvas_height - wall_bottom,
                      fill=wall_color, outline="black", width=2)

    # Add coordinate indicators
    canvas.create_text(wall_left - 10, canvas_height - wall_bottom + 5, text="0", anchor="e")
    canvas.create_text(wall_left - 10, canvas_height - wall_bottom - wall_height*scale - 5,
                    text=f"{wall_height}\"", anchor="e")
    canvas.create_text(wall_left + 5, canvas_height - wall_bottom + 15, text="0", anchor="n")
    canvas.create_text(wall_right - 5, canvas_height - wall_bottom + 15, text=f"{wall_width}\"", anchor="n")

    def show_item_popup(item_index):
        # Get the permanent object and its position
        permanent_object, position = permanent_objects[item_index]

        # Prepare the item data as a dictionary that popup_editor expects
        item_data = {
            "Name": permanent_object.name,  # Using the object's actual name
            "Width": permanent_object.width,
            "Height": permanent_object.height,
            "x": position["x"] if position else 0.0,
            "y": position["y"] if position else 0.0
        }

        open_popup_editor(
            root=root,
            item_index=item_index,
            item_data=item_data,  # Pass the prepared dictionary
            obstacles=[(obj.name, obj.width, obj.height) for obj, _ in permanent_objects],
            obstacle_names=obstacle_names,
            layout_items=layout_items,
            items=items,
            item_buttons=item_buttons,
            canvas=canvas,
            scale=scale,
            wall_left=wall_left,
            wall_bottom=wall_bottom,
            canvas_height=canvas_height,
            move_item_to_canvas=move_item_to_canvas,
            check_all_collisions=check_all_collisions,
            enforce_boundaries=lambda x, y, w, h: enforce_boundaries(x, y, w, h, wall_width, wall_height),
            popup_windows=popup_windows,
        )

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

    def move_item_to_canvas(item_index):
        item = items[item_index]
        x1 = wall_left + item.x * scale
        y1 = canvas_height - (wall_bottom + item.y * scale)  # Changed from (y + height)
        x2 = wall_left + (item.x + item.width) * scale
        y2 = canvas_height - (wall_bottom + (item.y + item.height) * scale)  # Changed from just y
        canvas.coords(item.id, x1, y1, x2, y2)

    def check_all_collisions():
        n = len(items)
        colliding = set()
        for i in range(n):
            for j in range(i+1, n):
                if rectangles_overlap(items[i], items[j]):
                    colliding.add(i)
                    colliding.add(j)
        for i, item in enumerate(items):
            canvas.itemconfig(item.id, outline="red" if i in colliding else "black")
        return len(colliding) > 0

    def rectangles_overlap(item1, item2):
        ax1, ay1 = item1.x, item1.y
        ax2, ay2 = item1.x + item1.width, item1.y + item1.height
        bx1, by1 = item2.x, item2.y
        bx2, by2 = item2.x + item2.width, item2.y + item2.height
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

    # Create draggable items for each permanent object
    buttons_per_row = 4
    for i, (obj, pos) in enumerate(permanent_objects):
        # Initialize position in layout_items
        layout_items[obstacle_names[i]] = pos if pos else {"x": 0.0, "y": 0.0}

        # Create draggable item
        di = DraggableItem(
            index=i,
            permanent_object=(obj, pos),
            move_item_to_canvas=move_item_to_canvas,
            check_all_collisions=check_all_collisions
        )
        items.append(di)

        # Create button for this item
        row = i // buttons_per_row
        col = i % buttons_per_row
        btn = ttk.Button(buttons_frame,
                        text=obj.name,
                        command=lambda idx=i: show_item_popup(idx))
        apply_primary_button_style(btn)
        btn.grid(row=row, column=col, padx=5, pady=5)  # Use grid layout for buttons
        item_buttons[i] = btn

    def save_and_continue():
        if check_all_collisions():
            popup = Toplevel(root)
            popup.title("Collision Detected")
            ttk.Label(popup, text="The program has identified an impossible layout. Would you like to keep editing?").pack(padx=10, pady=10)
            btn_frame = ttk.Frame(popup)
            btn_frame.pack(pady=10)
            btn_edit = ttk.Button(btn_frame, text="Keep Editing", command=popup.destroy)
            btn_save = ttk.Button(btn_frame, text="Continue Anyway", command=lambda: (popup.destroy(), continue_to_next()))
            apply_primary_button_style(btn_edit)
            apply_primary_button_style(btn_save)
            btn_edit.pack(side="left", padx=5)
            btn_save.pack(side="left", padx=5)
        else:
            continue_to_next()

    def continue_to_next():
        # Positions are already saved in the wall object through the DraggableItem class
        # Now just launch the SelectWallSpaceUI with the updated wall
        SelectWallSpaceUI(root, wall)

    def export_then_continue():
        file_path = filedialog.asksaveasfilename(defaultextension=".json", title="Save Project")
        if not file_path:
            return  # User cancelled

        # Export the wall with updated permanent object positions
        export_project(file_path, wall)
        SelectWallSpaceUI(root, file_path)

    def return_to_home():
        print("Returning to Home...")
        root.quit()

    # Bottom buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(side="bottom", fill="x", pady=10)

    back_to_home_button = ttk.Button(button_frame, text="< Back to Home", command=lambda: return_to_home(), width=15)
    apply_primary_button_style(back_to_home_button)
    back_to_home_button.pack(side="left", padx=10)

    next_button = ttk.Button(button_frame, text="Save and Next >", command=save_and_continue)
    apply_primary_button_style(next_button)
    next_button.pack(side="right", padx=10)