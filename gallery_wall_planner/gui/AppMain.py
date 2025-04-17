import tkinter as tk
from enum import Enum, auto

from gallery_wall_planner.models.gallery import Gallery



class ScreenType(Enum):
    """Enum representing the different screens in the application"""
    HOME = auto()
    NEW_GALLERY = auto()
    SELECT_WALL_SPACE = auto()
    PERMANENT_OBJECT = auto()
    ARTWORK_SELECTION = auto()


class AppMain():
    def __init__(self, root: tk.Tk):
        self.gallery = Gallery()
        print("Creating main application window...")
        self.root = root
        self.root.title("Gallery Wall Planner")
        self.root.geometry("1024x768")
        self.root.configure(bg="#F0F0F0")
        print("Creating main frame...")
        # Create a main frame and add it to root
        from gallery_wall_planner.gui.Screen_Base import Screen_Base
        self.frame_contents: Screen_Base = None      
        self.current_screen: ScreenType = ScreenType.HOME
        self.frame_main = tk.Frame(self.root, bg="#F0F0F0")
        self.frame_main.pack(fill=tk.BOTH, expand=True)
        self.frame_main.bind("<Configure>", self._load_or_resize)

        self._load_or_resize()

    def _load_or_resize(self, event=None):
        if self.frame_main:
            # Destroy all children of frame_main
            for widget in self.frame_main.winfo_children():
                widget.destroy()
        self.root.update_idletasks()
        self.frame_contents = None
        self.switch_screen(self.current_screen)

    def switch_screen(self, screen_type: ScreenType):
        """Switch to the specified screen type"""
        print(f"Switching to screen: {screen_type.name}")

        self.current_screen = screen_type
        
        if self.frame_contents:
            print(f"Destroying {self.frame_contents.__class__.__name__}")
            for widget in self.frame_contents.winfo_children():
                print(f"Destroying {widget.__class__.__name__}")
                widget.destroy()
            self.frame_contents.destroy()
            self.frame_contents = None
        
        # Load the appropriate screen
        if screen_type == ScreenType.HOME:
            self._load_home_screen()
        elif screen_type == ScreenType.NEW_GALLERY:
            self._load_new_gallery_screen()
        elif screen_type == ScreenType.SELECT_WALL_SPACE:
            self._load_select_wall_space_screen()
        elif screen_type == ScreenType.PERMANENT_OBJECT:
            self._load_permanent_object_screen()
        elif screen_type == ScreenType.ARTWORK_SELECTION:
            # TODO: Implement artwork selection screen
            pass
        else:
            print(f"Unknown screen type: {screen_type}")
            return
            
        # Call load_content on the new screen if it's a UIBase instance
        if hasattr(self.frame_contents, 'load_content'):
            self.frame_contents.load_content()
                
    def _load_home_screen(self):
        """Load the home screen"""
        from gallery_wall_planner.gui.Screen_Home import Screen_Home
        self.frame_contents = Screen_Home(self)
        print("Home screen loaded...")
        
    def _load_new_gallery_screen(self):
        """Load the new gallery screen"""
        from gallery_wall_planner.gui.Screen_NewGalleryUI import Screen_NewGalleryUI
        self.frame_contents = Screen_NewGalleryUI(self)

    def _load_select_wall_space_screen(self):
        """Load the select wall space screen"""
        from gallery_wall_planner.gui.Screen_SelectWallSpaceUI import Screen_SelectWallSpaceUI
        self.frame_contents = Screen_SelectWallSpaceUI(self)
    
    def _load_permanent_object_screen(self):
        """Load the permanent object screen"""
        from gallery_wall_planner.gui.Screen_PermanentObjectUI import Screen_PermanentObjectUI
        self.frame_contents = Screen_PermanentObjectUI(self)
    

    def quit_application(self):
        """Quit the application."""
        self.root.destroy()
