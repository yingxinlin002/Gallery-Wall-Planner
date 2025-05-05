import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog


from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.structures import Position, MeasureFrom, MeasureHorizontal, MeasureVertical
from typing import Optional

class PopupEditWallItem(PopupBase):
    def __init__(self, AppMain : AppMain, parent_button, *args, **kwargs):
        super().__init__(AppMain, "Edit Wall Item", 600, 400, *args, **kwargs)
        from gallery_wall_planner.gui.btn_wall_item import BTNWallItem
        self.parent_button: BTNWallItem = parent_button
        self.styles = get_ui_styles()
        self.current_position: Position = self.draggable_item.wall_object.position
        self.current_measure_from: MeasureFrom = MeasureFrom.EDGES
        self.current_measure_horizontal: MeasureHorizontal = MeasureHorizontal.LEFT
        self.current_measure_vertical: MeasureVertical = MeasureVertical.TOP
        
        # Load content after initialization
        self.load_content()
        
    @property
    def draggable_item(self):
        return self.parent_button.draggable_item

    def load_content(self):
        super().load_content()
        self.title_label = ttk.Label(self, text="Edit Wall Item", font=self.styles["title_font"])
        self.title_label.pack(pady=10, fill="x")

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(fill="both", expand=True, side="left")
        
        self.name_label = ttk.Label(self.left_frame, text="Name:")
        self.name_label.pack(pady=5)
        
        self.name_var = tk.StringVar(value=self.draggable_item.wall_object.name)
        self.name_entry = ttk.Entry(self.left_frame, textvariable=self.name_var)
        self.name_entry.pack(pady=5)
        
        self.width_label = ttk.Label(self.left_frame, text="Width:")
        self.width_label.pack(pady=5)
        
        self.width_var = tk.StringVar(value=self.draggable_item.wall_object.width)
        self.width_entry = ttk.Entry(self.left_frame, textvariable=self.width_var)
        self.width_entry.pack(pady=5)
        
        self.height_label = ttk.Label(self.left_frame, text="Height:")
        self.height_label.pack(pady=5)
        
        self.height_var = tk.StringVar(value=self.draggable_item.wall_object.height)
        self.height_entry = ttk.Entry(self.left_frame, textvariable=self.height_var)
        self.height_entry.pack(pady=5)

        if isinstance(self.draggable_item.wall_object, Artwork):
            self.artwork_label = ttk.Label(self.left_frame, text="Hanging Point:")
            self.artwork_label.pack(pady=5)
            
            self.artwork_hanging_point_var = tk.StringVar(value=self.draggable_item.wall_object.hanging_point)
            self.artwork_hanging_point_entry = ttk.Entry(self.left_frame, textvariable=self.artwork_hanging_point_var)
            self.artwork_hanging_point_entry.pack(pady=5)

            self.artwork_price_label = ttk.Label(self.left_frame, text="Price:")
            self.artwork_price_label.pack(pady=5)
            
            self.artwork_price_var = tk.StringVar(value=self.draggable_item.wall_object.price)
            self.artwork_price_entry = ttk.Entry(self.left_frame, textvariable=self.artwork_price_var)
            self.artwork_price_entry.pack(pady=5)

            self.artwork_image_label = ttk.Label(self.left_frame, text="Image:")
            self.artwork_image_label.pack(pady=5)
            
            self.image_path = tk.StringVar(value=self.draggable_item.wall_object.image_path)
            self.image_entry = ttk.Entry(self.left_frame, textvariable=self.image_path)
            self.image_entry.pack(pady=5)

            self.image_button = ttk.Button(self.left_frame, text="Browse", command=self.upload_image)
            self.image_button.pack(pady=5)


        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(fill="both", expand=True, side="right")

        self.position_label = ttk.Label(self.right_frame, text="Edit Position:")
        self.position_label.pack(pady=5)

        measure_from_label = ttk.Label(self.right_frame, text="Measure From:")
        measure_from_label.pack(pady=5)

        self.measure_from_var = tk.StringVar(value=MeasureFrom.EDGES.name)
        ttk.Radiobutton(self.right_frame, text="Edges", variable=self.measure_from_var, value=MeasureFrom.EDGES.name).pack(anchor="w", padx=20)
        ttk.Radiobutton(self.right_frame, text="Center", variable=self.measure_from_var, value=MeasureFrom.CENTER.name).pack(anchor="w", padx=20)

        self.measure_from_var.trace_add("write", lambda *_: self.update_position())

        self.measure_horizontal_var = tk.StringVar(value=MeasureHorizontal.LEFT.name)
        ttk.Radiobutton(self.right_frame, text="Left", variable=self.measure_horizontal_var, value=MeasureHorizontal.LEFT.name).pack(anchor="w", padx=20)
        ttk.Radiobutton(self.right_frame, text="Right", variable=self.measure_horizontal_var, value=MeasureHorizontal.RIGHT.name).pack(anchor="w", padx=20)

        self.measure_horizontal_var.trace_add("write", lambda *_: self.update_position())

        self.measure_vertical_var = tk.StringVar(value=MeasureVertical.TOP.name)
        ttk.Radiobutton(self.right_frame, text="Top", variable=self.measure_vertical_var, value=MeasureVertical.TOP.name).pack(anchor="w", padx=20)
        ttk.Radiobutton(self.right_frame, text="Bottom", variable=self.measure_vertical_var, value=MeasureVertical.BOTTOM.name).pack(anchor="w", padx=20)

        self.measure_vertical_var.trace_add("write", lambda *_: self.update_position())

        self.horizontal_distance_var = tk.StringVar(value=str(self.current_position.x))
        self.horizontal_distance_label = ttk.Label(self.right_frame, text="Horizontal Distance:")
        self.horizontal_distance_label.pack(pady=5)
        self.horizontal_distance_entry = ttk.Entry(self.right_frame, textvariable=self.horizontal_distance_var)
        self.horizontal_distance_entry.pack(pady=5)

        self.vertical_distance_var = tk.StringVar(value=str(self.current_position.y))
        self.vertical_distance_label = ttk.Label(self.right_frame, text="Vertical Distance:")
        self.vertical_distance_label.pack(pady=5)
        self.vertical_distance_entry = ttk.Entry(self.right_frame, textvariable=self.vertical_distance_var)
        self.vertical_distance_entry.pack(pady=5)
        
        self.save_button = ttk.Button(self.left_frame, text="Save", command=self.save)
        self.save_button.pack(pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path.set(file_path)
            messagebox.showinfo("Success", "Image uploaded successfully!")


    def save(self):
        self.update_position()
        if isinstance(self.draggable_item.wall_object, Artwork):
            wall_object = Artwork(
                name=self.name_var.get(),
                width=float(self.width_var.get()),
                height=float(self.height_var.get()),
                image_path=self.draggable_item.wall_object.image_path,
                price=self.draggable_item.wall_object.price,
                hanging_point=float(self.artwork_hanging_point_var.get())
            )
        else:
            wall_object = PermanentObject(
                name=self.name_var.get(),
                width=float(self.width_var.get()),
                height=float(self.height_var.get()),
                image_path=self.draggable_item.wall_object.image_path
            )
        wall_object.position = self.current_position
        if self.parent_button.update_wall_object(wall_object):
            self.on_close()

    def update_position(self):
        self.current_position = Position(0,0)
        if self.current_measure_from is MeasureFrom.EDGES:
            if self.current_measure_horizontal is MeasureHorizontal.LEFT:
                self.current_position.x = float(self.horizontal_distance_var.get())
            else:
                self.current_position.x = self.AppMain.gallery.current_wall.width - float(self.horizontal_distance_var.get()) - self.draggable_item.wall_object.width
            if self.current_measure_vertical is MeasureVertical.TOP:
                self.current_position.y = float(self.vertical_distance_var.get())
            else:
                self.current_position.y = self.AppMain.gallery.current_wall.height - float(self.vertical_distance_var.get()) - self.draggable_item.wall_object.height
        else:
            if self.current_measure_horizontal is MeasureHorizontal.LEFT:
                self.current_position.x = float(self.horizontal_distance_var.get()) - self.draggable_item.wall_object.width / 2
            else:
                self.current_position.x = self.AppMain.gallery.current_wall.width - float(self.horizontal_distance_var.get()) - self.draggable_item.wall_object.width / 2
            if self.current_measure_vertical is MeasureVertical.TOP:
                self.current_position.y = float(self.vertical_distance_var.get()) - self.draggable_item.wall_object.height / 2
            else:
                self.current_position.y = self.AppMain.gallery.current_wall.height - float(self.vertical_distance_var.get()) - self.draggable_item.wall_object.height / 2
        
        if self.measure_from_var.get() == MeasureFrom.EDGES.name:
            self.current_measure_from = MeasureFrom.EDGES
            if self.measure_horizontal_var.get() == MeasureHorizontal.LEFT.name:
                self.current_measure_horizontal = MeasureHorizontal.LEFT
                self.horizontal_distance_var.set(self.current_position.x)
            else:
                self.current_measure_horizontal = MeasureHorizontal.RIGHT
                self.horizontal_distance_var.set(self.AppMain.gallery.current_wall.width - self.current_position.x - self.draggable_item.wall_object.width)
            if self.measure_vertical_var.get() == MeasureVertical.TOP.name:
                self.current_measure_vertical = MeasureVertical.TOP
                self.vertical_distance_var.set(self.current_position.y)
            else:
                self.current_measure_vertical = MeasureVertical.BOTTOM
                self.vertical_distance_var.set(self.AppMain.gallery.current_wall.height - self.current_position.y - self.draggable_item.wall_object.height)
        else:
            self.current_measure_from = MeasureFrom.CENTER
            if self.measure_horizontal_var.get() == MeasureHorizontal.LEFT.name:
                self.current_measure_horizontal = MeasureHorizontal.LEFT
                self.horizontal_distance_var.set(self.current_position.x + self.draggable_item.wall_object.width / 2)
            else:
                self.current_measure_horizontal = MeasureHorizontal.RIGHT
                self.horizontal_distance_var.set(self.AppMain.gallery.current_wall.width - self.current_position.x - self.draggable_item.wall_object.width / 2)
            if self.measure_vertical_var.get() == MeasureVertical.TOP.name:
                self.current_measure_vertical = MeasureVertical.TOP
                self.vertical_distance_var.set(self.current_position.y + self.draggable_item.wall_object.height / 2)
            else:
                self.current_measure_vertical = MeasureVertical.BOTTOM
                self.vertical_distance_var.set(self.AppMain.gallery.current_wall.height - self.current_position.y - self.draggable_item.wall_object.height / 2)
            
            