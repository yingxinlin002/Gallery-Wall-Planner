import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
import os
from gallery_wall_planner.gui.popup_editor import open_popup_editor
from gallery_wall_planner.models.ui_styles import (
    init_styles,
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)


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


def launch_organize_art_ui(root):
    init_styles(root)
    root.title("Organize Artwork")

    global wall_name, wall_width, wall_height, wall_color
    global layout_items, popup_windows, items

    wall_name = "My Gallery Wall"
    wall_width = 220.0
    wall_height = 120.0
    wall_color = "#f5f5f5"

    fixed_obstacles = [
        {"Name": "Door", "Width": 40.25, "Height": 83.0125, "X": 10, "Y": 0},
        {"Name": "Fire Alarm", "Width": 4.0, "Height": 5.5, "X": 180, "Y": 90},
    ]

    art_pieces = [
        {"Name": "Flowers", "Width": 36, "Height": 30, "Image": False, "Hang": 8.125},
        {"Name": "Fruit Bowl", "Width": 24, "Height": 36, "Image": False, "Hang": 10.75},
        {"Name": "Laughing Family", "Width": 18, "Height": 24, "Image": False, "Hang": 8.5},
        {"Name": "Grim Scene", "Width": 24, "Height": 18, "Image": False, "Hang": 6.125},
        {"Name": "Trusted Friend", "Width": 10.0, "Height": 15.0, "Image": False, "Hang": 2.875},
    ]
    art_names = [f"Art{i+1}" for i in range(len(art_pieces))]
    layout_items = {}
    popup_windows = {}
    items = []

    for widget in root.winfo_children():
        widget.destroy()

    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(main_frame)
    header_frame.pack(side="top", fill="x", padx=10, pady=10)

    title_label = ttk.Label(header_frame, text="Organize Art")
    apply_header_label_style(title_label)
    title_label.pack(side="left")

    buttons_frame = ttk.Frame(header_frame)
    buttons_frame.pack(side="left", padx=20)
    item_buttons = {}

    canvas_width = 800
    canvas_height = 600
    canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height)
    apply_canvas_style(canvas)
    canvas.pack(fill="both", expand=True, padx=10, pady=10)

    margin = 50
    scale = min((canvas_width - 2*margin) / wall_width, (canvas_height - 2*margin) / wall_height)
    wall_left = margin
    wall_bottom = margin
    wall_right = wall_left + wall_width * scale
    wall_top = wall_bottom + wall_height * scale

    canvas.create_rectangle(wall_left, canvas_height - wall_top,
                            wall_right, canvas_height - wall_bottom,
                            fill=wall_color, outline="black", width=2)

    def create_fixed_item(obstacle):
        x1 = wall_left + obstacle["X"] * scale
        y1 = canvas_height - (wall_bottom + (obstacle["Y"] + obstacle["Height"]) * scale)
        x2 = wall_left + (obstacle["X"] + obstacle["Width"]) * scale
        y2 = canvas_height - (wall_bottom + obstacle["Y"] * scale)
        canvas.create_rectangle(x1, y1, x2, y2, fill="#999999", outline="black", width=2)

    for obs in fixed_obstacles:
        create_fixed_item(obs)

    def show_item_popup(item_index):
        open_popup_editor(
            root=root,
            item_index=item_index,
            obstacles=art_pieces,
            obstacle_names=art_names,
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

    class DraggableArt:
        def __init__(self, index, art_data, move_item_to_canvas, check_all_collisions):
            self.index = index
            self.art_data = art_data
            self.name = art_names[index]
            pos = layout_items.get(self.name, {"x": 0.0, "y": 0.0})
            self.x = pos["x"]
            self.y = pos["y"]
            self.width = art_data["Width"]
            self.height = art_data["Height"]
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

        # Check collisions between draggable items
        for i in range(n):
            for j in range(i + 1, n):
                if rectangles_overlap(items[i], items[j]):
                    colliding.add(i)
                    colliding.add(j)

        # Check collisions between draggable items and fixed obstacles
        for i, item in enumerate(items):
            for obstacle in fixed_obstacles:
                obs_x1 = obstacle["X"]
                obs_y1 = obstacle["Y"]
                obs_x2 = obs_x1 + obstacle["Width"]
                obs_y2 = obs_y1 + obstacle["Height"]

                item_x1 = item.x
                item_y1 = item.y
                item_x2 = item.x + item.width
                item_y2 = item.y + item.height

                if not (item_x2 <= obs_x1 or obs_x2 <= item_x1 or item_y2 <= obs_y1 or obs_y2 <= item_y1):
                    colliding.add(i)

        # Update visual outlines
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
    for i, art in enumerate(art_pieces):
        layout_items[art_names[i]] = {"x": offset, "y": 0.0}
        offset += art["Width"] + 2
        item = DraggableArt(
            index=i,
            art_data=art,
            move_item_to_canvas=move_item_to_canvas,
            check_all_collisions=check_all_collisions
        )
        items.append(item)
        btn = ttk.Button(buttons_frame, text=art["Name"], command=lambda idx=i: show_item_popup(idx))
        apply_primary_button_style(btn)
        btn.pack(side="left", padx=3)
        item_buttons[i] = btn

    def save_layout():
        if check_all_collisions():
            popup = Toplevel(root)
            popup.title("Collision Detected")
            ttk.Label(popup, text="The layout has overlapping items. Would you like to continue?").pack(padx=10, pady=10)
            btn_frame = ttk.Frame(popup)
            btn_frame.pack(pady=10)
            btn_edit = ttk.Button(btn_frame, text="Keep Editing", command=popup.destroy)
            btn_save = ttk.Button(btn_frame, text="Save Anyway", command=lambda: (popup.destroy(), write_to_file()))
            apply_primary_button_style(btn_edit)
            apply_primary_button_style(btn_save)
            btn_edit.pack(side="left", padx=5)
            btn_save.pack(side="left", padx=5)
        else:
            write_to_file()

    def write_to_file():
        filename = filedialog.asksaveasfilename(defaultextension=".txt", title="Save Layout")
        if not filename:
            return
        with open(filename, "w") as f:
            f.write(f"Wall Name: {wall_name}\n")
            f.write(f"Wall Width: {wall_width}\n")
            f.write(f"Wall Height: {wall_height}\n")
            f.write(f"Wall Color: {wall_color}\n\n")
            for i, art in enumerate(art_pieces):
                item_name = art_names[i]
                pos = layout_items.get(item_name, {"x": 0.0, "y": 0.0})
                center_x = pos["x"] + art["Width"] / 2
                center_y = pos["y"] + art["Height"] / 2
                f.write(f"Art Piece: {art['Name']}, Width: {art['Width']}, Height: {art['Height']}, Center: ({center_x:.2f}, {center_y:.2f})\n")
        messagebox.showinfo("Saved", f"Layout saved to {os.path.basename(filename)}")

    save_button = ttk.Button(root, text="Save and next", command=save_layout)
    apply_primary_button_style(save_button)
    save_button.pack(side="bottom", anchor="e", padx=10, pady=10)
    check_all_collisions()
