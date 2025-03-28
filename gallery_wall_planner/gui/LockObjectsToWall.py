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
def enforce_boundaries(x, y, width, height):
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
def launch_lock_objects_ui(root, permanent_objects, wall):
    print("imediate~~~~PERMANENT OBJECTS RECEIVED:", permanent_objects)
    init_styles(root)
    root.title("Place fixtures")

    global wall_name, wall_width, wall_height, wall_color
    global obstacles, obstacle_names, layout_items, popup_windows, items

    wall_name = wall.name
    wall_width = wall.width
    wall_height = wall.height
    wall_color = wall.color

    obstacles = []

    for obj in permanent_objects:
        obstacles.append({
            "Name": obj["name"],
            "Width": obj["width"],
            "Height": obj["height"],
            "Image": obj.get("image", False) or False
        })

    obstacle_names = [f"Obstacle{i+1}" for i in range(len(obstacles))]
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
    canvas_height = 500   # Reduced from 600
    canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height)
    apply_canvas_style(canvas)
    canvas.pack(padx=10, pady=10)

    margin = 50
    scale = min((canvas_width - 2*margin) / wall_width, (canvas_height - 2*margin) / wall_height)
    wall_left = margin
    wall_bottom = margin
    wall_right = wall_left + wall_width * scale
    wall_top = wall_bottom + wall_height * scale

    canvas.create_rectangle(wall_left, canvas_height - wall_top,
                            wall_right, canvas_height - wall_bottom,
                            fill=wall_color, outline="black", width=2)

    def show_item_popup(item_index):
        open_popup_editor(
            root=root,
            item_index=item_index,
            obstacles=obstacles,
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
            enforce_boundaries=enforce_boundaries,
            popup_windows=popup_windows,
        )

    class DraggableItem:
        def __init__(self, index, obstacle, move_item_to_canvas, check_all_collisions):
            self.index = index
            self.obstacle = obstacle
            self.name = obstacle_names[index]
            pos = layout_items.get(self.name, {"x": 0.0, "y": 0.0})
            self.x = pos["x"]
            self.y = pos["y"]
            self.width = obstacle["Width"]
            self.height = obstacle["Height"]
            self.id = None
            self.create_canvas_item()
            self._drag_data = {"x": 0, "y": 0}
            self.update_popup_fields = None
            self.move_item_to_canvas = move_item_to_canvas
            self.check_all_collisions = check_all_collisions

        def create_canvas_item(self):
            x1 = wall_left + self.x * scale
            y1 = canvas_height - (wall_bottom + (self.y + self.height) * scale)
            x2 = wall_left + (self.x + self.width) * scale
            y2 = canvas_height - (wall_bottom + self.y * scale)
            self.id = canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=2)
            canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_start)
            canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
            canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_drop)

        def on_start(self, event):
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

        def on_drag(self, event):
            dx = event.x - self._drag_data["x"]
            dy = event.y - self._drag_data["y"]
            canvas.move(self.id, dx, dy)
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y

        def on_drop(self, event):
            coords = canvas.coords(self.id)
            new_x = (coords[0] - wall_left) / scale
            new_y = (canvas_height - coords[3] - wall_bottom) / scale
            new_x, new_y = enforce_boundaries(new_x, new_y, self.width, self.height)
            self.x = new_x
            self.y = new_y
            layout_items[self.name] = {"x": self.x, "y": self.y}
            move_item_to_canvas(self.index)
            self.check_all_collisions()
            if self.update_popup_fields and self.index in popup_windows and popup_windows[self.index].winfo_exists():
                print(f"[DEBUG] Calling update_popup_fields for {self.name}")
                self.update_popup_fields()

    def move_item_to_canvas(item_index):
        item = items[item_index]
        x1 = wall_left + item.x * scale
        y1 = canvas_height - (wall_bottom + (item.y + item.height) * scale)
        x2 = wall_left + (item.x + item.width) * scale
        y2 = canvas_height - (wall_bottom + item.y * scale)
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

    offset = 0
    for i, obs in enumerate(obstacles):
        layout_items[obstacle_names[i]] = {"x": offset, "y": 0.0}
        offset += obs["Width"] + 2
        di = DraggableItem(
            index=i,
            obstacle=obs,
            move_item_to_canvas=move_item_to_canvas,
            check_all_collisions=check_all_collisions
        )
        items.append(di)
        btn = ttk.Button(buttons_frame, text=obs["Name"], command=lambda idx=i: show_item_popup(idx))
        apply_primary_button_style(btn)
        btn.pack(side="left", padx=3)
        item_buttons[i] = btn

    # Ensure the button frame is visible
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(side="bottom", fill="x", pady=10)

    next_button = ttk.Button(button_frame, text="Save and next", command=save_and_continue)
    apply_primary_button_style(next_button)
    next_button.pack(side="right", padx=10)

    def save_and_continue():
        if check_all_collisions():
            popup = Toplevel(root)
            popup.title("Collision Detected")
            ttk.Label(popup, text="The program has identified an impossible layout. Would you like to keep editing?").pack(padx=10, pady=10)
            btn_frame = ttk.Frame(popup)
            btn_frame.pack(pady=10)
            btn_edit = ttk.Button(btn_frame, text="Keep Editing", command=popup.destroy)
            btn_save = ttk.Button(btn_frame, text="Export Anyway", command=lambda: (popup.destroy(), export_then_continue()))
            apply_primary_button_style(btn_edit)
            apply_primary_button_style(btn_save)
            btn_edit.pack(side="left", padx=5)
            btn_save.pack(side="left", padx=5)
        else:
            export_then_continue()

    def export_then_continue():
        file_path = filedialog.asksaveasfilename(defaultextension=".json", title="Save Project")
        if not file_path:
            return  # User cancelled
        export_project(file_path, wall, permanent_objects, layout_items)
        SelectWallSpaceUI(root, file_path)