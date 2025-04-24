import tkinter as tk
from tkinter import ttk, messagebox
from gallery_wall_planner.gui.ui_styles import (
    init_styles,
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style,
    get_ui_styles
)
from gallery_wall_planner.deprecated.virtualWall import VirtualWall
from gallery_wall_planner.gui.Screen_Base import Screen_Base
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.gui.WallCanvas import WallCanvas
from gallery_wall_planner.models.structures import CanvasDimensions, Padding
from gallery_wall_planner.models.artwork import Artwork


class Screen_EditorUI(Screen_Base):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.selected_wall = AppMain.editor_wall
        self.styles = get_ui_styles()
        self.artwork_list = []
        self.sidebar_visible = True
        self.sidebar_width = 300
        self.sidebar_animation_running = False
        self.virtual_wall = None
        self.wall_canvas = None


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

        csv_button = tk.Button(self.add_artwork_frame,
                             text="Add Artwork by xlsx file",
                             command=self.open_artwork_xlsx_ui,
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

        self.imported_artwork_frame = self.create_collapsible_menu(
            self.control_panel, "Imported Artwork", expanded=True)

        self.create_artwork_list_frame()

        self.calc_button = tk.Button(self.control_panel,
                                   text="Calculate Installation Instruction",
                                   command=lambda: messagebox.showinfo("Info", "Calculate Installation Instruction button pushed"),
                                   bg=self.styles["bg_primary"],
                                   fg=self.styles["fg_white"],
                                   font=self.styles["button_font"],
                                   padx=self.styles["button_padx"],
                                   pady=self.styles["button_pady"])
        self.calc_button.pack(side="bottom", pady=10, fill="x")

        self.wall_space = tk.Frame(content_frame, bg="white")
        self.wall_space.pack(side="right", fill="both", expand=True)

        init_styles(self.wall_space)
        header_frame = ttk.Frame(self.wall_space)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)

        title_label = ttk.Label(header_frame, text="Organize Art")
        apply_header_label_style(title_label)
        title_label.pack(side="left")

        self.buttons_frame = ttk.Frame(header_frame)
        self.buttons_frame.pack(side="left", padx=20)
        self.item_buttons = {}

        canvas_dimensions = CanvasDimensions(800, 350, 50, Padding(10, 10, 10, 10))
        self.wall_canvas = WallCanvas(self.AppMain, self.wall_space, canvas_dimensions)
        self.wall_canvas.load_content()
        self.wall_canvas.add_fixed_item(self.selected_wall.permanent_objects)
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

            
    def initialize_virtual_wall(self):
        """Initialize the virtual wall display"""
        # Clear existing wall if any
        for widget in self.wall_space.winfo_children():
            widget.destroy()
        
        # Create new virtual wall
        self.virtual_wall = VirtualWall(self.wall_space, self.selected_wall)
        
        # Add existing artworks if any
        if hasattr(self.selected_wall, 'artwork'):
            for artwork in self.selected_wall.artwork:
                self.virtual_wall.add_artwork(artwork)
            

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
            self.root.after(10, update_animation)
        
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
        for widget in self.imported_artwork_frame.winfo_children():
            widget.destroy()
        self.artwork_list = []

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

        if hasattr(self.selected_wall, 'artwork'):
            for artwork in self.selected_wall.artwork:
                self.add_artwork_item(scrollable_frame, artwork)
        else:
            tk.Label(scrollable_frame,
                   text="No artworks added yet",
                   fg="gray").pack(pady=20)

    def add_artwork_item(self, parent, artwork: Artwork):
        """Create a clickable artwork item in the sidebar"""
        frame = tk.Frame(parent, bg="white", bd=1, relief="groove", padx=5, pady=5)
        frame.pack(fill="x", pady=2, padx=2)
        
        # Make the whole frame clickable
        frame.bind("<Button-1>", lambda e, a=artwork: self.add_artwork_to_wall(a))
        
        tk.Label(frame,
               text=f"{artwork.name} ({artwork.width}\" x {artwork.height}\")",
               font=self.styles["label_font"],
               bg="white").pack(anchor="w")

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

        self.artwork_list.append(frame)

    def add_artwork_to_wall(self, artwork):
        if not hasattr(self, 'virtual_wall'):
            self.virtual_wall = VirtualWall(self.wall_space, self.selected_wall)
        self.virtual_wall.add_artwork(artwork)

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

    def back_to_wall_selection(self):
        self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)

    def open_artwork_manual_ui(self):
        self.AppMain.switch_screen(ScreenType.ARTWORK_MANUAL)

    def open_artwork_xlsx_ui(self):
        self.AppMain.switch_screen(ScreenType.ARTWORK_XLSX)

    def refresh_artwork_list(self):
        """Refresh both the sidebar list and virtual wall"""
        self.create_artwork_list_frame()
        
        if hasattr(self.selected_wall, 'artwork') and self.selected_wall.artwork:
            if not self.virtual_wall:
                self.initialize_virtual_wall()
            else:
                # Clear and repopulate virtual wall
                for widget in self.wall_space.winfo_children():
                    widget.destroy()
                self.initialize_virtual_wall()
        else:
            # Clear virtual wall if no artworks
            if hasattr(self, 'virtual_wall'):
                for widget in self.wall_space.winfo_children():
                    widget.destroy()
                self.virtual_wall = None
            tk.Label(self.wall_space,
                   text="No artworks added yet",
                   font=self.styles["title_font"],
                   bg="white").pack(expand=True)
            
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
