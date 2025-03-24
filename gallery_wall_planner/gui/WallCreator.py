#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# DO NOT USE THIS IS LEGACY CODE FROM BEFORE WE STARTING USING NEWEXHIBIT.PY
# this only continues to exist because it has some features the new version does not, and we may want to circle back to them if we have time
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!/usr/bin/env python3
import re
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

# Global variables for later use
wall_name = ""
wall_width = None
wall_height = None
wall_color = "#d4d4d4"  # default rectangle color

# Validation functions
def validate_wall_name(new_value):
    """Allow only letters and numbers for wall_name."""
    if new_value == "" or re.match(r"^[A-Za-z0-9 ]*$", new_value):
        return True
    elif new_value:
        messagebox.showwarning("Invalid Input", "Only letters, numbers, and spaces are allowed.")
        return False

def validate_dimension(new_value):
    """Allow only numbers, and decimals for width and height."""
    if new_value == "" or re.match(r"^[0-9\.\,]*$", new_value):
        return True
    elif new_value:
        messagebox.showwarning("Invalid Input", "Only numbers, and decimals are allowed.")
        return False

# Function to update the rectangle based on entered dimensions
def update_rectangle(*args):
    global wall_width, wall_height, wall_color
    try:
        # Remove any commas and convert to float
        width_val = width_var.get().replace(",", "")
        height_val = height_var.get().replace(",", "")
        wall_width = float(width_val) if width_val else None
        wall_height = float(height_val) if height_val else None
    except ValueError:
        # If conversion fails, do nothing
        return

    # If both fields have valid numbers, update the rectangle's aspect ratio.
    if wall_width and wall_height and wall_height != 0:
        # Calculate ratio from user input.
        ratio = wall_width / wall_height
    else:
        # Default ratio 3:2 if inputs are not complete.
        ratio = 3/2

    # Determine canvas size (using a base height)
    base_height = 150
    new_width = int(base_height * ratio)
    new_height = base_height

    # Update the canvas size and redraw the rectangle.
    rect_canvas.config(width=new_width, height=new_height)
    # Clear previous rectangle and draw a new one.
    rect_canvas.delete("all")
    rect_canvas.create_rectangle(0, 0, new_width, new_height, fill=wall_color, outline="black")

# Function to launch the color picker
def choose_color():
    global wall_color
    color = colorchooser.askcolor(title="Choose wall color", initialcolor=wall_color)
    if color[1] is not None:
        wall_color = color[1]
        update_rectangle()

# Function for the NEXT button (for now, just prints values)
def on_next():
    global wall_name, wall_width, wall_height, wall_color
    wall_name = name_var.get()
    # Validate mandatory fields
    if not wall_name:
        messagebox.showwarning("Missing Data", "Please enter a wall name (letters and numbers only).")
        return
    if not width_var.get() or not height_var.get():
        messagebox.showwarning("Missing Data", "Please enter both width and height in inches (in decimal form).")
        return
    try:
        wall_width = float(width_var.get().replace(",", ""))
        wall_height = float(height_var.get().replace(",", ""))
    except ValueError:
        messagebox.showwarning("Invalid Data", "Width and Height must be valid numbers.")
        return

    # For demonstration, just print the collected data.
    print("Wall Name:", wall_name)
    print("Wall Width:", wall_width)
    print("Wall Height:", wall_height)
    print("Wall Color:", wall_color)
    messagebox.showinfo("NEXT", "Proceeding to the next step...")

# Create main window
root = tk.Tk()
root.title("Gallery Wall Creator")
root.geometry("700x600")  # initial size

# Create a canvas and a vertical/horizontal scrollbar for scrolling content.
main_canvas = tk.Canvas(root)
v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
h_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=main_canvas.xview)
main_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

v_scrollbar.pack(side="right", fill="y")
h_scrollbar.pack(side="bottom", fill="x")
main_canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas to hold all content.
content_frame = ttk.Frame(main_canvas, padding=20)
main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Update scroll region when the size of content changes.
def on_configure(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
content_frame.bind("<Configure>", on_configure)

# Title Label at the top, centered.
title_label = ttk.Label(content_frame, text="Gallery Wall Creator", font=("Helvetica", 24))
title_label.pack(pady=(10, 30))

# --- Wall Name Section ---
name_frame = ttk.Frame(content_frame)
name_frame.pack(pady=(0, 30), fill="x")

ttk.Label(name_frame, text="This wall is labeled").pack(side="left", padx=(0, 10))

# Variable and Entry for wall name with validation.
name_var = tk.StringVar()
name_vcmd = (root.register(validate_wall_name), '%P')
name_entry = ttk.Entry(name_frame, textvariable=name_var, validate="key", validatecommand=name_vcmd)
name_entry.pack(side="left", fill="x", expand=True)

# --- Dimensions Section (Width & Height) ---
dimensions_frame = ttk.Frame(content_frame)
dimensions_frame.pack(pady=(0, 30), fill="x")

# Left side: Width
width_frame = ttk.Frame(dimensions_frame)
width_frame.pack(side="left", expand=True, padx=10, fill="x")
ttk.Label(width_frame, text="Enter width").pack(side="top", anchor="w")
width_var = tk.StringVar()
width_vcmd = (root.register(validate_dimension), '%P')
width_entry = ttk.Entry(width_frame, textvariable=width_var, validate="key", validatecommand=width_vcmd)
width_entry.insert(0, "inches in decimal form")
width_entry.pack(side="top", fill="x", pady=5)

# Right side: Height
height_frame = ttk.Frame(dimensions_frame)
height_frame.pack(side="left", expand=True, padx=10, fill="x")
ttk.Label(height_frame, text="Enter height").pack(side="top", anchor="w")
height_var = tk.StringVar()
height_vcmd = (root.register(validate_dimension), '%P')
height_entry = ttk.Entry(height_frame, textvariable=height_var, validate="key", validatecommand=height_vcmd)
height_entry.insert(0, "inches in decimal form")
height_entry.pack(side="top", fill="x", pady=5)

# Bind events to update the rectangle when width or height changes
width_var.trace_add("write", update_rectangle)
height_var.trace_add("write", update_rectangle)

# --- Color Selector ---
color_button = ttk.Button(content_frame, text="Wall color selector", command=choose_color)
color_button.pack(pady=(0, 30))

# --- Rectangle Display ---
# Create a canvas for the rectangle. Start with a 3:2 ratio.
rect_canvas = tk.Canvas(content_frame, width=300, height=200, bg="white", highlightthickness=1, highlightbackground="black")
rect_canvas.pack(pady=(0, 30))
# Draw initial rectangle with default color.
rect_canvas.create_rectangle(0, 0, 300, 200, fill=wall_color, outline="black")

# --- NEXT Button at bottom right ---
button_frame = ttk.Frame(content_frame)
button_frame.pack(fill="both")
next_button = ttk.Button(button_frame, text="NEXT", command=on_next)
next_button.pack(side="right", padx=10, pady=10)

# Start the Tkinter event loop.
root.mainloop()
