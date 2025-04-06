import tkinter as tk
from tkinter import ttk, messagebox
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.gui.SelectWallSpaceUI import SelectWallSpaceUI

class EditorUI:
    def __init__(self, root, return_to_home, selected_wall):
        self.root = root
        self.return_to_home = return_to_home
        self.selected_wall = selected_wall
        self.styles = get_ui_styles()
        self.artwork_list = []  # Initialize the artwork_list
        self.sidebar_visible = True  # Track sidebar state
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

        # Container for sidebar and toggle button
        self.sidebar_container = tk.Frame(content_frame)
        self.sidebar_container.pack(side="left", fill="y")

        # Left Panel - Control Panel
        self.control_panel = tk.Frame(self.sidebar_container, width=300, bg="#f0f0f0")
        self.control_panel.pack(side="left", fill="y")

        # Sidebar toggle button - placed to the right of control panel
        self.toggle_btn = tk.Button(self.sidebar_container,
                                  text="◀",  # Arrow pointing left when sidebar is visible
                                  command=self.toggle_sidebar,
                                  bg="#e0e0e0",
                                  fg="black",
                                  bd=1,
                                  relief="raised",
                                  font=("Arial", 10))
        self.toggle_btn.pack(side="right", fill="y")

        # Collapsible menu for Add Artwork
        self.add_artwork_frame = self.create_collapsible_menu(
            self.control_panel, "Add Artwork", expanded=True)
        
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
                                command=self.open_artwork_manual_ui,
                                bg=self.styles["bg_info"],
                                fg=self.styles["fg_white"],
                                font=self.styles["button_font"],
                                padx=self.styles["button_padx"],
                                pady=self.styles["button_pady"])
        manual_button.pack(pady=5, fill="x")

        # Collapsible menu for Imported Artwork
        self.imported_artwork_frame = self.create_collapsible_menu(
            self.control_panel, "Imported Artwork", expanded=True)
        
        # Create a scrollable frame for artwork list
        self.create_artwork_list_frame()

        # Calculate Installation Instruction Button
        self.calc_button = tk.Button(self.control_panel,
                              text="Calculate Installation Instruction",
                              command=lambda: messagebox.showinfo("Info", "Calculate Installation Instruction button pushed"),
                              bg=self.styles["bg_primary"],
                              fg=self.styles["fg_white"],
                              font=self.styles["button_font"],
                              padx=self.styles["button_padx"],
                              pady=self.styles["button_pady"])
        self.calc_button.pack(side="bottom", pady=10, fill="x")

        # Right Panel - Gallery Wall Space
        self.wall_space = tk.Frame(content_frame, bg="white")
        self.wall_space.pack(side="right", fill="both", expand=True)

        # Placeholder for wall space
        self.wall_label = tk.Label(self.wall_space, 
                text=f"Wall Space: {self.selected_wall.name}\n{self.selected_wall.width}\" x {self.selected_wall.height}\"",
                font=self.styles["title_font"],
                bg="white")
        self.wall_label.pack(expand=True)

    def toggle_sidebar(self):
        """Toggle the sidebar visibility"""
        if self.sidebar_visible:
            # Hide the control panel
            self.control_panel.pack_forget()
            # Move toggle button to left side (now acts as the only visible element)
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(side="left", fill="y")
            self.toggle_btn.config(text="▶")  # Arrow pointing right when sidebar is hidden
            # Expand the wall space
            self.wall_space.pack_configure(expand=True, fill="both")
        else:
            # Show the control panel
            self.control_panel.pack(side="left", fill="y")
            # Move toggle button back to right side
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(side="right", fill="y")
            self.toggle_btn.config(text="◀")  # Arrow pointing left when sidebar is visible
            # Reset wall space packing
            self.wall_space.pack(side="right", fill="both", expand=True)
        
        self.sidebar_visible = not self.sidebar_visible

    # ... (rest of your methods remain exactly the same)
    def create_artwork_list_frame(self):
        """Create a scrollable frame for artwork list"""
        # Clear existing widgets and artwork list
        for widget in self.imported_artwork_frame.winfo_children():
            widget.destroy()
        self.artwork_list = []  # Reset the artwork list
        
        # Rest of the method remains the same...
        canvas = tk.Canvas(self.imported_artwork_frame, bg="white")
        scrollbar = tk.Scrollbar(self.imported_artwork_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

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

        # Display all artworks in the selected wall
        if hasattr(self.selected_wall, 'artwork'):
            for artwork in self.selected_wall.artwork:
                self.add_artwork_item(scrollable_frame, artwork)
        else:
            tk.Label(scrollable_frame, 
                    text="No artworks added yet",
                    fg="gray").pack(pady=20)

    def add_artwork_item(self, parent, artwork):
        """Add a single artwork item to the list"""
        frame = tk.Frame(parent, bg="white", bd=1, relief="groove", padx=5, pady=5)
        frame.pack(fill="x", pady=2, padx=2)
        
        # Artwork name and basic info
        tk.Label(frame, 
                text=f"{artwork.name} ({artwork.width}\" x {artwork.height}\")",
                font=self.styles["label_font"],
                bg="white").pack(anchor="w")
        
        # Additional details
        details = []
        if artwork.medium:
            details.append(f"Medium: {artwork.medium}")
        if artwork.price > 0:
            details.append(f"Price: ${artwork.price:,.2f}")
        if artwork.nfs:
            details.append("Not For Sale")
            
        if details:
            tk.Label(frame,
                    text=", ".join(details),
                    font=self.styles.get("small_font", ("Arial", 10)),
                    bg="white").pack(anchor="w")

        # Add to our tracking list
        self.artwork_list.append(frame)

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

    def open_artwork_manual_ui(self):
        from gallery_wall_planner.gui.ArtworkManuallyUI import ArtworkManuallyUI
        # Clear current UI
        for widget in self.root.winfo_children():
            widget.destroy()
        # Open manual artwork UI with a callback to refresh the editor
        ArtworkManuallyUI(self.root, 
                         lambda: EditorUI(self.root, self.return_to_home, self.selected_wall),
                         self.selected_wall)

    def refresh_artwork_list(self):
        """Refresh the artwork list display"""
        self.create_artwork_list_frame()