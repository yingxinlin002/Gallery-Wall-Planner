import tkinter as tk
from tkinter import font
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from PIL import Image, ImageTk
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.gui.Screen_Base import Screen_Base


class Screen_Home(Screen_Base):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.image_path = "gallery_wall_planner/gallery background.png"
        self.image = None
        self.background_image = None
        self.content_frame = None
        self.canvas = None
        # self._create_content()
    #     self.bind("<Configure>", self._resize_image)
    #     self._resize_image()  # Initial setup


        
    # def _resize_image(self, event=None):
    #     # Load and resize the image to fit the canvas size
    #     try:
    #         img = Image.open(self.image_path)
    #         img = img.resize((self.winfo_width(), self.winfo_height()), Image.LANCZOS)
    #         self.image = ImageTk.PhotoImage(img)
    #         self.delete("all")  # Clear everything on the canvas
    #         self.create_image(0, 0, image=self.image, anchor="nw")
            
    #         # Recreate the content frame if it exists
    #         if self.content_frame:
    #             self.content_frame.destroy()
    #         self._create_content()
    #     except Exception as e:
    #         print(f"Error loading background image: {e}")
    
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
        
        # Add the buttons with consistent styling
        tk.Button(self.content_frame, 
                  text="New Exhibit", 
                  command=lambda: self.AppMain.switch_screen(ScreenType.NEW_GALLERY), 
                  **button_style).pack(pady=10)
        
        tk.Button(self.content_frame, 
                  text="Load Exhibit", 
                  command=lambda: self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE), 
                  **button_style).pack(pady=10)
        
        quit_button_style = button_style.copy()
        quit_button_style["bg"] = "#69718A" 
        quit_button_style["activebackground"] = "#8A92A5"
        tk.Button(self.content_frame, 
                  text="Quit", 
                  command= self.AppMain.quit_application, 
                  **quit_button_style).pack(pady=10)