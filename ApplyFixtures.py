#!/usr/bin/env python3
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Global list for storing created obstacle dictionaries and their names.
obstacles = []      # List of dictionaries
obstacle_names = [] # List of names ("Obstacle1", "Obstacle2", ...)

# --------------------- Validation Functions ---------------------
def validate_name(new_value):
    """Allow only letters, numbers, and spaces in the Name field."""
    if new_value == "" or re.match(r'^[A-Za-z0-9 ]*$', new_value):
        return True
    else:
        messagebox.showwarning("Invalid Input", "Only letters, numbers, and spaces are allowed in the Name field.")
        return False

def validate_decimal(new_value):
    """Allow only valid decimal numbers in the dimension fields."""
    if new_value == "" or re.match(r'^\d*\.?\d*$', new_value):
        return True
    else:
        messagebox.showwarning("Invalid Input", "Only decimal numbers (and an optional dot) are allowed.")
        return False

# --------------------- Preset Item Setup ---------------------
def preset_item(item_type):
    """When one of the preset buttons is pressed, auto-fill the fields accordingly."""
    if item_type == "Door":
        name_var.set("Door")
        width_var.set("40.25")
        height_var.set("83.0125")
    elif item_type == "Fire Alarm":
        name_var.set("Fire Alarm")
        width_var.set("4")
        height_var.set("5.5")
    elif item_type == "Fire Sprinkler":
        name_var.set("Fire Sprinkler")
        width_var.set("3.25")
        height_var.set("3.25")
    elif item_type == "Light Switch":
        name_var.set("Light Switch")
        width_var.set("2.75")
        height_var.set("4.625")
    elif item_type == "Custom":
        name_entry.delete(0, tk.END)
        name_entry.insert(0, "Custom")
        width_var.set("")
        height_var.set("")
    # Enable the fields and the image selection button once a preset is chosen.
    name_entry.config(state="normal")
    width_entry.config(state="normal")
    height_entry.config(state="normal")
    image_button.config(state="normal")
    check_item_fields()

# --------------------- Field Checking and Image Selection ---------------------
def check_item_fields(*args):
    """Enable the 'Save and add next item' button only if all three mandatory fields are nonempty.
       For Custom items, the Name field must be changed from 'Custom'."""
    name_text = name_var.get().strip()
    if name_text and name_text != "Custom" and width_var.get().strip() and height_var.get().strip():
        save_item_button.config(state="normal")
    else:
        save_item_button.config(state="disabled")
    check_save_next_button()

def select_image():
    """Open a file dialog so the user can choose an image file."""
    filename = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
    )
    if filename:
        # Only display the file name (last part of the path)
        image_label.config(text=filename.split("/")[-1])
        global selected_image
        selected_image = filename
    else:
        selected_image = None

# --------------------- Saving an Item ---------------------
def save_item():
    """Create a new dictionary from the entered item values and add it to the global list."""
    global obstacles, obstacle_names, selected_image
    n = name_var.get().strip()
    w_text = width_var.get().strip()
    h_text = height_var.get().strip()

    if not n or n == "Custom":
        messagebox.showwarning("Missing Information", "Please provide a valid Name (letters and numbers only).")
        return
    if not w_text or not h_text:
        messagebox.showwarning("Missing Information", "Width and Height are mandatory.")
        return

    try:
        w = float(w_text)
        h = float(h_text)
    except ValueError:
        messagebox.showwarning("Invalid Data", "Width and Height must be valid decimal numbers.")
        return

    # Create the dictionary. For Image, use the selected filename if available; otherwise, False.
    item = {
        "Name": n,
        "Width": w,
        "Height": h,
        "Image": selected_image if selected_image else False
    }
    obstacle_num = len(obstacles) + 1
    dict_name = f"Obstacle{obstacle_num}"
    obstacles.append(item)
    obstacle_names.append(dict_name)
    messagebox.showinfo("Item Saved", f"Saved {dict_name}")
    
    # Reset the fields for the next entry.
    name_var.set("")
    width_var.set("")
    height_var.set("")
    image_label.config(text="No image selected")
    selected_image = None
    save_item_button.config(state="disabled")
    check_save_next_button()

def check_save_next_button():
    """Enable the bottom 'Save and next' button if either:
       - 'No' is selected for permanent items, or
       - 'Yes' is selected and at least one item has been saved."""
    if permanent_var.get() == "No" or (permanent_var.get() == "Yes" and len(obstacles) > 0):
        save_next_button.config(state="normal")
    else:
        save_next_button.config(state="disabled")

