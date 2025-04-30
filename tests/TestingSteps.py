import tkinter as tk
from gallery_wall_planner.gui.app_main import ScreenType
from tests.AppTestContext import AppTestContext
from gallery_wall_planner.gui.screen_home import Screen_Home
from gallery_wall_planner.gui.screen_permanent_object_ui import ScreenPermanentObjectUI

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
        assert context.app.current_screen == ScreenType.PERMANENT_OBJECT, \
            f"Screen did not change to PERMANENT_OBJECT, current screen: {context.app.current_screen}"
        
        # Verify that we're on the PermanentObjectUI screen
        assert isinstance(context.app.frame_contents, ScreenPermanentObjectUI), \
            "Not on the PermanentObjectUI screen"
        
        return new_wall
    
    @staticmethod
    def select_no_permanent_objects(context: AppTestContext):
        """Select the 'No' option for permanent objects on the wall"""
        # Verify that we're on the PermanentObjectUI screen
        assert context.app.current_screen == ScreenType.PERMANENT_OBJECT, \
            f"Not on the PERMANENT_OBJECT screen, current screen: {context.app.current_screen}"
        
        # Select the 'No' radio button
        context.app.frame_contents.rdb_add_permanent_object_no.invoke()
        
        # Process events
        context.update()
        
        # Verify that the has_permanent_items variable is set to False
        assert context.app.frame_contents.has_permanent_items.get() is False, \
            "has_permanent_items is not False after selecting 'No'"
    
    @staticmethod
    def select_yes_permanent_objects(context: AppTestContext):
        """Select the 'Yes' option for permanent objects on the wall"""
        # Verify that we're on the PermanentObjectUI screen
        assert context.app.current_screen == ScreenType.PERMANENT_OBJECT, \
            f"Not on the PERMANENT_OBJECT screen, current screen: {context.app.current_screen}"
        
        # Select the 'Yes' radio button
        context.app.frame_contents.rdb_add_permanent_object_yes.invoke()
        
        # Process events
        context.update()
        
        # Verify that the has_permanent_items variable is set to True
        assert context.app.frame_contents.has_permanent_items.get() is True, \
            "has_permanent_items is not True after selecting 'Yes'"
        
        # Verify that the permanent object input fields are visible
        assert hasattr(context.app.frame_contents, 'name_entry'), "Name entry field not found"
        assert hasattr(context.app.frame_contents, 'width_entry'), "Width entry field not found"
        assert hasattr(context.app.frame_contents, 'height_entry'), "Height entry field not found"
        assert hasattr(context.app.frame_contents, 'browse_button'), "Browse button not found"
        assert hasattr(context.app.frame_contents, 'add_permanent_object_button'), "Add permanent object button not found"
    
    @staticmethod
    def add_permanent_object(context: AppTestContext, name="Test Door", width="24", height="80"):
        """Add a permanent object to the wall"""
        # Verify that we're on the PermanentObjectUI screen and the 'Yes' option is selected
        assert context.app.current_screen == ScreenType.PERMANENT_OBJECT, \
            f"Not on the PERMANENT_OBJECT screen, current screen: {context.app.current_screen}"
        assert context.app.frame_contents.has_permanent_items.get() is True, \
            "has_permanent_items is not True, cannot add permanent object"
        
        # Clear and fill the name field
        context.app.frame_contents.name_entry.delete(0, tk.END)
        context.app.frame_contents.name_entry.insert(0, name)
        
        # Clear and fill the width field
        context.app.frame_contents.width_entry.delete(0, tk.END)
        context.app.frame_contents.width_entry.insert(0, width)
        
        # Clear and fill the height field
        context.app.frame_contents.height_entry.delete(0, tk.END)
        context.app.frame_contents.height_entry.insert(0, height)
        
        # Process events
        context.update()
        
        # Get the wall before adding the permanent object
        wall = context.app.gallery.current_wall
        initial_count = len(wall.permanent_objects)
        
        # Click the add permanent object button
        context.app.frame_contents.add_permanent_object_button.invoke()
        
        # Process events
        context.update()
        
        # Verify that a permanent object was added
        new_count = len(wall.permanent_objects)
        assert new_count > initial_count, "No permanent object was added"
        
        # Return the properties of the added object
        return {
            "name": name,
            "width": float(width),
            "height": float(height)
        }
    
    @staticmethod
    def verify_permanent_object(wall, permanent_object_properties):
        """Verify that a permanent object was added to the wall with the expected properties"""
        # Verify that the permanent object was added to the wall
        permanent_objects = wall.permanent_objects
        assert len(permanent_objects) > 0, "Wall should have at least one permanent object"
        
        # Verify the permanent object properties
        permanent_object = permanent_objects[-1]  # Get the most recently added permanent object
        assert permanent_object.name == permanent_object_properties["name"], \
            f"Permanent object name is incorrect: {permanent_object.name}"
        assert permanent_object.width == permanent_object_properties["width"], \
            f"Permanent object width is incorrect: {permanent_object.width}"
        assert permanent_object.height == permanent_object_properties["height"], \
            f"Permanent object height is incorrect: {permanent_object.height}"
        
        # Verify that the position is set
        assert hasattr(permanent_object, 'position'), "Permanent object does not have position attribute"
        assert hasattr(permanent_object.position, 'x'), "Position does not have x attribute"
        assert hasattr(permanent_object.position, 'y'), "Position does not have y attribute"
        
        return permanent_object
    
    @staticmethod
    def submit_permanent_object_form(context: AppTestContext, has_permanent_objects=False):
        """Submit the permanent object form"""
        # Verify that we're on the PermanentObjectUI screen
        assert context.app.current_screen == ScreenType.PERMANENT_OBJECT, \
            f"Not on the PERMANENT_OBJECT screen, current screen: {context.app.current_screen}"
        
        # Verify that the submit button is enabled
        assert context.app.frame_contents.submit_button.cget("state") == "normal", \
            "Submit button is not enabled"
        
        # Get the current wall before submission
        wall = context.app.gallery.current_wall
        
        # Click the submit button
        context.app.frame_contents.submit_button.invoke()
        
        # Process events
        context.update()
        
        # Verify that the wall still exists in the gallery
        walls = context.app.gallery.get_walls()
        assert len(walls) > 0, "Wall was removed from the gallery"
        
        if has_permanent_objects:
            # Verify that we've moved to the LOCK_OBJECTS_TO_WALL screen
            assert context.app.current_screen == ScreenType.LOCK_OBJECTS_TO_WALL, \
                f"Screen did not change to LOCK_OBJECTS_TO_WALL, current screen: {context.app.current_screen}"
            
            # Verify that the wall has permanent objects
            assert len(wall.permanent_objects) > 0, "Wall should have permanent objects"
        else:
            # Verify that we've moved to the SELECT_WALL_SPACE screen (when no permanent objects)
            assert context.app.current_screen == ScreenType.SELECT_WALL_SPACE, \
                f"Screen did not change to SELECT_WALL_SPACE, current screen: {context.app.current_screen}"
            
            # Verify that the wall has no permanent objects
            assert len(wall.permanent_objects) == 0, "Wall should not have any permanent objects"
    
    @staticmethod
    def simulate_drag_item(draggable_item, start_x=100, start_y=100, end_x=150, end_y=150, offset_x=50, canvas_y=100):
        """Simulate dragging a DraggableItem from one position to another
        
        Args:
            draggable_item: The DraggableItem to drag
            start_x: The starting x coordinate for the drag event
            start_y: The starting y coordinate for the drag event
            end_x: The ending x coordinate for the drag event
            end_y: The ending y coordinate for the drag event
            offset_x: The x offset to apply to the wall position (for mocking coordinates)
            canvas_y: The y position on the canvas (for mocking coordinates)
            
        Returns:
            The updated position of the draggable item
        """
        from unittest.mock import MagicMock
        from gallery_wall_planner.models.structures import Position
        
        # Record the initial position
        initial_position = Position(
            draggable_item.wall_object.position.x,
            draggable_item.wall_object.position.y
        )
        
        # Simulate dragging the item
        # First, simulate the start of a drag operation
        start_event = MagicMock()
        start_event.x = start_x
        start_event.y = start_y
        draggable_item.on_start(start_event)
        
        # Then simulate a drag operation
        drag_event = MagicMock()
        drag_event.x = end_x
        drag_event.y = end_y
        draggable_item.on_drag(drag_event)
        
        # Finally, simulate dropping the item
        drop_event = MagicMock()
        drop_event.x = end_x
        drop_event.y = end_y
        
        # Mock the canvas.coords method to handle both getting and setting coordinates
        original_coords = draggable_item.parent_ui.canvas.coords
            
        def mock_coords(*args):
            if len(args) == 1 and args[0] == draggable_item.id:
                # Getting coordinates
                x1 = draggable_item.parent_ui.wall_position.wall_left + offset_x
                y1 = canvas_y
                x2 = x1 + draggable_item.wall_object.width * draggable_item.parent_ui.screen_scale
                y2 = y1 + draggable_item.wall_object.height * draggable_item.parent_ui.screen_scale
                return [x1, y1, x2, y2]
            elif len(args) == 5 and args[0] == draggable_item.id:
                # Setting coordinates - just pass through to the original method
                return original_coords(*args)
            else:
                # For any other calls, pass through to the original method
                return original_coords(*args)
            
        # Apply the mock
        draggable_item.parent_ui.canvas.coords = mock_coords
        
        # Now drop the item
        draggable_item.on_drop(drop_event)
        
        # Verify that the position has been updated
        assert draggable_item.wall_object.position.x != initial_position.x, "X position should have changed"
        assert draggable_item.wall_object.position.y != initial_position.y, "Y position should have changed"
        
        # Return the new position
        return draggable_item.wall_object.position

