import os
import json
import pytest
import tempfile
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanentObject import PermanentObject
from gallery_wall_planner.models.wall_line import SingleLine

class TestWall:
    """Test suite for the Wall class"""
    
    def test_init_with_defaults(self):
        """Test initialization with default values"""
        wall = Wall("Test Wall", 120, 96)
        assert wall.name == "Test Wall"
        assert wall.width == 120
        assert wall.height == 96
        assert wall.color == "White"  # Default color
        assert len(wall.artwork) == 0
        assert len(wall.wall_lines) == 0
        assert len(wall.permanent_objects) == 0
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values"""
        wall = Wall("Gallery Wall", 240, 120, "Beige")
        assert wall.name == "Gallery Wall"
        assert wall.width == 240
        assert wall.height == 120
        assert wall.color == "Beige"
    
    # Name validation tests
    def test_name_validation_non_string(self):
        """Test name validation for non-string values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Name must be a string"):
            wall.name = 123
    
    def test_name_validation_empty(self):
        """Test name validation for empty string"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Name cannot be empty"):
            wall.name = ""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            wall.name = "   "  # Only whitespace
    
    # Width validation tests
    def test_width_validation_non_numeric(self):
        """Test width validation for non-numeric values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Width must be a number"):
            wall.width = "invalid"
    
    def test_width_validation_non_positive(self):
        """Test width validation for non-positive values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Width must be positive"):
            wall.width = 0
        with pytest.raises(ValueError, match="Width must be positive"):
            wall.width = -10
    
    # Height validation tests
    def test_height_validation_non_numeric(self):
        """Test height validation for non-numeric values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Height must be a number"):
            wall.height = "invalid"
    
    def test_height_validation_non_positive(self):
        """Test height validation for non-positive values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Height must be positive"):
            wall.height = 0
        with pytest.raises(ValueError, match="Height must be positive"):
            wall.height = -10
    
    # Color validation tests
    def test_color_validation_non_string(self):
        """Test color validation for non-string values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Color must be a string"):
            wall.color = 123
    
    # Artwork list validation tests
    def test_artwork_validation_non_list(self):
        """Test artwork validation for non-list values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Artwork must be a list"):
            wall.artwork = "invalid"
    
    def test_artwork_validation_invalid_items(self):
        """Test artwork validation for invalid items in list"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="All items in artwork list must be Artwork objects"):
            wall.artwork = [123, "invalid"]
    
    def test_artwork_validation_valid_items(self):
        """Test artwork validation for valid items in list"""
        wall = Wall("Test Wall", 120, 96)
        artwork1 = Artwork("Art 1", "Oil", 20, 30)
        artwork2 = Artwork("Art 2", "Acrylic", 15, 25)
        wall.artwork = [artwork1, artwork2]
        assert len(wall.artwork) == 2
        assert wall.artwork[0] == artwork1
        assert wall.artwork[1] == artwork2
    
    # Wall lines list validation tests
    def test_wall_lines_validation_non_list(self):
        """Test wall_lines validation for non-list values"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="Wall lines must be a list"):
            wall.wall_lines = "invalid"
    
    def test_wall_lines_validation_invalid_items(self):
        """Test wall_lines validation for invalid items in list"""
        wall = Wall("Test Wall", 120, 96)
        with pytest.raises(ValueError, match="All items in wall_lines list must be SingleLine objects"):
            wall.wall_lines = [123, "invalid"]
    
    def test_wall_lines_validation_valid_items(self):
        """Test wall_lines validation for valid items in list"""
        wall = Wall("Test Wall", 120, 96)
        line1 = SingleLine(10, 20, 100)
        line2 = SingleLine(30, 40, 80)
        wall.wall_lines = [line1, line2]
        assert len(wall.wall_lines) == 2
        assert wall.wall_lines[0] == line1
        assert wall.wall_lines[1] == line2
    
    # Permanent objects methods tests
    def test_add_permanent_object(self):
        """Test adding a permanent object to the wall"""
        wall = Wall("Test Wall", 120, 96)
        obj = PermanentObject("Window", 36, 48)
        
        # Add with default position
        result = wall.add_permanent_object(obj)
        assert result is True
        assert len(wall.permanent_objects) == 1
        assert wall.permanent_objects[0] == obj
    
    def test_remove_permanent_object_by_instance(self):
        """Test removing a permanent object by instance"""
        wall = Wall("Test Wall", 120, 96)
        obj = PermanentObject("Window", 36, 48)
        wall.add_permanent_object(obj)
        
        # Remove by instance
        result = wall.remove_permanent_object(obj)
        assert result is True
        assert len(wall.permanent_objects) == 0
    
    def test_remove_permanent_object_by_name(self):
        """Test removing a permanent object by name"""
        wall = Wall("Test Wall", 120, 96)
        obj = PermanentObject("Window", 36, 48)
        wall.add_permanent_object(obj)
        
        # Remove by name
        result = wall.remove_permanent_object("Window")
        assert result is True
        assert len(wall.permanent_objects) == 0
    
    def test_get_permanent_object_by_name(self):
        """Test getting a permanent object by name"""
        wall = Wall("Test Wall", 120, 96)
        obj1 = PermanentObject("Window", 36, 48)
        obj2 = PermanentObject("Door", 32, 80)
        wall.add_permanent_object(obj1)
        wall.add_permanent_object(obj2)
        
        found_obj = wall.get_permanent_object_by_name("Window")
        assert found_obj == obj1
        
        not_found_obj = wall.get_permanent_object_by_name("Fireplace")
        assert not_found_obj is None
    
    # Artwork methods tests
    def test_add_artwork(self):
        """Test adding artwork to the wall"""
        wall = Wall("Test Wall", 120, 96)
        artwork = Artwork("Landscape", "Oil", 24, 36)
        
        wall.add_artwork(artwork)
        assert len(wall.artwork) == 1
        assert wall.artwork[0] == artwork
    
    def test_remove_artwork(self):
        """Test removing artwork from the wall"""
        wall = Wall("Test Wall", 120, 96)
        artwork = Artwork("Landscape", "Oil", 24, 36)
        wall.add_artwork(artwork)
        
        result = wall.remove_artwork(artwork)
        assert result is True
        assert len(wall.artwork) == 0
    
    def test_get_artwork_by_name(self):
        """Test getting artwork by name"""
        wall = Wall("Test Wall", 120, 96)
        artwork1 = Artwork("Landscape", "Oil", 24, 36)
        artwork2 = Artwork("Portrait", "Acrylic", 18, 24)
        wall.add_artwork(artwork1)
        wall.add_artwork(artwork2)
        
        found_art = wall.get_artwork_by_name("Landscape")
        assert found_art == artwork1
        
        not_found_art = wall.get_artwork_by_name("Abstract")
        assert not_found_art is None
    
    # Export and save tests
    def test_export_wall(self):
        """Test exporting wall data to dictionary"""
        wall = Wall("Test Wall", 120, 96, "Cream")
        artwork = Artwork("Landscape", "Oil", 24, 36)
        obj = PermanentObject("Window", 36, 48)
        wall.add_artwork(artwork)
        wall.add_permanent_object(obj)
        
        export_data = wall.export_wall()
        assert export_data["name"] == "Test Wall"
        assert export_data["width"] == 120
        assert export_data["height"] == 96
        assert export_data["color"] == "Cream"
        assert len(export_data["artwork"]) == 1
        assert len(export_data["permanent_objects"]) == 1
    
    def test_save_and_load_from_file(self):
        """Test saving wall data to file and loading it back"""
        wall = Wall("Test Wall", 120, 96, "Cream")
        obj = PermanentObject("Window", 36, 48)
        wall.add_permanent_object(obj, 20, 30)
        
        # Create a temporary file for the test
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            filename = temp_file.name
        
        try:
            # Save to file
            wall.save_to_file(filename)
            
            # Load from file
            loaded_wall = Wall.load_from_file(filename)
            
            # Verify loaded data
            assert loaded_wall.name == "Test Wall"
            assert loaded_wall.width == 120
            assert loaded_wall.height == 96
            assert loaded_wall.color == "Cream"
            assert len(loaded_wall.permanent_objects) == 1
            assert loaded_wall.permanent_objects[0].name == "Window"
            assert loaded_wall.permanent_objects[0].width == 36
            assert loaded_wall.permanent_objects[0].height == 48
        finally:
            # Clean up the temporary file
            if os.path.exists(filename):
                os.remove(filename)
    
    # String representation test
    def test_str_representation(self):
        """Test string representation of the wall"""
        wall = Wall("Test Wall", 120, 96)
        artwork = Artwork("Landscape", "Oil", 24, 36)
        obj = PermanentObject("Window", 36, 48)
        wall.add_artwork(artwork)
        wall.add_permanent_object(obj)
        
        string_repr = str(wall)
        assert "Test Wall" in string_repr
        assert "120.0\" x 96.0\"" in string_repr
        assert "Artwork: 1 items" in string_repr
        assert "Permanent Objects: 1 items" in string_repr
