import tkinter as tk
from tkinter import messagebox, ttk
from gallery_wall_planner.models.wall import Wall

class SelectWallSpaceUI:
    def __init__(self, root, return_to_home):
        self.root = root
        self.return_to_home = return_to_home
        # Create a default wall space for demonstration purposes
        self.walls = [Wall("Example Wall", 100, 75, "grey")]
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

        # Scrollable list for wall spaces
        self.wall_listbox = tk.Listbox(left_panel, width=30, height=10, font=("Arial", 12))
        self.wall_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Add walls to the listbox
        for wall in self.walls:
            self.wall_listbox.insert(tk.END, wall.name)

        # Create New Wall Space Button
        tk.Button(left_panel, text="Create New Wall Space", command=self.create_new_wall_space, width=20, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="bottom", pady=10)

        # Right Panel: Wall space preview (placeholder)
        right_panel = tk.Frame(content_frame, width=500, bg="#ffffff")
        right_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Placeholder for wall space preview
        tk.Label(right_panel, text="Wall Space Preview", font=("Arial", 16), bg="#ffffff").pack(pady=50)

        # Bottom Buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=10)

        # Back to Home Button (Left Side)
        tk.Button(bottom_frame, text="< Back to Home", command=self.return_to_home, width=15, bg="#69718A", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="left", padx=10)

        # Export Layout Button (Center)
        tk.Button(bottom_frame, text="Export Layout", command=self.export_layout, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="left", padx=10)

        # Continue Button (Right Side)
        tk.Button(bottom_frame, text="Continue >", command=self.continue_to_next, width=15, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side="right", padx=10)

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