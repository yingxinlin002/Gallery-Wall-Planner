import pytest
import tkinter as tk
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gallery_wall_planner.gui.AppMain import AppMain, ScreenType
from gallery_wall_planner.gui.Screen_Home import Screen_Home
from gallery_wall_planner.gui.Screen_PermanentObjectUI import Screen_PermanentObjectUI
from gallery_wall_planner.models.wall import Wall
from tests.AppTestContext import AppTestContext
from tests.TestingSteps import TestingSteps


def test_permanent_object_no_option():
    """
    Integration test that verifies selecting 'No' for permanent objects
    and submitting the form works correctly
    """
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
        
        # Verify that the wall was created and we're on the PermanentObjectUI screen
        new_wall = TestingSteps.verify_wall_creation(context, expected_properties)
        
        # Select the 'No' option for permanent objects
        TestingSteps.select_no_permanent_objects(context)
        
        # Submit the form and verify the results
        # This method now includes verification of screen transition to SELECT_WALL_SPACE
        # and checks that the wall has no permanent objects
        TestingSteps.submit_permanent_object_form(context)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
