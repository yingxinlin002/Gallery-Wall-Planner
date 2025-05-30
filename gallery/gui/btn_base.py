

import tkinter as tk

from gallery.gui.ui_styles import get_ui_styles

class BTNBase(tk.Frame):
    def __init__(self, parent_frame : tk.Frame, *args, **kwargs):
        super().__init__(parent_frame, bg="white", *args, **kwargs)
        self.styles = get_ui_styles()
        self.label: tk.Label = None
        self.edit_button: tk.Button = None
        self.edit_button_text: str = "Edit"
        self.item_text: str = ""

        
    def load_content(self):
        self.label = tk.Label(self,
               text=self.item_text,
               font=self.styles["label_font"],
               bg="#fff",
               justify="left",
               anchor="w",
                )
        self.label.pack(side="left", fill="both", padx=5, expand=True)
        self.edit_button = tk.Button(self, text=self.edit_button_text, command=self.on_edit_clicked)
        self.edit_button.pack(side="right", padx=5)
        self.label.bind("<Button-1>", self.on_clicked)

    def on_clicked(self, event):
        print(f"Clicked on {self.item_text}")

    def on_edit_clicked(self):
        print(f"Edit clicked on {self.item_text}")
