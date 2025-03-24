import tkinter as tk
from tkinter import ttk, messagebox
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.gui.SelectWallSpaceUI import SelectWallSpaceUI  # Import SelectWallSpaceUI

class EditorUI:
    def __init__(self, root, return_to_home, selected_wall):
        self.root = root
        self.return_to_home = return_to_home
        self.selected_wall = selected_wall
        self.styles = get_ui_styles()
        self.create_ui()

    def create_ui(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Back button at top left
        back_button = tk.Button(main_frame,
                              text="< Back to Wall Selection",
                              command=self.back_to_wall_selection,
                              bg=self.styles["bg_secondary"],
                              fg=self.styles["fg_white"],
                              font=self.styles["button_font"],
                              padx=self.styles["button_padx"],
                              pady=self.styles["button_pady"])
        back_button.pack(side="top", anchor="nw", padx=10, pady=10)

        # Content frame below back button
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        # Left Panel - Control Panel with collapsible menus
        control_panel = tk.Frame(content_frame, width=300, bg="#f0f0f0")
        control_panel.pack(side="left", fill="y")

        # Collapsible menu for Add Artwork
        self.add_artwork_frame = self.create_collapsible_menu(
            control_panel, "Add Artwork", expanded=True)
        
        # Add Artwork Content
        csv_button = tk.Button(self.add_artwork_frame,
                             text="Import Artwork by CSV file",
                             command=lambda: messagebox.showinfo("Info", "Import Artwork by CSV file button pushed"),
                             bg=self.styles["bg_info"],
                             fg=self.styles["fg_white"],
                             font=self.styles["button_font"],
                             padx=self.styles["button_padx"],
                             pady=self.styles["button_pady"])
        csv_button.pack(pady=5, fill="x")
        
        manual_button = tk.Button(self.add_artwork_frame,
                                text="Add Artwork Manually",
                                command=lambda: messagebox.showinfo("Info", "Add Artwork Manually button pushed"),
                                bg=self.styles["bg_info"],
                                fg=self.styles["fg_white"],
                                font=self.styles["button_font"],
                                padx=self.styles["button_padx"],
                                pady=self.styles["button_pady"])
        manual_button.pack(pady=5, fill="x")

        # Collapsible menu for Imported Artwork
        self.imported_artwork_frame = self.create_collapsible_menu(
            control_panel, "Imported Artwork", expanded=False)
        
        # Placeholder for imported artwork list
        tk.Label(self.imported_artwork_frame, 
                text="Imported artwork will appear here",
                fg="gray").pack(pady=50)

        # Calculate Installation Instruction Button
        calc_button = tk.Button(control_panel,
                              text="Calculate Installation Instruction",
                              command=lambda: messagebox.showinfo("Info", "Calculate Installation Instruction button pushed"),
                              bg=self.styles["bg_primary"],
                              fg=self.styles["fg_white"],
                              font=self.styles["button_font"],
                              padx=self.styles["button_padx"],
                              pady=self.styles["button_pady"])
        calc_button.pack(side="bottom", pady=10, fill="x")

        # Right Panel - Gallery Wall Space
        wall_space = tk.Frame(content_frame, bg="white")
        wall_space.pack(side="right", fill="both", expand=True)

        # Placeholder for wall space
        tk.Label(wall_space, 
                text=f"Wall Space: {self.selected_wall.name}\n{self.selected_wall.width}\" x {self.selected_wall.height}\"",
                font=self.styles["title_font"],
                bg="white").pack(expand=True)

    def create_collapsible_menu(self, parent, title, expanded=True):
        """Create a collapsible menu frame with toggle button"""
        menu_frame = tk.Frame(parent, bg="#e0e0e0", bd=1, relief="raised")
        menu_frame.pack(fill="x", pady=2)
        
        # Header with toggle button
        header = tk.Frame(menu_frame, bg="#e0e0e0")
        header.pack(fill="x")
        
        toggle_btn = tk.Button(header,
                             text="▼" if expanded else "▶",
                             command=lambda: self.toggle_menu(menu_frame, toggle_btn, content_frame),
                             bg="#e0e0e0",
                             fg="black",
                             bd=0,
                             font=("Arial", 10))
        toggle_btn.pack(side="left")
        
        tk.Label(header,
                text=title,
                font=self.styles["label_font"],
                bg="#e0e0e0").pack(side="left", padx=5)
        
        # Content frame
        content_frame = tk.Frame(menu_frame, bg="white")
        if expanded:
            content_frame.pack(fill="x")
        else:
            content_frame.pack_forget()
        
        return content_frame

    def toggle_menu(self, menu_frame, toggle_btn, content_frame):
        """Toggle the collapsible menu visibility"""
        if content_frame.winfo_ismapped():
            content_frame.pack_forget()
            toggle_btn.config(text="▶")
        else:
            content_frame.pack(fill="x")
            toggle_btn.config(text="▼")

    def back_to_wall_selection(self):
        """Navigate back to the SelectWallSpaceUI"""
        SelectWallSpaceUI(self.root, self.return_to_home)