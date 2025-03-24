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
popup_windows = {}  # Dictionary to store open popups by item index

# -------------------------
# Function: Enforce Boundaries
# -------------------------
def enforce_boundaries(x, y, width, height):
    """Ensures the object remains inside the wall boundaries."""
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
    # Close any existing popup for this item
    if item_index in popup_windows:
        popup_windows[item_index].destroy()
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
    popup.geometry("300x400")

    # Create a frame inside the popup to center everything
    content_frame = ttk.Frame(popup)
    content_frame.pack(expand=True)  # Use expand to center in the popup

    # Center all content
    content_frame.grid_columnconfigure(0, weight=1)

    # Variables for fields
    name_var = tk.StringVar(value=item_data["Name"])
    width_var = tk.DoubleVar(value=width_val)
    height_var = tk.DoubleVar(value=height_val)

    # Track the popup window globally
    popup_windows[item_index] = popup

    def update_popup_fields():
        """Update all coordinate fields when the object moves."""
        if popup.winfo_exists():
            print(f"Popup update triggered for {item_name}")  # Debugging print
            pos = layout_items.get(item_name, {"x": 0.0, "y": 0.0})
            new_bl = (pos["x"], pos["y"])
            new_tl = (new_bl[0], new_bl[1] + height_var.get())
            new_tr = (new_bl[0] + width_var.get(), new_bl[1] + height_var.get())
            new_br = (new_bl[0] + width_var.get(), new_bl[1])
            new_center = (new_bl[0] + width_var.get() / 2, new_bl[1] + height_var.get() / 2)

            # Update all popup fields dynamically
            bl_var.set(f"{new_bl[0]:.2f}, {new_bl[1]:.2f}")
            tl_var.set(f"{new_tl[0]:.2f}, {new_tl[1]:.2f}")
            tr_var.set(f"{new_tr[0]:.2f}, {new_tr[1]:.2f}")
            br_var.set(f"{new_br[0]:.2f}, {new_br[1]:.2f}")
            center_var.set(f"{new_center[0]:.2f}, {new_center[1]:.2f}")
            
            popup.update_idletasks()  # Force the popup to refresh
            popup.update()  # Force UI to redraw

    items[item_index].update_popup_fields = update_popup_fields

    # Register this function for real-time updates
    items[item_index].update_popup_fields = update_popup_fields

    # Define buttons first so we can modify them later
    edit_button = ttk.Button(content_frame, text="Edit Physical Object")
    save_button = ttk.Button(content_frame, text="Save Changes to Object")

    # Editable fields for Name, Width, and Height (side-by-side layout)
    ttk.Label(content_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
    name_entry = ttk.Entry(content_frame, textvariable=name_var, justify="center", state="disabled")
    name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Width:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
    width_entry = ttk.Entry(content_frame, textvariable=width_var, justify="center", state="disabled")
    width_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Height:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
    height_entry = ttk.Entry(content_frame, textvariable=height_var, justify="center", state="disabled")
    height_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

    #Enables editing of the Name, Width, and Height fields
    def enable_editing():
        name_entry.config(state="normal")
        width_entry.config(state="normal")
        height_entry.config(state="normal")

        edit_button.config(state="disabled")  # Disable Edit button
        save_button.config(state="normal")   # Enable Save button


    def apply_physical_changes():
        """Update the name, width, and height while keeping the center unchanged."""
        new_name = name_var.get().strip()
        try:
            new_width = float(width_var.get())
            new_height = float(height_var.get())
        except ValueError:
            messagebox.showerror("Error", "Width and Height must be numeric values")
            return
    
        if new_width <= 0 or new_height <= 0:
            messagebox.showerror("Error", "Width and Height must be greater than zero")
            return

        # Preserve center, update bottom-left coordinates
        new_bl_x = center[0] - new_width / 2
        new_bl_y = center[1] - new_height / 2

        # Keep track of the old name before renaming. If not done, the item will be lost in the layout_items dict.
        old_name = items[item_index].name
        # Reassign update_popup_fields before changing name. Second half of old_name is to ensure the popup continues updating.
        item_obj = items[item_index]  # Assign reference to avoid modifying the list directly
        update_func = item_obj.update_popup_fields  # Preserve update function

        # Update obstacle properties
        obstacles[item_index]["Name"] = new_name
        obstacles[item_index]["Width"] = new_width
        obstacles[item_index]["Height"] = new_height

        # Update global layout info
        layout_items[new_name] = {"x": new_bl_x, "y": new_bl_y}

        # Update the GUI button name dynamically
        item_buttons[item_index].config(text=new_name)

        # Update the DraggableItem properties
        item_obj = items[item_index]  # Assign the reference to a variable
        item_obj.name = new_name
        item_obj.width = new_width
        item_obj.height = new_height
        item_obj.x = new_bl_x
        item_obj.y = new_bl_y

        # **Fix: Restore update function reference**
        item_obj.update_popup_fields = update_func  # Ensure function reference is maintained

        # **Fix: Call `update_popup_fields()` explicitly after edit**
        item_obj.update_popup_fields()  # Force update

        # Move and resize the object on the canvas
        move_item_to_canvas(item_index)

        # Check for collisions after resizing
        check_all_collisions()

        # Reassign update_popup_fields to ensure the popup continues updating**
        items[item_index].update_popup_fields = update_popup_fields

        # Lock the fields again
        name_entry.config(state="disabled")
        width_entry.config(state="disabled")
        height_entry.config(state="disabled")

        # Swap button states back
        save_button.config(state="disabled")
        edit_button.config(state="normal")


    # Configure buttons with initial states
    edit_button.config(command=enable_editing, state="normal")  # Enabled initially
    save_button.config(command=apply_physical_changes, state="disabled")  # Disabled initially

    # Place buttons in the UI
    edit_button.grid(row=3, column=0, columnspan=1, pady=10, padx=5)
    save_button.grid(row=3, column=1, columnspan=1, pady=10, padx=5)

    # Add a horizontal separator
    ttk.Separator(content_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

    # Show computed coordinates (keeping label & value side-by-side)
    
    # Removed: Static coordinate labels (now editable)
    # ttk.Label(content_frame, text="Bottom Left:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
    # bl_var = tk.StringVar(value=f"{bl[0]:.2f}, {bl[1]:.2f}")
    # ttk.Label(content_frame, textvariable=bl_var).grid(row=5, column=1, sticky="w", padx=5, pady=2)

    # Updated: Make Bottom Left editable
    ttk.Label(content_frame, text="Bottom Left:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
    bl_var = tk.StringVar(value=f"{bl[0]:.2f}, {bl[1]:.2f}")
    bl_entry = ttk.Entry(content_frame, textvariable=bl_var, justify="center")
    bl_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)
    
    # Removed: Static Top Left label
    # ttk.Label(content_frame, text="Top Left:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
    # tl_var = tk.StringVar(value=f"{tl[0]:.2f}, {tl[1]:.2f}")
    # ttk.Label(content_frame, textvariable=tl_var).grid(row=6, column=1, sticky="w", padx=5, pady=2)

    # Updated: Make Top Left editable
    ttk.Label(content_frame, text="Top Left:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
    tl_var = tk.StringVar(value=f"{tl[0]:.2f}, {tl[1]:.2f}")
    tl_entry = ttk.Entry(content_frame, textvariable=tl_var, justify="center")
    tl_entry.grid(row=6, column=1, sticky="w", padx=5, pady=2)

    # Removed: Static Top Right label
    # ttk.Label(content_frame, text="Top Right:").grid(row=7, column=0, sticky="e", padx=5, pady=2)
    # tr_var = tk.StringVar(value=f"{tr[0]:.2f}, {tr[1]:.2f}")
    # ttk.Label(content_frame, textvariable=tr_var).grid(row=7, column=1, sticky="w", padx=5, pady=2)

    # Updated: Make Top Right editable
    ttk.Label(content_frame, text="Top Right:").grid(row=7, column=0, sticky="e", padx=5, pady=2)
    tr_var = tk.StringVar(value=f"{tr[0]:.2f}, {tr[1]:.2f}")
    tr_entry = ttk.Entry(content_frame, textvariable=tr_var, justify="center")
    tr_entry.grid(row=7, column=1, sticky="w", padx=5, pady=2)

    # Removed: Static Bottom Right label
    # ttk.Label(content_frame, text="Bottom Right:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
    # br_var = tk.StringVar(value=f"{br[0]:.2f}, {br[1]:.2f}")
    # ttk.Label(content_frame, textvariable=br_var).grid(row=8, column=1, sticky="w", padx=5, pady=2)

    # Updated: Make Bottom Right editable
    ttk.Label(content_frame, text="Bottom Right:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
    br_var = tk.StringVar(value=f"{br[0]:.2f}, {br[1]:.2f}")
    br_entry = ttk.Entry(content_frame, textvariable=br_var, justify="center")
    br_entry.grid(row=8, column=1, sticky="w", padx=5, pady=2)

    # Updated: Center remains editable
    ttk.Label(content_frame, text="Center (editable):").grid(row=9, column=0, sticky="e", padx=5, pady=2)
    center_var = tk.StringVar(value=f"{center[0]:.2f}, {center[1]:.2f}")
    center_entry = ttk.Entry(content_frame, textvariable=center_var, justify="center")
    center_entry.grid(row=9, column=1, sticky="w", padx=5, pady=2)

    # Function to update all coordinate fields dynamically
    def update_coordinates(source_field):
        try:
            new_x, new_y = map(float, eval(f"{source_field}_var").get().split(','))

            if source_field == "bl":
                new_bl = (new_x, new_y)
            elif source_field == "tl":
                new_bl = (new_x, new_y - height_val)
            elif source_field == "tr":
                new_bl = (new_x - width_val, new_y - height_val)
            elif source_field == "br":
                new_bl = (new_x - width_val, new_y)
            elif source_field == "center":
                new_bl = (new_x - width_val / 2, new_y - height_val / 2)

            new_bl = enforce_boundaries(new_bl[0], new_bl[1], width_val, height_val)
            new_tl = (new_bl[0], new_bl[1] + height_val)
            new_tr = (new_bl[0] + width_val, new_bl[1] + height_val)
            new_br = (new_bl[0] + width_val, new_bl[1])
            new_center = (new_bl[0] + width_val / 2, new_bl[1] + height_val / 2)

            bl_var.set(f"{new_bl[0]:.2f}, {new_bl[1]:.2f}")
            tl_var.set(f"{new_tl[0]:.2f}, {new_tl[1]:.2f}")
            tr_var.set(f"{new_tr[0]:.2f}, {new_tr[1]:.2f}")
            br_var.set(f"{new_br[0]:.2f}, {new_br[1]:.2f}")
            center_var.set(f"{new_center[0]:.2f}, {new_center[1]:.2f}")

            # Update object position immediately
            layout_items[item_name] = {"x": new_bl[0], "y": new_bl[1]}
            items[item_index].x = new_bl[0]
            items[item_index].y = new_bl[1]

            # Move the item on the canvas in real-time
            move_item_to_canvas(item_index)

            # Check for collisions dynamically
            check_all_collisions()

        except ValueError:
            pass

    # Bind coordinate fields to update on focus loss
    bl_entry.bind("<FocusOut>", lambda e: update_coordinates("bl"))
    tl_entry.bind("<FocusOut>", lambda e: update_coordinates("tl"))
    tr_entry.bind("<FocusOut>", lambda e: update_coordinates("tr"))
    br_entry.bind("<FocusOut>", lambda e: update_coordinates("br"))
    center_entry.bind("<FocusOut>", lambda e: update_coordinates("center"))

    # Save function remains unchanged
    def save_popup():
        try:
            cx_str, cy_str = center_var.get().split(',')
            new_center = (float(cx_str.strip()), float(cy_str.strip()))
        except Exception:
            messagebox.showerror("Error", "Center must be entered as 'x, y'")
            return

        new_bl, new_tl, new_tr, new_br, new_center = recalc_from_center(new_center)
        corrected_x, corrected_y = enforce_boundaries(new_bl[0], new_bl[1], width_val, height_val)
        corrected_bl = (corrected_x, corrected_y)

        # Recalculate other corners based on the corrected bottom-left
        corrected_tl = (corrected_bl[0], corrected_bl[1] + height_val)
        corrected_tr = (corrected_bl[0] + width_val, corrected_bl[1] + height_val)
        corrected_br = (corrected_bl[0] + width_val, corrected_bl[1])
        corrected_center = (corrected_bl[0] + width_val / 2, corrected_bl[1] + height_val / 2)

        bl_var.set(f"{corrected_bl[0]:.2f}, {corrected_bl[1]:.2f}")
        tl_var.set(f"{corrected_tl[0]:.2f}, {corrected_tl[1]:.2f}")
        tr_var.set(f"{corrected_tr[0]:.2f}, {corrected_tr[1]:.2f}")
        br_var.set(f"{corrected_br[0]:.2f}, {corrected_br[1]:.2f}")

        layout_items[item_name] = {"x": corrected_bl[0], "y": corrected_bl[1]}
        items[item_index].x = corrected_bl[0]
        items[item_index].y = corrected_bl[1]
        move_item_to_canvas(item_index)
        check_all_collisions()
        popup.destroy()

    ttk.Button(content_frame, text="Save", command=save_popup).grid(row=18, column=0, columnspan=2, pady=10)



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
        self.update_popup_fields = None  # Placeholder for popup update function

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
        new_x, new_y = enforce_boundaries(new_x, new_y, self.width, self.height)

        self.x = new_x
        self.y = new_y
        layout_items[self.name] = {"x": self.x, "y": self.y}
        # Snap back into proper position.
        move_item_to_canvas(self.index)
        check_all_collisions()

        if self.update_popup_fields:
            print(f"Updating popup for {self.name}")  # Debugging line
            self.update_popup_fields()

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
