# NewExhibitUI.py
import tkinter as tk
from tkinter import messagebox, colorchooser
import re
from gallery_wall_planner.models import shared_state

class NewGalleryUI:
    def __init__(self, root, return_to_home):
        self.root = root
        self.return_to_home = return_to_home
        self.wall_width = None
        self.wall_height = None
        self.wall_color = "white"  # Default wall color
        self.create_new_exhibit_popup()

    def create_new_exhibit_popup(self):
        # Create a popup window for new exhibit options
        self.popup = tk.Toplevel(self.root)
        self.popup.title("New Exhibit")
        self.popup.geometry("300x150")

        # Center the popup on the screen
        self.center_popup(self.popup, 300, 150)  # Width: 300, Height: 150

        # Add buttons to the popup window
        tk.Button(self.popup, text="Start from Scratch", command=self.start_from_scratch, width=20, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(pady=10)
        tk.Button(self.popup, text="Load from an Existing Wall", command=self.load_from_existing, width=20, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(pady=10)

    def center_popup(self, popup, width, height):
        """
        Center the popup window on the screen.
        :param popup: The popup window to center.
        :param width: The width of the popup window.
        :param height: The height of the popup window.
        """
        # Get the screen width and height
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        # Calculate the x and y coordinates to center the popup
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Set the popup's geometry
        popup.geometry(f"{width}x{height}+{x}+{y}")

    def start_from_scratch(self):
        self.popup.destroy()  # Close the popup
        self.show_wall_info_page()

    def load_from_existing(self):
        messagebox.showerror("Error", "No existing walls found.")
        self.popup.destroy()

    def show_wall_info_page(self):
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Add a title
        tk.Label(self.root, text="New Gallery Wall", font=("Arial", 24)).pack(pady=20)
        
        # Wall Name
        tk.Label(self.root, text="Wall Name:", font=("Arial", 12)).pack(pady=5)
        self.wall_name_entry = tk.Entry(self.root, font=("Arial", 12))
        self.wall_name_entry.insert(0, "South Wall")  # Placeholder text
        self.wall_name_entry.config(fg="grey")
        self.wall_name_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.wall_name_entry, "South Wall"))
        self.wall_name_entry.bind("<FocusOut>", lambda event: self.add_placeholder(self.wall_name_entry, "South Wall"))
        self.wall_name_entry.pack(pady=5)
        
        # Wall Width
        tk.Label(self.root, text="Wall Width (inches):", font=("Arial", 12)).pack(pady=5)
        self.wall_width_entry = tk.Entry(self.root, font=("Arial", 12))
        self.wall_width_entry.insert(0, "313")  # Placeholder text
        self.wall_width_entry.config(fg="grey")
        self.wall_width_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.wall_width_entry, "inches"))
        self.wall_width_entry.bind("<FocusOut>", lambda event: self.add_placeholder(self.wall_width_entry, "inches"))
        self.wall_width_entry.pack(pady=5)
        
        # Wall Height
        tk.Label(self.root, text="Wall Height (inches):", font=("Arial", 12)).pack(pady=5)
        self.wall_height_entry = tk.Entry(self.root, font=("Arial", 12))
        self.wall_height_entry.insert(0, "96")  # Placeholder text
        self.wall_height_entry.config(fg="grey")
        self.wall_height_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.wall_height_entry, "inches"))
        self.wall_height_entry.bind("<FocusOut>", lambda event: self.add_placeholder(self.wall_height_entry, "inches"))
        self.wall_height_entry.pack(pady=5)
        
        # Wall Color
        color_frame = tk.Frame(self.root)
        color_frame.pack(pady=5)

        tk.Label(color_frame, text="Wall Color:", font=("Arial", 12)).pack(side="left", padx=(0, 10))

        # Color Box
        self.color_box = tk.Label(color_frame, bg=self.wall_color, width=10, height=2)
        self.color_box.pack(side="left", padx=(0, 10))

        # Pick Color Button
        tk.Button(color_frame, text="Pick Color", command=self.pick_color, width=10, bg="#5F3FCA", fg="white", font=("Helvetica", 10, "bold"), relief="raised", padx=5, pady=5).pack(side="left")
        
        # Wall Preview Canvas
        self.preview_canvas = tk.Canvas(self.root, width=400, height=300, bg="white", highlightthickness=1, highlightbackground="black")
        self.preview_canvas.pack(pady=20)
        
        # Bind events to update the preview when width or height changes
        self.wall_width_entry.bind("<KeyRelease>", self.update_preview)
        self.wall_height_entry.bind("<KeyRelease>", self.update_preview)
        
        # Back and Submit Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", pady=10)

        # Back to Home Button (Left Side)
        tk.Button(button_frame, text="< Back to Home", command=self.return_to_home, width=15, bg="#69718A", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="left", padx=10)

        # Submit and Next Button (Right Side)
        tk.Button(button_frame, text="Submit and Next >", command=self.submit_wall_info, width=15, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="right", padx=10)

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def add_placeholder(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    def pick_color(self):
        color = colorchooser.askcolor()[1]  # Open color picker
        if color:
            self.wall_color = color
            self.color_box.config(bg=self.wall_color)
            self.update_preview()

    def update_preview(self, event=None):
        # Clear the canvas
        self.preview_canvas.delete("all")
        
        # Get width and height from entries
        try:
            wall_width = float(re.sub(r"[^0-9.]", "", self.wall_width_entry.get()).strip())
            wall_height = float(re.sub(r"[^0-9.]", "", self.wall_height_entry.get()).strip())
        except ValueError:
            return  # Do nothing if inputs are invalid
        
        # Calculate aspect ratio and scale to fit canvas
        canvas_width = 400
        canvas_height = 300
        ratio = min(canvas_width / wall_width, canvas_height / wall_height)
        scaled_width = wall_width * ratio
        scaled_height = wall_height * ratio
        
        # Draw the wall preview
        x0 = (canvas_width - scaled_width) / 2
        y0 = (canvas_height - scaled_height) / 2
        x1 = x0 + scaled_width
        y1 = y0 + scaled_height
        self.preview_canvas.create_rectangle(x0, y0, x1, y1, fill=self.wall_color, outline="black")
        
        # Draw height and width lines with labels
        self.preview_canvas.create_line(x0, y1, x0 - 10, y1, fill="black")  # Width line start
        self.preview_canvas.create_line(x1, y1, x1 + 10, y1, fill="black")  # Width line end
        self.preview_canvas.create_text((x0 + x1) / 2, y1 + 15, text=f"{wall_width} inches", anchor="n")
        
        self.preview_canvas.create_line(x0, y0, x0, y0 - 10, fill="black")  # Height line start
        self.preview_canvas.create_line(x0, y1, x0, y1 + 10, fill="black")  # Height line end
        self.preview_canvas.create_text(x0 - 15, (y0 + y1) / 2, text=f"{wall_height} inches", anchor="e", angle=90)
    
    def submit_wall_info(self):
        wall_name = self.wall_name_entry.get()
        wall_width_str = self.wall_width_entry.get()
        wall_height_str = self.wall_height_entry.get()
        
        # Validate inputs
        if wall_name == "" or wall_width_str == "" or wall_height_str == "":
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        try:
            wall_width = float(re.sub(r"[^0-9.]", "", wall_width_str).strip())
            wall_height = float(re.sub(r"[^0-9.]", "", wall_height_str).strip())
        except ValueError:
            messagebox.showerror("Error", "Width and height must be numbers.")
            return
        
        # Create a new wall object
        from gallery_wall_planner.models.wall import Wall
        wall = Wall(wall_name, wall_width, wall_height, self.wall_color)
        
        shared_state.add_wall(wall)

        print(wall.toString())
        
        # Navigate to PermanentObjectUI
        from gallery_wall_planner.gui.permanentObjectUI import PermanentObjectUI
        PermanentObjectUI(self.root, self.return_to_home)