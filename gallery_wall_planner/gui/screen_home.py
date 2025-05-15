import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from PIL import Image, ImageTk
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.gui.screen_base import ScreenBase
from gallery_wall_planner.models.project_exporter import import_gallery_from_excel
import traceback


class ScreenHome(ScreenBase):
    """Home screen of the application. It provides options to create a new gallery, load an existing one, or continue the last project."""
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        import os
        self.image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "gallery background.png"))
        self.image = None
        self.background_image = None
        self.content_frame = None
        self.canvas = None
    
    def load_content(self):
        """Create the content that goes on top of the background"""
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.configure(width=self.AppMain.frame_main.winfo_width(), height=self.AppMain.frame_main.winfo_height())
        try:
            img = Image.open(self.image_path)
            img = img.resize((self.AppMain.frame_main.winfo_width(), self.AppMain.frame_main.winfo_height()), Image.LANCZOS)
            self.image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.image, anchor="nw")
            
        except Exception as e:
            print(f"Error loading background image: {e}")
        self.content_frame = tk.Frame(self, bg="", bd=0)  # Transparent background
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        # Add the title label with a stylish font
        title_font = font.Font(family="Helvetica", size=36, weight="bold")
        tk.Label(self.content_frame, 
                 text="Gallery Wall Planner", 
                 font=title_font, 
                 bg="white", 
                 fg="#5F3FCA", 
                 padx=20, 
                 pady=10).pack(pady=(0, 50))
        
        # Button style configuration
        button_style = {
            "width": 25,
            "bg": "#5F3FCA",
            "fg": "white",
            "font": get_ui_styles()["button_font"],
            "relief": "raised",
            "padx": 10,
            "pady": 10,
            "bd": 0,
            "highlightthickness": 0,
            "activebackground": "#7A5FFA"
        }
        
        if self.check_last_project():
            tk.Button(self.content_frame,
                  text="Continue Last Project", 
                  command=lambda: self.continue_last_project(), 
                  **button_style).pack(pady=10)
        
        # Add the buttons with consistent styling
        tk.Button(self.content_frame, 
                  text="New Exhibit", 
                  command=lambda: self.AppMain.switch_screen(ScreenType.NEW_GALLERY), 
                  **button_style).pack(pady=10)
        
        tk.Button(self.content_frame, 
                  text="Load Exhibit", 
                  command=self.load_exhibit,
                  **button_style).pack(pady=10)
        
        quit_button_style = button_style.copy()
        quit_button_style["bg"] = "#69718A" 
        quit_button_style["activebackground"] = "#8A92A5"
        tk.Button(self.content_frame, 
                  text="Quit", 
                  command= self.AppMain.quit_application, 
                  **quit_button_style).pack(pady=10)
        
    def check_last_project(self):
        """Check if the last project exists and prompt to continue"""
        import os
        last_project_path = os.path.join(self.AppMain.user_dir, "_temp.xlsx")
        if os.path.exists(last_project_path):
            # If last project > 6kb
            if os.path.getsize(last_project_path) > 6144:
                return True
        else:
            return False
        
    def continue_last_project(self):
        """Load the last project if it exists"""
        import os
        last_project_path = os.path.join(self.AppMain.user_dir, "_temp.xlsx")
        if os.path.exists(last_project_path):
            try:
                self.AppMain.gallery = import_gallery_from_excel(last_project_path)
                self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)
            except Exception as e:
                traceback.print_exc()
                messagebox.showerror("Error", str(e))

    def load_exhibit(self):
        """Load an existing exhibit from an Excel file"""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        print(file_path)
        try:
            # TODO: Add error handling
            self.AppMain.gallery = import_gallery_from_excel(file_path)
            self.AppMain.save_file_path = file_path
            self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", str(e))
