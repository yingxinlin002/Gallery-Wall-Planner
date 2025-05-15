import tkinter as tk
from tkinter import colorchooser

from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.gui.btn_wall import BTNWall
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.models.wall import Wall

class PopupEditWall(PopupBase):
    """Popup window for editing wall properties"""
    def __init__(self, AppMain : AppMain, btn : BTNWall, *args, **kwargs):
        super().__init__(AppMain, "Edit Wall", 300, 400, *args, **kwargs)
        self.btn = btn


    def load_content(self):
        super().load_content()
        # Main container
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        tk.Label(
            main_frame,
            text="Edit Wall",
            font=("Arial", 24)
        ).pack(pady=(0, 20))
        
        # Wall Name
        name_frame = tk.Frame(main_frame)
        name_frame.pack(pady=5)
        tk.Label(
            name_frame,
            text="Wall Name:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.wall_name_entry = tk.Entry(name_frame, font=("Arial", 12), width=15)
        self.wall_name_entry.insert(0, self.btn.wall.name)
        self.wall_name_entry.pack(side="left")

        # Wall Width
        width_frame = tk.Frame(main_frame)
        width_frame.pack(pady=5)
        tk.Label(
            width_frame,
            text="Wall Width:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.wall_width_entry = tk.Entry(width_frame, font=("Arial", 12), width=15)
        self.wall_width_entry.insert(0, self.btn.wall.width)
        self.wall_width_entry.pack(side="left")

        # Wall Height
        height_frame = tk.Frame(main_frame)
        height_frame.pack(pady=5)
        tk.Label(
            height_frame,
            text="Wall Height:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.wall_height_entry = tk.Entry(height_frame, font=("Arial", 12), width=15)
        self.wall_height_entry.insert(0, self.btn.wall.height)
        self.wall_height_entry.pack(side="left")

        # Wall Color
        color_frame = tk.Frame(main_frame)
        color_frame.pack(pady=5)
        tk.Label(
            color_frame,
            text="Wall Color:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 10))
        self.color_box = tk.Label(color_frame, bg=self.btn.wall.color, width=10, height=1)
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

        self.submit_button = tk.Button(
            main_frame,
            text="Submit",
            command=self.submit_wall_info,
            width=15,
            bg="#5F3FCA",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="raised"
        )
        self.submit_button.pack(pady=(20, 0))

        self.delete_button = tk.Button(
            main_frame,
            text="Delete",
            command=self.delete_wall,
            width=15,
            bg="#5F3FCA",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="raised"
        )
        self.delete_button.pack(pady=(20, 0))

    def delete_wall(self):
        """Delete the wall"""
        self.btn.delete_wall()
        self.on_close()

    def submit_wall_info(self):
        """Submit the wall information"""
        new_wall = Wall(
            self.wall_name_entry.get(),
            float(self.wall_width_entry.get()),
            float(self.wall_height_entry.get()),
            self.color_box.cget("bg")
        )
        self.btn.update_wall(new_wall)
        self.on_close()
        

    def pick_color(self):
        """Open color picker dialog and set the selected color to the color box"""
        color = colorchooser.askcolor()[1]
        if color:
            self.color_box.config(bg=color)

        