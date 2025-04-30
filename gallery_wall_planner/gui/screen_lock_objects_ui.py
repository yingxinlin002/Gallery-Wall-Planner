import tkinter as tk
from tkinter import ttk, Toplevel
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.screen_base import ScreenBase
from gallery_wall_planner.gui.ui_styles import (
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from gallery_wall_planner.gui.popup_editor import open_popup_editor
from gallery_wall_planner.models.structures import WallPosition, CanvasDimensions, Padding
from gallery_wall_planner.gui.wall_canvas import WallCanvas
from gallery_wall_planner.gui.collapsible_menu import CollapsibleMenu
from gallery_wall_planner.gui.btn_wall_item import BTNWallItem



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
        print(f"Root size: {self.AppMain.root.winfo_width()} x {self.AppMain.root.winfo_height()}")


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

        self.collapsible_menu = CollapsibleMenu(content_frame, "Permanent Objects")
        self.collapsible_menu.load_content()
        self.collapsible_menu.pack(side="left", fill="y")
        

        # Make canvas non-expanding to free space below
        canvas_frame = ttk.Frame(content_frame)
        canvas_frame.pack(side="right", fill="both", expand=True)

        canvas_dimensions = CanvasDimensions(
            self.AppMain.root.winfo_width() - 400, 
            self.AppMain.root.winfo_height() - 200, 
            50, Padding(10, 10, 10, 10))
        self.wall_canvas = WallCanvas(self.AppMain, canvas_frame, canvas_dimensions)
        self.wall_canvas.load_content()
        # self.canvas_width = 800
        # self.canvas_height = 350
        # self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height)
        # apply_canvas_style(self.canvas)
        # self.canvas.pack(padx=10, pady=10)

        # margin = 50
        # self.screen_scale = min((self.canvas_width - 2 * margin) / self.wall.width, (self.canvas_height - 2 * margin) / self.wall.height)
        # self.wall_position = WallPosition(
        #     margin, 
        #     margin, 
        #     margin + self.wall.width * self.screen_scale, 
        #     margin + self.wall.height * self.screen_scale
        # )

        # Draw wall background
        # self.canvas.create_rectangle(self.wall_position.wall_left, self.canvas_height - self.wall_position.wall_bottom - self.wall.height*self.screen_scale,
        #                   self.wall_position.wall_right, self.canvas_height - self.wall_position.wall_bottom,
        #                   fill=self.wall.color, outline="black", width=2)

        # # Add coordinate indicators
        # self.canvas.create_text(self.wall_position.wall_left - 10, self.canvas_height - self.wall_position.wall_bottom + 5, text="0", anchor="e")
        # self.canvas.create_text(self.wall_position.wall_left - 10, self.canvas_height - self.wall_position.wall_bottom - self.wall.height*self.screen_scale - 5,
        #                 text=f"{self.wall.height}\"", anchor="e")
        # self.canvas.create_text(self.wall_position.wall_left + 5, self.canvas_height - self.wall_position.wall_bottom + 15, text="0", anchor="n")
        # self.canvas.create_text(self.wall_position.wall_right - 5, self.canvas_height - self.wall_position.wall_bottom + 15, text=f"{self.wall.width}\"", anchor="n")

        # Create draggable items for each permanent object
        buttons_per_row = 4
        self.wall_canvas.add_draggables(self.wall.permanent_objects_dict)
        for _, obj in self.wall_canvas.draggable_items.items():
            #pos = obj.position
            # Initialize position in layout_items
            #self.layout_items[self.obstacle_names[i]] = pos if pos else {"x": 0.0, "y": 0.0}

            # Create draggable item
            # di = WallItem_Draggable(
            #     index=i,
            #     wall_object=obj,
            #     parent_ui=self.wall_canvas,
            #     name=obj.name
            # )
            # # self.items.append(di)
            # self.wall_canvas.draggable_items.append(di)

            # Create button for this item
            # row = i // buttons_per_row
            # col = i % buttons_per_row
            # btn = ttk.Button(self.collapsible_menu.menu_frame,
            #                  text=obj.name,
            #                  command=lambda idx=i: self.show_item_popup(idx))
            # apply_primary_button_style(btn)
            # btn.grid(row=row, column=col, padx=5, pady=5)  # Use grid layout for buttons
            # item_buttons[i] = btn
            btn = BTNWallItem(self.collapsible_menu.menu_frame, obj)
            btn.pack(side="top", fill="x", padx=5, pady=5)
            btn.load_content()
            

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

    # def export_then_continue(self):
    #     file_path = filedialog.asksaveasfilename(defaultextension=".json", title="Save Project")
    #     if not file_path:
    #         return  # User cancelled

    #     # Export the wall with updated permanent object positions
    #     export_project(file_path, wall)
    #     # TODO what is this supposed to be doing?
    #     SelectWallSpaceUI(root, file_path)

    # TODO Create Popup class
    def show_item_popup(self, item_index):
        print("showing popup for item", item_index)
        print("Needs to be fixed")
        return
        # Get the permanent object and its position
        permanent_object, position = self.wall.permanent_objects[item_index]

        # Prepare the item data as a dictionary that popup_editor expects
        item_data = {
            "Name": permanent_object.name,  # Using the object's actual name
            "Width": permanent_object.width,
            "Height": permanent_object.height,
            "x": position["x"] if position else 0.0,
            "y": position["y"] if position else 0.0
        }

        open_popup_editor(
            root=root,
            item_index=item_index,
            item_data=item_data,  # Pass the prepared dictionary
            obstacles=[(obj.name, obj.width, obj.height) for obj, _ in permanent_objects],
            obstacle_names=obstacle_names,
            layout_items=layout_items,
            items=items,
            item_buttons=item_buttons,
            canvas=canvas,
            scale=scale,
            wall_left=wall_left,
            wall_bottom=wall_bottom,
            canvas_height=canvas_height,
            move_item_to_canvas=move_item_to_canvas,
            check_all_collisions=check_all_collisions,
            enforce_boundaries=lambda x, y, w, h: enforce_boundaries(x, y, w, h, wall_width, wall_height),
            popup_windows=popup_windows,
        )


