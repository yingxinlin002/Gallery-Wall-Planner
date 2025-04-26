from typing import Optional
from gallery_wall_planner.models.structures import Position

class WallObject:
    """
    Base class for objects that can be placed on a wall (artwork, permanent objects)
    
    This class contains common properties and methods shared between Artwork and PermanentObject classes.
    """
    def __init__(self, name: str, width: float, height: float, image_path: Optional[str] = None):
        """
        Initialize a wall object with basic properties
        
        Args:
            name (str): Name/identifier of the object
            width (float): Width in inches
            height (float): Height in inches
            image_path (str, optional): Path to reference image. Defaults to None.
        """
        self._name = None
        self._width = None
        self._height = None
        self._image_path = None
        self._position = Position(0, 0)  # Default position
        
        # Set properties with validation
        self.name = name
        self.width = width
        self.height = height
        self.image_path = image_path
        self._id : str = ""
    
    @property
    def name(self) -> str:
        """Get the object's name"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the object's name with validation"""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name must be a non-empty string")
        self._name = value
    
    @property
    def width(self) -> float:
        """Get the object's width"""
        return self._width
    
    @width.setter
    def width(self, value: float):
        """Set the object's width with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Width must be a number")
        if value <= 0:
            raise ValueError("Width must be positive")
        self._width = float(value)
    
    @property
    def height(self) -> float:
        """Get the object's height"""
        return self._height
    
    @height.setter
    def height(self, value: float):
        """Set the object's height with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Height must be a number")
        if value <= 0:
            raise ValueError("Height must be positive")
        self._height = float(value)
    
    @property
    def image_path(self) -> Optional[str]:
        """Get the object's image path"""
        return self._image_path
    
    @image_path.setter
    def image_path(self, value: Optional[str]):
        """Set the object's image path with validation"""
        if value is not None and not isinstance(value, str):
            raise ValueError("Image path must be a string or None")
        self._image_path = value
    
    @property
    def position(self) -> Position:
        """Get the object's current position"""
        return self._position
    
    @position.setter
    def position(self, value: Position):
        """Set the object's position"""
        self._position = value

    @property
    def id(self) -> str:
        """Get the object's unique identifier"""
        return self._id
    
    def get_bounds(self):
        """
        Returns the object's bounding coordinates (x1, y1, x2, y2)
        
        Returns:
            tuple: (left, bottom, right, top) coordinates in inches
        """
        return (
            self.position.x,
            self.position.y,
            self.position.x + self.width,
            self.position.y + self.height
        )
    
    def __str__(self):
        """String representation for debugging"""
        pos_str = f"at ({self.position.x}, {self.position.y})"
        return f"{self.__class__.__name__}: {self.name} ({self.width}\" x {self.height}\") {pos_str}"
