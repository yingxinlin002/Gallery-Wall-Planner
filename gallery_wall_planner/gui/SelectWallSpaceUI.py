import tkinter as tk
from tkinter import messagebox, ttk
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.gallery import Gallery

class SelectWallSpaceUI:
    def __init__(self, root, return_to_home):
        self.root = root
        self.return_to_home = return_to_home
        self.walls = Gallery.get_walls()
        self.delete_buttons = {}
        self.create_ui()

    def create_ui(self):
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Add a title
        tk.Label(self.root, text="Select Wall Space", font=("Arial", 24)).pack(pady=20, anchor="w")

        # Main content frame
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True)

        # Left Panel: List of wall spaces
        left_panel = tk.Frame(content_frame, width=300, bg="#f0f0f0")
        left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Scrollable list for wall spaces with a frame to hold both name and delete button
        self.list_container = tk.Frame(left_panel)
        self.list_container.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.wall_listbox = tk.Listbox(self.list_container, width=25, height=10, font=("Arial", 12))
        self.wall_listbox.pack(side="left", fill="both", expand=True)

        # Add walls to the listbox
        for wall in self.walls:
            self.wall_listbox.insert(tk.END, wall.name)

        # Bind selection event to update the preview and show delete button
        self.wall_listbox.bind("<<ListboxSelect>>", self.on_wall_selected)

        # Create New Wall Space Button
        tk.Button(left_panel, text="Create New Wall Space", command=self.create_new_wall_space, width=20, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="bottom", pady=10)

        # Right Panel: Wall space preview
        right_panel = tk.Frame(content_frame, width=500, bg="#ffffff")
        right_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Canvas for wall preview
        self.preview_canvas = tk.Canvas(right_panel, width=400, height=300, bg="white", highlightthickness=1, highlightbackground="black")
        self.preview_canvas.pack(pady=20)

        # Label for wall details
        self.wall_details_label = tk.Label(right_panel, text="Select a wall to preview", font=("Arial", 12), bg="#ffffff")
        self.wall_details_label.pack(pady=10)

        # Bottom Buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=10)

        # Back to Home Button (Left Side)
        tk.Button(bottom_frame, text="< Back to Home", command=self.return_to_home, width=15, bg="#69718A", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="left", padx=10)

        # Export Layout Button (Center)
        tk.Button(bottom_frame, text="Export Layout", command=self.export_layout, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="left", padx=10)

        # Continue Button (Right Side)
        tk.Button(bottom_frame, text="Continue >", command=self.continue_to_next, width=15, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="right", padx=10)

    def on_wall_selected(self, event=None):
        """Handle wall selection - update preview and show delete button"""
        self.update_wall_preview()
        
        # Remove any existing delete button
        for btn in self.delete_buttons.values():
            btn.destroy()
        self.delete_buttons.clear()

        selected_index = self.wall_listbox.curselection()
        if selected_index:
            wall = self.walls[selected_index[0]]
            
            # Create delete button
            delete_btn = tk.Button(
                self.list_container,
                text="×",  # Using × symbol instead of X
                fg="red",
                font=("Arial", 12, "bold"),
                bd=0,
                command=lambda w=wall: self.delete_wall(w)
            )
            delete_btn.pack(side="right", padx=(0, 5))
            
            # Add tooltip
            self.create_tooltip(delete_btn, f"Delete {wall.name}")
            
            # Store reference to button
            self.delete_buttons[wall.name] = delete_btn

    def create_tooltip(self, widget, text):
        """Create a simple tooltip that appears on hover"""
        tooltip = tk.Toplevel(self.root)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        
        label = tk.Label(tooltip, text=text, bg="lightyellow", relief="solid", borderwidth=1)
        label.pack()
        
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        tooltip.bind("<Leave>", leave)

    def delete_wall(self, wall):
        """Handle wall deletion with confirmation"""
        confirm = messagebox.askyesno(
            "Delete Wall", 
            f"Are you sure you want to delete '{wall.name}'?",
            parent=self.root
        )
        
        if confirm:
            # Remove from gallery
            Gallery.remove_wall(wall)
            
            # Update UI
            self.walls = Gallery.get_walls()
            self.wall_listbox.delete(0, tk.END)
            for wall in self.walls:
                self.wall_listbox.insert(tk.END, wall.name)
            
            # Clear preview
            self.preview_canvas.delete("all")
            self.wall_details_label.config(text="Select a wall to preview")
            
            # Remove delete button
            if wall.name in self.delete_buttons:
                self.delete_buttons[wall.name].destroy()
                del self.delete_buttons[wall.name]

    def create_new_wall_space(self):
        # Navigate to NewGalleryUI to create a new wall space
        from gallery_wall_planner.gui.NewExhibitUI import NewGalleryUI
        NewGalleryUI(self.root, self.return_to_home)

    def export_layout(self):
        # Export the selected wall layout
        selected_wall = self.get_selected_wall()
        if selected_wall:
            exported_data = selected_wall.export_wall()
            messagebox.showinfo("Export Layout", f"Layout exported successfully!\n{exported_data}")
        else:
            messagebox.showwarning("Error", "Please select a wall space to export.")

    def continue_to_next(self):
        # Continue to the next step with the selected wall
        selected_wall = self.get_selected_wall()
        if selected_wall:
            messagebox.showinfo("Continue", f"Selected Wall: {selected_wall.toString()}")
        else:
            messagebox.showwarning("Error", "Please select a wall space to continue.")

    def get_selected_wall(self):
        # Get the selected wall from the listbox
        selected_index = self.wall_listbox.curselection()
        if selected_index:
            return self.walls[selected_index[0]]
        return None

    def update_wall_preview(self, event=None):
        """Update the wall preview canvas and details when a wall is selected."""
        selected_wall = self.get_selected_wall()
        if selected_wall:
            # Clear the canvas
            self.preview_canvas.delete("all")

            # Draw the wall preview
            canvas_width = 400
            canvas_height = 300
            wall_width = selected_wall.width
            wall_height = selected_wall.height

            # Calculate aspect ratio and scale to fit canvas
            ratio = min(canvas_width / wall_width, canvas_height / wall_height)
            scaled_width = wall_width * ratio
            scaled_height = wall_height * ratio

            # Draw the wall rectangle
            x0 = (canvas_width - scaled_width) / 2
            y0 = (canvas_height - scaled_height) / 2
            x1 = x0 + scaled_width
            y1 = y0 + scaled_height
            self.preview_canvas.create_rectangle(x0, y0, x1, y1, fill=selected_wall.color, outline="black")

            # Draw height and width lines with labels
            self.preview_canvas.create_line(x0, y1, x0 - 10, y1, fill="black")  # Width line start
            self.preview_canvas.create_line(x1, y1, x1 + 10, y1, fill="black")  # Width line end
            self.preview_canvas.create_text((x0 + x1) / 2, y1 + 15, text=f"{wall_width} inches", anchor="n")

            self.preview_canvas.create_line(x0, y0, x0, y0 - 10, fill="black")  # Height line start
            self.preview_canvas.create_line(x0, y1, x0, y1 + 10, fill="black")  # Height line end
            self.preview_canvas.create_text(x0 - 15, (y0 + y1) / 2, text=f"{wall_height} inches", anchor="e", angle=90)

            # Update wall details label
            self.wall_details_label.config(text=f"Wall: {selected_wall.name}\nColor: {selected_wall.color}")