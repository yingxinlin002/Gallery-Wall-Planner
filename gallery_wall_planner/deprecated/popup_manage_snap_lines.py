import tkinter as tk
from tkinter import ttk

from gallery_wall_planner.gui.popup_base import PopupBase
from gallery_wall_planner.gui.screen_editor_ui import ScreenEditorUI
from gallery_wall_planner.models.wall_line import SingleLine, Orientation

class ManageSnapLinesPopup(PopupBase):
    def __init__(self, AppMain : AppMain, parent_ui: 'Screen_EditorUI', *args, **kwargs):
        super().__init__(AppMain, "Manage Snap Lines", 400, 320, *args, **kwargs)
        self.parent_ui: ScreenEditorUI = parent_ui

    def load_content(self):
        if not self.snap_lines:
            ttk.Label(self, text="No snap lines to manage.").pack(padx=10, pady=10)
            return

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_configure)

        for idx, line in enumerate(self.snap_lines):
            line_frame = ttk.Frame(frame)
            line_frame.pack(fill="x", pady=5, padx=10)

            orientation_str = line.orientation.value.capitalize() if isinstance(line.orientation, Orientation) else "Unknown"
            alignment_str = self.get_alignment_string(line)
            label_text = f"{orientation_str} - {alignment_str} - {line.distance:.2f}\""
            ttk.Label(line_frame, text=label_text).pack(side="left")

            ttk.Button(
                line_frame,
                text="Edit",
                command=lambda i=idx: self.edit_snap_line(i, self)
            ).pack(side="right", padx=5)

            ttk.Button(
                line_frame,
                text="Delete",
                command=lambda i=idx: self.delete_snap_line(i, popup)
            ).pack(side="right", padx=5)