# --------------------- Permanent Items Section ---------------------
def on_permanent_change():
    """Show or hide the additional section based on the radio button selection."""
    if permanent_var.get() == "Yes":
        additional_frame.pack(fill="x", padx=10, pady=10)
    else:
        additional_frame.forget()
    check_save_next_button()

# --------------------- Main Application Setup ---------------------
root = tk.Tk()
root.title("Apply fixtures")
root.geometry("800x600")

# Main container frame
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# --- Top Section: Permanent Items Question ---
question_frame = ttk.Frame(main_frame)
question_frame.pack(fill="x", pady=10)
question_label = ttk.Label(question_frame, text="Are there any permanent items on the wall?")
question_label.pack(side="left", padx=(0, 10))
permanent_var = tk.StringVar(value="")
radio_yes = ttk.Radiobutton(question_frame, text="Yes", variable=permanent_var, value="Yes", command=on_permanent_change)
radio_yes.pack(side="left", padx=5)
radio_no = ttk.Radiobutton(question_frame, text="No", variable=permanent_var, value="No", command=on_permanent_change)
radio_no.pack(side="left", padx=5)

# --- Additional Section (Shown only if "Yes" is selected) ---
additional_frame = ttk.Frame(main_frame)
# (Not packed initially; on_permanent_change() will pack it when needed)

# Preset Buttons Row
preset_frame = ttk.Frame(additional_frame)
preset_frame.pack(fill="x", pady=10)
preset_label = ttk.Label(preset_frame, text="Please enter items one at a time")
preset_label.pack(side="left", padx=(0, 10))
for item in ["Door", "Fire Alarm", "Fire Sprinkler", "Light Switch", "Custom"]:
    btn = ttk.Button(preset_frame, text=item, command=lambda it=item: preset_item(it))
    btn.pack(side="left", padx=5)

# Fields for entering item details
fields_frame = ttk.Frame(additional_frame)
fields_frame.pack(fill="x", pady=10)

# Name field
name_row = ttk.Frame(fields_frame)
name_row.pack(fill="x", pady=5)
ttk.Label(name_row, text="Name").pack(side="left", padx=5)
name_var = tk.StringVar()
name_vcmd = (root.register(validate_name), '%P')
name_entry = ttk.Entry(name_row, textvariable=name_var, validate="key", validatecommand=name_vcmd, state="disabled")
name_entry.pack(side="left", padx=5, fill="x", expand=True)
name_var.trace_add("write", check_item_fields)

# Width field
width_row = ttk.Frame(fields_frame)
width_row.pack(fill="x", pady=5)
ttk.Label(width_row, text="Width").pack(side="left", padx=5)
width_var = tk.StringVar()
width_vcmd = (root.register(validate_decimal), '%P')
width_entry = ttk.Entry(width_row, textvariable=width_var, validate="key", validatecommand=width_vcmd, state="disabled")
width_entry.pack(side="left", padx=5, fill="x", expand=True)
width_var.trace_add("write", check_item_fields)

# Height field
height_row = ttk.Frame(fields_frame)
height_row.pack(fill="x", pady=5)
ttk.Label(height_row, text="Height").pack(side="left", padx=5)
height_var = tk.StringVar()
height_vcmd = (root.register(validate_decimal), '%P')
height_entry = ttk.Entry(height_row, textvariable=height_var, validate="key", validatecommand=height_vcmd, state="disabled")
height_entry.pack(side="left", padx=5, fill="x", expand=True)
height_var.trace_add("write", check_item_fields)

# Image field: Label and Button
image_row = ttk.Frame(fields_frame)
image_row.pack(fill="x", pady=5)
ttk.Label(image_row, text="Image").pack(side="left", padx=5)
image_button = ttk.Button(image_row, text="Select Image", command=select_image, state="disabled")
image_button.pack(side="left", padx=5)
image_label = ttk.Label(image_row, text="No image selected")
image_label.pack(side="left", padx=5)

# Variable to store the selected image filename (or None)
selected_image = None

# "Save and add next item" button (for adding one obstacle)
save_item_button = ttk.Button(additional_frame, text="Save and add next item", command=save_item, state="disabled")
save_item_button.pack(anchor="e", pady=10)

# --- Bottom Section: "Save and next" button ---
save_next_button = ttk.Button(main_frame, text="Save and next", command=lambda: messagebox.showinfo("Next", "Proceeding..."), state="disabled")
save_next_button.pack(anchor="se", pady=10)

root.mainloop()
