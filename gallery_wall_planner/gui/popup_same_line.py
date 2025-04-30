from tkinter import Toplevel, ttk

from gallery_wall_planner.models.wall_line import SingleLine
from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.gui.ui_styles import apply_primary_button_style

class PopupSameLine(PopupBase):
    def __init__(self, AppMain : AppMain, parent_ui: 'Screen_EditorUI', new_line: SingleLine, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.new_line = new_line
        self.parent_ui = parent_ui

    def load_content(self):
        confirm_popup = Toplevel(self.AppMain.root)
        confirm_popup.title("Line Already Exists")

        ttk.Label(confirm_popup, text="A snap line at this location already exists.\nWould you like to add it anyway?").pack(padx=20, pady=(15, 10))

        button_frame = ttk.Frame(confirm_popup)
        button_frame.pack(pady=10)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=confirm_popup.destroy)
        apply_primary_button_style(cancel_btn)
        cancel_btn.pack(side="left", padx=5)

        add_btn = ttk.Button(button_frame, text="Add Anyway", command=confirm_add)
        apply_primary_button_style(add_btn)
        add_btn.pack(side="left", padx=5)
