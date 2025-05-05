import tkinter as tk
from tkinter import ttk, Toplevel
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.screen_base import ScreenBase
from gallery_wall_planner.gui.ui_styles import (
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from gallery_wall_planner.models.structures import WallPosition, CanvasDimensions, Padding
from gallery_wall_planner.gui.wall_canvas import WallCanvas
from gallery_wall_planner.gui.collapsible_menu import CollapsibleMenu
from gallery_wall_planner.gui.btn_wall_item import BTNWallItem
from gallery_wall_planner.gui.scroll_box_vertical import ScrollBoxVertical
from gallery_wall_planner.gui.btn_new_wall_item import BTNNewWallItem
from typing import Dict

class ScreenLockObjectsUI(ScreenBase):
    
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.obstacle_names = [f"Obstacle{i+1}" for i in range(len(self.AppMain.gallery.current_wall.permanent_objects_dict))]
        self.layout_items = {}
        self.popup_windows = {}
        from gallery_wall_planner.gui.wall_item_draggable import WallItemDraggable
        self.items: list[WallItemDraggable] = []
        self.content_frame = None
        self.wall_canvas = None
        # self.canvas = None
        # self.canvas_height = None
        # self.canvas_width = None
        self.wall = self.AppMain.gallery.current_wall
        self.screen_scale = None
        self.wall_position: WallPosition = None

        self.back_to_home_button = None
        self.next_button = None

        self.collapsible_menu = None

        self.permanent_object_buttons: Dict[str, BTNWallItem] = {}


    def load_content(self):
        """This method should be overridden by child classes to load their specific content.
        It will be called when the screen is switched to this UI component.
        """
        header_frame = ttk.Frame(self)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)

        title_label = ttk.Label(header_frame, text="Place fixtures")
        apply_header_label_style(title_label)
        title_label.pack(side="left")

        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        # buttons_frame = ttk.Frame(header_frame)
        # buttons_frame.pack(side="left", padx=20)
        # item_buttons = {}

        self.left_panel = ttk.Frame(content_frame, width=300)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.collapsible_menu = CollapsibleMenu(self.left_panel, "Permanent Objects")
        self.collapsible_menu.load_content()
        self.collapsible_menu.pack(side="left", fill="y")

        self.scroll_box = ScrollBoxVertical(self.collapsible_menu.menu_frame)
        self.scroll_box.load_content()
        self.scroll_box.pack(side="top", fill="y")
        
        

        # Make canvas non-expanding to free space below
        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.pack(side="right", fill="both", expand=True)

        canvas_dimensions = CanvasDimensions(
            self.AppMain.root.winfo_width() - 400, 
            self.AppMain.root.winfo_height() - 200, 
            50, Padding(10, 10, 10, 10))
        self.wall_canvas = WallCanvas(self.AppMain, canvas_frame, canvas_dimensions)
        self.wall_canvas.load_content()

        self.wall_canvas.create_draggables(self.wall.permanent_objects_dict)
        for _, obj in self.wall_canvas.draggable_items.items():
            btn = BTNWallItem(self.scroll_box.scrollable_frame, obj)
            btn.pack(side="top", fill="x", padx=5, pady=5)
            btn.load_content()
            self.permanent_object_buttons[obj.wall_object.id] = btn
            
        self.add_permanent_object_button = BTNNewWallItem(self.collapsible_menu.menu_frame, self, False)
        self.add_permanent_object_button.load_content()
        self.add_permanent_object_button.pack(side="bottom", fill="x", padx=5, pady=5)

        # Bottom buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        self.back_to_home_button = ttk.Button(button_frame, text="< Back to Home", 
        command=lambda: self.AppMain.switch_screen(ScreenType.HOME), width=15)
        apply_primary_button_style(self.back_to_home_button)
        self.back_to_home_button.pack(side="left", padx=10)

        self.next_button = ttk.Button(button_frame, text="Save and Next >", command=self.save_and_continue)
        apply_primary_button_style(self.next_button)
        self.next_button.pack(side="right", padx=10)

    def new_wall_item_button(self, draggable_item : 'WallItemDraggable'):
        self.AppMain.gallery.current_wall.add_permanent_object(draggable_item.wall_object)
        self.wall_canvas.add_draggable(draggable_item)
        btn = BTNWallItem(self.scroll_box.scrollable_frame, draggable_item)
        btn.pack(side="top", fill="x", padx=5, pady=5)
        btn.load_content()
        self.permanent_object_buttons[draggable_item.wall_object.id] = btn        

    def save_and_continue(self):
        if self.wall_canvas.check_all_collisions():
            popup = Toplevel(self.AppMain.root)
            popup.title("Collision Detected")
            ttk.Label(popup, text="The program has identified an impossible layout. Would you like to keep editing?").pack(padx=10, pady=10)
            btn_frame = ttk.Frame(popup)
            btn_frame.pack(pady=10)
            btn_edit = ttk.Button(btn_frame, text="Keep Editing", command=popup.destroy)
            btn_save = ttk.Button(btn_frame, text="Continue Anyway", command=lambda: (popup.destroy(), self.continue_to_next()))
            apply_primary_button_style(btn_edit)
            apply_primary_button_style(btn_save)
            btn_edit.pack(side="left", padx=5)
            btn_save.pack(side="left", padx=5)
        else:
            self.continue_to_next()

    def continue_to_next(self):
        # Positions are already saved in the wall object through the DraggableItem class
        # Now just launch the SelectWallSpaceUI with the updated wall
        self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)

