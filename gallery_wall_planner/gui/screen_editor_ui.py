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
from gallery_wall_planner.gui.popup_even_spacing import PopupEvenSpacing
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

    def load_content(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Header frame for navigation buttons
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=10)

        # Back to Wall Selection button
        back_button = tk.Button(header_frame,
                                text="< Back to Wall Selection",
                                command=lambda: self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE),
                                bg=self.styles["bg_secondary"],
                                fg=self.styles["fg_white"],
                                font=self.styles["button_font"],
                                padx=self.styles["button_padx"],
                                pady=self.styles["button_pady"])
        back_button.pack(side="left", anchor="w")

        # Save button
        from gallery_wall_planner.gui.btns_save import BTNSSave
        save_buttons = BTNSSave(header_frame, self.AppMain)
        save_buttons.load_content()
        save_buttons.pack(side="right", anchor="e")

        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

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

        
        even_spacing_button = tk.Button(self.actions_frame,
                                        text="Even Spacing",
                                        command=lambda: PopupEvenSpacing(self.AppMain),
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

    def create_artwork_list_frame(self):
        """Create the frame for displaying imported artworks in the sidebar."""

        self.artwork_list = []  # Clear existing list

        self.artwork_scroll_box = ScrollBoxVertical(self.artwork_tab_frame)
        self.artwork_scroll_box.load_content()
        self.artwork_scroll_box.pack(side="left", fill="both", expand=True)

        # Add artworks to the list
        if len(self.AppMain.gallery.current_wall.artwork) > 0 or len(self.AppMain.gallery.unplaced_artwork) > 0:
            from gallery_wall_planner.gui.btn_wall_item import BTNWallItem, WallItemState
            for artwork in self.AppMain.gallery.unplaced_artwork:
                btn = BTNWallItem(self.AppMain, self.artwork_scroll_box.scrollable_frame, artwork, ScreenType.EDITOR, state=WallItemState.ACTIVE)
                btn.pack(side="top", fill="x", padx=5, pady=5)
                btn.load_content()
            for artwork in self.AppMain.gallery.current_wall.artwork:
                btn = BTNWallItem(self.AppMain, self.artwork_scroll_box.scrollable_frame, artwork, ScreenType.EDITOR)
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
