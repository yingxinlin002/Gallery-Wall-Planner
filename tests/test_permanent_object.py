import pytest
import sys
import os
from typing import Optional

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gallery_wall_planner.models.permanentObject import PermanentObject


class TestPermanentObject:
    """Test suite for the PermanentObject class"""

    def test_init_with_defaults(self):
        """Test initialization with default values"""
        obj = PermanentObject("Test Object", 10, 20)
        assert obj.name == "Test Object"
        assert obj.width == 10
        assert obj.height == 20
        assert obj.image_path is None
        assert obj.position is None

    def test_init_with_custom_values(self):
        """Test initialization with custom values"""
        obj = PermanentObject("Custom Object", 30, 40, "path/to/image.jpg")
        assert obj.name == "Custom Object"
        assert obj.width == 30
        assert obj.height == 40
        assert obj.image_path == "path/to/image.jpg"
        assert obj.position is None

    def test_name_validation_empty_string(self):
        """Test validation for empty name"""
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            PermanentObject("", 10, 20)

    def test_name_validation_whitespace_string(self):
        """Test validation for whitespace-only name"""
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            PermanentObject("   ", 10, 20)

    def test_name_validation_non_string(self):
        """Test validation for non-string name"""
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            PermanentObject(123, 10, 20)

    def test_width_validation_zero(self):
        """Test validation for zero width"""
        with pytest.raises(ValueError, match="Width must be a positive number"):
            PermanentObject("Test Object", 0, 20)

    def test_width_validation_negative(self):
        """Test validation for negative width"""
        with pytest.raises(ValueError, match="Width must be a positive number"):
            PermanentObject("Test Object", -10, 20)

    def test_width_validation_non_numeric(self):
        """Test validation for non-numeric width"""
        with pytest.raises(ValueError, match="Width must be a positive number"):
            PermanentObject("Test Object", "10", 20)

    def test_height_validation_zero(self):
        """Test validation for zero height"""
        with pytest.raises(ValueError, match="Height must be a positive number"):
            PermanentObject("Test Object", 10, 0)

    def test_height_validation_negative(self):
        """Test validation for negative height"""
        with pytest.raises(ValueError, match="Height must be a positive number"):
            PermanentObject("Test Object", 10, -20)

    def test_height_validation_non_numeric(self):
        """Test validation for non-numeric height"""
        with pytest.raises(ValueError, match="Height must be a positive number"):
            PermanentObject("Test Object", 10, "20")

    def test_image_path_validation_non_string(self):
        """Test validation for non-string image path"""
        with pytest.raises(ValueError, match="Image path must be a string or None"):
            PermanentObject("Test Object", 10, 20, 123)

    def test_position_property(self):
        """Test the position property getter and setter"""
        obj = PermanentObject("Test Object", 10, 20)
        assert obj.position is None
        
        # Set position
        obj.position = {'x': 30, 'y': 40}
        assert obj.position == {'x': 30, 'y': 40}
        
        # Change position
        obj.position = {'x': 50, 'y': 60}
        assert obj.position == {'x': 50, 'y': 60}

    def test_get_bounds_with_position(self):
        """Test the get_bounds method when position is set"""
        obj = PermanentObject("Test Object", 10, 20)
        obj.position = {'x': 30, 'y': 40}
        
        # Get bounds
        bounds = obj.get_bounds()
        
        # Check bounds (x1, y1, x2, y2)
        assert bounds == (30, 40, 40, 60)

    def test_get_bounds_without_position(self):
        """Test the get_bounds method when position is not set"""
        obj = PermanentObject("Test Object", 10, 20)
        
        # Get bounds without position should return None
        assert obj.get_bounds() is None

    def test_str_representation(self):
        """Test the string representation of the object"""
        obj = PermanentObject("Test Object", 10, 20)
        str_rep = str(obj)
        
        # The string representation should contain the name
        assert "Test Object" in str_rep
        
        # Set position and check again
        obj.position = {'x': 30, 'y': 40}
        str_rep = str(obj)
        
        # Should now contain position information
        assert "30" in str_rep
        assert "40" in str_rep
