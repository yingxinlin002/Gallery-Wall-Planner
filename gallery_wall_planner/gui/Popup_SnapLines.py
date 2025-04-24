
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Optional, List

from gallery_wall_planner.gui.Popup_Base import Popup_Base
from gallery_wall_planner.gui.AppMain import AppMain
from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.models.wall_line import Orientation, HorizontalAlignment, VerticalAlignment

from gallery_wall_planner.gui.ui_styles import apply_primary_button_style


class Popup_SnapLines(Popup_Base):
    
    def __init__(self, AppMain : AppMain, parent_ui: 'Screen_EditorUI', existing_line: Optional[SingleLine] = None, *args, **kwargs):
        super().__init__(AppMain, "Add Snap Line" if existing_line is None else "Edit Snap Line", 300, 320, *args, **kwargs)
        from gallery_wall_planner.gui.Screen_EditorUI import Screen_EditorUI
        self.parent_ui: Screen_EditorUI = parent_ui
        self.existing_line = existing_line
        self.align_buttons: List[tk.Radiobutton] = []
        self.alignment_frame: ttk.Frame = None
        self.orientation_var: tk.StringVar = None
        self.alignment_var: tk.StringVar = None
        self.distance_var: tk.DoubleVar = None

    def load_content(self):
        # Orientation Radio Buttons
        self.orientation_var = tk.StringVar(value=self.existing_line.orientation.name if self.existing_line else Orientation.HORIZONTAL.name)
        ttk.Label(self, text="Orientation:").pack(anchor="w", padx=10, pady=(10, 0))
        ttk.Radiobutton(self, text="Horizontal", variable=self.orientation_var, value=Orientation.HORIZONTAL.name).pack(anchor="w", padx=20)
        ttk.Radiobutton(self, text="Vertical", variable=self.orientation_var, value=Orientation.VERTICAL.name).pack(anchor="w", padx=20)

        # Alignment Radio Buttons
        self.alignment_var = tk.StringVar(value=self.existing_line.alignment.name if self.existing_line else HorizontalAlignment.CENTER.name)
        self.alignment_frame = ttk.Frame(self)
        self.alignment_frame.pack(anchor="w", padx=10, pady=(10, 0))

        ttk.Label(self.alignment_frame, text="Alignment:").pack(anchor="w")

        self.align_buttons = []

        # Trigger the alignment buttons update when orientation changes
        self.orientation_var.trace_add("write", lambda *_: self.update_alignment_buttons(self.orientation_var))
        self.update_alignment_buttons(self.orientation_var)

        # Distance Entry
        ttk.Label(self, text="Distance (inches):").pack(anchor="w", padx=10, pady=(10, 0))
        self.distance_var = tk.DoubleVar(value=self.existing_line.distance if self.existing_line else 0.0)
        distance_entry = ttk.Entry(self, textvariable=self.distance_var)
        distance_entry.pack(padx=10, fill="x")

        save_btn = ttk.Button(self, text="Save", command=self.save)
        apply_primary_button_style(save_btn)
        save_btn.pack(pady=10)

        self.transient(self.AppMain.root)
        self.grab_set()
        self.wait_window()

    def update_alignment_buttons(self, orientation_var: tk.StringVar):
        # Clear existing buttons
        for btn in self.align_buttons:
            btn.destroy()
        self.align_buttons.clear()

        current_orientation = Orientation[orientation_var.get()]
        for alignment in Orientation.alignment_options(current_orientation):
            b = ttk.Radiobutton(self.alignment_frame, text=alignment.name.capitalize(), variable=self.alignment_var, value=alignment.name)
            b.pack(anchor="w", padx=20)
            self.align_buttons.append(b)

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

        if Orientation[self.orientation_var.get()] == Orientation.HORIZONTAL and distance > self.AppMain.editor_wall.height:
            messagebox.showerror("Error", f"Distance exceeds wall height ({self.AppMain.editor_wall.height} inches).")
            return

        if Orientation[self.orientation_var.get()] == Orientation.VERTICAL and distance > self.AppMain.editor_wall.width:
            messagebox.showerror("Error", f"Distance exceeds wall width ({self.AppMain.editor_wall.width} inches).")
            return

        orientation_enum = Orientation[self.orientation_var.get()]
        alignment_str = self.alignment_var.get().upper()
        if orientation_enum == Orientation.HORIZONTAL and alignment_str in ["TOP", "CENTER", "BOTTOM"]:
            alignment_enum = HorizontalAlignment[alignment_str]
        elif orientation_enum == Orientation.VERTICAL and alignment_str in ["LEFT", "CENTER", "RIGHT"]:
            alignment_enum = VerticalAlignment[alignment_str]
        else:
            alignment_enum = HorizontalAlignment.CENTER if orientation_enum == Orientation.HORIZONTAL else VerticalAlignment.CENTER


        print(f"[DEBUG] snap_line_popup Saving: orientation={orientation_enum}, alignment={alignment_enum}, type={type(alignment_enum)}")

        updated_line = SingleLine(
            orientation=orientation_enum,
            alignment=alignment_enum,
            distance=distance,
            snap_to=True,
            moveable=True
        )

        for line in self.AppMain.editor_wall.wall_lines:
            if line.approximate_equal(updated_line):
                self.show_duplicate_line_popup(updated_line)
                br
        self.destroy()
