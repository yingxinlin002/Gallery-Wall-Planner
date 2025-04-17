import tkinter as tk
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.gui.Screen_Base import Screen_Base
from gallery_wall_planner.gui.ui_styles import (
    init_styles,
    apply_primary_button_style,
    apply_header_label_style,
    apply_canvas_style
)
from DraggableItem import DraggableItem

class Screen_LockObjectsUI(Screen_Base):
    
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.obstacle_names = [f"Obstacle{i+1}" for i in range(len(self.AppMain.gallery.permanent_objects))]
        self.layout_items = {}
        self.popup_windows = {}
        self.items = []
        self.content_frame = None
        self.canvas = None


    def load_content(self):
        """This method should be overridden by child classes to load their specific content.
        It will be called when the screen is switched to this UI component.
        """
        content_frame = tk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        header_frame = tk.Frame(content_frame)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)

        title_label = tk.Label(header_frame, text="Place fixtures")
        apply_header_label_style(title_label)
        title_label.pack(side="left")

        buttons_frame = tk.Frame(header_frame)
        buttons_frame.pack(side="left", padx=20)
        item_buttons = {}

        # Make canvas non-expanding to free space below
        canvas_frame = tk.Frame(content_frame)
        canvas_frame.pack(side="top", fill="both", expand=True)

        canvas_width = 800
        canvas_height = 350
        self.canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height)
        apply_canvas_style(self.canvas)
        self.canvas.pack(padx=10, pady=10)

        margin = 50
        scale = min((canvas_width - 2*margin) / wall_width, (canvas_height - 2*margin) / wall_height)
        wall_left = margin
        wall_bottom = margin
        wall_right = wall_left + wall_width * scale
        wall_top = wall_bottom + wall_height * scale

        # Draw wall background
        self.canvas.create_rectangle(wall_left, canvas_height - wall_bottom - wall_height*scale,
                          wall_right, canvas_height - wall_bottom,
                          fill=wall_color, outline="black", width=2)

        # Add coordinate indicators
        self.canvas.create_text(wall_left - 10, canvas_height - wall_bottom + 5, text="0", anchor="e")
        self.canvas.create_text(wall_left - 10, canvas_height - wall_bottom - wall_height*scale - 5,
                        text=f"{wall_height}\"", anchor="e")
        self.canvas.create_text(wall_left + 5, canvas_height - wall_bottom + 15, text="0", anchor="n")
        self.canvas.create_text(wall_right - 5, canvas_height - wall_bottom + 15, text=f"{wall_width}\"", anchor="n")

        # Create draggable items for each permanent object
        buttons_per_row = 4
        for i, (obj, pos) in enumerate(permanent_objects):
            # Initialize position in layout_items
            self.layout_items[self.obstacle_names[i]] = pos if pos else {"x": 0.0, "y": 0.0}

            # Create draggable item
            di = DraggableItem(
                index=i,
                permanent_object=(obj, pos),
                move_item_to_canvas=move_item_to_canvas,
                check_all_collisions=check_all_collisions
            )
            self.items.append(di)

            # Create button for this item
            row = i // buttons_per_row
            col = i % buttons_per_row
            btn = tk.Button(buttons_frame,
                             text=obj.name,
                             command=lambda idx=i: show_item_popup(idx))
            apply_primary_button_style(btn)
            btn.grid(row=row, column=col, padx=5, pady=5)  # Use grid layout for buttons
            item_buttons[i] = btn

        # Bottom buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(side="bottom", fill="x", pady=10)

        back_to_home_button = tk.Button(button_frame, text="< Back to Home", command=lambda: return_to_home(), width=15)
        apply_primary_button_style(back_to_home_button)
        back_to_home_button.pack(side="left", padx=10)

        next_button = tk.Button(button_frame, text="Save and Next >", command=save_and_continue)
        apply_primary_button_style(next_button)
        next_button.pack(side="right", padx=10)

    def enforce_boundaries(self, x, y, width, height, wall_width, wall_height):
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x + width > wall_width:
            x = wall_width - width
        if y + height > wall_height:
            y = wall_height - height
        return x, y

    def move_item_to_canvas(self,item_index):
        item = self.items[item_index]
        x1 = wall_left + item.x * scale
        y1 = canvas_height - (wall_bottom + item.y * scale)  # Changed from (y + height)
        x2 = wall_left + (item.x + item.width) * scale
        y2 = canvas_height - (wall_bottom + (item.y + item.height) * scale)  # Changed from just y
        self.canvas.coords(item.id, x1, y1, x2, y2)

    def check_all_collisions(self):
        n = len(self.items)
        colliding = set()
        for i in range(n):
            for j in range(i+1, n):
                if self.rectangles_overlap(self.items[i], self.items[j]):
                    colliding.add(i)
                    colliding.add(j)
        for i, item in enumerate(self.items):
            self.canvas.itemconfig(item.id, outline="red" if i in colliding else "black")
        return len(colliding) > 0

    def rectangles_overlap(self,item1, item2):
        ax1, ay1 = item1.x, item1.y
        ax2, ay2 = item1.x + item1.width, item1.y + item1.height
        bx1, by1 = item2.x, item2.y
        bx2, by2 = item2.x + item2.width, item2.y + item2.height
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)

    def save_and_continue(self):
        if check_all_collisions():
            popup = Toplevel(root)
            popup.title("Collision Detected")
            tk.Label(popup, text="The program has identified an impossible layout. Would you like to keep editing?").pack(padx=10, pady=10)
            btn_frame = tk.Frame(popup)
            btn_frame.pack(pady=10)
            btn_edit = tk.Button(btn_frame, text="Keep Editing", command=popup.destroy)
            btn_save = tk.Button(btn_frame, text="Continue Anyway", command=lambda: (popup.destroy(), continue_to_next()))
            apply_primary_button_style(btn_edit)
            apply_primary_button_style(btn_save)
            btn_edit.pack(side="left", padx=5)
            btn_save.pack(side="left", padx=5)
        else:
            continue_to_next()

    def continue_to_next(self):
        # Positions are already saved in the wall object through the DraggableItem class
        # Now just launch the SelectWallSpaceUI with the updated wall
        SelectWallSpaceUI(root, wall)

    def export_then_continue(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", title="Save Project")
        if not file_path:
            return  # User cancelled

        # Export the wall with updated permanent object positions
        export_project(file_path, wall)
        SelectWallSpaceUI(root, file_path)

    def return_to_home(self):
        print("Returning to Home...")
        root.quit()
