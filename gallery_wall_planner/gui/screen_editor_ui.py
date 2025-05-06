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
from gallery_wall_planner.gui.screen_base import ScreenBase
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.wall_canvas import WallCanvas
from gallery_wall_planner.models.structures import CanvasDimensions, Padding
from gallery_wall_planner.gui.popup_install_instruct import InstallInstructionPopup
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.gui.popup_snap_lines import PopupSnapLines
from gallery_wall_planner.models.wall_line import SingleLine, Orientation
from gallery_wall_planner.gui.collapsible_menu import CollapsibleMenu
from gallery_wall_planner.gui.scroll_box_vertical import ScrollBoxVertical
from gallery_wall_planner.gui.btn_snap_line import BTNSnapLine
from typing import Dict

class ArtBtn(tk.Button):
    def toggle_bg(self, on: bool = True):
        if on:
            self.configure(background="red")
        else:
            self.configure(background="green")

class ScreenEditorUI(ScreenBase):
    def __init__(self, AppMain: AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.styles = get_ui_styles()
        self.artwork_list = []
        self.sidebar_visible = True
        self.sidebar_width = 300
        self.sidebar_animation_running = False
        self.wall_canvas : WallCanvas = None
        self.selected_artwork : Artwork = None
        self.wall_space = None  # Initialize wall_space as None
        self.tab_frame = None
        self.artwork_tab_btn = None
        self.snap_lines_tab_btn = None
        self.artwork_tab_frame: tk.Frame = None
        self.snap_lines_tab_frame: tk.Frame = None
        self.actions_frame = None
        self.snap_line_buttons: Dict[str, BTNSnapLine] = {}

    def handle_installation_popup(self):
        print("Installation popup")
    #     # This should pass the full DraggableArt objects, not just names
    #     open_install_instruct_popup(self._root(), self.selected_wall, self.virtual_wall.items)

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

        # self.tab_frame = tk.Frame(self.control_panel)
        # self.tab_frame.pack(side="top", fill="x")
        # header = tk.Frame(self.tab_frame, bg="#e0e0e0")
        # header.pack(fill="x")

        # tk.Label(header,
        #        text="Tabs",
        #        font=self.styles["label_font"],
        #        bg="#e0e0e0").pack(side="left", padx=5)


        # self.artwork_tab_btn = tk.Button(self.tab_frame,
        #                                 text="Artwork",
        #                                 command=self.show_artwork_tab,
        #                                 bg=self.styles["bg_info"],
        #                                 fg=self.styles["fg_white"],
        #                                 font=self.styles["button_font"],
        #                                 padx=self.styles["button_padx"],
        #                                 pady=self.styles["button_pady"])
        # self.artwork_tab_btn.pack(side="left", fill="x")

        # self.snap_lines_tab_btn = tk.Button(self.tab_frame,
        #                                     text="Snap Lines",
        #                                     command=self.show_snap_lines_tab,
        #                                     bg=self.styles["bg_info"],
        #                                     fg=self.styles["fg_white"],
        #                                     font=self.styles["button_font"],
        #                                     padx=self.styles["button_padx"],
        #                                     pady=self.styles["button_pady"])
        # self.snap_lines_tab_btn.pack(side="left", fill="x")

        self.collapsible_menu = CollapsibleMenu(content_frame, "")
        self.collapsible_menu.load_content()
        self.collapsible_menu.pack(side="left", fill="y")

        self.artwork_tab_frame = self.create_collapsible_menu(
            self.collapsible_menu.menu_frame, "Imported Artwork", expanded=True)

        self.create_artwork_list_frame()

        self.snap_lines_tab_frame = self.create_collapsible_menu(
            self.collapsible_menu.menu_frame, "Snap Lines", expanded=False)


        # Add new Tool menu with Even Spacing button
        self.actions_frame = tk.Frame(self.collapsible_menu.menu_frame)
        self.actions_frame.pack(side="bottom", fill="x")
        header = tk.Frame(self.actions_frame, bg="#e0e0e0")
        header.pack(fill="x")

        tk.Label(header,
               text="Actions",
               font=self.styles["label_font"],
               bg="#e0e0e0").pack(side="left", padx=5)

        manual_button = tk.Button(self.actions_frame,
                                text="Add Artwork",
                                command=self.open_artwork_manual_ui,
                                bg=self.styles["bg_info"],
                                fg=self.styles["fg_white"],
                                font=self.styles["button_font"],
                                padx=self.styles["button_padx"],
                                pady=self.styles["button_pady"])
        manual_button.pack(pady=5, fill="x")

        self.add_snap_line_button = tk.Button(self.actions_frame,
                                            text="Add Snap Line",
                                            command=self.add_new_snap_line_popup,
                                            bg=self.styles["bg_info"],
                                            fg=self.styles["fg_white"],
                                            font=self.styles["button_font"],
                                            padx=self.styles["button_padx"],
                                            pady=self.styles["button_pady"])
        self.add_snap_line_button.pack(pady=5, fill="x")

        
        from gallery_wall_planner.utils.even_spacing import apply_even_spacing

        even_spacing_button = tk.Button(self.actions_frame,
                                        text="Even Spacing",
                                        command=lambda: apply_even_spacing(self.wall_canvas, self.AppMain.gallery.current_wall.artwork),
                                        bg=self.styles["bg_primary"],
                                        fg=self.styles["fg_white"],
                                        font=self.styles["button_font"],
                                        padx=self.styles["button_padx"],
                                        pady=self.styles["button_pady"])
        even_spacing_button.pack(pady=5, fill="x")

        self.calc_button = tk.Button(self.actions_frame,
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

        title_label = ttk.Label(header_frame, text="Organize Art")
        apply_header_label_style(title_label)
        title_label.pack(side="left")

        self.buttons_frame = ttk.Frame(header_frame)
        self.buttons_frame.pack(side="left", padx=20)
        self.item_buttons = {}

        canvas_dimensions = CanvasDimensions(self.AppMain.root.winfo_width() - 400, 
                                            self.AppMain.root.winfo_height() - 200, 
                                            50, Padding(10, 10, 10, 10))
        self.wall_canvas = WallCanvas(self.AppMain, self.wall_space, canvas_dimensions)
        self.wall_canvas.load_content()
        self.wall_canvas.add_fixed_items(self.AppMain.gallery.current_wall.permanent_objects_dict)
        #TODO  Only add artwork that has been placed on the wall.
        self.wall_canvas.create_draggables(self.AppMain.gallery.current_wall.artwork_dict)

        self.create_snap_lines_list_frame()
        self.wall_canvas.draw_snap_lines()

        # self.canvas = tk.Canvas(self.wall_space, width=self.canvas_width, height=self.canvas_height)
        # apply_canvas_style(self.canvas)
        # self.canvas.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # snap_button_frame = ttk.Frame(self.wall_space)
        # snap_button_frame.pack(fill="x", padx=10, pady=(0, 10))

        # add_line_btn = ttk.Button(snap_button_frame, text="Add Snap Line", command=self.add_new_snap_line)
        # apply_primary_button_style(add_line_btn)
        # add_line_btn.pack(side="left", padx=5)

        # edit_line_btn = ttk.Button(snap_button_frame, text="Move/Delete Line", command=self.open_manage_lines_popup)
        # apply_primary_button_style(edit_line_btn)
        # edit_line_btn.pack(side="left", padx=5)

    # def initialize_virtual_wall(self):
    #     """Initialize the virtual wall display"""
    #     # Clear existing wall if any
    #     for widget in self.wall_space.winfo_children():
    #         widget.destroy()
    #
    #     # Create new virtual wall
    #     self.virtual_wall = VirtualWall(
    #         self.wall_space,
    #         self.AppMain.editor_wall,
    #         on_drag_callback=self.show_measurement_lines
    #     )
    #
    #     # Add existing artworks if any
    #     if hasattr(self.AppMain.editor_wall, 'artwork'):
    #         for artwork in self.AppMain.editor_wall.artwork:
    #             self.virtual_wall.add_artwork(artwork)
    #
    #     # Highlight selected artwork if one exists
    #     if (hasattr(self.AppMain, 'editor_artwork_selected') and
    #         self.AppMain.editor_artwork_selected):
    #         self.highlight_artwork(self.AppMain.editor_artwork_selected)

    # def highlight_artwork(self, artwork):
    #     """Highlight the artwork on the virtual wall"""
    #     if not hasattr(self, 'virtual_wall') or not self.virtual_wall:
    #         return
    #
    #     # Reset all highlights first
    #     for item in self.virtual_wall.items:
    #         self.virtual_wall.canvas.itemconfig(item.id, outline="black", width=2)
    #
    #     # Find and highlight the selected artwork
    #     for item in self.virtual_wall.items:
    #         if hasattr(item, 'art_data') and item.art_data.get("Name") == artwork.name:
    #             self.virtual_wall.canvas.itemconfig(item.id, outline="#800080", width=4)  # Purple highlight
    #             break
    #
    # def show_measurement_lines(self, item_id, x1, y1, x2, y2):
    #     """Show measurement lines and distances while dragging"""
    #     # Clear previous measurement lines
    #     self.virtual_wall.canvas.delete("measurement")
    #
    #     # Get wall boundaries
    #     wall_left = self.virtual_wall.margin
    #     wall_bottom = self.virtual_wall.margin
    #     wall_right = wall_left + self.selected_wall.width * self.virtual_wall.scale
    #     wall_top = self.virtual_wall.canvas_height - (wall_bottom + self.selected_wall.height * self.virtual_wall.scale)
    #
    #     # Draw horizontal measurement lines
    #     self.virtual_wall.canvas.create_line(
    #         wall_left, y1, x1, y1,
    #         fill="gray", dash=(2, 2), tags="measurement", width=1
    #     )
    #     self.virtual_wall.canvas.create_line(
    #         x2, y1, wall_right, y1,
    #         fill="gray", dash=(2, 2), tags="measurement", width=1
    #     )
    #
    #     # Draw vertical measurement lines
    #     self.virtual_wall.canvas.create_line(
    #         x1, wall_top, x1, y1,
    #         fill="gray", dash=(2, 2), tags="measurement", width=1
    #     )
    #     self.virtual_wall.canvas.create_line(
    #         x1, y2, x1, self.virtual_wall.canvas_height - wall_bottom,
    #         fill="gray", dash=(2, 2), tags="measurement", width=1
    #     )
    #
    #     # Calculate distances in inches
    #     left_dist = (x1 - wall_left) / self.virtual_wall.scale
    #     right_dist = (wall_right - x2) / self.virtual_wall.scale
    #     top_dist = (self.virtual_wall.canvas_height - y1 - wall_bottom) / self.virtual_wall.scale
    #     bottom_dist = (y2 - wall_top) / self.virtual_wall.scale
    #
    #     # Display distances
    #     self.virtual_wall.canvas.create_text(
    #         (wall_left + x1)/2, y1-10,
    #         text=f"{left_dist:.1f}\"",
    #         fill="black", tags="measurement"
    #     )
    #     self.virtual_wall.canvas.create_text(
    #         (x2 + wall_right)/2, y1-10,
    #         text=f"{right_dist:.1f}\"",
    #         fill="black", tags="measurement"
    #     )
    #     self.virtual_wall.canvas.create_text(
    #         x1+10, (wall_top + y1)/2,
    #         text=f"{top_dist:.1f}\"",
    #         fill="black", tags="measurement"
    #     )
    #     self.virtual_wall.canvas.create_text(
    #         x1+10, (y2 + self.virtual_wall.canvas_height - wall_bottom)/2,
    #         text=f"{bottom_dist:.1f}\"",
    #         fill="black", tags="measurement"
    #     )

    def create_artwork_list_frame(self):
        """Create the frame for displaying imported artworks in the sidebar."""

        self.artwork_list = []  # Clear existing list

        self.artwork_scroll_box = ScrollBoxVertical(self.artwork_tab_frame)
        self.artwork_scroll_box.load_content()
        self.artwork_scroll_box.pack(side="left", fill="both", expand=True)

        # Add artworks to the list
        if len(self.AppMain.gallery.current_wall.artwork) > 0 or len(self.AppMain.gallery.unplaced_artwork) > 0:
            # TODO: Need to figure out how we're storing artwork first
            from gallery_wall_planner.gui.btn_wall_item import BTNWallItem, WallItemState
            for artwork in self.AppMain.gallery.current_wall.artwork:
                btn = BTNWallItem(self.AppMain, self.artwork_scroll_box.scrollable_frame, artwork, ScreenType.EDITOR)
                btn.pack(side="top", fill="x", padx=5, pady=5)
                btn.load_content()
            for artwork in self.AppMain.gallery.unplaced_artwork:
                btn = BTNWallItem(self.AppMain, self.artwork_scroll_box.scrollable_frame, artwork, ScreenType.EDITOR, state=WallItemState.ACTIVE)
                btn.pack(side="top", fill="x", padx=5, pady=5)
                btn.load_content()
        else:
            tk.Label(self.artwork_scroll_box.scrollable_frame,
                     text="No artworks added yet",
                     fg="gray").pack(pady=20)

    def create_snap_lines_list_frame(self):
        print("create_snap_lines_list_frame")
        self.snap_lines_scroll_box = ScrollBoxVertical(self.snap_lines_tab_frame)
        self.snap_lines_scroll_box.load_content()
        self.snap_lines_scroll_box.pack(side="left", fill="both", expand=True)

        # Add snap lines to the list
        if self.AppMain.gallery.current_wall.wall_lines:
            from gallery_wall_planner.gui.btn_snap_line import BTNSnapLine
            for snap_line in self.AppMain.gallery.current_wall.wall_lines:
                self.add_snap_line(snap_line)
        else:
            tk.Label(self.snap_lines_scroll_box.scrollable_frame,
                     text="No snap lines added yet",
                     fg="gray").pack(pady=20)


    # TODO Deprecated to be removed
    def add_artwork_item(self, parent, artwork: Artwork):
        """Create a clickable artwork item in the sidebar"""
        print(f"adding {artwork.name}")
        art_btn = ArtBtn(parent, text=f"{artwork.name} ({artwork.width}\" × {artwork.height}\")")
        art_btn.config(command=lambda: (self.select_artwork(artwork), art_btn.toggle_bg()))
        art_btn.pack(fill="x", pady=2, padx=2)

    def select_artwork(self, artwork: Artwork):
        """Handle artwork selection from the sidebar."""
        print(f"DEBUG: select_artwork called with {artwork.name}")
        self.wall_canvas.create_draggable(artwork)


    def create_collapsible_menu(self, parent, title, expanded=True):
        menu_frame = tk.Frame(parent, bg="#e0e0e0", bd=1, relief="raised")
        menu_frame.pack(fill="x", pady=2)

        header = tk.Frame(menu_frame, bg="#e0e0e0")
        header.pack(fill="x")

        content_frame = tk.Frame(menu_frame, bg="white")
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

        if expanded:
            content_frame.pack(fill="x")
        # else:
        #     content_frame.pack_forget()

        return content_frame

    def toggle_menu(self, menu_frame, toggle_btn, content_frame):
        self.artwork_tab_frame.pack_forget()
        self.snap_lines_tab_frame.pack_forget()
        if content_frame.winfo_ismapped():
            content_frame.pack_forget()
            toggle_btn.config(text="▶")
        else:
            content_frame.pack(fill="x")
            toggle_btn.config(text="▼")

    def apply_even_spacing(self):
        """Apply even spacing to artworks using the utility function"""
        from gallery_wall_planner.utils.even_spacing import apply_even_spacing
        if not hasattr(self.AppMain.gallery.current_wall, 'artwork') or not self.AppMain.gallery.current_wall.artwork:
            messagebox.showinfo("Info", "No artworks to space")
            return
        
        # Get wall dimensions from your WallCanvas or selected_wall
        wall_width = self.AppMain.gallery.current_wall.width  # or get from canvas dimensions
        wall_height = self.AppMain.gallery.current_wall.height
        
        # Apply spacing
        updated_artworks = apply_even_spacing(
            self.AppMain.gallery.current_wall.artwork,
            wall_width,
            wall_height
        )
        
        # Update the wall with new positions
        self.AppMain.gallery.current_wall.artwork = updated_artworks
        
        # Refresh the display
        self.wall_canvas.refresh_artworks()
        messagebox.showinfo("Success", "Artworks evenly spaced")

    def handle_installation_popup(self):
        """Handle the installation instructions popup button click"""
        if not hasattr(self.AppMain.gallery, 'current_wall') or not self.AppMain.gallery.current_wall:
            messagebox.showwarning("Warning", "No wall selected")
            return
        
        # Get all artwork 
        all_artwork = self.AppMain.gallery.current_wall.artwork
        
        if not all_artwork:
            messagebox.showwarning("Warning", "No artwork placed on the wall")
            return
        
        # Open the popup with the current wall and placed artwork
        InstallInstructionPopup(self.AppMain)
        
    def back_to_wall_selection(self):
        self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)

    def open_artwork_manual_ui(self):
        self.AppMain.switch_screen(ScreenType.ARTWORK_MANUAL)


    def add_new_snap_line_popup(self):
        PopupSnapLines(self.AppMain, self)

    def draw_snap_lines(self):
        self.wall_canvas.draw_snap_lines()

    def add_new_snap_line(self, line: SingleLine):
        self.add_snap_line(line)
        self.AppMain.gallery.current_wall.add_wall_line(line)
        self.draw_snap_lines()

    def add_snap_line(self, line: SingleLine):
        if len(self.AppMain.gallery.current_wall.wall_lines) == 0:
            for widget in self.snap_lines_scroll_box.scrollable_frame.winfo_children():
                widget.destroy()
        from gallery_wall_planner.gui.btn_snap_line import BTNSnapLine
        btn = BTNSnapLine(self.snap_lines_scroll_box.scrollable_frame, line, self.AppMain, self)
        btn.pack(side="top", fill="x", padx=5, pady=5)
        btn.load_content()
        self.snap_line_buttons[line.id] = btn

    def update_snap_line(self, old_line: SingleLine, new_line: SingleLine):
        print("[DEBUG] update_snap_line called")
        self.AppMain.gallery.current_wall.update_wall_line(old_line.id, new_line)
        self.snap_line_buttons[old_line.id].destroy()
        self.snap_line_buttons.pop(old_line.id)
        self.add_snap_line(new_line)
        self.draw_snap_lines()

    def delete_snap_line(self, line: SingleLine):
        self.AppMain.gallery.current_wall.remove_wall_line(line.id)
        self.snap_line_buttons[line.id].destroy()
        self.snap_line_buttons.pop(line.id)
        self.draw_snap_lines()
