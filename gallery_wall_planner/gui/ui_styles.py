# ui_styles.py

import tkinter as tk
from tkinter import ttk

def get_ui_styles():
    return {
        "title_font": ("Arial", 24),
        "label_font": ("Arial", 12),
        "button_font": ("Helvetica", 12, "bold"),
        "button_padx": 10,
        "button_pady": 5,
        "button_width": 15,
        "bg_primary": "#5F3FCA",
        "bg_secondary": "#69718A",
        "bg_success": "#4CAF50",
        "bg_info": "#2196F3",
        "small_font": ("Arial", 10),
        "fg_white": "white",
    }

def init_styles(root):
    style = ttk.Style(master=root)
    style.theme_use("clam")
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TButton", font=("Helvetica", 12, "bold"), padding=6)
    style.configure("Header.TLabel", font=("Arial", 20, "bold"))

def apply_primary_button_style(widget):
    styles = get_ui_styles()
    style = ttk.Style()
    style.configure("Primary.TButton",
                    font=styles["button_font"],
                    padding=(styles["button_padx"], styles["button_pady"]))
    widget.config(style="Primary.TButton", width=styles["button_width"])

def apply_previous_button_style(widget):
    styles = get_ui_styles()
    style = ttk.Style()
    style.configure("Previous.TButton",
                    font=styles["button_font"],
                    padding=(styles["button_padx"], styles["button_pady"]),
                    background=styles["bg_back_home"])
    widget.config(style="Previous.TButton", width=styles["button_width"])

def apply_header_label_style(widget):
    styles = get_ui_styles()
    widget.config(
        font=styles["title_font"]
    )

def apply_canvas_style(widget):
    widget.config(bg="white", highlightthickness=0)
