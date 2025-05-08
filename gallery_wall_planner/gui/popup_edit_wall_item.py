import tkinter as tk
from tkinter import ttk


from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.structures import Position, MeasureFrom, MeasureHorizontal, MeasureVertical
from gallery_wall_planner.models.wall_object import WallObject
from typing import Union, Optional

class PopupEditWallItem(PopupBase):
    def __init__(self, 
            app_main : AppMain, 
            wall_object : Union[Artwork, PermanentObject, None], 
            screen_type : ScreenType, 
            is_artwork : Optional[bool] = None,
            *args, **kwargs):
        super().__init__(app_main, "Edit Wall Item", 700, 600, *args, **kwargs)
        self.screen_type: ScreenType = screen_type
        self.is_artwork: Optional[bool] = is_artwork
        self.wall_object: Union[Artwork, PermanentObject] = None
        self.is_new: bool = False
        if wall_object is None:
            self.is_new = True
            if is_artwork:
                self.wall_object = Artwork(
                    name="New Artwork",
                    width=30,
                    height=30,
                    image_path="",
                    price=0,
                    hanging_point=0,
                )
            else:
                self.wall_object = PermanentObject(
                    name="New Permanent Object",
                    width=30,
                    height=30,
                )
        else:
            self.wall_object = wall_object
        self.styles = get_ui_styles()
        self.current_position: Position = self.wall_object.position
        self.current_width: float = self.wall_object.width
        self.current_height: float = self.wall_object.height
        self.current_measure_from: MeasureFrom = MeasureFrom.EDGES
        self.current_measure_horizontal: MeasureHorizontal = MeasureHorizontal.LEFT
        self.current_measure_vertical: MeasureVertical = MeasureVertical.TOP
        
        # Load content after initialization
        self.load_content()
        
    def load_content(self):
        super().load_content()
        self.title_label = ttk.Label(self, text="Edit Wall Item", font=self.styles["title_font"])
        self.title_label.pack(pady=10, fill="x")

        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(fill="both", expand=True, side="left")
        
        self.name_label = ttk.Label(self.left_frame, text="Name:")
        self.name_label.pack(pady=5)
        
        self.name_var = tk.StringVar(value=self.wall_object.name)
        self.name_entry = ttk.Entry(self.left_frame, textvariable=self.name_var)
        self.name_entry.pack(pady=5)
        
        self.width_label = ttk.Label(self.left_frame, text="Width:")
        self.width_label.pack(pady=5)
        
        self.width_var = tk.StringVar(value=self.current_width)
        self.width_entry = ttk.Entry(self.left_frame, textvariable=self.width_var)
        self.width_entry.pack(pady=5)
        
        self.height_label = ttk.Label(self.left_frame, text="Height:")
        self.height_label.pack(pady=5)
        
        self.height_var = tk.StringVar(value=self.current_height)
        self.height_entry = ttk.Entry(self.left_frame, textvariable=self.height_var)
        self.height_entry.pack(pady=5)

        if isinstance(self.wall_object, Artwork):
            self.artwork_label = ttk.Label(self.left_frame, text="Hanging Point:")
            self.artwork_label.pack(pady=5)
            
            self.artwork_hanging_point_var = tk.StringVar(value=self.wall_object.hanging_point)
            self.artwork_hanging_point_entry = ttk.Entry(self.left_frame, textvariable=self.artwork_hanging_point_var)
            self.artwork_hanging_point_entry.pack(pady=5)

            self.artwork_price_label = ttk.Label(self.left_frame, text="Price:")
            self.artwork_price_label.pack(pady=5)
            
            self.artwork_price_var = tk.StringVar(value=self.wall_object.price)
            self.artwork_price_entry = ttk.Entry(self.left_frame, textvariable=self.artwork_price_var)
            self.artwork_price_entry.pack(pady=5)

        self.artwork_image_label = ttk.Label(self.left_frame, text="Image:")
        self.artwork_image_label.pack(pady=5)

        self.image_path_var = tk.StringVar(value=self.wall_object.image_path)
        self.image_entry = ttk.Entry(self.left_frame, textvariable=self.image_path_var)
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

        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill="x", side="bottom")
        
        self.save_button = ttk.Button(self.bottom_frame, text="Save", command=self.save)
        self.save_button.pack(side="left", padx=10)

        self.delete_button = ttk.Button(self.bottom_frame, text="Delete", command=self.delete)
        self.delete_button.pack(side="right", padx=10)

    def upload_image(self):
        file_path = self.filedialog_askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path_var.set(file_path)
            self.messagebox_showinfo("Success", "Image uploaded successfully!")

    def delete(self):
        if isinstance(self.wall_object, PermanentObject):
            self.app_main.gallery.current_wall.remove_permanent_object(self.wall_object)
        elif isinstance(self.wall_object, Artwork):
            self.app_main.gallery.current_wall.remove_artwork(self.wall_object)
        self.app_main.switch_screen(self.screen_type)
        self.on_close()

    def save(self):
        self.update_position()
        if isinstance(self.wall_object, Artwork):
            wall_object = Artwork(
                name=self.name_var.get(),
                width=float(self.width_var.get()),
                height=float(self.height_var.get()),
                image_path=self.image_path_var.get(),
                price=float(self.artwork_price_var.get()),
                hanging_point=float(self.artwork_hanging_point_var.get())
            )
        else:
            wall_object = PermanentObject(
                name=self.name_var.get(),
                width=float(self.width_var.get()),
                height=float(self.height_var.get()),
                image_path=self.image_path_var.get()
            )
        wall_object.position = self.current_position
        if self.is_new and wall_object.id in self.app_main.gallery.current_wall.permanent_objects_dict:
            self.messagebox_showerror("Error", "Wall Object already exists")
            return
        if self.app_main.gallery.current_wall.check_object_collision(wall_object, [self.wall_object.id]):
            if not self.messagebox_askyesno("Error", "Object collides with another object. Do you want to continue?"):
                return
        if self.is_new:
            if isinstance(self.wall_object, Artwork):
                self.app_main.gallery.current_wall.add_artwork(wall_object)
            else:
                self.app_main.gallery.current_wall.add_permanent_object(wall_object)
        else:
            self.app_main.gallery.current_wall.update_wall_item(self.wall_object.id, wall_object)
        self.app_main.switch_screen(self.screen_type)
        self.on_close()

    def update_position(self):
        self.current_position = Position(0,0)
        self.current_width = float(self.width_var.get())
        self.current_height = float(self.height_var.get())
        if self.current_measure_from is MeasureFrom.EDGES:
            if self.current_measure_horizontal is MeasureHorizontal.LEFT:
                self.current_position.x = float(self.horizontal_distance_var.get())
            else:
                self.current_position.x = self.app_main.gallery.current_wall.width - float(self.horizontal_distance_var.get()) - self.current_width
            if self.current_measure_vertical is MeasureVertical.TOP:
                self.current_position.y = float(self.vertical_distance_var.get())
            else:
                self.current_position.y = self.app_main.gallery.current_wall.height - float(self.vertical_distance_var.get()) - self.current_height
        else:
            if self.current_measure_horizontal is MeasureHorizontal.LEFT:
                self.current_position.x = float(self.horizontal_distance_var.get()) - self.current_width / 2
            else:
                self.current_position.x = self.app_main.gallery.current_wall.width - float(self.horizontal_distance_var.get()) - self.current_width / 2
            if self.current_measure_vertical is MeasureVertical.TOP:
                self.current_position.y = float(self.vertical_distance_var.get()) - self.current_height / 2
            else:
                self.current_position.y = self.app_main.gallery.current_wall.height - float(self.vertical_distance_var.get()) - self.current_height / 2
        
        self.current_position.x, self.current_position.y = self.app_main.gallery.current_wall.enforce_boundaries(self.current_position.x, self.current_position.y, self.current_width, self.current_height)

        if self.measure_from_var.get() == MeasureFrom.EDGES.name:
            self.current_measure_from = MeasureFrom.EDGES
            if self.measure_horizontal_var.get() == MeasureHorizontal.LEFT.name:
                self.current_measure_horizontal = MeasureHorizontal.LEFT
                self.horizontal_distance_var.set(self.current_position.x)
            else:
                self.current_measure_horizontal = MeasureHorizontal.RIGHT
                self.horizontal_distance_var.set(self.app_main.gallery.current_wall.width - self.current_position.x - self.current_width)
            if self.measure_vertical_var.get() == MeasureVertical.TOP.name:
                self.current_measure_vertical = MeasureVertical.TOP
                self.vertical_distance_var.set(self.current_position.y)
            else:
                self.current_measure_vertical = MeasureVertical.BOTTOM
                self.vertical_distance_var.set(self.app_main.gallery.current_wall.height - self.current_position.y - self.current_height)
        else:
            self.current_measure_from = MeasureFrom.CENTER
            if self.measure_horizontal_var.get() == MeasureHorizontal.LEFT.name:
                self.current_measure_horizontal = MeasureHorizontal.LEFT
                self.horizontal_distance_var.set(self.current_position.x + self.current_width / 2)
            else:
                self.current_measure_horizontal = MeasureHorizontal.RIGHT
                self.horizontal_distance_var.set(self.app_main.gallery.current_wall.width - self.current_position.x - self.current_width / 2)
            if self.measure_vertical_var.get() == MeasureVertical.TOP.name:
                self.current_measure_vertical = MeasureVertical.TOP
                self.vertical_distance_var.set(self.current_position.y + self.current_height / 2)
            else:
                self.current_measure_vertical = MeasureVertical.BOTTOM
                self.vertical_distance_var.set(self.app_main.gallery.current_wall.height - self.current_position.y - self.current_height / 2)
            
            