import pytest
import tkinter as tk
import sys
import os
import importlib
import inspect
import contextlib
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.screen_home import ScreenHome

from tests.AppTestContext import AppTestContext
from tests.TestingSteps import TestingSteps

@pytest.fixture
def app():
    """Fixture to set up the Tkinter root and app instance for tests"""
    with AppTestContext() as context:
        yield context.app


def test_initial_screen_is_home(app):
    """Test that the initial screen is the home screen"""
    # Verify that the current screen is set to HOME
    assert app.current_screen == ScreenType.HOME
    
    # Verify that the frame_contents is an instance of Screen_Home
    assert isinstance(app.frame_contents, ScreenHome)
    
    # Verify that the home screen has the expected title
    title_label = None
    for widget in app.frame_contents.content_frame.winfo_children():
        if isinstance(widget, tk.Label) and "Gallery Wall Planner" in widget.cget("text"):
            title_label = widget
            break
    
    assert title_label is not None, "Home screen title not found"
    assert title_label.cget("text") == "Gallery Wall Planner"


def test_main_module_structure():
    """Test the structure of the main module without running it"""
    # This test verifies that the main.py file has the expected structure
    # without actually executing the code
    
    # Import the main module
    import gallery_wall_planner.main
    
    # Check that the main module has the expected imports and structure
    assert hasattr(gallery_wall_planner.main, 'AppMain')
    assert hasattr(gallery_wall_planner.main, 'tk')
    
    # Check that the main module has the expected main block
    main_code = inspect.getsource(gallery_wall_planner.main)
    assert "if __name__ == \"__main__\"" in main_code
    assert "app = AppMain(root)" in main_code


def test_main_integration():
    """Integration test that actually runs a minimal version of the app"""
    # This is a more realistic test that actually creates the app
    # but doesn't show the window and exits immediately
    
    # Patch mainloop to prevent the app from blocking
    with patch('tkinter.Tk.mainloop'), AppTestContext() as context:
        TestingSteps.assert_home_screen(context)


def test_new_exhibit_button_click_integration():
    """Integration test that verifies the 'New Exhibit' button works correctly"""
    # This test simulates clicking the 'New Exhibit' button and verifies
    # that it correctly switches to the NEW_GALLERY screen and no popup appears
    # when there are no existing walls
    
    # Patch mainloop to prevent the app from blocking
    with patch('tkinter.Tk.mainloop'), AppTestContext() as context:
        # Verify home screen is loaded
        TestingSteps.assert_home_screen(context)
        
        # Make sure gallery has no walls
        assert len(context.app.gallery.get_walls()) == 0, "Gallery should have no walls initially"
        
        # Transition to the new gallery screen
        TestingSteps.transition_to_new_gallery_screen(context)
        
        # Verify that the popup was NOT created
        assert not hasattr(context.app.frame_contents, 'popup') or context.app.frame_contents.popup is None, "Popup was created when it shouldn't have been"

def test_popup_new_exhibit_integration():
    """Integration test that verifies the 'New Exhibit' popup works correctly"""
    # This test simulates clicking the 'New Exhibit' button and verifies
    # that the popup appears when there are existing walls
    
    # Patch mainloop to prevent the app from blocking
    with patch('tkinter.Tk.mainloop'), AppTestContext() as context:
        # Verify home screen is loaded
        TestingSteps.assert_home_screen(context)
        
        # Add a test wall to the gallery
        from gallery_wall_planner.models.wall import Wall
        test_wall = Wall("Test Wall", 200, 150, "white")
        context.app.gallery.add_wall(test_wall)
        
        # Transition to the new gallery screen
        TestingSteps.transition_to_new_gallery_screen(context)
        
        # Verify that the popup was created
        assert hasattr(context.app.frame_contents, 'popup'), "Popup was not created"
        assert context.app.frame_contents.popup is not None, "Popup is None"
        
        # Process events to ensure popup is fully loaded
        context.update()

def test_back_to_home_button_integration():
    """Integration test that verifies the 'Back to Home' button works correctly"""
    # This test simulates clicking the 'New Exhibit' button to go to the new gallery screen,
    # then clicking the 'Back to Home' button to return to the home screen
    
    # Patch mainloop to prevent the app from blocking
    with patch('tkinter.Tk.mainloop'), AppTestContext() as context:
        # Verify home screen is loaded
        TestingSteps.assert_home_screen(context)
        
        # Transition to the new gallery screen
        TestingSteps.transition_to_new_gallery_screen(context)
        
        # Now that the Screen_NewGalleryUI class has been updated to properly store button references,
        # we can directly access the back_to_home_button instance variable
        back_button = context.app.frame_contents.back_to_home_button
        
        # Verify that the button was found
        assert back_button is not None, "Back to Home button not found"
        
        # Simulate clicking the button
        back_button.invoke()
        
        # Process events again
        context.update()
        
        # Verify home screen is loaded
        TestingSteps.assert_home_screen(context)
        


if __name__ == "__main__":
    pytest.main(["-v", __file__])
