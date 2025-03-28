import tkinter as tk
from tkinter import messagebox, filedialog
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.artwork import Artwork

class ArtworkManuallyUI:
    def __init__(self, root, return_to_editor, selected_wall):
        self.root = root
        self.return_to_editor = return_to_editor
        self.selected_wall = selected_wall
        self.styles = get_ui_styles()
        self.artwork_items = []  # To store created artwork objects
        self.create_ui()

    def create_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container with left and right panes
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left pane - Form
        left_pane = tk.Frame(main_container)
        main_container.add(left_pane)

        # Right pane - Artwork list
        right_pane = tk.Frame(main_container)
        main_container.add(right_pane)

        # Title
        tk.Label(left_pane, 
                text="Enter Artwork Manually", 
                font=self.styles["title_font"]).pack(pady=20)

        # Instruction
        tk.Label(left_pane,
                text="Please enter artwork details:",
                font=self.styles["label_font"]).pack(pady=10)

        # Form frame with grid layout
        form_frame = tk.Frame(left_pane)
        form_frame.pack(pady=10)

        # Form fields with examples
        fields = [
            ("Name*:", "name_entry", "e.g., Starry Night"),
            ("Medium:", "medium_entry", "e.g., Oil on canvas"),
            ("Width* (inches):", "width_entry", "e.g., 24.5"),
            ("Height* (inches):", "height_entry", "e.g., 36.0"),
            ("Hanging Point* (inches from top):", "hanging_entry", "e.g., 12.0"),
            ("Depth (inches):", "depth_entry", "e.g., 2.0"),
            ("Price (USD):", "price_entry", "e.g., 2500.00"),
            ("Not For Sale:", "nfs_entry", "")  # Empty example text for NFS
        ]

        for row, (label_text, attr_name, example_text) in enumerate(fields[:-1]):  # Skip NFS for now
            tk.Label(form_frame, 
                    text=label_text, 
                    font=self.styles["label_font"]).grid(row=row, column=0, sticky="e", pady=5)
            
            entry = tk.Entry(form_frame, font=self.styles["label_font"], fg="grey")
            entry.insert(0, example_text)
            entry.bind("<FocusIn>", lambda event, e=entry, t=example_text: self.clear_example(event, e, t))
            entry.bind("<FocusOut>", lambda event, e=entry, t=example_text: self.restore_example(event, e, t))
            entry.grid(row=row, column=1, pady=5, padx=5)
            setattr(self, attr_name, entry)

        # Add NFS checkbox in the next row
        row = len(fields) - 1  # Last row
        tk.Label(form_frame,
                text=fields[-1][0],  # "Not For Sale:"
                font=self.styles["label_font"]).grid(row=row, column=0, sticky="e", pady=5)
        
        # NFS checkbox frame to align with entry widgets
        nfs_frame = tk.Frame(form_frame)
        nfs_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        self.nfs_var = tk.BooleanVar()
        tk.Checkbutton(nfs_frame,
                      variable=self.nfs_var,
                      font=self.styles["label_font"]).pack(side="left")

        # Image upload
        row += 1
        self.image_path = tk.StringVar()
        tk.Label(form_frame, 
                text="Image:", 
                font=self.styles["label_font"]).grid(row=row, column=0, sticky="e", pady=5)
        
        tk.Button(form_frame, 
                text="Browse", 
                command=self.upload_image,
                width=10,
                bg=self.styles["bg_info"],
                fg=self.styles["fg_white"],
                font=self.styles["button_font"]).grid(row=row, column=1, pady=5, padx=5, sticky="w")

        # Buttons frame
        button_frame = tk.Frame(left_pane)
        button_frame.pack(pady=20)

        # Create Artwork button
        tk.Button(button_frame,
                text="Create Artwork",
                command=self.create_artwork,
                width=self.styles["button_width"],
                bg=self.styles["bg_success"],
                fg=self.styles["fg_white"],
                font=self.styles["button_font"],
                padx=self.styles["button_padx"],
                pady=self.styles["button_pady"]).pack(side="left", padx=10)

        # Back to Editor button
        tk.Button(button_frame,
                text="Back to Editor",
                command=self.back_to_editor,
                width=self.styles["button_width"],
                bg=self.styles["bg_secondary"],
                fg=self.styles["fg_white"],
                font=self.styles["button_font"],
                padx=self.styles["button_padx"],
                pady=self.styles["button_pady"]).pack(side="right", padx=10)

        # Right pane - Artwork list
        tk.Label(right_pane,
                text="Created Artworks",
                font=self.styles["title_font"]).pack(pady=10)

        # Create scrollable frame for artwork list
        self.artwork_canvas = tk.Canvas(right_pane, bg="white")
        scrollbar = tk.Scrollbar(right_pane, orient="vertical", command=self.artwork_canvas.yview)
        self.artwork_frame = tk.Frame(self.artwork_canvas, bg="white")

        self.artwork_frame.bind(
            "<Configure>",
            lambda e: self.artwork_canvas.configure(
                scrollregion=self.artwork_canvas.bbox("all")
            )
        )

        self.artwork_canvas.create_window((0, 0), window=self.artwork_frame, anchor="nw")
        self.artwork_canvas.configure(yscrollcommand=scrollbar.set)

        self.artwork_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display existing artworks if any
        self.update_artwork_list()

    def update_artwork_list(self):
        """Update the artwork list display"""
        # Clear existing artwork items
        for widget in self.artwork_frame.winfo_children():
            widget.destroy()
        
        # Display all artworks in the selected wall
        if hasattr(self.selected_wall, 'artwork'):
            for artwork in self.selected_wall.artwork:
                self.add_artwork_to_list(artwork)
        else:
            tk.Label(self.artwork_frame,
                    text="No artworks added yet",
                    fg="gray").pack(pady=20)

    def add_artwork_to_list(self, artwork):
        """Add an artwork item to the list"""
        frame = tk.Frame(self.artwork_frame, bg="white", bd=1, relief="groove", padx=10, pady=5)
        frame.pack(fill="x", pady=5, padx=5)
        
        # Artwork name and dimensions
        tk.Label(frame,
                text=f"{artwork.name} ({artwork.width}\" × {artwork.height}\")",
                font=self.styles["label_font"],
                bg="white").pack(anchor="w")
        
        # Medium and price
        details = []
        if artwork.medium:
            details.append(f"Medium: {artwork.medium}")
        if artwork.price > 0:
            details.append(f"Price: ${artwork.price:,.2f}")
        if artwork.nfs:
            details.append("NFS")
            
        if details:
            tk.Label(frame,
                    text=" | ".join(details),
                    font=self.styles["small_font"],
                    bg="white").pack(anchor="w")
        
        # Add to our tracking list
        self.artwork_items.append(frame)

    # [Rest of the methods remain the same...]
    # clear_example, restore_example, upload_image, create_artwork, 
    # show_artwork_preview, clear_form, back_to_editor methods

    def clear_example(self, event, entry, example_text):
        """Clear the example text when entry is focused"""
        if entry.get() == example_text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def restore_example(self, event, entry, example_text):
        """Restore example text if entry is empty"""
        if not entry.get():
            entry.insert(0, example_text)
            entry.config(fg="grey")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path.set(file_path)
            messagebox.showinfo("Success", "Image uploaded successfully!")

    def create_artwork(self):
        # Get values from entries
        name = self.name_entry.get()
        medium = self.medium_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()
        hanging_point = self.hanging_entry.get()
        depth = self.depth_entry.get()
        price = self.price_entry.get()
        nfs = self.nfs_var.get()
        image_path = self.image_path.get()

        # Validate required fields
        required_fields = [
            ("Name", name, "e.g., Starry Night"),
            ("Width", width, "e.g., 24.5"),
            ("Height", height, "e.g., 36.0"),
            ("Hanging Point", hanging_point, "e.g., 12.0")
        ]
        
        for field_name, field_value, example_text in required_fields:
            if not field_value:
                messagebox.showerror("Error", f"Please fill in {field_name}")
                return

        try:
            # Convert inputs to proper types
            width = float(width)
            height = float(height)
            hanging_point = float(hanging_point)
            depth = float(depth) if depth and depth != "e.g., 2.0" else 0.0
            price = float(price) if price and price != "e.g., 2500.00" else 0.0
            
            # Create Artwork object with all parameters
            artwork = Artwork(
                name=name,
                medium=medium,
                width=width,
                height=height,
                depth=depth,
                hanging_point=hanging_point,
                price=price,
                nfs=nfs,
                image_path=image_path
            )
            
            # Add artwork to the selected wall
            self.selected_wall.add_artwork(artwork)
            self.show_artwork_preview(artwork)
            self.clear_form()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def show_artwork_preview(self, artwork):
        """Show the newly created artwork in the list"""
        # Add the artwork to our list display
        self.add_artwork_to_list(artwork)
        
        # Optional: Scroll to the bottom to show the new artwork
        self.artwork_canvas.yview_moveto(1.0)

    def clear_form(self):
        """Clear all form fields for new entry"""
        # Entry fields with their example texts
        entries = [
            (self.name_entry, "e.g., Starry Night"),
            (self.medium_entry, "e.g., Oil on canvas"),
            (self.width_entry, "e.g., 24.5"),
            (self.height_entry, "e.g., 36.0"),
            (self.hanging_entry, "e.g., 12.0"),
            (self.depth_entry, "e.g., 2.0"),
            (self.price_entry, "e.g., 2500.00")
        ]
        
        # Clear each entry and restore example text
        for entry, example in entries:
            entry.delete(0, tk.END)
            entry.insert(0, example)
            entry.config(fg="grey")
        
        # Reset other fields
        self.image_path.set("")
        self.nfs_var.set(False)

    def back_to_editor(self):
        """Return to the editor UI"""
        from gallery_wall_planner.gui.editorUI import EditorUI
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
        # Navigate back to EditorUI with the updated wall
        EditorUI(self.root, self.return_to_editor, self.selected_wall)