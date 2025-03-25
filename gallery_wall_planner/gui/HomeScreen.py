

#!/usr/bin/env python3
import tkinter as tk
import os

def on_new():
    print("New button pressed")

def on_load():
    print("Load button pressed")

def on_quit():
    root.quit()

# Create the main window
root = tk.Tk()
root.title("Gallery Wall Planner")

# Set an initial window size (optional)
root.geometry("400x300")

# Configure the grid to allow responsiveness
root.columnconfigure(0, weight=1)
# Set up two rows: one for the title and one for the buttons.
root.rowconfigure(1, weight=1)

# Title label, centered at the top
title_label = tk.Label(root, text="Gallery Wall Planner", font=("Helvetica", 24))
title_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

# Create a frame for the buttons to better control layout and spacing
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

# Configure the frame to have one column that expands
button_frame.columnconfigure(0, weight=1)
# Create three rows in the frame and let them expand equally to maintain spacing
for i in range(3):
    button_frame.rowconfigure(i, weight=1)

# New Button
new_button = tk.Button(button_frame, text="New", command=on_new, width=15, height=2)
new_button.grid(row=0, column=0, pady=5)

# Load Button
load_button = tk.Button(button_frame, text="Load", command=on_load, width=15, height=2)
load_button.grid(row=1, column=0,pady=5)

# Quit Button
quit_button = tk.Button(button_frame, text="Quit", command=on_quit, width=15, height=2)
quit_button.grid(row=2, column=0,pady=5)

# Start the main event loop
root.mainloop()












#!/usr/bin/env python3
import tkinter as tk
from PIL import Image, ImageTk

def on_new():
    print("New button pressed")

def on_load():
    print("Load button pressed")

def on_quit():
    root.quit()

try:
    resample_filter = Image.Resampling.LANCZOS  # Pillow ≥ 9.1.0
except AttributeError:
    resample_filter = Image.ANTIALIAS  # Older versions

def resize_background(event):
    if original_image is not None:
        try:
            # Resize the original image to the current window size
            new_width = event.width
            new_height = event.height
            resized = original_image.resize((new_width, new_height), resample_filter)
            # Update the PhotoImage and the label displaying it
            bg_image = ImageTk.PhotoImage(resized)
            background_label.config(image=bg_image)
            background_label.image = bg_image  # Keep a reference!
        except Exception as e:
            print(f"Error resizing background image: {e}")

def resize_background(event):
    if original_image is not None:
        new_width = max(event.width, 1)
        new_height = max(event.height, 1)
        try:
            resized = original_image.resize((new_width, new_height), resample_filter)
            bg_image = ImageTk.PhotoImage(resized)
            background_label.config(image=bg_image)
            background_label.image = bg_image  # prevent garbage collection
        except Exception as e:
            print(f"[Warning] Failed to resize background: {e}")

# Create the main window
root = tk.Tk()
root.title("Gallery Wall Planner")
root.geometry("600x400")  # initial size

# Load the background image (hard-coded to GalleryWall.png)
original_image = None
if os.path.exists("GalleryWall.png"):
    original_image = Image.open("GalleryWall.png")

# Create a label to display the background image and fill the entire window.
background_label = tk.Label(root)
background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

# Bind the window resizing to the resize function
root.bind("<Configure>", resize_background)

# Create a container frame for widgets with transparent background
container = tk.Frame(root, bg="", highlightthickness=0)
container.grid(row=0, column=0, sticky="nsew")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Configure grid for the container for responsiveness
container.columnconfigure(0, weight=1)
container.rowconfigure(1, weight=1)

# Title label, centered at the top
title_label = tk.Label(container, text="Gallery Wall Planner", font=("Helvetica", 24), bg="white")
title_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

# Create a frame for the buttons to control layout and spacing
button_frame = tk.Frame(container, bg="", highlightthickness=0)
button_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
button_frame.columnconfigure(0, weight=1)
for i in range(3):
    button_frame.rowconfigure(i, weight=1)

# New Button
new_button = tk.Button(button_frame, text="New", command=on_new)
new_button.grid(row=0, column=0, sticky="ew", pady=5)

# Load Button
load_button = tk.Button(button_frame, text="Load", command=on_load)
load_button.grid(row=1, column=0, sticky="ew", pady=5)

# Quit Button
quit_button = tk.Button(button_frame, text="Quit", command=on_quit)
quit_button.grid(row=2, column=0, sticky="ew", pady=5)

# Ensure the container is above the background image
container.lift()

# Start the main event loop
root.mainloop()



