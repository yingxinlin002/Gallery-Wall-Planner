import os
import json
import pytest
import tempfile
from gallery_wall_planner.models.wall_line import SingleLine, LineOrientation, LineAlignment

class TestSingleLine:
    """Test suite for the SingleLine class"""
    
    def test_init_with_defaults(self):
        """Test initialization with default values"""
        line = SingleLine()
        assert line.x_cord == 0
        assert line.y_cord == 0
        assert line.length == 0
        assert line.angle == 0
        assert line.snap_to is True
        assert line.moveable is True
        assert line.orientation == LineOrientation.HORIZONTAL
        assert line.alignment == LineAlignment.CENTER
        assert line.distance == 0
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values"""
        line = SingleLine(
            x=10,
            y=20,
            length=100,
            angle=45,
            snap_to=False,
            moveable=False,
            orientation=LineOrientation.VERTICAL,
            alignment=LineAlignment.TOP,
            distance=5
        )
        assert line.x_cord == 10
        assert line.y_cord == 20
        assert line.length == 100
        assert line.angle == 45
        assert line.snap_to is False
        assert line.moveable is False
        assert line.orientation == LineOrientation.VERTICAL
        assert line.alignment == LineAlignment.TOP
        assert line.distance == 5
    
    def test_init_with_string_enums(self):
        """Test initialization with string values for enums"""
        line = SingleLine(
            orientation="vertical",
            alignment="top"
        )
        assert line.orientation == LineOrientation.VERTICAL
        assert line.alignment == LineAlignment.TOP
    
    # X coordinate validation tests
    def test_x_cord_validation_non_numeric(self):
        """Test x_cord validation for non-numeric values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="X-coordinate must be a number"):
            line.x_cord = "invalid"
    
    # Y coordinate validation tests
    def test_y_cord_validation_non_numeric(self):
        """Test y_cord validation for non-numeric values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Y-coordinate must be a number"):
            line.y_cord = "invalid"
    
    # Length validation tests
    def test_length_validation_negative(self):
        """Test length validation for negative values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Length cannot be negative"):
            line.length = -10
    
    def test_length_validation_non_numeric(self):
        """Test length validation for non-numeric values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Length must be a number"):
            line.length = "invalid"
    
    # Angle validation tests
    def test_angle_validation_non_numeric(self):
        """Test angle validation for non-numeric values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Angle must be a number"):
            line.angle = "invalid"
    
    def test_angle_normalization(self):
        """Test angle normalization to 0-360 range"""
        line = SingleLine()
        
        # Test angle > 360
        line.angle = 370
        assert line.angle == 10
        
        # Test angle < 0
        line.angle = -90
        assert line.angle == 270
    
    # Snap to validation tests
    def test_snap_to_validation_non_boolean(self):
        """Test snap_to validation for non-boolean values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Snap-to must be a boolean"):
            line.snap_to = "invalid"
    
    # Moveable validation tests
    def test_moveable_validation_non_boolean(self):
        """Test moveable validation for non-boolean values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Moveable must be a boolean"):
            line.moveable = "invalid"
    
    # Orientation validation tests
    def test_orientation_validation_invalid_string(self):
        """Test orientation validation for invalid string values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Invalid orientation value"):
            line.orientation = "invalid"
    
    def test_orientation_validation_non_string_or_enum(self):
        """Test orientation validation for non-string and non-enum values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Orientation must be a LineOrientation enum or a valid string value"):
            line.orientation = 123
    
    # Alignment validation tests
    def test_alignment_validation_invalid_string(self):
        """Test alignment validation for invalid string values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Invalid alignment value"):
            line.alignment = "invalid"
    
    def test_alignment_validation_non_string_or_enum(self):
        """Test alignment validation for non-string and non-enum values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Alignment must be a LineAlignment enum or a valid string value"):
            line.alignment = 123
    
    # Distance validation tests
    def test_distance_validation_negative(self):
        """Test distance validation for negative values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Distance cannot be negative"):
            line.distance = -10
    
    def test_distance_validation_non_numeric(self):
        """Test distance validation for non-numeric values"""
        line = SingleLine()
        with pytest.raises(ValueError, match="Distance must be a number"):
            line.distance = "invalid"
    
    # Export snap line test
    def test_export_snap_line(self):
        """Test exporting snap line to a file"""
        line = SingleLine(x=10, y=20, length=100)
        
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the snap line
            file_path = line.export_snap_line(directory=temp_dir)
            
            # Check that the file was created
            assert os.path.exists(file_path)
            
            # Check that the file has the expected name format
            assert "line_10_20_snap_line_export.json" in file_path
            
            # Check that the file contains the expected data
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert 'x_cord' in data
                assert data['x_cord'] == 10
                assert data['y_cord'] == 20
                assert data['length'] == 100
                assert data['orientation'] == "horizontal"
                assert data['alignment'] == "center"
