
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Optional, List

from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.models.wall_line import Orientation, HorizontalAlignment, VerticalAlignment

from gallery_wall_planner.gui.ui_styles import apply_primary_button_style


class PopupSnapLines(PopupBase):
    
    def __init__(self, AppMain : AppMain, parent_ui: 'Screen_EditorUI', existing_line: Optional[SingleLine] = None, *args, **kwargs):
        super().__init__(AppMain, "Add Snap Line" if existing_line is None else "Edit Snap Line", 300, 320, *args, **kwargs)
        from gallery_wall_planner.gui.screen_editor_ui import ScreenEditorUI
        self.parent_ui: ScreenEditorUI = parent_ui
        self.existing_line: Optional[SingleLine] = existing_line
        self.orientation_var: tk.StringVar = None
        self.distance_var: tk.DoubleVar = None
        self.load_content()

    def load_content(self):
        super().load_content()
        # Orientation Radio Buttons
        self.orientation_var = tk.StringVar(value=self.existing_line.orientation.name if self.existing_line else Orientation.HORIZONTAL.name)
        ttk.Label(self, text="Orientation:").pack(anchor="w", padx=10, pady=(10, 0))
        ttk.Radiobutton(self, text="Horizontal", variable=self.orientation_var, value=Orientation.HORIZONTAL.name).pack(anchor="w", padx=20)
        ttk.Radiobutton(self, text="Vertical", variable=self.orientation_var, value=Orientation.VERTICAL.name).pack(anchor="w", padx=20)

        # Distance Entry
        ttk.Label(self, text="Distance (inches):").pack(anchor="w", padx=10, pady=(10, 0))
        self.distance_var = tk.DoubleVar(value=self.existing_line.distance if self.existing_line else 0.0)
        distance_entry = ttk.Entry(self, textvariable=self.distance_var)
        distance_entry.pack(padx=10, fill="x")

        save_btn = ttk.Button(self, text="Save", command=self.save)
        apply_primary_button_style(save_btn)
        save_btn.pack(pady=10)

        if self.existing_line:
            delete_btn = ttk.Button(self, text="Delete", command=self.delete)
            apply_primary_button_style(delete_btn)
            delete_btn.pack(pady=10)

        # No need for window management code here as it's handled in PopupBase

    # Save Button
    def save(self):
        try:
            distance = float(self.distance_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Distance must be a number.")
            return
        
        # After parsing the float, check if the distance is valid within wall constraints
        if distance < 0:
            messagebox.showerror("Error", "Distance cannot be negative.")
            return

        if Orientation[self.orientation_var.get()] == Orientation.HORIZONTAL and distance > self.app_main.gallery.current_wall.height:
            messagebox.showerror("Error", f"Distance exceeds wall height ({self.app_main.gallery.current_wall.height} inches).")
            return

        if Orientation[self.orientation_var.get()] == Orientation.VERTICAL and distance > self.app_main.gallery.current_wall.width:
            messagebox.showerror("Error", f"Distance exceeds wall width ({self.app_main.gallery.current_wall.width} inches).")
            return

        orientation_enum = Orientation[self.orientation_var.get()]

        updated_line = SingleLine(
            orientation=orientation_enum,
            alignment=HorizontalAlignment.CENTER,
            distance=distance,
            snap_to=True,
            moveable=True
        )

        if self.existing_line:
            self.parent_ui.update_snap_line(self.existing_line, updated_line)
        else:
            self.parent_ui.add_new_snap_line(updated_line)
        self.on_close()

    def delete(self):
        self.parent_ui.delete_snap_line(self.existing_line)
        self.on_close()
        