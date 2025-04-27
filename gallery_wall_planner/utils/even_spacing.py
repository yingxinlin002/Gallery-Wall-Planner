import tkinter as tk
from tkinter import ttk, messagebox

def apply_even_spacing(wall_canvas, imported_artworks):
    """
    Apply even spacing to the selected artworks on the wall canvas.

    Args:
        wall_canvas: The WallCanvas instance where the artworks are displayed.
        imported_artworks: List of imported artworks to be evenly spaced.
    """
    def on_confirm():
        try:
            # Get left and right points from user input
            left_point = float(left_point_entry.get())
            right_point = float(right_point_entry.get())

            if left_point >= right_point:
                messagebox.showerror("Error", "Left point must be less than the right point.")
                return

            # Ensure points are within wall boundaries
            if left_point < 0 or right_point > wall_canvas.canvas_dimensions.width:
                messagebox.showerror("Error", "Points must be within the wall boundaries.")
                return

            # Ensure artworks are selected
            if not selected_artworks:
                messagebox.showerror("Error", "No artworks selected.")
                return

            # Calculate spacing
            total_width = sum(artwork.width for artwork in selected_artworks)
            available_space = right_point - left_point
            if total_width > available_space:
                messagebox.showerror("Error", "Artworks exceed the available space.")
                return

            spacing = (available_space - total_width) / (len(selected_artworks) - 1)

            # Update artwork positions
            current_x = left_point
            for artwork in selected_artworks:
                artwork.x = current_x
                artwork.y = 62  # Default height at 62 inches
                if artwork.id not in wall_canvas.draggable_items:
                    wall_canvas.add_draggable(artwork)  # Ensure artwork is registered
                wall_canvas.move_item_to_canvas(artwork)
                current_x += artwork.width + spacing

            # Close the popup
            popup.destroy()
            messagebox.showinfo("Success", "Artworks have been evenly spaced.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for the points.")

    def on_select_artwork():
        """Handle artwork selection."""
        selected = artwork_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select at least one artwork.")
            return
        for idx in selected:
            selected_artworks.append(imported_artworks[idx])
        messagebox.showinfo("Success", "Artworks selected. You can now confirm.")

    # Create the popup window
    popup = tk.Toplevel()
    popup.title("Even Spacing")
    popup.geometry("400x400")

    # Left and right points input
    ttk.Label(popup, text="Enter the left and right points (in inches):").pack(pady=10)
    left_point_frame = ttk.Frame(popup)
    left_point_frame.pack(pady=5)
    ttk.Label(left_point_frame, text="Left Point:").pack(side="left", padx=5)
    left_point_entry = ttk.Entry(left_point_frame)
    left_point_entry.pack(side="left", padx=5)

    right_point_frame = ttk.Frame(popup)
    right_point_frame.pack(pady=5)
    ttk.Label(right_point_frame, text="Right Point:").pack(side="left", padx=5)
    right_point_entry = ttk.Entry(right_point_frame)
    right_point_entry.pack(side="left", padx=5)

    # Artwork selection
    ttk.Label(popup, text="Select artworks to distribute (in order):").pack(pady=10)
    artwork_listbox = tk.Listbox(popup, selectmode="multiple", height=10)
    artwork_listbox.pack(fill="both", expand=True, padx=10, pady=5)

    # Populate the listbox with imported artworks
    for artwork in imported_artworks:
        artwork_listbox.insert(tk.END, f"{artwork.name} ({artwork.width}\" x {artwork.height}\")")

    # Buttons
    button_frame = ttk.Frame(popup)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Select Artworks", command=on_select_artwork).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Confirm", command=on_confirm).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)

    # Track selected artworks
    selected_artworks = []