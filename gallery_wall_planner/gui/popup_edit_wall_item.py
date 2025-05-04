import tkinter as tk
from tkinter import ttk, messagebox
from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.gui.ui_styles import get_ui_styles

class PopupEditWallItem(PopupBase):
    def __init__(self, AppMain: AppMain, parent_button, *args, **kwargs):
        super().__init__(AppMain, "Edit Wall Item", 300, 500, *args, **kwargs)
        from gallery_wall_planner.gui.btn_wall_item import BTNWallItem
        self.parent_button: BTNWallItem = parent_button
        self.styles = get_ui_styles()

        self.load_content()
        
    @property
    def draggable_item(self):
        return self.parent_button.draggable_item

    def load_content(self):
        self.title_label = ttk.Label(self, text="Edit Wall Item", font=self.styles["title_font"])
        self.title_label.pack(pady=10)

        self.name_label = ttk.Label(self, text="Name:")
        self.name_label.pack(pady=5)

        self.name_var = tk.StringVar(value=self.draggable_item.wall_object.name)
        self.name_entry = ttk.Entry(self, textvariable=self.name_var)
        self.name_entry.pack(pady=5)

        self.width_label = ttk.Label(self, text="Width:")
        self.width_label.pack(pady=5)

        self.width_var = tk.StringVar(value=self.draggable_item.wall_object.width)
        self.width_entry = ttk.Entry(self, textvariable=self.width_var)
        self.width_entry.pack(pady=5)

        self.height_label = ttk.Label(self, text="Height:")
        self.height_label.pack(pady=5)

        self.height_var = tk.StringVar(value=self.draggable_item.wall_object.height)
        self.height_entry = ttk.Entry(self, textvariable=self.height_var)
        self.height_entry.pack(pady=5)

        if isinstance(self.draggable_item.wall_object, Artwork):
            self.artwork_label = ttk.Label(self, text="Hanging Point:")
            self.artwork_label.pack(pady=5)

            self.artwork_hanging_point_var = tk.StringVar(value=self.draggable_item.wall_object.hanging_point)
            self.artwork_hanging_point_entry = ttk.Entry(self, textvariable=self.artwork_hanging_point_var)
            self.artwork_hanging_point_entry.pack(pady=5)

        # Coordinates for all 4 corners (Bottom Left, Top Left, Top Right, Bottom Right)
        self.bl_var = tk.StringVar()
        self.tl_var = tk.StringVar()
        self.tr_var = tk.StringVar()
        self.br_var = tk.StringVar()
        self.center_var = tk.StringVar()

        # Update coordinates for corners and center based on current position
        self.update_coordinates()

        # Display (x, y) for corners and center
        ttk.Label(self, text="Bottom Left:").pack(pady=5)
        self.bl_entry = ttk.Entry(self, textvariable=self.bl_var, state="normal")  # Editable
        self.bl_entry.pack(pady=5)
        self.bl_entry.bind("<FocusOut>", lambda e: self.handle_manual_edit(self.bl_var, "bl"))

        ttk.Label(self, text="Top Left:").pack(pady=5)
        self.tl_entry = ttk.Entry(self, textvariable=self.tl_var, state="normal")  # Editable
        self.tl_entry.pack(pady=5)
        self.tl_entry.bind("<FocusOut>", lambda e: self.handle_manual_edit(self.tl_var, "tl"))

        ttk.Label(self, text="Top Right:").pack(pady=5)
        self.tr_entry = ttk.Entry(self, textvariable=self.tr_var, state="normal")  # Editable
        self.tr_entry.pack(pady=5)
        self.tr_entry.bind("<FocusOut>", lambda e: self.handle_manual_edit(self.tr_var, "tr"))

        ttk.Label(self, text="Bottom Right:").pack(pady=5)
        self.br_entry = ttk.Entry(self, textvariable=self.br_var, state="normal")  # Editable
        self.br_entry.pack(pady=5)
        self.br_entry.bind("<FocusOut>", lambda e: self.handle_manual_edit(self.br_var, "br"))

        ttk.Label(self, text="Center:").pack(pady=5)
        self.center_entry = ttk.Entry(self, textvariable=self.center_var, state="normal")  # Editable
        self.center_entry.pack(pady=5)
        self.center_entry.bind("<FocusOut>", lambda e: self.handle_manual_edit(self.center_var, "center"))

        # Save Button
        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.save_button.pack(pady=10)

        # Bind coordinate changes to update canvas
        self.width_entry.bind("<FocusOut>", lambda e: self.update_coordinates())
        self.height_entry.bind("<FocusOut>", lambda e: self.update_coordinates())

        # Ensure that the popup window is large enough to accommodate all elements
        self.geometry("350x450")  # Adjust the size based on the number of widgets


    def update_coordinates(self):
        # Update coordinates for all 5 positions (corners and center)
        w = float(self.width_var.get())
        h = float(self.height_var.get())
        
        # Use dot notation to access 'x' and 'y' attributes of the Position object
        position = self.draggable_item.wall_object.position
        x = position.x  # Assuming 'Position' class has 'x' and 'y' attributes
        y = position.y  # Same for 'y'

        # Calculate the corners and center
        bl = (x, y)
        tl = (x, y + h)
        tr = (x + w, y + h)
        br = (x + w, y)
        center = (x + w / 2, y + h / 2)

        # Update the variables that are displayed
        self.bl_var.set(f"{bl[0]:.2f}, {bl[1]:.2f}")
        self.tl_var.set(f"{tl[0]:.2f}, {tl[1]:.2f}")
        self.tr_var.set(f"{tr[0]:.2f}, {tr[1]:.2f}")
        self.br_var.set(f"{br[0]:.2f}, {br[1]:.2f}")
        self.center_var.set(f"{center[0]:.2f}, {center[1]:.2f}")


    def handle_manual_edit(self, entry_var, coordinate_type):
        try:
            # Get the updated value from the entry field
            new_value = float(entry_var.get())

            # Update position based on the coordinate being edited
            if coordinate_type == "bl":  # Bottom Left
                self.draggable_item.wall_object.position.x = new_value
                self.draggable_item.wall_object.position.y = new_value
            elif coordinate_type == "tl":  # Top Left
                self.draggable_item.wall_object.position.y = new_value
            elif coordinate_type == "tr":  # Top Right
                self.draggable_item.wall_object.position.x = new_value
            elif coordinate_type == "br":  # Bottom Right
                self.draggable_item.wall_object.position.x = new_value
            elif coordinate_type == "center":  # Center
                self.draggable_item.wall_object.position.x = new_value
                self.draggable_item.wall_object.position.y = new_value

            # Recalculate corners and center when any coordinate is updated
            self.update_coordinates()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric value.")

    def save(self):
        try:
            # Save the updated coordinates
            width = float(self.width_var.get())
            height = float(self.height_var.get())

            # Create new wall object based on updated data
            if isinstance(self.draggable_item.wall_object, Artwork):
                wall_object = Artwork(
                    name=self.name_var.get(),
                    width=width,
                    height=height,
                    image_path=self.draggable_item.wall_object.image_path,
                    price=self.draggable_item.wall_object.price,
                    hanging_point=float(self.artwork_hanging_point_var.get())
                )
            else:
                wall_object = PermanentObject(
                    name=self.name_var.get(),
                    width=width,
                    height=height,
                    image_path=self.draggable_item.wall_object.image_path
                )

            wall_object.position = self.draggable_item.wall_object.position
            self.parent_button.update_wall_object(wall_object)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numeric values.")
