import tkinter as tk
from tkinter import ttk, messagebox
from gallery_wall_planner.gui.ui_styles import (
    init_styles,
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style,
    get_ui_styles
)
# from gallery_wall_planner.deprecated.virtualWall import VirtualWall
from gallery_wall_planner.gui.Screen_Base import Screen_Base
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.gui.WallCanvas import WallCanvas
from gallery_wall_planner.models.structures import CanvasDimensions, Padding
from gallery_wall_planner.gui.popup_install_instruct import open_install_instruct_popup  # NEW IMPORT INSIDE WHERE "Calculate Installation Instruction" BUTTON LIVES
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.utils.floating_toolbar import FloatingToolbar

class ArtBtn(tk.Button):
    def toggle_bg(self, on: bool = True):
        if on:
            self.configure(background="red")
        else:
            self.configure(background="green")

class Screen_EditorUI(Screen_Base):
    def __init__(self, AppMain: AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.selected_wall = AppMain.editor_wall
        self.styles = get_ui_styles()
        self.artwork_list = []
        self.sidebar_visible = True
        self.sidebar_width = 300
        self.sidebar_animation_running = False
        self.wall_canvas: WallCanvas = None
        self.selected_artwork: Artwork = None
        self.wall_space = None  # Initialize wall_space as None

        # Initialize floating toolbar
        self.floating_toolbar = None

    def load_content(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        back_button = tk.Button(main_frame,
                              text="< Back to Wall Selection",
                              command=lambda: self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE),
                              bg=self.styles["bg_secondary"],
                              fg=self.styles["fg_white"],
                              font=self.styles["button_font"],
                              padx=self.styles["button_padx"],
                              pady=self.styles["button_pady"])
        back_button.pack(side="top", anchor="nw", padx=10, pady=10)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        # Sidebar container setup
        self.sidebar_container = tk.Frame(content_frame)
        self.sidebar_container.pack(side="left", fill="y")

        # Control panel with initial width
        self.control_panel = tk.Frame(self.sidebar_container,
                                    width=self.sidebar_width,
                                    bg="#f0f0f0")
        self.control_panel.pack(side="left", fill="y")
        self.control_panel.pack_propagate(False)  # Prevent children from changing width

        # Toggle button with improved styling
        self.toggle_btn = tk.Button(self.sidebar_container,
                                  text="◀",
                                  command=self.toggle_sidebar,
                                  bg="#e0e0e0",
                                  fg="black",
                                  bd=1,
                                  relief="raised",
                                  font=("Arial", 10),
                                  width=3)
        self.toggle_btn.pack(side="right", fill="y")

        # Add collapsible menus
        self.add_artwork_frame = self.create_collapsible_menu(
            self.control_panel, "Add Artwork", expanded=True)

        # csv_button = tk.Button(self.add_artwork_frame,
        #                      text="Add Artwork by xlsx file",
        #                      command=self.open_artwork_xlsx_ui,
        #                      bg=self.styles["bg_info"],
        #                      fg=self.styles["fg_white"],
        #                      font=self.styles["button_font"],
        #                      padx=self.styles["button_padx"],
        #                      pady=self.styles["button_pady"])
        # csv_button.pack(pady=5, fill="x")

        manual_button = tk.Button(self.add_artwork_frame,
                                text="Add Artwork Manually",
                                command=self.open_artwork_manual_ui,
                                bg=self.styles["bg_info"],
                                fg=self.styles["fg_white"],
                                font=self.styles["button_font"],
                                padx=self.styles["button_padx"],
                                pady=self.styles["button_pady"])
        manual_button.pack(pady=5, fill="x")

        self.imported_artwork_frame = self.create_collapsible_menu(
            self.control_panel, "Imported Artwork", expanded=True)

        self.create_artwork_list_frame()

        # Add new Tool menu with Even Spacing button
        self.tools_frame = self.create_collapsible_menu(self.control_panel, "Tools", expanded=True)
        
        from gallery_wall_planner.utils.even_spacing import apply_even_spacing

        even_spacing_button = tk.Button(self.tools_frame,
                                        text="Even Spacing",
                                        command=lambda: apply_even_spacing(self.wall_canvas, self.selected_wall.artwork),
                                        bg=self.styles["bg_primary"],
                                        fg=self.styles["fg_white"],
                                        font=self.styles["button_font"],
                                        padx=self.styles["button_padx"],
                                        pady=self.styles["button_pady"])
        even_spacing_button.pack(pady=5, fill="x")

        self.calc_button = tk.Button(self.control_panel,
                                    text="Calculate Installation Instruction",
                                    command=self.handle_installation_popup,
                                    bg=self.styles["bg_primary"],
                                    fg=self.styles["fg_white"],
                                    font=self.styles["button_font"],
                                    padx=self.styles["button_padx"],
                                    pady=self.styles["button_pady"])
        self.calc_button.pack(side="bottom", pady=10, fill="x")


        # Initialize wall_space
        self.wall_space = tk.Frame(content_frame, bg="white")
        self.wall_space.pack(side="right", fill="both", expand=True)

        init_styles(self.wall_space)
        header_frame = ttk.Frame(self.wall_space)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)

        self.buttons_frame = ttk.Frame(header_frame)
        self.buttons_frame.pack(side="left", padx=20)
        self.item_buttons = {}

        canvas_dimensions = CanvasDimensions(800, 350, 50, Padding(10, 10, 10, 10))
        self.wall_canvas = WallCanvas(self.AppMain, self.wall_space, canvas_dimensions)
        self.wall_canvas.load_content()
        self.wall_canvas.add_fixed_items(self.selected_wall.permanent_objects_dict)

        # self.canvas = tk.Canvas(self.wall_space, width=self.canvas_width, height=self.canvas_height)
        # apply_canvas_style(self.canvas)
        # self.canvas.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        snap_button_frame = ttk.Frame(self.wall_space)
        snap_button_frame.pack(fill="x", padx=10, pady=(0, 10))

        add_line_btn = ttk.Button(snap_button_frame, text="Add Snap Line", command=self.add_new_snap_line)
        apply_primary_button_style(add_line_btn)
        add_line_btn.pack(side="left", padx=5)

        edit_line_btn = ttk.Button(snap_button_frame, text="Move/Delete Line", command=self.open_manage_lines_popup)
        apply_primary_button_style(edit_line_btn)
        edit_line_btn.pack(side="left", padx=5)

        # Initialize floating toolbar
        self.floating_toolbar = FloatingToolbar(
            self.wall_canvas.canvas,
            on_edit_callback=self.open_edit_popup,
            on_lock_toggle_callback=self.toggle_lock_artwork
        )
        
        # Add draggable items for each artwork
        for artwork in self.selected_wall.artwork:
            self.wall_canvas.add_draggable(artwork)

        # Bind canvas click to hide the toolbar
        self.wall_canvas.canvas.bind("<Button-1>", self.on_canvas_click)

    def handle_installation_popup(self):
        print("Installation popup")
    #     # This should pass the full DraggableArt objects, not just names
    #     open_install_instruct_popup(self._root(), self.selected_wall, self.virtual_wall.items)

    def on_canvas_click(self, event):
        """Hide the floating toolbar when clicking on the canvas."""
        self.floating_toolbar.hide()
        self.clear_artwork_highlight()

    def on_artwork_click(self, artwork, event):
        print(f"[DEBUG] Artwork clicked: {artwork.name}")
        self.selected_artwork = artwork
        self.highlight_artwork(artwork)

        # Show the toolbar near the clicked artwork
        self.floating_toolbar.show(event.x_root, event.y_root)

    def highlight_artwork(self, artwork):
        """Highlight the selected artwork with a purple outline."""
        if artwork.id in self.wall_canvas.draggable_items:
            item = self.wall_canvas.draggable_items[artwork.id]
            self.wall_canvas.canvas.itemconfig(item.id, outline="purple", width=3)

    def clear_artwork_highlight(self):
        """Clear the highlight from all artworks."""
        for item in self.wall_canvas.draggable_items.values():
            self.wall_canvas.canvas.itemconfig(item.id, outline="black", width=1)

    def toggle_lock_artwork(self):
        """Toggle the lock/unlock state of the selected artwork."""
        if self.selected_artwork:
            self.selected_artwork.locked = not getattr(self.selected_artwork, "locked", False)
            state = "locked" if self.selected_artwork.locked else "unlocked"
            messagebox.showinfo("Lock/Unlock", f"Artwork '{self.selected_artwork.name}' is now {state}.")

    def open_edit_popup(self):
        """Open a popup to edit the selected artwork."""
        if not self.selected_artwork:
            return

        popup = tk.Toplevel(self)
        popup.title("Edit Artwork")
        popup.geometry("400x400")
        popup.attributes("-topmost", True)

        # Artwork details
        fields = {
            "Name": self.selected_artwork.name,
            "Hanging Point": self.selected_artwork.hanging_point,
            "Height": self.selected_artwork.height,
            "Width": self.selected_artwork.width,
            "Depth": self.selected_artwork.depth,
            "Medium": self.selected_artwork.medium,
            "Price": self.selected_artwork.price,
            "NFS": self.selected_artwork.nfs,
            "Notes": self.selected_artwork.notes,
        }

        entries = {}
        for idx, (label, value) in enumerate(fields.items()):
            ttk.Label(popup, text=label).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(popup)
            entry.insert(0, str(value))
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            entries[label] = entry

        # Save button
        def save_changes():
            for label, entry in entries.items():
                setattr(self.selected_artwork, label.lower().replace(" ", "_"), entry.get())
            messagebox.showinfo("Edit Artwork", "Artwork details updated successfully.")
            popup.destroy()

        ttk.Button(popup, text="Save", command=save_changes).grid(row=len(fields), column=0, columnspan=2, pady=10)

        # Cancel button
        ttk.Button(popup, text="Cancel", command=popup.destroy).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

    def animate_sidebar(self, target_width):
        """Smoothly animate the sidebar width change"""
        if self.sidebar_animation_running:
            return
            
        self.sidebar_animation_running = True
        
        current_width = self.control_panel.winfo_width()
        step = 15  # Pixels to move each frame
        direction = 1 if target_width > current_width else -1
        
        def update_animation():
            nonlocal current_width
            current_width += step * direction
            
            # Check if we've reached or passed the target
            if (direction == 1 and current_width >= target_width) or \
            (direction == -1 and current_width <= target_width):
                current_width = target_width
                self.control_panel.config(width=current_width)
                self.sidebar_animation_running = False
                self.finalize_sidebar_state()
                return
            
            self.control_panel.config(width=current_width)
            self.after(10, update_animation)  # Changed from self.root.after to self.after
        
        update_animation()

    def finalize_sidebar_state(self):
        """Final adjustments after animation completes"""
        if self.sidebar_visible:
            self.toggle_btn.config(text="◀")
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(side="right", fill="y")
        else:
            self.toggle_btn.config(text="▶")
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(side="left", fill="y")

    def toggle_sidebar(self):
        """Toggle sidebar visibility with animation"""
        if self.sidebar_animation_running:
            return
            
        if self.sidebar_visible:
            self.animate_sidebar(0)
        else:
            self.animate_sidebar(self.sidebar_width)
        
        self.sidebar_visible = not self.sidebar_visible

    def create_artwork_list_frame(self):
        """Create the frame for displaying imported artworks in the sidebar."""
        for widget in self.imported_artwork_frame.winfo_children():
            widget.destroy()

        self.artwork_list = []  # Clear existing list

        # Create scrollable canvas for artwork list
        canvas = tk.Canvas(self.imported_artwork_frame, bg="white")
        scrollbar = tk.Scrollbar(self.imported_artwork_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add artworks to the list
        if hasattr(self.selected_wall, 'artwork') and self.selected_wall.artwork:
            for artwork in self.selected_wall.artwork:
                self.add_artwork_item(scrollable_frame, artwork)
        else:
            tk.Label(scrollable_frame,
                     text="No artworks added yet",
                     fg="gray").pack(pady=20)

    def add_artwork_item(self, parent, artwork: Artwork):
        """Create a clickable artwork item in the sidebar"""
        print(f"adding {artwork.name}")
        art_btn = ArtBtn(parent, text=f"{artwork.name} ({artwork.width}\" × {artwork.height}\")")
        art_btn.config(command=lambda: (self.select_artwork(artwork), art_btn.toggle_bg()))
        art_btn.pack(fill="x", pady=2, padx=2)
        # frame = tk.Frame(parent, bg="white", bd=1, relief="groove", padx=5, pady=5)
        # frame.pack(fill="x", pady=2, padx=2)
        # frame.artwork = artwork  # Store reference to artwork
        #
        # # Highlight if this is the selected artwork
        # if self.selected_artwork and self.selected_artwork == artwork:
        #     frame.config(bg="#f0f0ff")  # Light purple background
        #
        # # Make the whole frame clickable
        # # frame.bind("<Button-1>", lambda e, a=artwork: self.select_artwork(a))
        # frame.bind("<Button-1>", lambda e: print(f"clicked {artwork.name}"))
        #
        # # Artwork name and dimensions
        # tk.Label(frame,
        #          text=f"{artwork.name} ({artwork.width}\" × {artwork.height}\")",
        #          font=self.styles["label_font"],
        #          bg=frame["bg"]).pack(anchor="w")
        #
        # self.artwork_list.append(frame)

    def select_artwork(self, artwork: Artwork):
        """Handle artwork selection from the sidebar."""
        print(f"DEBUG: select_artwork called with {artwork.name}")
        # btn.config(bg='red')
        self.wall_canvas.add_draggable(artwork)
        
        # # Store the selected artwork
        # self.selected_artwork = artwork
        #
        # # Update highlights in the sidebar
        # for item in self.artwork_list:
        #     if hasattr(item, 'artwork') and item.artwork == artwork:
        #         item.config(bg="#f0f0ff")  # Light purple for selected
        #         # Also update any labels inside the frame
        #         for child in item.winfo_children():
        #             if isinstance(child, tk.Label):
        #                 child.config(bg="#f0f0ff")
        #     else:
        #         item.config(bg="white")  # White for others
        #         # Also update any labels inside the frame
        #         for child in item.winfo_children():
        #             if isinstance(child, tk.Label):
        #                 child.config(bg="white")
        # self.selected_artwork = artwork
        #
        # # Update highlights in the sidebar
        # for item in self.artwork_list:
        #     if item.artwork == artwork:
        #         item.config(bg="#f0f0ff")  # Light purple for selected
        #     else:
        #         item.config(bg="white")  # White for others
        #
        # # Initialize virtual wall if it doesn't exist
        # if not hasattr(self, 'virtual_wall') or not self.virtual_wall:
        #     self.initialize_virtual_wall()
        #
        # # Add to virtual wall if not already present
        # if not self.is_artwork_on_wall(artwork):
        #     self.virtual_wall.add_artwork(artwork)
        #
        # # Highlight on virtual wall
        # self.highlight_artwork(artwork)
        #
    # def is_artwork_on_wall(self, artwork):
    #     """Check if artwork is already on the virtual wall."""
    #     if not hasattr(self, 'virtual_wall') or not self.virtual_wall:
    #         return False
    #
    #     for item in getattr(self.virtual_wall, 'items', []):
    #         if hasattr(item, 'art_data') and item.art_data.get("Name") == artwork.name:
    #             return True
    #     return False

    def create_collapsible_menu(self, parent, title, expanded=True):
        menu_frame = tk.Frame(parent, bg="#e0e0e0", bd=1, relief="raised")
        menu_frame.pack(fill="x", pady=2)

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

        content_frame = tk.Frame(menu_frame, bg="white")
        if expanded:
            content_frame.pack(fill="x")
        else:
            content_frame.pack_forget()

        return content_frame

    def toggle_menu(self, menu_frame, toggle_btn, content_frame):
        if content_frame.winfo_ismapped():
            content_frame.pack_forget()
            toggle_btn.config(text="▶")
        else:
            content_frame.pack(fill="x")
            toggle_btn.config(text="▼")

    def apply_even_spacing(self):
        """Apply even spacing to artworks using the utility function"""
        from gallery_wall_planner.utils.even_spacing import apply_even_spacing
        if not hasattr(self.selected_wall, 'artwork') or not self.selected_wall.artwork:
            messagebox.showinfo("Info", "No artworks to space")
            return
        
        # Get wall dimensions from your WallCanvas or selected_wall
        wall_width = self.selected_wall.width  # or get from canvas dimensions
        wall_height = self.selected_wall.height
        
        # Apply spacing
        updated_artworks = apply_even_spacing(
            self.selected_wall.artwork,
            wall_width,
            wall_height
        )
        
        # Update the wall with new positions
        self.selected_wall.artwork = updated_artworks
        
        # Refresh the display
        self.wall_canvas.refresh_artworks()
        messagebox.showinfo("Success", "Artworks evenly spaced")
        
    def back_to_wall_selection(self):
        self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)

    def open_artwork_manual_ui(self):
        self.AppMain.switch_screen(ScreenType.ARTWORK_MANUAL)

    def open_artwork_xlsx_ui(self):
        self.AppMain.switch_screen(ScreenType.ARTWORK_XLSX)

    # def refresh_artwork_list(self):
    #     """Refresh both the sidebar list and virtual wall"""
    #     self.create_artwork_list_frame()
    #
    #     if hasattr(self.selected_wall, 'artwork') and self.selected_wall.artwork:
    #         if not self.virtual_wall:
    #             self.initialize_virtual_wall()
    #         else:
    #             # Clear and repopulate virtual wall
    #             for widget in self.wall_space.winfo_children():
    #                 widget.destroy()
    #             self.initialize_virtual_wall()
    #
    #         # Re-highlight selected artwork if any
    #         if self.selected_artwork:
    #             self.highlight_artwork(self.selected_artwork)
    #     else:
    #         # Clear virtual wall if no artworks
    #         if hasattr(self, 'virtual_wall'):
    #             for widget in self.wall_space.winfo_children():
    #                 widget.destroy()
    #             self.virtual_wall = None
    #             self.selected_artwork = None
    #
    #         tk.Label(self.wall_space,
    #                text="No artworks added yet",
    #                font=self.styles["title_font"],
    #                bg="white").pack(expand=True)
            
    def add_to_virtual_wall(self, artwork):
        """Add artwork to the virtual wall when clicked"""
        print("[DEBUG] add_to_virtual_wall called")
        # if not hasattr(self, 'virtual_wall'):
        #     # Initialize virtual wall if not exists
        #     for widget in self.wall_space.winfo_children():
        #         widget.destroy()
        #     self.virtual_wall = VirtualWall(
        #         self.wall_space,
        #         self.selected_wall,
        #         [artwork]
        #     )
        # else:
        #     # Add to existing virtual wall
        #     self.virtual_wall.add_artwork_to_wall(artwork)

    def add_new_snap_line(self):
        print("[DEBUG] add_new_snap_line called")

        # def handle_save(new_line):
        #     print(f"[DEBUG] Saving Snap Line line.orientation={new_line.orientation}, line.alignment={new_line.alignment}, type={type(new_line.alignment)}")
        #     for existing in self.snap_lines:
        #         if (existing.orientation == new_line.orientation and abs(existing.distance - new_line.distance) < 0.05):
        #             self.show_duplicate_line_popup(new_line)
        #             return
        #     self.snap_lines.append(new_line)
        #     self.selected_wall.wall_lines = self.snap_lines
        #     self.draw_snap_lines()

        # open_snap_line_popup(
        #     self.parent,
        #     handle_save,
        #     wall_width=self.wall_width,
        #     wall_height=self.wall_height
        # )


    def open_manage_lines_popup(self):
        print("[DEBUG] open_manage_lines_popup called")

        # popup = Toplevel(self.parent)
        # popup.title("Manage Snap Lines")
        # popup.geometry("400x300")

        # if not self.snap_lines:
        #     ttk.Label(popup, text="No snap lines to manage.").pack(padx=10, pady=10)
        #     return

        # canvas = tk.Canvas(popup)
        # scrollbar = ttk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        # canvas.configure(yscrollcommand=scrollbar.set)

        # scrollbar.pack(side="right", fill="y")
        # canvas.pack(side="left", fill="both", expand=True)

        # frame = ttk.Frame(canvas)
        # canvas.create_window((0, 0), window=frame, anchor="nw")

        # def on_configure(event):
        #     canvas.configure(scrollregion=canvas.bbox("all"))

        # frame.bind("<Configure>", on_configure)

        # for idx, line in enumerate(self.snap_lines):
        #     line_frame = ttk.Frame(frame)
        #     line_frame.pack(fill="x", pady=5, padx=10)

        #     orientation_str = line.orientation.value.capitalize() if isinstance(line.orientation, Orientation) else "Unknown"
        #     alignment_str = self.get_alignment_string(line)
        #     label_text = f"{orientation_str} - {alignment_str} - {line.distance:.2f}\""
        #     ttk.Label(line_frame, text=label_text).pack(side="left")

        #     ttk.Button(
        #         line_frame,
        #         text="Edit",
        #         command=lambda i=idx: self.edit_snap_line(i, popup)
        #     ).pack(side="right", padx=5)

        #     ttk.Button(
        #         line_frame,
        #         text="Delete",
        #         command=lambda i=idx: self.delete_snap_line(i, popup)
        #     ).pack(side="right", padx=5)
