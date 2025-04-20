import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
# from gallery_wall_planner.models.wall_line import SingleLine, Orientation, HorizontalAlignment, VerticalAlignment # Naming convention was causing crash when fixing virtualWall.py. This can be deleted, but wanted to leave an explanation here for now.
from gallery_wall_planner.models.wall_line import (
    SingleLine,
    Orientation,
    HorizontalAlignment,
    VerticalAlignment
)
from gallery_wall_planner.gui.ui_styles import apply_primary_button_style

def open_snap_line_popup(root, on_save_callback, existing_line=None, wall_width=100, wall_height=100):
    popup = Toplevel(root)
    popup.title("Add Snap Line" if existing_line is None else "Edit Snap Line")
    popup.geometry("300x320")

    # Orientation Radio Buttons
    orientation_var = tk.StringVar(value=existing_line.orientation.name if existing_line else Orientation.HORIZONTAL.name)
    ttk.Label(popup, text="Orientation:").pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Radiobutton(popup, text="Horizontal", variable=orientation_var, value=Orientation.HORIZONTAL.name).pack(anchor="w", padx=20)
    ttk.Radiobutton(popup, text="Vertical", variable=orientation_var, value=Orientation.VERTICAL.name).pack(anchor="w", padx=20)

    # Alignment Radio Buttons
    alignment_var = tk.StringVar(value=existing_line.alignment.name if existing_line else HorizontalAlignment.CENTER.name)
    alignment_frame = ttk.Frame(popup)
    alignment_frame.pack(anchor="w", padx=10, pady=(10, 0))

    ttk.Label(alignment_frame, text="Alignment:").pack(anchor="w")

    align_buttons = []

    def update_alignment_buttons():
        # Clear existing buttons
        for btn in align_buttons:
            btn.destroy()
        align_buttons.clear()

        current_orientation = Orientation[orientation_var.get()]
        for alignment in Orientation.alignment_options(current_orientation):
            b = ttk.Radiobutton(alignment_frame, text=alignment.name.capitalize(), variable=alignment_var, value=alignment.name)
            b.pack(anchor="w", padx=20)
            align_buttons.append(b)

    # Trigger the alignment buttons update when orientation changes
    orientation_var.trace_add("write", lambda *_: update_alignment_buttons())
    update_alignment_buttons()

    # Distance Entry
    ttk.Label(popup, text="Distance (inches):").pack(anchor="w", padx=10, pady=(10, 0))
    distance_var = tk.DoubleVar(value=existing_line.distance if existing_line else 0.0)
    distance_entry = ttk.Entry(popup, textvariable=distance_var)
    distance_entry.pack(padx=10, fill="x")

    # Save Button
    def save():
        try:
            distance = float(distance_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Distance must be a number.")
            return
        
        # After parsing the float, check if the distance is valid within wall constraints
        if distance < 0:
            messagebox.showerror("Error", "Distance cannot be negative.")
            return

        if Orientation[orientation_var.get()] == Orientation.HORIZONTAL and distance > wall_height:
            messagebox.showerror("Error", f"Distance exceeds wall height ({wall_height} inches).")
            return

        if Orientation[orientation_var.get()] == Orientation.VERTICAL and distance > wall_width:
            messagebox.showerror("Error", f"Distance exceeds wall width ({wall_width} inches).")
            return

        orientation_enum = Orientation[orientation_var.get()]
        alignment_str = alignment_var.get().upper()
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

        popup.destroy()
        on_save_callback(updated_line)

    save_btn = ttk.Button(popup, text="Save", command=save)
    apply_primary_button_style(save_btn)
    save_btn.pack(pady=10)

    popup.transient(root)
    popup.grab_set()
    popup.wait_window()
