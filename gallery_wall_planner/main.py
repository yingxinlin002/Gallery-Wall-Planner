import sys
import os
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gallery_wall_planner.gui.NewGalleryUI import NewGalleryUI
from gallery_wall_planner.gui.SelectWallSpaceUI import SelectWallSpaceUI
from gallery_wall_planner.models.gallery import Gallery
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.permanentObject import PermanentObject

from gallery_wall_planner.config import Config

from gallery_wall_planner.gui.AppMain import AppMain

# Initialize example wall once at startup
example_wall = Wall("Example Wall", 200, 125, "grey")
standard_door = PermanentObject("Main Door", 36, 80)
example_wall.add_permanent_object(standard_door, x=82, y=0)

# Gallery.add_wall(example_wall)

class BackgroundImage(tk.Canvas):
    def __init__(self, parent, image_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.image_path = image_path
        self.image = None
        self.background_image = None
        self.content_frame = None
        self.bind("<Configure>", self._resize_image)
        self._resize_image()  # Initial setup


        
    def _resize_image(self, event=None):
        # Load and resize the image to fit the canvas size
        try:
            img = Image.open(self.image_path)
            img = img.resize((self.winfo_width(), self.winfo_height()), Image.LANCZOS)
            self.image = ImageTk.PhotoImage(img)
            self.delete("all")  # Clear everything on the canvas
            self.create_image(0, 0, image=self.image, anchor="nw")
            
            # Recreate the content frame if it exists
            if self.content_frame:
                self.content_frame.destroy()
            self._create_content()
        except Exception as e:
            print(f"Error loading background image: {e}")
    
    def _create_content(self):
        """Create the content that goes on top of the background"""
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
            "font": button_font,
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
                  command=lambda: NewGalleryUI(root, create_home_menu), 
                  **button_style).pack(pady=10)
        
        tk.Button(self.content_frame, 
                  text="Load Exhibit", 
                  command=lambda: SelectWallSpaceUI(root, create_home_menu), 
                  **button_style).pack(pady=10)
        
        quit_button_style = button_style.copy()
        quit_button_style["bg"] = "#69718A"
        quit_button_style["activebackground"] = "#8A92A5"
        tk.Button(self.content_frame, 
                  text="Quit", 
                  command=quit_application, 
                  **quit_button_style).pack(pady=10)

def create_home_menu():
    """Create the home menu with buttons."""
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create background canvas with content
    bg_canvas = BackgroundImage(root, "gallery_wall_planner/gallery background.png")
    bg_canvas.pack(fill="both", expand=True)

def quit_application():
    """Quit the application."""
    root.destroy()

# config = Config()
# config.write_config()

# # Create the main application window
# root = tk.Tk()
# root.title("Gallery Wall Planner")
# root.geometry("1024x768")

# # Define a custom font for the buttons
# button_font = font.Font(family="Helvetica", size=14, weight="bold")

# # Create the home menu
# create_home_menu()

# # Start the main event loop
# root.mainloop()

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple App")

        self.label_var = tk.StringVar()
        self.label_var.set("Initial Value")

        self.label = tk.Label(root, textvariable=self.label_var)
        self.label.pack(pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(pady=5)

        self.button = tk.Button(root, text="Update Label", command=self.update_label)
        self.button.pack(pady=5)

    def update_label(self):
        new_text = self.entry.get()
        if new_text:
            self.label_var.set(f"Updated to: {new_text}")
        else:
            self.label_var.set("Entry was empty!")

if __name__ == "__main__":
    print("Starting Gallery Wall Planner...")
    root = tk.Tk()
    print("Creating main application window...")
    app = AppMain(root)
    print("Starting main event loop...")
    root.mainloop()