import tkinter as tk
from gallery_wall_planner.gui.app_main import ScreenType
from tests.AppTestContext import AppTestContext
from gallery_wall_planner.gui.screen_home import Screen_Home
from gallery_wall_planner.deprecated.screen_permanent_object_ui import ScreenPermanentObjectUI

class TestingSteps:
    
    @staticmethod
    def assert_home_screen(context: AppTestContext):
        """Verify that the home screen is loaded"""
        assert context.app.current_screen == ScreenType.HOME
        assert isinstance(context.app.frame_contents, Screen_Home)

    @staticmethod
    def transition_to_new_gallery_screen(context: AppTestContext):
        """Transition to the new gallery screen"""
        # Find the "New Exhibit" button
        new_exhibit_button = context.find_button(context.app.frame_contents.content_frame, "New Exhibit")
        
        # Verify that the button was found
        assert new_exhibit_button is not None, "New Exhibit button not found"
        
        # Simulate clicking the button
        new_exhibit_button.invoke()
        
        # Process events again
        context.update()
        
        # Verify that the screen has changed to NEW_GALLERY
        assert context.app.current_screen == ScreenType.NEW_GALLERY
    
    @staticmethod
    def fill_and_submit_wall_form(context: AppTestContext, wall_name="Test Wall", wall_width="200", wall_height="150"):
        """Fill out the wall creation form and submit it"""
        # Set wall name
        context.app.frame_contents.wall_name_entry.delete(0, tk.END)
        context.app.frame_contents.wall_name_entry.insert(0, wall_name)
        
        # Set wall width
        context.app.frame_contents.wall_width_entry.delete(0, tk.END)
        context.app.frame_contents.wall_width_entry.insert(0, wall_width)
        
        # Set wall height
        context.app.frame_contents.wall_height_entry.delete(0, tk.END)
        context.app.frame_contents.wall_height_entry.insert(0, wall_height)
        
        # Process events to update the preview
        context.update()
        
        # Get the current wall color before submission
        wall_color = context.app.frame_contents.wall_color
        
        # Submit the form
        context.app.frame_contents.submit_and_next_button.invoke()
        
        # Process events again
        context.update()
        
        # Return the expected wall properties for verification
        return {
            "name": wall_name,
            "width": float(wall_width),
            "height": float(wall_height),
            "color": wall_color
        }
    
    @staticmethod
    def verify_wall_creation(context: AppTestContext, expected_properties):
        """Verify that the wall was created with the expected properties"""
        # Verify that the wall was added to the gallery
        walls = context.app.gallery.get_walls()
        assert len(walls) > 0, "No walls were added to the gallery"
        
        # Verify the wall properties
        new_wall = walls[-1]  # Get the most recently added wall
        assert new_wall.name == expected_properties["name"], f"Wall name is incorrect: {new_wall.name}"
        assert new_wall.width == expected_properties["width"], f"Wall width is incorrect: {new_wall.width}"
        assert new_wall.height == expected_properties["height"], f"Wall height is incorrect: {new_wall.height}"
        assert new_wall.color == expected_properties["color"], f"Wall color is incorrect: {new_wall.color}"
        
        # Verify that the screen has changed to PERMANENT_OBJECT
        assert context.app.current_screen == ScreenType.LOCK_OBJECTS_TO_WALL, \
            f"Screen did not change to PERMANENT_OBJECT, current screen: {context.app.current_screen}"
        
        # Verify that we're on the PermanentObjectUI screen
        assert isinstance(context.app.frame_contents, ScreenPermanentObjectUI), \
            "Not on the PermanentObjectUI screen"
        
        return new_wall
    
