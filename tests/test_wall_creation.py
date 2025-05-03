import pytest
import tkinter as tk
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.screen_home import Screen_Home
from gallery_wall_planner.models.wall import Wall
from tests.AppTestContext import AppTestContext
from tests.TestingSteps import TestingSteps


def test_wall_creation_form_submission():
    """Integration test that verifies the wall creation form works correctly"""
    # This test simulates filling out the wall creation form and submitting it
    
    # Patch mainloop to prevent the app from blocking
    with patch('tkinter.Tk.mainloop'), AppTestContext() as context:
        # Verify home screen is loaded
        TestingSteps.assert_home_screen(context)
        
        # Make sure gallery has no walls initially
        assert len(context.app.gallery.get_walls()) == 0, "Gallery should have no walls initially"
        
        # Transition to the new gallery screen
        TestingSteps.transition_to_new_gallery_screen(context)
        
        # Fill out the wall creation form and submit it
        expected_properties = TestingSteps.fill_and_submit_wall_form(context)
        
        # Verify that the wall was created with the expected properties
        TestingSteps.verify_wall_creation(context, expected_properties)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
