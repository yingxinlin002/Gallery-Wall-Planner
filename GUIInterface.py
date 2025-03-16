#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
import os

# -------------------------
# Mock Data from Previous Programs
# -------------------------
# These variables simulate the data from "Gallery Wall Creator" and "apply_fixtures.py"
wall_name   = "My Gallery Wall"
wall_width  = 220.0    # in inches
wall_height = 120.0     # in inches
wall_color  = "#d4d4d4"

# Simulated array of dictionaries (each created in apply_fixtures.py)
# Each dictionary has keys: "Name", "Width", "Height", "Image"
obstacles = [
    {"Name": "Door",         "Width": 40.25,  "Height": 83.0125, "Image": False},
    {"Name": "Fire Alarm",   "Width": 4.0,    "Height": 5.5,     "Image": False},
    {"Name": "Fire Sprinkler", "Width": 3.25, "Height": 3.25,    "Image": False},
    {"Name": "Light Switch", "Width": 2.75,   "Height": 4.625,   "Image": False},
    {"Name": "Custom",       "Width": 10.0,   "Height": 15.0,    "Image": False},
]
# This list will hold the names (like "Obstacle1", "Obstacle2", ...) in order.
obstacle_names = [f"Obstacle{i+1}" for i in range(len(obstacles))]

# -------------------------
# Global variables for saving layout information
# (After items are placed and/or edited)
layout_items = {}  # keys will be obstacle names, values are dicts including position info

# -------------------------
# Main Application Window Setup
# -------------------------
root = tk.Tk()
root.title("Place fixtures")

# Create a main frame with a header area and a canvas area.
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Header Frame: Contains the title and one button per obstacle.
header_frame = ttk.Frame(main_frame)
header_frame.pack(side="top", fill="x", padx=10, pady=5)

title_label = ttk.Label(header_frame, text="Place fixtures", font=("Helvetica", 16))
title_label.pack(side="left")

