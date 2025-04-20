import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from gallery_wall_planner.models.wall_line import (
    SingleLine,
    LineOrientation,  # Use LineOrientation instead of Orientation
    LineAlignment,    # Use LineAlignment instead of Horizontal/VerticalAlignment
    Orientation,      # Only needed if you use it elsewhere
    HorizontalAlignment,  # Only needed if you use it elsewhere
    VerticalAlignment     # Only needed if you use it elsewhere
)
from gallery_wall_planner.gui.ui_styles import apply_primary_button_style

def open_snap_line_popup(root, on_save_callback, existing_line=None, wall_width=100, wall_height=100):
    popup = Toplevel(root)
    popup.title("Add Snap Line" if existing_line is None else "Edit Snap Line")
    popup.geometry("300x320")

    # Orientation Radio Buttons - using LineOrientation enum
    orientation_var = tk.StringVar(value=existing_line.orientation.value if existing_line else LineOrientation.HORIZONTAL.value)
    ttk.Label(popup, text="Orientation:").pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Radiobutton(popup, text="Horizontal", variable=orientation_var, value=LineOrientation.HORIZONTAL.value).pack(anchor="w", padx=20)
    ttk.Radiobutton(popup, text="Vertical", variable=orientation_var, value=LineOrientation.VERTICAL.value).pack(anchor="w", padx=20)

    # Alignment Radio Buttons - using LineAlignment enum
    alignment_var = tk.StringVar(value=existing_line.alignment.value if existing_line else LineAlignment.CENTER.value)
    alignment_frame = ttk.Frame(popup)
    alignment_frame.pack(anchor="w", padx=10, pady=(10, 0))

    ttk.Label(alignment_frame, text="Alignment:").pack(anchor="w")

    align_options = {
        LineOrientation.HORIZONTAL: [LineAlignment.TOP, LineAlignment.CENTER, LineAlignment.BOTTOM],
        LineOrientation.VERTICAL: [LineAlignment.LEFT, LineAlignment.CENTER, LineAlignment.RIGHT]
    }

    align_buttons = []

    def update_alignment_buttons():
        # Clear existing buttons
        for btn in align_buttons:
            btn.destroy()
        align_buttons.clear()

        current_orientation = LineOrientation(orientation_var.get())
        for alignment in align_options[current_orientation]:
            b = ttk.Radiobutton(alignment_frame, 
                              text=alignment.value.capitalize(), 
                              variable=alignment_var, 
                              value=alignment.value)
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
        
        if distance < 0:
            messagebox.showerror("Error", "Distance cannot be negative.")
            return

        current_orientation = LineOrientation(orientation_var.get())
        if current_orientation == LineOrientation.HORIZONTAL and distance > wall_height:
            messagebox.showerror("Error", f"Distance exceeds wall height ({wall_height} inches).")
            return

        if current_orientation == LineOrientation.VERTICAL and distance > wall_width:
            messagebox.showerror("Error", f"Distance exceeds wall width ({wall_width} inches).")
            return

        # Create the updated line using the enums
        updated_line = SingleLine(
            orientation=LineOrientation(orientation_var.get()),
            alignment=LineAlignment(alignment_var.get()),
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