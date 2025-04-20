from __future__ import annotations
import tkinter as tk
from gallery_wall_planner.gui.Popup_Base import Popup_Base
from gallery_wall_planner.gui.AppMain import AppMain

class Popup_NewExhibit(Popup_Base):
    def __init__(self, AppMain : AppMain, parent_ui: 'Screen_NewGalleryUI', *args, **kwargs):
        super().__init__(AppMain, "New Exhibit", 300, 150, *args, **kwargs)
        from gallery_wall_planner.gui.Screen_NewGalleryUI import Screen_NewGalleryUI
        self.parent_ui: Screen_NewGalleryUI = parent_ui


    def load_content(self):
        # Add buttons to the popup window
        tk.Button(
            self,
            text="Start from Scratch",
            command=self.start_from_scratch,
            width=20,
            bg="#5F3FCA",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="raised",
            padx=10,
            pady=5
        ).pack(pady=10)

        tk.Button(
            self,
            text="Load from an Existing Wall",
            command=self.load_from_existing,
            width=20,
            bg="#5F3FCA",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="raised",
            padx=10,
            pady=5
        ).pack(pady=10)

    def start_from_scratch(self):
        self.parent_ui.start_from_scratch()
        self.destroy()

    def load_from_existing(self):
        self.parent_ui.load_from_existing()
        self.destroy()
        
