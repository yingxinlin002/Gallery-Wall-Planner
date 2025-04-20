from unittest.mock import patch, MagicMock

from gallery_wall_planner.gui.AppMain import ScreenType
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.structures import Position
from gallery_wall_planner.gui.WallItem_Draggable import WallItem_Draggable
from tests.TestingSteps import TestingSteps
from tests.AppTestContext import AppTestContext


def test_lock_objects_dragging():
    """
    Integration test that verifies dragging permanent objects in the LockObjectsUI screen
    and saving the layout works correctly
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
        # This method includes verification of screen transition to LOCK_OBJECTS_TO_WALL
        TestingSteps.submit_permanent_object_form(context, has_permanent_objects=True)
        
        # Verify we're on the LOCK_OBJECTS_TO_WALL screen
        assert context.app.current_screen == ScreenType.LOCK_OBJECTS_TO_WALL, \
            f"Not on the LOCK_OBJECTS_TO_WALL screen, current screen: {context.app.current_screen}"
        
        # Get the LockObjectsUI screen
        lock_objects_ui = context.app.frame_contents
        
        # Verify that the DraggableItem was created for the permanent object
        assert len(lock_objects_ui.items) == 1, "Should have one draggable item"
        draggable_item = lock_objects_ui.items[0]
        assert isinstance(draggable_item, WallItem_Draggable), "Item should be a DraggableItem"
        assert draggable_item.wall_object == permanent_object, "DraggableItem should reference the correct permanent object"
        
        # Record the initial position for later comparison
        initial_position = Position(
            draggable_item.wall_object.position.x,
            draggable_item.wall_object.position.y
        )
        
        # Simulate dragging the item using the TestingSteps helper method
        new_position = TestingSteps.simulate_drag_item(
            draggable_item,
            start_x=100,
            start_y=100,
            end_x=150,
            end_y=150,
            offset_x=50,
            canvas_y=100
        )
        
        # Verify that the position has been updated
        assert draggable_item.wall_object.position.x != initial_position.x, "X position should have changed"
        assert draggable_item.wall_object.position.y != initial_position.y, "Y position should have changed"
        
        # Verify that the position in the layout_items dictionary has been updated
        assert draggable_item.name in lock_objects_ui.layout_items, "Item should be in layout_items"
        assert lock_objects_ui.layout_items[draggable_item.name]["x"] == draggable_item.wall_object.position.x, \
            "X position in layout_items should match permanent object position"
        assert lock_objects_ui.layout_items[draggable_item.name]["y"] == draggable_item.wall_object.position.y, \
            "Y position in layout_items should match permanent object position"
        
        # Then call save_and_continue
        lock_objects_ui.next_button.invoke()
        
        # Verify that we've switched to the SELECT_WALL_SPACE screen
        assert context.app.current_screen == ScreenType.SELECT_WALL_SPACE, \
            f"Not on the SELECT_WALL_SPACE screen, current screen: {context.app.current_screen}"
        
        # Verify that the permanent object position has been saved
        assert permanent_object.position.x == draggable_item.wall_object.position.x, \
            "Permanent object position should be preserved after switching screens"
        assert permanent_object.position.y == draggable_item.wall_object.position.y, \
            "Permanent object position should be preserved after switching screens"
