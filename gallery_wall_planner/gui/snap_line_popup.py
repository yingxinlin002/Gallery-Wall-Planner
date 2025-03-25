import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.gui.ui_styles import apply_primary_button_style

def open_snap_line_popup(root, on_save_callback, existing_line=None, wall_width=100, wall_height=100):
    popup = Toplevel(root)
    popup.title("Add Snap Line" if existing_line is None else "Edit Snap Line")
    popup.geometry("300x320")

    # Orientation Radio Buttons
    orientation_var = tk.StringVar(value=existing_line.orientation if existing_line else "horizontal")
    ttk.Label(popup, text="Orientation:").pack(anchor="w", padx=10, pady=(10, 0))
    ttk.Radiobutton(popup, text="Horizontal", variable=orientation_var, value="horizontal").pack(anchor="w", padx=20)
    ttk.Radiobutton(popup, text="Vertical", variable=orientation_var, value="vertical").pack(anchor="w", padx=20)

    # Alignment Radio Buttons
    alignment_var = tk.StringVar(value=existing_line.alignment if existing_line else "center")
    alignment_frame = ttk.Frame(popup)
    alignment_frame.pack(anchor="w", padx=10, pady=(10, 0))

    ttk.Label(alignment_frame, text="Alignment:").pack(anchor="w")

    align_options = {
        "horizontal": ["top", "center", "bottom"],
        "vertical": ["left", "center", "right"]
    }

    align_buttons = []

    def update_alignment_buttons():
        for btn in align_buttons:
            btn.destroy()
        align_buttons.clear()

        current = orientation_var.get()
        for val in align_options[current]:
            b = ttk.Radiobutton(alignment_frame, text=val.capitalize(), variable=alignment_var, value=val)
            b.pack(anchor="w", padx=20)
            align_buttons.append(b)

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
        
        # After parsing the float we need to use info from the wall to make sure these can not be placed out of bounds:
        if distance < 0:
            messagebox.showerror("Error", "Distance cannot be negative.")
            return

        if orientation_var.get() == "horizontal" and distance > wall_height:
            messagebox.showerror("Error", f"Distance exceeds wall height ({wall_height} inches).")
            return

        if orientation_var.get() == "vertical" and distance > wall_width:
            messagebox.showerror("Error", f"Distance exceeds wall width ({wall_width} inches).")
            return

        updated_line = SingleLine(
            orientation=orientation_var.get(),
            alignment=alignment_var.get(),
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
