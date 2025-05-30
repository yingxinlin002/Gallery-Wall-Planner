import tkinter as tk
from tkinter import messagebox
from gallery.gui.app_main import AppMain, ScreenType
from gallery.gui.screen_base import ScreenBase
from gallery.models.wall import Wall
from typing import Dict, Optional
from gallery.gui.btn_wall import BTNWall
from gallery.gui.scroll_box_vertical import ScrollBoxVertical
from gallery.gui.btns_save import BTNSSave

class ScreenSelectWallSpaceUI(ScreenBase):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.walls = AppMain.gallery.get_walls()
        self.delete_buttons = {}
        self.btn_create_new_wall_space = None
        self.btn_export_layout = None
        self.btn_continue = None
        self.btn_back = None
        self.wall_btns : Dict[str, BTNWall] = {}

    def load_content(self):
        # Clear the current frame

        # Add a title
        tk.Label(self, text="Select Wall Space", font=("Arial", 24)).pack(pady=20, anchor="w")

        # Main content frame
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        # Left Panel: List of wall spaces
        left_panel = tk.Frame(content_frame, width=300, bg="#f0f0f0")
        left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Scrollable list for wall spaces with a frame to hold both name and delete button
        self.scroll_box = ScrollBoxVertical(left_panel)
        self.scroll_box.pack(side="top", fill="both", expand=True)
        self.scroll_box.load_content()

        self.list_container = self.scroll_box.scrollable_frame

        for wall in self.walls:
            btn = BTNWall(self.list_container, wall, self.AppMain, self)
            btn.pack(side="top",fill="x",expand=True, padx=5, pady=5)
            btn.load_content()
            self.wall_btns[wall.id] = btn

        # Create New Wall Space Button
        self.btn_create_new_wall_space = tk.Button(left_panel, text="Create New Wall Space", command=self.create_new_wall_space, width=20, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5)
        self.btn_create_new_wall_space.pack(side="bottom")

        # Edit permanent objects
        self.btn_edit_permanent_objects = tk.Button(left_panel, text="Edit Permanent Objects", command=self.edit_permanent_objects, width=20, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5)
        self.btn_edit_permanent_objects.pack(side="bottom")
        
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
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill="x", pady=10)

        # Back to Home Button (Left Side)
        self.btn_back = tk.Button(bottom_frame, text="< Back to Home", command=lambda: self.AppMain.switch_screen(ScreenType.HOME), width=15, bg="#69718A", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5)
        self.btn_back.pack(side="left", padx=10)

        # Save Buttons
        self.btns_save = BTNSSave(bottom_frame, self.AppMain)
        self.btns_save.pack(side="left", padx=10)
        self.btns_save.load_content()

        # Continue Button (Right Side)
        self.btn_continue = tk.Button(bottom_frame, text="Continue >", command=self.continue_to_next, width=15, bg="#5F3FCA", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5)
        self.btn_continue.pack(side="right", padx=10)


    def create_new_wall_space(self):
        # Navigate to NewGalleryUI to create a new wall space
        self.AppMain.switch_screen(ScreenType.NEW_GALLERY)
        
    def edit_permanent_objects(self):
        if self.AppMain.gallery.current_wall:
            self.AppMain.switch_screen(ScreenType.LOCK_OBJECTS_TO_WALL)
        else:
            messagebox.showwarning("Error", "Please select a wall space to edit permanent objects.")

    def export_layout(self):
        # Export the selected wall layout
        selected_wall = self.AppMain.gallery.current_wall
        if selected_wall:
            # exported_data = selected_wall.export_wall()
            messagebox.showinfo("Export Layout", f"Layout exported successfully!\n")
        else:
            messagebox.showwarning("Error", "Please select a wall space to export.")

    def continue_to_next(self):
        self.AppMain.switch_screen(ScreenType.EDITOR)

    def remove_wall_btn(self, wall_id : str):
        if wall_id in self.wall_btns:
            self.wall_btns[wall_id].destroy()
            self.wall_btns.pop(wall_id)
            self.update_wall_preview()
        

    def update_wall_preview(self, event=None):
        """Update the wall preview canvas and details when a wall is selected."""
        selected_wall = self.AppMain.gallery.current_wall
        # Clear the canvas
        self.preview_canvas.delete("all")
        self.wall_details_label.config(text="Select a wall to preview")
        for btn in self.wall_btns.values():
            if selected_wall and btn.wall.id == selected_wall.id:
                btn.label.configure(bg="yellow")
            else:
                btn.label.configure(bg="#fff")

        if selected_wall:
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

            # Draw permanent objects
            for _,obj in selected_wall.permanent_objects_dict.items():
                pos = obj.position
                if pos:  # Only draw if object has a position
                    obj_x0 = x0 + pos.x * ratio
                    obj_y0 = y0 + pos.y * ratio  # Adjust for bottom-left origin
                    obj_x1 = obj_x0 + obj.width * ratio
                    obj_y1 = obj_y0 + obj.height * ratio
                    
                    # Draw object rectangle
                    self.preview_canvas.create_rectangle(
                        obj_x0, obj_y0, obj_x1, obj_y1,
                        fill="lightblue", outline="black", width=2
                    )
                    
                    # Draw object name (if space allows)
                    if (obj_x1 - obj_x0) > 40 and (obj_y1 - obj_y0) > 20:  # Only draw if object is large enough
                        self.preview_canvas.create_text(
                            (obj_x0 + obj_x1)/2, (obj_y0 + obj_y1)/2,
                            text=obj.name, fill="black", font=("Arial", 8)
                        )

            # Draw height and width lines with labels
            self.preview_canvas.create_line(x0, y1, x0 - 10, y1, fill="black")  # Width line start
            self.preview_canvas.create_line(x1, y1, x1 + 10, y1, fill="black")  # Width line end
            self.preview_canvas.create_text((x0 + x1)/2, y1 + 15, text=f"{wall_width}\"", anchor="n")

            self.preview_canvas.create_line(x0, y0, x0, y0 - 10, fill="black")  # Height line start
            self.preview_canvas.create_line(x0, y1, x0, y1 + 10, fill="black")  # Height line end
            self.preview_canvas.create_text(x0 - 15, (y0 + y1)/2, text=f"{wall_height}\"", anchor="e", angle=90)

            # Update wall details label with object count
            obj_count = len(selected_wall.permanent_objects_dict)
            self.wall_details_label.config(
                text=f"Wall: {selected_wall.name}\n"
                    f"Dimensions: {wall_width}\" x {wall_height}\"\n"
                    f"Color: {selected_wall.color}\n"
                    f"Permanent Objects: {obj_count}"
            )

        