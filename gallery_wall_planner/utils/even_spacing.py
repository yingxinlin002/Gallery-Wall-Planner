import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Tuple, Optional
from gallery_wall_planner.gui.wall_canvas import WallCanvas
from gallery_wall_planner.models.artwork import Artwork

def apply_even_spacing(wall_canvas: WallCanvas, imported_artworks: List[Artwork]) -> None:
    """
    Apply even spacing to selected artworks on the wall canvas with interactive UI.

    Features:
    - Visual selection of artworks with order tracking
    - Real-time calculation of total width
    - Customizable X and Y positions
    - Input validation

    Args:
        wall_canvas: The WallCanvas instance where artworks are displayed
        imported_artworks: List of imported artworks to be spaced
    """

    # Constants
    DEFAULT_Y_POSITION = 62  # Default height in inches
    MIN_SPACING = 0.5  # Minimum spacing between artworks in inches

    class SpacingUI:
        def __init__(self, master):
            self.master = master
            self.selected_artworks: List[Artwork] = []
            self.selection_order: Dict[int, int] = {}
            self.setup_ui()

        def setup_ui(self):
            """Initialize all UI components."""
            self.master.title("Even Spacing Tool")
            self.master.geometry("500x650")  # Increased height for Y position input
            self.master.attributes("-topmost", True)

            # Main container
            main_frame = ttk.Frame(self.master)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Input section
            self.setup_input_section(main_frame)

            # Position section
            self.setup_position_section(main_frame)

            # Artwork selection
            self.setup_selection_section(main_frame)

            # Info display
            self.setup_info_section(main_frame)

            # Action buttons
            self.setup_action_buttons(main_frame)

        def setup_input_section(self, parent):
            """Setup spacing boundary inputs."""
            input_frame = ttk.LabelFrame(parent, text="Spacing Boundaries (inches)")
            input_frame.pack(fill="x", pady=(0, 10))

            # Left boundary
            ttk.Label(input_frame, text="Left Boundary:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.left_entry = ttk.Entry(input_frame)
            self.left_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.left_entry.insert(0, "0")

            # Right boundary
            ttk.Label(input_frame, text="Right Boundary:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.right_entry = ttk.Entry(input_frame)
            self.right_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            self.right_entry.insert(0, f"{wall_canvas.wall.width:.1f}")

            input_frame.columnconfigure(1, weight=1)

        def setup_position_section(self, parent):
            """Setup position inputs including new Y position field."""
            position_frame = ttk.LabelFrame(parent, text="Artwork Position")
            position_frame.pack(fill="x", pady=(0, 10))

            # Y Position
            ttk.Label(position_frame, text="Center height from floor (standard: 62\")", font=("TkDefaultFont", 8)).grid(row=1, column=1, sticky="w", padx=5)
            self.y_entry = ttk.Entry(position_frame)
            self.y_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.y_entry.insert(0, f"{DEFAULT_Y_POSITION}")  # Default value

            # Add tooltip/info label
            ttk.Label(position_frame,
                     text="Distance from bottom of wall",
                     font=("TkDefaultFont", 8)).grid(row=1, column=1, sticky="w", padx=5)

            position_frame.columnconfigure(1, weight=1)

        def setup_selection_section(self, parent):
            """Setup artwork selection listbox."""
            selection_frame = ttk.LabelFrame(parent, text="Select Artworks (click to select order)")
            selection_frame.pack(fill="both", expand=True, pady=(0, 10))

            # Listbox with scrollbar
            self.listbox = tk.Listbox(
                selection_frame,
                selectmode="multiple",
                height=10,
                activestyle="none",
                font=("TkDefaultFont", 10)
            )

            scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=self.listbox.yview)
            self.listbox.config(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            self.listbox.pack(side="left", fill="both", expand=True)

            # Populate listbox
            for artwork in imported_artworks:
                self.listbox.insert(tk.END, f"{artwork.name} ({artwork.width}\" × {artwork.height}\")")

            self.listbox.bind("<<ListboxSelect>>", self.on_artwork_select)

        def setup_info_section(self, parent):
            """Setup information display labels."""
            info_frame = ttk.Frame(parent)
            info_frame.pack(fill="x", pady=(0, 10))

            self.selected_label = ttk.Label(info_frame, text="Selected: 0")
            self.selected_label.pack(side="left", padx=5)

            self.width_label = ttk.Label(info_frame, text="Total Width: 0.0\"")
            self.width_label.pack(side="left", padx=5)

            self.spacing_label = ttk.Label(info_frame, text="Spacing: -")
            self.spacing_label.pack(side="right", padx=5)

        def setup_action_buttons(self, parent):
            """Setup action buttons."""
            button_frame = ttk.Frame(parent)
            button_frame.pack(fill="x")

            ttk.Button(
                button_frame,
                text="Apply Spacing",
                command=self.apply_spacing,
                style="Accent.TButton"
            ).pack(side="left", padx=5)

            ttk.Button(
                button_frame,
                text="Cancel",
                command=self.master.destroy
            ).pack(side="right", padx=5)

        def get_y_position(self) -> Optional[float]:
            """Validate and return Y position input."""
            try:
                y_pos = float(self.y_entry.get())
                if y_pos < 0 or y_pos > wall_canvas.wall.height:
                    messagebox.showerror("Error",
                                       f"Y position must be between 0 and {wall_canvas.wall.height} inches")
                    return None
                return y_pos
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for Y position")
                return None

        def on_artwork_select(self, event):
            """Handle artwork selection with order tracking that toggles and renumbers."""
            selected_idx = self.listbox.curselection()

            if not selected_idx:  # If nothing is selected, do nothing
                return

            clicked_idx = selected_idx[-1]  # Get the most recently clicked item

            # Toggle selection - if already selected, remove it
            if clicked_idx in self.selection_order:
                # Remove the clicked item and renumber remaining items
                removed_order = self.selection_order.pop(clicked_idx)
                # Decrement orders higher than the removed one
                self.selection_order = {
                    idx: (order if order < removed_order else order - 1)
                    for idx, order in self.selection_order.items()
                }
            else:
                # Add the clicked item with the next available order number
                next_order = len(self.selection_order) + 1
                self.selection_order[clicked_idx] = next_order

            # Update the selected artworks list based on current selection order
            sorted_selection = sorted(self.selection_order.items(), key=lambda x: x[1])
            self.selected_artworks = [imported_artworks[idx] for idx, _ in sorted_selection]

            # Update the display to show current numbering
            self.update_display()

        def update_display(self):
            """Update all display elements."""
            # Update listbox with order indicators
            self.listbox.delete(0, tk.END)
            for idx, artwork in enumerate(imported_artworks):
                order = f" {self.selection_order[idx]}" if idx in self.selection_order else ""
                self.listbox.insert(tk.END, f"{artwork.name} ({artwork.width}\" × {artwork.height}\"){order}")

            # Update info labels
            total_width = sum(art.width for art in self.selected_artworks)
            self.selected_label.config(text=f"Selected: {len(self.selected_artworks)}")
            self.width_label.config(text=f"Total Width: {total_width:.1f}\"")

            # Calculate and display projected spacing
            try:
                left = float(self.left_entry.get())
                right = float(self.right_entry.get())
                if right > left and self.selected_artworks:
                    spacing = (right - left - total_width) / (len(self.selected_artworks) + 1)
                    self.spacing_label.config(text=f"Spacing: {spacing:.1f}\"")
            except ValueError:
                pass

        def validate_inputs(self) -> Tuple[Optional[float], Optional[float]]:
            """Validate and return spacing boundaries."""
            try:
                left = float(self.left_entry.get())
                right = float(self.right_entry.get())

                if left < 0 or right > wall_canvas.wall.width:
                    messagebox.showerror("Error", "Boundaries must be within wall dimensions.")
                    return None, None

                if left >= right:
                    messagebox.showerror("Error", "Left boundary must be less than right boundary.")
                    return None, None

                return left, right
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for boundaries.")
                return None, None

        def apply_spacing(self):
            """Apply the calculated spacing to selected artworks."""
            left, right = self.validate_inputs()
            if left is None:
                return

            y_pos_center = self.get_y_position()
            if y_pos_center is None:
                return

            if not self.selected_artworks:
                messagebox.showerror("Error", "Please select at least one artwork.")
                return

            total_width = sum(art.width for art in self.selected_artworks)
            available_space = right - left
            spacing = (available_space - total_width) / (len(self.selected_artworks) + 1)

            if spacing < MIN_SPACING:
                if not messagebox.askyesno(
                    "Warning",
                    f"Calculated spacing ({spacing:.1f}\") is very small. Continue anyway?"
                ):
                    return

            # Position artworks
            current_x = left + spacing

            for artwork in self.selected_artworks:
                # Calculate position in inches (wall coordinates)
                artwork.x = current_x
                # Calculate Y position so center is at y_pos_center
                artwork.y = y_pos_center - (artwork.height / 2)

                # Debug output
                # center_x = artwork.x + (artwork.width / 2)
                # center_y = artwork.y + (artwork.height / 2)
                # print(f"Positioning {artwork.name}:")
                # print(f"  Center X (inches): {center_x:.1f}")
                # print(f"  Center Y (inches): {center_y:.1f} (from bottom: {y_pos_center:.1f})")
                # print(f"  Artwork size: {artwork.width}\" × {artwork.height}\"")

                # Check boundaries - now checking if entire artwork fits
                artwork.x, artwork.y = wall_canvas.enforce_boundaries_even_spacing(
                    artwork.x, artwork.y, 
                    artwork.width, artwork.height
                )
                
                # print(f"  After boundary check: X={artwork.x:.1f}, Y={artwork.y:.1f}")

                # Check if artwork already exists on canvas
                if artwork.id in wall_canvas.draggable_items:
                    # Update existing draggable
                    draggable = wall_canvas.draggable_items[artwork.id]
                    draggable.wall_object.x = artwork.x
                    draggable.wall_object.y = artwork.y
                    draggable.update_position()
                else:
                    # Add new draggable
                    wall_canvas.add_draggable(artwork)

                current_x += artwork.width + spacing
            
            self.master.destroy()

    # Create and run the UI
    root = tk.Toplevel()
    SpacingUI(root)
    root.mainloop()