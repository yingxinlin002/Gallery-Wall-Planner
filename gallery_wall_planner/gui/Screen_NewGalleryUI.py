import tkinter as tk
from tkinter import messagebox, colorchooser
import re
from gallery_wall_planner.models.wall import Wall  
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.gui.Screen_Base import Screen_Base
from gallery_wall_planner.gui.Popup_NewExhibit import Popup_NewExhibit

class Screen_NewGalleryUI(Screen_Base):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.wall_width = None
        self.wall_height = None
        self.wall_color = "white"  # Default wall color
        self.content_frame = None

        self.popup = None

        self.back_to_home_button = None
        self.submit_and_next_button = None
        self.color_picker_button = None

        # self.create_new_exhibit_popup()

    # def create_new_exhibit_popup(self):
    #     """Create initial popup window for new exhibit options"""
    #     self.popup = tk.Toplevel(self.AppMain.root)
    #     self.popup.title("New Exhibit")
    #     self.popup.geometry("300x150")
    #     self.center_popup(self.popup, 300, 150)

    #     # Add buttons to the popup window
    #     tk.Button(
    #         self.popup,
    #         text="Start from Scratch",
    #         command=self.start_from_scratch,
    #         width=20,
    #         bg="#5F3FCA",
    #         fg="white",
    #         font=("Helvetica", 12, "bold"),
    #         relief="raised",
    #         padx=10,
    #         pady=5
    #     ).pack(pady=10)

    #     tk.Button(
    #         self.popup,
    #         text="Load from an Existing Wall",
    #         command=self.load_from_existing,
    #         width=20,
    #         bg="#5F3FCA",
    #         fg="white",
    #         font=("Helvetica", 12, "bold"),
    #         relief="raised",
    #         padx=10,
    #         pady=5
    #     ).pack(pady=10)

    # def center_popup(self, popup, width, height):
    #     """Center the popup window on screen"""
    #     screen_width = popup.winfo_screenwidth()
    #     screen_height = popup.winfo_screenheight()
    #     x = (screen_width // 2) - (width // 2)
    #     y = (screen_height // 2) - (height // 2)
    #     popup.geometry(f"{width}x{height}+{x}+{y}")

    def start_from_scratch(self):
        """Handle starting a new wall from scratch"""
        print("Starting a new wall from scratch...")

    def load_from_existing(self):
        """Handle loading from existing wall"""
        print("Loading from existing wall...")
        # existing_walls = global_gallery.get_walls()
        # if not existing_walls:
        #     messagebox.showerror("Error", "No existing walls found.")
        # else:
        #     # Implement logic to select from existing walls
        #     messagebox.showinfo("Info", "Feature coming soon!")
        # self.popup.destroy()

    

    def load_content(self):
        """Show the wall creation form with centered inputs"""
        # for widget in self.AppMain.root.winfo_children():
        #     widget.destroy()

        print("Loading new gallery screen...")
        
        # Main container
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            main_frame,
            text="New Gallery Wall",
            font=("Arial", 24)
        ).pack(pady=(0, 20))
        
        # Centered form container
        form_container = tk.Frame(main_frame)
        form_container.pack()

        # Form frame with centered contents
        form_frame = tk.Frame(form_container)
        form_frame.pack()

        # Wall Name - Centered row
        name_frame = tk.Frame(form_frame)
        name_frame.pack(pady=5)
        tk.Label(
            name_frame,
            text="Wall Name:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.wall_name_entry = tk.Entry(name_frame, font=("Arial", 12), width=15)
        self.wall_name_entry.insert(0, "South Wall")
        self.wall_name_entry.config(fg="grey")
        self.wall_name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.wall_name_entry, "South Wall"))
        self.wall_name_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.wall_name_entry, "South Wall"))
        self.wall_name_entry.pack(side="left")
        
        # Wall Width - Centered row
        width_frame = tk.Frame(form_frame)
        width_frame.pack(pady=5)
        tk.Label(
            width_frame,
            text="Width (inches):",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.wall_width_entry = tk.Entry(width_frame, font=("Arial", 12), width=10)
        self.wall_width_entry.insert(0, "313")
        self.wall_width_entry.config(fg="grey")
        self.wall_width_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.wall_width_entry, "313"))
        self.wall_width_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.wall_width_entry, "313"))
        self.wall_width_entry.pack(side="left")
        
        # Wall Height - Centered row
        height_frame = tk.Frame(form_frame)
        height_frame.pack(pady=5)
        tk.Label(
            height_frame,
            text="Height (inches):",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.wall_height_entry = tk.Entry(height_frame, font=("Arial", 12), width=10)
        self.wall_height_entry.insert(0, "96")
        self.wall_height_entry.config(fg="grey")
        self.wall_height_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.wall_height_entry, "96"))
        self.wall_height_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.wall_height_entry, "96"))
        self.wall_height_entry.pack(side="left")
        
        # Wall Color - Centered row
        color_frame = tk.Frame(form_frame)
        color_frame.pack(pady=5)
        tk.Label(
            color_frame,
            text="Wall Color:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))

        self.color_box = tk.Label(color_frame, bg=self.wall_color, width=10, height=1)
        self.color_box.pack(side="left", padx=(0, 10))

        self.color_picker_button = tk.Button(
            color_frame,
            text="Pick",
            command=self.pick_color,
            width=5,
            bg="#5F3FCA",
            fg="white",
            font=("Helvetica", 10),
            relief="raised"
        )
        self.color_picker_button.pack(side="left")

        # Create a container for canvas and buttons
        canvas_button_container = tk.Frame(main_frame)
        canvas_button_container.pack(pady=(20, 0), fill="both", expand=True)

        # Wall Preview
        preview_frame = tk.Frame(canvas_button_container)
        preview_frame.pack(fill="both", expand=True)

        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=400,
            height=250,
            bg="white",
            highlightthickness=1,
            highlightbackground="black"
        )
        self.preview_canvas.pack()

        # Buttons at bottom of canvas container
        button_frame = tk.Frame(canvas_button_container)
        button_frame.pack(fill="x", pady=(10, 0))

        self.back_to_home_button = tk.Button(
            button_frame,
            text="< Back to Home",
            command=lambda: self.AppMain.switch_screen(ScreenType.HOME),
            width=15,
            bg="#69718A",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="raised"
        )
        self.back_to_home_button.pack(side="left", padx=10)

        self.submit_and_next_button = tk.Button(
            button_frame,
            text="Submit and Next >",
            command=self.submit_wall_info,
            width=15,
            bg="#5F3FCA",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="raised"
        )
        self.submit_and_next_button.pack(side="right", padx=10)

        # Bind events
        self.wall_width_entry.bind("<KeyRelease>", self.update_preview)
        self.wall_height_entry.bind("<KeyRelease>", self.update_preview)

        if len(self.AppMain.gallery.get_walls()) > 0:
            self.popup = Popup_NewExhibit(self.AppMain, self)
            self.popup.load_content()

        # Initial preview
        self.update_preview()

    def clear_placeholder(self, entry, placeholder):
        """Clear placeholder text"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def add_placeholder(self, entry, placeholder):
        """Add placeholder text"""
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    def pick_color(self):
        """Open color picker and update wall color"""
        color = colorchooser.askcolor()[1]
        if color:
            self.wall_color = color
            self.color_box.config(bg=self.wall_color)
            self.update_preview()

    def update_preview(self, event=None):
        """Update the wall preview canvas"""
        self.preview_canvas.delete("all")

        try:
            wall_width = float(re.sub(r"[^0-9.]", "", self.wall_width_entry.get()).strip())
            wall_height = float(re.sub(r"[^0-9.]", "", self.wall_height_entry.get()).strip())
        except ValueError:
            return

        canvas_width = 400
        canvas_height = 300
        ratio = min(canvas_width / wall_width, canvas_height / wall_height)
        scaled_width = wall_width * ratio
        scaled_height = wall_height * ratio

        x0 = (canvas_width - scaled_width) / 2
        y0 = (canvas_height - scaled_height) / 2
        x1 = x0 + scaled_width
        y1 = y0 + scaled_height

        # Draw wall
        self.preview_canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=self.wall_color,
            outline="black"
        )

        # Draw dimensions
        self.preview_canvas.create_line(x0, y1, x0 - 10, y1, fill="black")
        self.preview_canvas.create_line(x1, y1, x1 + 10, y1, fill="black")
        self.preview_canvas.create_text(
            (x0 + x1)/2, y1 + 15,
            text=f"{wall_width} inches",
            anchor="n"
        )

        self.preview_canvas.create_line(x0, y0, x0, y0 - 10, fill="black")
        self.preview_canvas.create_line(x0, y1, x0, y1 + 10, fill="black")
        self.preview_canvas.create_text(
            x0 - 15, (y0 + y1)/2,
            text=f"{wall_height} inches",
            anchor="e",
            angle=90
        )

    def submit_wall_info(self):
        """Validate and submit the new wall information"""
        wall_name = self.wall_name_entry.get()
        wall_width_str = self.wall_width_entry.get()
        wall_height_str = self.wall_height_entry.get()
        
        if not all([wall_name, wall_width_str, wall_height_str]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        try:
            wall_width = float(re.sub(r"[^0-9.]", "", wall_width_str).strip())
            wall_height = float(re.sub(r"[^0-9.]", "", wall_height_str).strip())
        except ValueError:
            messagebox.showerror("Error", "Width and height must be numbers.")
            return
        
        # Create and save the new wall
        new_wall = Wall(
            name=wall_name,
            width=wall_width,
            height=wall_height,
            color=self.wall_color
        )

        self.AppMain.gallery.add_wall(new_wall)
        self.AppMain.switch_screen(ScreenType.PERMANENT_OBJECT)
        
        # Navigate to PermanentObjectUI
        # from gallery_wall_planner.gui.permanentObjectUI import PermanentObjectUI
        # for widget in self.root.winfo_children():
        #     widget.destroy()
        # PermanentObjectUI(self.root, self.return_to_home, new_wall)

    