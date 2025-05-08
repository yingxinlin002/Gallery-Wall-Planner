import tkinter as tk
from tkinter import ttk

from typing import Optional, Tuple, List, Dict

from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.models.artwork import Artwork


class PopupEvenSpacing(PopupBase):
    DEFAULT_Y_POSITION = 62  # Default height in inches
    MIN_SPACING = 0.5  # Minimum spacing between artworks in inches
    def __init__(self, app_main: AppMain, *args, **kwargs):
        super().__init__(app_main, "Even Spacing", 500, 650, *args, **kwargs)
        self.load_content()
        self.selected_artworks: List[Artwork] = []
    
    def load_content(self):
        super().load_content()
        # Main container
        main_frame = ttk.Frame(self)
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
        self.right_entry.insert(0, f"{self.app_main.gallery.current_wall.width:.1f}")

        input_frame.columnconfigure(1, weight=1)

    def setup_position_section(self, parent):
        """Setup position inputs including new Y position field."""
        position_frame = ttk.LabelFrame(parent, text="Artwork Position")
        position_frame.pack(fill="x", pady=(0, 10))

        # Y Position
        ttk.Label(position_frame, text="Center height from floor (standard: 62\")", font=("TkDefaultFont", 8)).grid(row=1, column=1, sticky="w", padx=5)
        self.y_entry = ttk.Entry(position_frame)
        self.y_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.y_entry.insert(0, f"{self.DEFAULT_Y_POSITION}")  # Default value

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
        for artwork in self.app_main.gallery.current_wall.artwork:
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
            command=self.on_close
        ).pack(side="right", padx=5)

    def get_y_position(self) -> Optional[float]:
        """Validate and return Y position input."""
        try:
            y_pos = float(self.y_entry.get())
            if y_pos < 0 or y_pos > self.app_main.gallery.current_wall.height:
                self.messagebox_showerror("Error",
                                    f"Y position must be between 0 and {self.app_main.gallery.current_wall.height} inches")
                return None
            return self.app_main.gallery.current_wall.height - y_pos
        except ValueError:
            self.messagebox_showerror("Error", "Please enter a valid number for Y position")
            return None

    def on_artwork_select(self, event):
        """Handle artwork selection with order tracking that toggles and renumbers."""
        selected_idx = self.listbox.curselection()

        if not selected_idx:  # If nothing is selected, do nothing
            return

        clicked_idx = selected_idx[-1]  # Get the most recently clicked item

        # Toggle selection - if already selected, remove it
        if self.app_main.gallery.current_wall.artwork[clicked_idx] in self.selected_artworks:
            self.selected_artworks.pop(self.selected_artworks.index(self.app_main.gallery.current_wall.artwork[clicked_idx]))
        else:
            self.selected_artworks.append(self.app_main.gallery.current_wall.artwork[clicked_idx])

        # Update the display to show current numbering
        self.update_display()

    def update_display(self):
        """Update all display elements."""
        # Update listbox with order indicators
        self.listbox.delete(0, tk.END)
        for idx, artwork in enumerate(self.app_main.gallery.current_wall.artwork):
            art_order: int = -1
            for selected_idx, selected_artwork in enumerate(self.selected_artworks):
                if selected_artwork == artwork:
                    art_order = selected_idx
            order = f" ({art_order + 1})" if art_order != -1 else ""
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

            if left < 0 or right > self.app_main.gallery.current_wall.width:
                self.messagebox_showerror("Error", "Boundaries must be within wall dimensions.")
                return None, None

            if left >= right:
                self.messagebox_showerror("Error", "Left boundary must be less than right boundary.")
                return None, None

            return left, right
        except ValueError:
            self.messagebox_showerror("Error", "Please enter valid numbers for boundaries.")
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
            self.messagebox_showerror("Error", "Please select at least one artwork.")
            return

        total_width = sum(art.width for art in self.selected_artworks)
        available_space = right - left
        if available_space < total_width:
            self.messagebox_showerror("Error", "Not enough space for selected artworks.")
            return
        spacing = (available_space - total_width) / (len(self.selected_artworks) + 1)


        if spacing < self.MIN_SPACING:
            if not self.messagebox_askyesno(
                "Warning",
                f"Calculated spacing ({spacing:.1f}\") is very small. Continue anyway?"
            ):
                return

        # Position artworks
        current_x = left + spacing

        for artwork in self.selected_artworks:
            # Calculate position in inches (wall coordinates)
            artwork.position.x = current_x
            # Calculate Y position so center is at y_pos_center
            artwork.position.y = y_pos_center - (artwork.height / 2)

            self.app_main.gallery.current_wall.update_wall_item(artwork.id, artwork)


            current_x += artwork.width + spacing
        
        self.app_main.switch_screen(ScreenType.EDITOR)
        self.on_close()