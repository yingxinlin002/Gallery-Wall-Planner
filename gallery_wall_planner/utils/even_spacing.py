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
                messagebox.showerror("Error", f"Artworks exceed the available space. Total width: {total_width}, Available space: {available_space}.")
                return

            # Calculate spacing: n+1 gaps for n artworks
            num_artworks = len(selected_artworks)
            spacing = (available_space - total_width) / (num_artworks + 1)

            # Update artwork positions
            current_x = left_point + spacing  # Start at left_point + spacing
            for artwork in selected_artworks:
                artwork.x = current_x
                artwork.y = 62  # Default height at 62 inches
                if artwork.id not in wall_canvas.draggable_items:
                    wall_canvas.add_draggable(artwork)  # Ensure artwork is registered
                wall_canvas.move_item_to_canvas(artwork)
                current_x += artwork.width + spacing  # Move to the next position

            # Close the popup
            popup.destroy()
            messagebox.showinfo("Success", f"Artworks have been evenly spaced. Total width: {total_width}, Spacing: {spacing:.2f}.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for the points.")

    def on_artwork_select(event):
        """Handle live updates when artworks are selected."""
        selected = artwork_listbox.curselection()

        # Toggle selection
        for idx in selected:
            if idx in selection_order:
                # Remove from selection
                del selection_order[idx]
            else:
                # Add to selection
                selection_order[idx] = len(selection_order) + 1

        # Sort selection order by the order of selection
        sorted_selection = sorted(selection_order.items(), key=lambda x: x[1])
        selected_artworks.clear()
        for idx, _ in sorted_selection:
            selected_artworks.append(imported_artworks[idx])

        # Update the listbox to show the selection order
        update_listbox_with_order()

        # Update labels for selected count and total width
        total_width = sum(artwork.width for artwork in selected_artworks)
        selected_count_label.config(text=f"Selected Artworks: {len(selected_artworks)}")
        total_width_label.config(text=f"Total Width: {total_width:.2f} inches")

    def update_listbox_with_order():
        """Update the listbox to display the selection order."""
        artwork_listbox.delete(0, tk.END)
        for idx, artwork in enumerate(imported_artworks):
            order_label = f" ({selection_order[idx]})" if idx in selection_order else ""
            artwork_listbox.insert(tk.END, f"{artwork.name} ({artwork.width}\" x {artwork.height}\"){order_label}")

    # Create the popup window
    popup = tk.Toplevel()
    popup.title("Even Spacing")
    popup.geometry("500x500")

    # Make the popup stay on top of other windows
    popup.attributes("-topmost", True)

    # Left and right points input
    input_frame = ttk.LabelFrame(popup, text="Spacing Input")
    input_frame.pack(fill="x", padx=10, pady=10)
    ttk.Label(input_frame, text="Left Point:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    left_point_entry = ttk.Entry(input_frame)
    left_point_entry.grid(row=0, column=1, padx=5, pady=5)
    left_point_entry.insert(0, "0")  # Default value

    ttk.Label(input_frame, text="Right Point:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    right_point_entry = ttk.Entry(input_frame)
    right_point_entry.grid(row=1, column=1, padx=5, pady=5)
    right_point_entry.insert(0, f"{wall_canvas.canvas_dimensions.width}")  # Default value

    # Artwork selection
    selection_frame = ttk.LabelFrame(popup, text="Artwork Selection")
    selection_frame.pack(fill="both", expand=True, padx=10, pady=10)
    artwork_listbox = tk.Listbox(selection_frame, selectmode="multiple", height=10)
    artwork_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    # Add scrollbar for the listbox
    scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=artwork_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    artwork_listbox.config(yscrollcommand=scrollbar.set)

    # Populate the listbox with imported artworks
    for artwork in imported_artworks:
        artwork_listbox.insert(tk.END, f"{artwork.name} ({artwork.width}\" x {artwork.height}\")")

    # Bind the listbox selection event to live updates
    artwork_listbox.bind("<<ListboxSelect>>", on_artwork_select)

    # Selected artworks info
    info_frame = ttk.Frame(popup)
    info_frame.pack(fill="x", padx=10, pady=5)
    selected_count_label = ttk.Label(info_frame, text="Selected Artworks: 0")
    selected_count_label.pack(side="left", padx=5)
    total_width_label = ttk.Label(info_frame, text="Total Width: 0.00 inches")
    total_width_label.pack(side="left", padx=5)

    # Buttons
    button_frame = ttk.Frame(popup)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Confirm", command=on_confirm, style="Accent.TButton").pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side="left", padx=5)

    # Track selected artworks and their order
    selected_artworks = []
    selection_order = {}