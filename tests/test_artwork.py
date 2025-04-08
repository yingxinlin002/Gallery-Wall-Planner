import os
import json
import pytest
import tempfile
from gallery_wall_planner.models.artwork import Artwork

class TestArtwork:
    """Test suite for the Artwork class"""
    
    def test_init_with_defaults(self):
        """Test initialization with default values"""
        artwork = Artwork()
        assert artwork.name == ""
        assert artwork.medium == ""
        assert artwork.height == 0
        assert artwork.width == 0
        assert artwork.depth == 0
        assert artwork.hanging_point == 0
        assert artwork.price == 0
        assert artwork.nfs is False
        assert artwork.image_path == ""
        assert artwork.notes == ""
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values"""
        artwork = Artwork(
            name="Test Artwork",
            medium="Oil on Canvas",
            height=24,
            width=36,
            depth=1.5,
            hanging_point=12,
            price=1000,
            nfs=True,
            image_path="/path/to/image.jpg",
            notes="This is a test artwork"
        )
        assert artwork.name == "Test Artwork"
        assert artwork.medium == "Oil on Canvas"
        assert artwork.height == 24
        assert artwork.width == 36
        assert artwork.depth == 1.5
        assert artwork.hanging_point == 12
        assert artwork.price == 1000
        assert artwork.nfs is True
        assert artwork.image_path == "/path/to/image.jpg"
        assert artwork.notes == "This is a test artwork"
    
    # Name validation tests
    def test_name_validation_non_string(self):
        """Test name validation for non-string values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Name must be a string"):
            artwork.name = 123
    
    # Medium validation tests
    def test_medium_validation_non_string(self):
        """Test medium validation for non-string values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Medium must be a string"):
            artwork.medium = 123
    
    # Height validation tests
    def test_height_validation_negative(self):
        """Test height validation for negative values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Height cannot be negative"):
            artwork.height = -10
    
    def test_height_validation_non_numeric(self):
        """Test height validation for non-numeric values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Height must be a number"):
            artwork.height = "invalid"
    
    # Width validation tests
    def test_width_validation_negative(self):
        """Test width validation for negative values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Width cannot be negative"):
            artwork.width = -10
    
    def test_width_validation_non_numeric(self):
        """Test width validation for non-numeric values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Width must be a number"):
            artwork.width = "invalid"
    
    # Depth validation tests
    def test_depth_validation_negative(self):
        """Test depth validation for negative values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Depth cannot be negative"):
            artwork.depth = -10
    
    def test_depth_validation_non_numeric(self):
        """Test depth validation for non-numeric values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Depth must be a number"):
            artwork.depth = "invalid"
    
    # Hanging point validation tests
    def test_hanging_point_validation_negative(self):
        """Test hanging point validation for negative values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Hanging point cannot be negative"):
            artwork.hanging_point = -10
    
    def test_hanging_point_validation_non_numeric(self):
        """Test hanging point validation for non-numeric values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Hanging point must be a number"):
            artwork.hanging_point = "invalid"
    
    # Price validation tests
    def test_price_validation_negative(self):
        """Test price validation for negative values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Price cannot be negative"):
            artwork.price = -10
    
    def test_price_validation_non_numeric(self):
        """Test price validation for non-numeric values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Price must be a number"):
            artwork.price = "invalid"
    
    # NFS validation tests
    def test_nfs_validation_non_boolean(self):
        """Test nfs validation for non-boolean values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="NFS must be a boolean"):
            artwork.nfs = "invalid"
    
    # Image path validation tests
    def test_image_path_validation_non_string(self):
        """Test image path validation for non-string values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Image path must be a string"):
            artwork.image_path = 123
    
    # Notes validation tests
    def test_notes_validation_non_string(self):
        """Test notes validation for non-string values"""
        artwork = Artwork()
        with pytest.raises(ValueError, match="Notes must be a string"):
            artwork.notes = 123
    
    # String representation test
    def test_str_representation(self):
        """Test the string representation of the artwork"""
        artwork = Artwork(name="Test Artwork", width=36, height=24)
        str_rep = str(artwork)
        
        # The string representation should contain the name and dimensions
        assert "Test Artwork" in str_rep
        assert "36" in str_rep
        assert "24" in str_rep
    
    # Export artwork test
    def test_export_artwork(self):
        """Test exporting artwork to a file"""
        artwork = Artwork(name="Test Artwork", medium="Oil on Canvas")
        
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the artwork
            file_path = artwork.export_artwork(directory=temp_dir)
            
            # Check that the file was created
            assert os.path.exists(file_path)
            
            # Check that the file has the expected name format
            assert "Test_Artwork_artwork_export.json" in file_path
            
            # Check that the file contains the expected data
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert "_name" in data
                assert data["_name"] == "Test Artwork"
                assert data["_medium"] == "Oil on Canvas"
    
    def test_export_artwork_special_chars(self):
        """Test exporting artwork with special characters in the name"""
        artwork = Artwork(name="Test: Artwork! With @#$% Special & Characters")
        
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the artwork
            file_path = artwork.export_artwork(directory=temp_dir)
            
            # Check that the file was created
            assert os.path.exists(file_path)
            
            # Check that the file has the expected sanitized name
            assert "Test_Artwork_With_Special_Characters_artwork_export.json" in file_path
    
    def test_export_artwork_empty_name(self):
        """Test exporting artwork with an empty name"""
        artwork = Artwork(name="")
        
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export the artwork
            file_path = artwork.export_artwork(directory=temp_dir)
            
            # Check that the file was created
            assert os.path.exists(file_path)
            
            # Check that the file has the fallback name
            assert "artwork_artwork_export.json" in file_path
