import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.screen_base import ScreenBase
from gallery_wall_planner.gui.ui_styles import (
    apply_primary_button_style,
    apply_header_label_style,
    get_ui_styles
)
from gallery_wall_planner.gui.wall_canvas import WallCanvas
from gallery_wall_planner.models.structures import WallPosition, CanvasDimensions, Padding
from gallery_wall_planner.gui.collapsible_menu import CollapsibleMenu
from gallery_wall_planner.gui.btn_wall_item import BTNWallItem
from gallery_wall_planner.models.permanent_object import PermanentObject
from tkinter import filedialog
from gallery_wall_planner.gui.scroll_box_vertical import ScrollBoxVertical


class ScreenLockObjectsUI(ScreenBase):
    def __init__(self, AppMain: AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.name = "Lock Objects"
        self.styles = get_ui_styles()
        self.wall_list = []  # Replaced artwork list with wall list
        self.sidebar_visible = True
        self.sidebar_width = 300
        self.sidebar_animation_running = False
        self.wall_canvas: WallCanvas = None
        self.selected_wall: WallPosition = None  # Updated to WallPosition
        self.wall_space = None  # Initialize wall_space as None
        self.tab_frame = None
        self.wall_tab_btn = None  # Replaced artwork tab button with wall tab button
        self.actions_frame = None

    def add_permanent_object(self, name, width, height):
        """Add permanent object to the wall and place it visually on the canvas."""
        if not name or not width or not height:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        width = float(width)
        height = float(height)
        permanent_object = PermanentObject(name=name, width=width, height=height)

        # Debugging: Check if object is created
        print(f"Creating Permanent Object: {permanent_object.name}, Width: {width}, Height: {height}")

        # Add to the wall
        self.AppMain.gallery.current_wall.add_permanent_object(permanent_object)

        # Debugging: Check if object is added to the wall
        print(f"Permanent Object Added to Wall: {self.AppMain.gallery.current_wall.permanent_objects_dict}")

        # Clear and recreate canvas (or its contents)
        self.wall_canvas.clear_all_items()  # Custom method to clear canvas if necessary
        self.wall_canvas.add_draggables(self.AppMain.gallery.current_wall.permanent_objects_dict)

        # Update the UI (list of objects)
        self.create_wall_list_frame()

        messagebox.showinfo("Success", "Permanent object added successfully!")



    def create_collapsible_menu(self, parent, title, expanded=True):
        """Create and return a collapsible menu frame."""
        menu_frame = tk.Frame(parent, bg="#e0e0e0", bd=1, relief="raised")
        menu_frame.pack(fill="x", pady=2)

        header = tk.Frame(menu_frame, bg="#e0e0e0")
        header.pack(fill="x")

        content_frame = tk.Frame(menu_frame, bg="white")
        toggle_btn = ttk.Button(header, text="▼" if expanded else "▶",
                                command=lambda: self.toggle_menu(menu_frame, toggle_btn, content_frame),
                                style="TButton")  # Updated to use ttk style for consistent theming
        toggle_btn.pack(side="left")

        tk.Label(header, text=title, font=self.styles["label_font"], bg="#e0e0e0").pack(side="left", padx=5)

        if expanded:
            content_frame.pack(fill="x")

        return content_frame

    def load_content(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        back_button = tk.Button(main_frame,
                                text="< Back to Wall Selection",
                                command=lambda: self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE),
                                bg=self.styles["bg_secondary"],
                                fg=self.styles["fg_white"],
                                font=self.styles["button_font"],
                                padx=self.styles["button_padx"],
                                pady=self.styles["button_pady"])
        back_button.pack(side="top", anchor="nw", padx=10, pady=10)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        self.collapsible_menu = CollapsibleMenu(content_frame, "")
        self.collapsible_menu.load_content()
        self.collapsible_menu.pack(side="left", fill="y")

        self.wall_tab_frame = self.create_collapsible_menu(
            self.collapsible_menu.menu_frame, "Permanent Objects", expanded=True)  # Changed title to Permanent Objects
        self.create_wall_list_frame()  # Updated to wall list frame

        self.actions_frame = tk.Frame(self.collapsible_menu.menu_frame)
        self.actions_frame.pack(side="bottom", fill="x")
        header = tk.Frame(self.actions_frame, bg="#e0e0e0")
        header.pack(fill="x")

        tk.Label(header,
                 text="Actions",
                 font=self.styles["label_font"],
                 bg="#e0e0e0").pack(side="left", padx=5)

        manual_button = tk.Button(self.actions_frame,
                                  text="Add Permanent Object",  # Changed button text
                                  command=self.open_permanent_object_popup,  # Open the new popup for permanent objects
                                  bg=self.styles["bg_info"],
                                  fg=self.styles["fg_white"],
                                  font=self.styles["button_font"],
                                  padx=self.styles["button_padx"],
                                  pady=self.styles["button_pady"])
        manual_button.pack(pady=5, fill="x")

        # Replacing "Even Spacing" Button with "Back to Home"
        back_to_home_button = tk.Button(self.actions_frame,
                                        text="< Back to Home",
                                        command=lambda: self.AppMain.switch_screen(ScreenType.HOME),
                                        bg=self.styles["bg_primary"],
                                        fg=self.styles["fg_white"],
                                        font=self.styles["button_font"],
                                        padx=self.styles["button_padx"],
                                        pady=self.styles["button_pady"])
        back_to_home_button.pack(pady=5, fill="x")

        # Replacing "Calculate Installation Instruction" Button with "Save and Next"
        save_and_next_button = tk.Button(self.actions_frame,
                                         text="Save and Next >",
                                         command=self.save_and_continue,
                                         bg=self.styles["bg_primary"],
                                         fg=self.styles["fg_white"],
                                         font=self.styles["button_font"],
                                         padx=self.styles["button_padx"],
                                         pady=self.styles["button_pady"])
        save_and_next_button.pack(side="bottom", pady=10, fill="x")

        # Replacing Canvas Section
        canvas_frame = tk.Frame(content_frame)  # Switched back to tk.Frame to avoid ttk issues
        canvas_frame.pack(side="right", fill="both", expand=True)

        canvas_dimensions = CanvasDimensions(self.AppMain.root.winfo_width() - 400, self.AppMain.root.winfo_height() - 200, 50, Padding(10, 10, 10, 10))
        self.wall_canvas = WallCanvas(self.AppMain, canvas_frame, canvas_dimensions)
        self.wall_canvas.load_content()
        self.wall_canvas.add_draggables(self.AppMain.gallery.current_wall.permanent_objects_dict)  # Replaced with wall-related dictionary
        self.wall_canvas.add_fixed_items(self.AppMain.gallery.current_wall.wall_lines_dict)  # Replaced with wall-related dictionary

    def open_permanent_object_popup(self):
        """Open a popup to add a new permanent object."""
        popup = Toplevel(self.AppMain.root)
        popup.title("Add Permanent Object")

        # Create the form fields for permanent object
        name_label = tk.Label(popup, text="Name")
        name_label.pack(padx=10, pady=5)
        name_entry = tk.Entry(popup)
        name_entry.pack(padx=10, pady=5)

        width_label = tk.Label(popup, text="Width (inches)")
        width_label.pack(padx=10, pady=5)
        width_entry = tk.Entry(popup)
        width_entry.pack(padx=10, pady=5)

        height_label = tk.Label(popup, text="Height (inches)")
        height_label.pack(padx=10, pady=5)
        height_entry = tk.Entry(popup)
        height_entry.pack(padx=10, pady=5)

        image_label = tk.Label(popup, text="Upload Image (optional)")
        image_label.pack(padx=10, pady=5)
        browse_button = tk.Button(popup, text="Browse", command=lambda: self.upload_image(popup))
        browse_button.pack(padx=10, pady=5)

        submit_button = tk.Button(popup, text="Add", command=lambda: (print("Button clicked"), self.add_permanent_object(name_entry.get(), width_entry.get(), height_entry.get())))
        submit_button.pack(pady=10)

    def upload_image(self, popup):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            messagebox.showinfo("Success", "Image uploaded successfully!")

    def add_permanent_object(self, name, width, height):
        """Add permanent object to the wall and place it visually on the canvas."""
        print(f"add_permanent_object called with: {name}, {width}, {height}")

        if not name or not width or not height:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        width = float(width)
        height = float(height)
        permanent_object = PermanentObject(name=name, width=width, height=height)

        # Debugging: Check if object is created
        print(f"Creating Permanent Object: {permanent_object.name}, Width: {width}, Height: {height}")

        # Add to the wall
        self.AppMain.gallery.current_wall.add_permanent_object(permanent_object)

        # Debugging: Check if object is added to the wall
        print(f"Permanent Object Added to Wall: {self.AppMain.gallery.current_wall.permanent_objects_dict}")

        # Refresh the canvas by adding the new object (re-populate the draggable objects)
        self.wall_canvas.add_draggables(self.AppMain.gallery.current_wall.permanent_objects_dict)

        # Update the list on the left-hand side
        self.create_wall_list_frame()

        # Inform the user that the object was added successfully
        messagebox.showinfo("Success", "Permanent object added successfully!")

        
    def save_and_continue(self):
        """Proceed to next screen after checking for collisions.""" 
        if self.wall_canvas.check_all_collisions():
            popup = Toplevel(self.AppMain.root)
            popup.title("Collision Detected")
            ttk.Label(popup, text="The program has identified an impossible layout. Would you like to keep editing?").pack(padx=10, pady=10)
            btn_frame = tk.Frame(popup)
            btn_frame.pack(pady=10)
            btn_edit = ttk.Button(btn_frame, text="Keep Editing", command=popup.destroy)
            btn_save = ttk.Button(btn_frame, text="Continue Anyway", command=lambda: (popup.destroy(), self.continue_to_next()))
            apply_primary_button_style(btn_edit)
            apply_primary_button_style(btn_save)
            btn_edit.pack(side="left", padx=5)
            btn_save.pack(side="left", padx=5)
        else:
            self.continue_to_next()

    def continue_to_next(self):
        """Proceed to the next screen.""" 
        self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)

    def create_wall_list_frame(self):
        """Create the frame for displaying imported walls in the collapsible menu.""" 
        self.wall_list = []  # Clear existing list
        self.wall_scroll_box = ScrollBoxVertical(self.wall_tab_frame)
        self.wall_scroll_box.load_content()
        self.wall_scroll_box.pack(side="left", fill="both", expand=True)

        if hasattr(self.AppMain.gallery.current_wall, 'walls') and self.AppMain.gallery.current_wall.walls:
            for wall in self.AppMain.gallery.current_wall.walls:  # Iterating over walls instead of artwork
                self.add_wall_item(self.wall_scroll_box.scrollable_frame, wall)
        else:
            tk.Label(self.wall_scroll_box.scrollable_frame, text="No objects added yet", fg="gray").pack(pady=20)

    def add_wall_item(self, parent_frame, wall):
        """Add a single wall item to the frame.""" 
        btn = BTNWallItem(parent_frame, wall)  # Using BTNWallItem instead of artwork button
        btn.pack(side="top", fill="x", padx=5, pady=5)
        btn.load_content()
