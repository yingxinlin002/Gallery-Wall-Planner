import tkinter as tk
from tkinter import messagebox, filedialog
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.artwork import Artwork  # New import

class ArtworkManuallyUI:
    def __init__(self, root, return_to_editor, selected_wall):
        self.root = root
        self.return_to_editor = return_to_editor
        self.selected_wall = selected_wall
        self.styles = get_ui_styles()
        self.create_ui()

    def create_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Title
        tk.Label(container, 
                text="Enter Artwork Manually", 
                font=self.styles["title_font"]).pack(pady=20)

        # Instruction
        tk.Label(container,
                text="Please enter artworks:",
                font=self.styles["label_font"]).pack(pady=10)

        # Form frame with grid layout
        form_frame = tk.Frame(container)
        form_frame.pack(pady=10)

        # Form fields
        fields = [
            ("Name:", "name_entry"),
            ("Width (inches):", "width_entry"),
            ("Height (inches):", "height_entry"),
            ("Hanging Point (inches from top):", "hanging_entry"),
            ("Depth (optional, inches):", "depth_entry")
        ]

        for row, (label_text, attr_name) in enumerate(fields):
            tk.Label(form_frame, 
                    text=label_text, 
                    font=self.styles["label_font"]).grid(row=row, column=0, sticky="e", pady=5)
            
            entry = tk.Entry(form_frame, font=self.styles["label_font"])
            entry.grid(row=row, column=1, pady=5, padx=5)
            setattr(self, attr_name, entry)

        # Image upload
        self.image_path = tk.StringVar()
        tk.Label(form_frame, 
                text="Image (optional):", 
                font=self.styles["label_font"]).grid(row=len(fields), column=0, sticky="e", pady=5)
        
        tk.Button(form_frame, 
                text="Browse", 
                command=self.upload_image,
                width=10,
                bg=self.styles["bg_info"],
                fg=self.styles["fg_white"],
                font=self.styles["button_font"]).grid(row=len(fields), column=1, pady=5, padx=5, sticky="w")

        # Artwork preview area
        self.preview_frame = tk.Frame(container)
        self.preview_frame.pack(pady=20, fill="x")
        
        # Buttons frame
        button_frame = tk.Frame(container)
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

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path.set(file_path)
            messagebox.showinfo("Success", "Image uploaded successfully!")

    def create_artwork(self):
        # Get values from entries
        name = self.name_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()
        hanging_point = self.hanging_entry.get()
        depth = self.depth_entry.get()
        image_path = self.image_path.get()

        # Validate required fields
        if not all([name, width, height, hanging_point]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return

        try:
            # Convert inputs to proper types
            width = float(width)
            height = float(height)
            hanging_point = float(hanging_point)
            depth = float(depth) if depth else 0.0
            
            # Create Artwork object with positional arguments
            artwork = Artwork(
                name,          # Positional argument for name
                width,         # Positional argument for width
                height,        # Positional argument for height
                depth,         # Positional argument for depth
                hanging_point, # Positional argument for hanging_point
                image_path     # Positional argument for image_path
            )
            
            # Add artwork to the selected wall
            self.selected_wall.add_artwork(artwork)
            
            # Show success message and preview
            messagebox.showinfo("Success", f"Artwork '{name}' added to wall '{self.selected_wall.name}'")
            self.show_artwork_preview(artwork)
            
            # Clear form for next entry
            self.clear_form()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def show_artwork_preview(self, artwork):
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Create a scrollable preview area
        canvas = tk.Canvas(self.preview_frame)
        scrollbar = tk.Scrollbar(self.preview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Show artwork details in the scrollable frame
        details = [
            f"Artwork: {artwork.name}",
            f"Wall: {self.selected_wall.name}",
            f"Dimensions: {artwork.width}\" W × {artwork.height}\" H",
            f"Hanging Point: {artwork.hanging_point}\" from top"
        ]
        
        if artwork.depth > 0:
            details.append(f"Depth: {artwork.depth}\"")
        
        if artwork.image_path:
            details.append(f"Image: {artwork.image_path}")

        for i, detail in enumerate(details):
            tk.Label(scrollable_frame,
                    text=detail,
                    font=self.styles["label_font"]).pack(anchor="w", pady=2)

    def clear_form(self):
        """Clear all form fields for new entry"""
        self.name_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.hanging_entry.delete(0, tk.END)
        self.depth_entry.delete(0, tk.END)
        self.image_path.set("")

    def back_to_editor(self):
        """Return to the editor UI"""
        from gallery_wall_planner.gui.editorUI import EditorUI
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
        # Navigate back to EditorUI with the updated wall
        EditorUI(self.root, self.return_to_editor, self.selected_wall)