# Create a frame for item buttons.
buttons_frame = ttk.Frame(header_frame)
buttons_frame.pack(side="left", padx=20)
# For each obstacle, create a button using its "Name".
item_buttons = {}
def show_item_popup(item_index):
    # Popup that shows item details and allows editing.
    item_data = obstacles[item_index]
    item_name = obstacle_names[item_index]
    # Get current layout info (position in inches) from layout_items; if not present, default to (0,0)
    pos = layout_items.get(item_name, {"x":0.0, "y":0.0})
    # Compute the five key points based on the center coordinate.
    width_val = item_data["Width"]
    height_val = item_data["Height"]
    # Assume bottom_left = pos. Then center = (x + width/2, y + height/2)
    bl = (pos["x"], pos["y"])
    center = (bl[0] + width_val/2, bl[1] + height_val/2)
    tl = (bl[0], bl[1] + height_val)
    tr = (bl[0] + width_val, bl[1] + height_val)
    br = (bl[0] + width_val, bl[1])
    
    def recalc_from_center(new_center):
        # Given a new center, recalc bottom_left and other corners.
        cx, cy = new_center
        bl_new = (cx - width_val/2, cy - height_val/2)
        tl_new = (bl_new[0], bl_new[1] + height_val)
        tr_new = (bl_new[0] + width_val, bl_new[1] + height_val)
        br_new = (bl_new[0] + width_val, bl_new[1])
        return bl_new, tl_new, tr_new, br_new, new_center

    popup = Toplevel(root)
    popup.title(f"Edit {item_name}")
    
    # Display current info.
    ttk.Label(popup, text=f"Name: {item_data['Name']}").grid(row=0, column=0, columnspan=2, pady=5)
    ttk.Label(popup, text=f"Width: {width_val}").grid(row=1, column=0, columnspan=2, pady=5)
    ttk.Label(popup, text=f"Height: {height_val}").grid(row=2, column=0, columnspan=2, pady=5)
    
    # Show computed coordinates.
    bl_var = tk.StringVar(value=f"{bl[0]:.2f}, {bl[1]:.2f}")
    tl_var = tk.StringVar(value=f"{tl[0]:.2f}, {tl[1]:.2f}")
    tr_var = tk.StringVar(value=f"{tr[0]:.2f}, {tr[1]:.2f}")
    br_var = tk.StringVar(value=f"{br[0]:.2f}, {br[1]:.2f}")
    center_var = tk.StringVar(value=f"{center[0]:.2f}, {center[1]:.2f}")
    
    ttk.Label(popup, text="Bottom Left:").grid(row=3, column=0, sticky="e")
    ttk.Label(popup, textvariable=bl_var).grid(row=3, column=1, sticky="w")
    ttk.Label(popup, text="Top Left:").grid(row=4, column=0, sticky="e")
    ttk.Label(popup, textvariable=tl_var).grid(row=4, column=1, sticky="w")
    ttk.Label(popup, text="Top Right:").grid(row=5, column=0, sticky="e")
    ttk.Label(popup, textvariable=tr_var).grid(row=5, column=1, sticky="w")
    ttk.Label(popup, text="Bottom Right:").grid(row=6, column=0, sticky="e")
    ttk.Label(popup, textvariable=br_var).grid(row=6, column=1, sticky="w")
    
    ttk.Label(popup, text="Center (editable):").grid(row=7, column=0, sticky="e")
    center_entry = ttk.Entry(popup, textvariable=center_var)
    center_entry.grid(row=7, column=1, sticky="w")
    
    def save_popup():
        try:
            cx_str, cy_str = center_var.get().split(',')
            new_center = (float(cx_str.strip()), float(cy_str.strip()))
        except Exception:
            messagebox.showerror("Error", "Center must be entered as 'x, y'")
            return
        new_bl, new_tl, new_tr, new_br, new_center = recalc_from_center(new_center)
        # Update display fields.
        bl_var.set(f"{new_bl[0]:.2f}, {new_bl[1]:.2f}")
        tl_var.set(f"{new_tl[0]:.2f}, {new_tl[1]:.2f}")
        tr_var.set(f"{new_tr[0]:.2f}, {new_tr[1]:.2f}")
        br_var.set(f"{new_br[0]:.2f}, {new_br[1]:.2f}")
        # Update the global layout info...
        layout_items[item_name] = {"x": new_bl[0], "y": new_bl[1]}
        # Also update the DraggableItem object's internal coordinates.
        items[item_index].x = new_bl[0]
        items[item_index].y = new_bl[1]
        move_item_to_canvas(item_index)  # update its drawing
        popup.destroy()
    
    ttk.Button(popup, text="Save", command=save_popup).grid(row=8, column=0, columnspan=2, pady=10)

# Create an Item Button for each obstacle.
for i, obs in enumerate(obstacles):
    btn = ttk.Button(buttons_frame, text=obs["Name"], command=lambda idx=i: show_item_popup(idx))
    btn.pack(side="left", padx=3)
    item_buttons[i] = btn

# -------------------------
# Canvas for the wall and fixtures
# -------------------------
# We will draw the wall at a fixed canvas size, and compute a scale factor.
canvas_width = 800
canvas_height = 600
canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, bg="white")
canvas.pack(fill="both", expand=True, padx=10, pady=10)

# Compute scale factor so that the wall (in inches) fits inside the canvas with a margin.
margin = 50
scale = min((canvas_width - 2*margin) / wall_width, (canvas_height - 2*margin) / wall_height)

# Wall drawing parameters
wall_left = margin
wall_bottom = margin
wall_right = wall_left + wall_width * scale
wall_top = wall_bottom + wall_height * scale

# Draw the wall (a rectangle with the wall_color).
canvas.create_rectangle(wall_left, canvas_height - wall_top,
                        wall_right, canvas_height - wall_bottom,
                        fill=wall_color, outline="black", width=2)

