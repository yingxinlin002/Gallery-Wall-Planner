import tkinter as tk
from enum import Enum, auto
from typing import Optional

from gallery_wall_planner.models.gallery import Gallery
from gallery_wall_planner.models.artwork import Artwork  # Import Artwork class


class ScreenType(Enum):
    """Enum representing the different screens in the application"""
    LOCK_OBJECTS_TO_WALL = auto()
    HOME = auto()
    NEW_GALLERY = auto()
    SELECT_WALL_SPACE = auto()
    PERMANENT_OBJECT = auto()
    ARTWORK_SELECTION = auto()
    EDITOR = auto()
    ARTWORK_MANUAL = auto()


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
        from gallery_wall_planner.gui.screen_base import ScreenBase
        self.frame_contents: ScreenBase = None      
        self.current_screen: ScreenType = ScreenType.HOME
        self.frame_main = tk.Frame(self.root, bg="#F0F0F0")
        self.frame_main.pack(fill=tk.BOTH, expand=True)
        self.frame_main.bind("<Configure>", self._load_or_resize)

        self.save_file_path: Optional[str] = None

        self._load_or_resize()

    def _load_or_resize(self, event=None):
        self.switch_screen(self.current_screen)

    def switch_screen(self, screen_type: ScreenType):
        """Switch to the specified screen type"""
        print(f"Switching to screen: {screen_type.name}")
        
        if self.frame_main:
            # Destroy all children of frame_main
            for widget in self.frame_main.winfo_children():
                widget.destroy()
        self.root.update_idletasks()
        self.frame_contents = None
        
        # Load the appropriate screen
        if screen_type == ScreenType.HOME:
            self._load_home_screen()  # Home screen loading method, ensure no popups are involved
        elif screen_type == ScreenType.NEW_GALLERY:
            self._load_new_gallery_screen()
        elif screen_type == ScreenType.SELECT_WALL_SPACE:
            self._load_select_wall_space_screen()
        elif screen_type == ScreenType.PERMANENT_OBJECT:
            self._load_permanent_object_screen()
        elif screen_type == ScreenType.EDITOR:
            self._load_editor_screen()
        elif screen_type == ScreenType.LOCK_OBJECTS_TO_WALL:
            self._load_lock_objects_to_wall_screen()
        elif screen_type == ScreenType.ARTWORK_MANUAL:
            self._load_artwork_manual_screen()
        elif screen_type == ScreenType.ARTWORK_SELECTION:
            pass

        # Call load_content on the new screen if it's a UIBase instance
        if hasattr(self.frame_contents, 'load_content'):
            self.frame_contents.load_content()


    def _load_home_screen(self):
        """Load the home screen"""
        from gallery_wall_planner.gui.screen_home import ScreenHome
        self.frame_contents = ScreenHome(self)
        print("Home screen loaded...")
        
    def _load_new_gallery_screen(self):
        """Load the new gallery screen"""
        from gallery_wall_planner.gui.screen_new_gallery_ui import ScreenNewGalleryUI
        self.frame_contents = ScreenNewGalleryUI(self)

    def _load_select_wall_space_screen(self):
        """Load the select wall space screen"""
        from gallery_wall_planner.gui.screen_select_wall_space_ui import ScreenSelectWallSpaceUI
        self.frame_contents = ScreenSelectWallSpaceUI(self)
    
    def _load_permanent_object_screen(self):
        """Load the permanent object screen"""
        from gallery_wall_planner.gui.screen_permanent_object_ui import ScreenPermanentObjectUI
        self.frame_contents = ScreenPermanentObjectUI(self)
    
    def _load_editor_screen(self):
        """Load the editor screen"""
        from gallery_wall_planner.gui.screen_editor_ui import ScreenEditorUI
        self.frame_contents = ScreenEditorUI(self)

    def _load_lock_objects_to_wall_screen(self):
        """Load the lock objects to wall screen"""
        from gallery_wall_planner.gui.screen_lock_objects_ui import ScreenLockObjectsUI
        self.frame_contents = ScreenLockObjectsUI(self)

    def _load_artwork_manual_screen(self):
        """Load the artwork manual screen"""
        from gallery_wall_planner.gui.screen_artwork_manually_ui import ScreenArtworkManuallyUI
        self.frame_contents = ScreenArtworkManuallyUI(self)

    def _load_artwork_xlsx_screen(self):
        """Load the artwork xlsx screen"""
        from gallery_wall_planner.deprecated.screen_artwork_xlsx_ui import ScreenArtworkxlsxUI
        self.frame_contents = ScreenArtworkxlsxUI(self)

    def quit_application(self):
        """Quit the application."""
        self.root.destroy()
