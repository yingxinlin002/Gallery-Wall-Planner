import pytest
import sys
import os
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gallery_wall_planner.gui.screen_home import Screen_Home
from gallery_wall_planner.models.wall import Wall
from tests.AppTestContext import AppTestContext
from tests.TestingSteps import TestingSteps


def test_add_permanent_object():
    """
    Integration test that verifies adding a permanent object to the wall
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
        expected_wall_properties = TestingSteps.fill_and_submit_wall_form(context)
        
        # Verify that the wall was created and we're on the PermanentObjectUI screen
        new_wall: Wall = TestingSteps.verify_wall_creation(context, expected_wall_properties)
        
        # Verify that the wall has no permanent objects initially
        assert len(new_wall.permanent_objects) == 0, "Wall should have no permanent objects initially"
        
        # Select the 'Yes' option for permanent objects
        TestingSteps.select_yes_permanent_objects(context)
        
        # Add a permanent object to the wall
        permanent_object_properties = TestingSteps.add_permanent_object(
            context, 
            name="Test Door", 
            width="24", 
            height="80"
        )
        
        # Verify that the permanent object was added to the wall with the expected properties
        permanent_object = TestingSteps.verify_permanent_object(new_wall, permanent_object_properties)
        
        # Submit the form and verify the results
        # This method now includes verification of screen transition to LOCK_OBJECTS_TO_WALL
        # and checks that the wall has permanent objects
        TestingSteps.submit_permanent_object_form(context, has_permanent_objects=True)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