# -------------------------
# Draggable Item Class
# -------------------------
class DraggableItem:
    def __init__(self, index, obstacle):
        self.index = index
        self.obstacle = obstacle  # dictionary with Name, Width, Height, Image
        # Default position: if not already set in layout_items, set at (0,0)
        self.name = obstacle_names[index]
        pos = layout_items.get(self.name, {"x": 0.0, "y": 0.0})
        self.x = pos["x"]
        self.y = pos["y"]
        self.width = obstacle["Width"]
        self.height = obstacle["Height"]
        # Create a canvas rectangle representing the item.
        self.id = None
        self.create_canvas_item()
        self._drag_data = {"x": 0, "y": 0}

    def create_canvas_item(self):
        # Convert from wall (inches, origin bottom-left) to canvas coordinates.
        x1 = wall_left + self.x * scale
        y1 = canvas_height - (wall_bottom + (self.y + self.height) * scale)
        x2 = wall_left + (self.x + self.width) * scale
        y2 = canvas_height - (wall_bottom + self.y * scale)
        self.id = canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black", width=2)
        # Bind drag events.
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
        # After dragging, update self.x and self.y based on new canvas position.
        coords = canvas.coords(self.id)  # [x1, y1, x2, y2]
        new_x = (coords[0] - wall_left) / scale
        # Correct conversion: bottom-left in canvas is at (x1, y2).
        new_y = (canvas_height - coords[3] - wall_bottom) / scale

        # Constrain so item does not go outside the wall.
        if new_x < 0:
            new_x = 0
        if new_y < 0:
            new_y = 0
        if new_x + self.width > wall_width:
            new_x = wall_width - self.width
        if new_y + self.height > wall_height:
            new_y = wall_height - self.height

        self.x = new_x
        self.y = new_y
        layout_items[self.name] = {"x": self.x, "y": self.y}
        # Snap back into proper position.
        move_item_to_canvas(self.index)
        check_all_collisions()

def move_item_to_canvas(item_index):
    # Reposition the canvas rectangle for item at item_index.
    item = items[item_index]
    x1 = wall_left + item.x * scale
    y1 = canvas_height - (wall_bottom + (item.y + item.height) * scale)
    x2 = wall_left + (item.x + item.width) * scale
    y2 = canvas_height - (wall_bottom + item.y * scale)
    canvas.coords(item.id, x1, y1, x2, y2)

def check_all_collisions():
    # For each pair of items, check if their rectangles (in wall inches) overlap.
    n = len(items)
    colliding = set()
    for i in range(n):
        for j in range(i+1, n):
            if rectangles_overlap(items[i], items[j]):
                colliding.add(i)
                colliding.add(j)
    # Update outlines.
    for i, item in enumerate(items):
        if i in colliding:
            canvas.itemconfig(item.id, outline="red")
        else:
            canvas.itemconfig(item.id, outline="black")
    return len(colliding) > 0

def rectangles_overlap(item1, item2):
    # Each item: bottom-left (x,y), width, height.
    ax1, ay1 = item1.x, item1.y
    ax2, ay2 = item1.x + item1.width, item1.y + item1.height
    bx1, by1 = item2.x, item2.y
    bx2, by2 = item2.x + item2.width, item2.y + item2.height
    if ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1:
        return False
    return True

# Create DraggableItem objects for each obstacle.
items = []
offset = 0
for i, obs in enumerate(obstacles):
    layout_items[obstacle_names[i]] = {"x": offset, "y": 0.0}
    di = DraggableItem(i, obs)
    items.append(di)
    offset += obs["Width"] + 2  # add 2 inches gap

# -------------------------
# Bottom "Save and next" Button
# -------------------------
def save_layout():
    # Check for collisions.
    if check_all_collisions():
        def keep_editing():
            popup.destroy()
        def save_as_is():
            popup.destroy()
            write_to_file()
        popup = Toplevel(root)
        popup.title("Collision Detected")
        ttk.Label(popup, text="The program has identified an impossible layout. Would you like to keep editing?").pack(padx=10, pady=10)
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Keep Editing", command=keep_editing).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save as is", command=save_as_is).pack(side="left", padx=5)
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
        for i, obs in enumerate(obstacles):
            item_name = obstacle_names[i]
            pos = layout_items.get(item_name, {"x": 0.0, "y": 0.0})
            center_x = pos["x"] + obs["Width"] / 2
            center_y = pos["y"] + obs["Height"] / 2
            f.write(f"Item Type: {obs['Name']}, Name: {obs['Name']}, Width: {obs['Width']}, Height: {obs['Height']}, Center: ({center_x:.2f}, {center_y:.2f})\n")
    messagebox.showinfo("Saved", f"Layout saved to {os.path.basename(filename)}")

save_next_btn = ttk.Button(root, text="Save and next", command=save_layout)
save_next_btn.pack(side="bottom", anchor="e", padx=10, pady=10)

root.mainloop()
