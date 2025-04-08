from typing import Optional, Tuple

class PermanentObject:
    def __init__(self, name: str, width: float, height: float, image_path: Optional[str] = None):
        """
        Represents a permanent object on a wall (e.g., door, window, switch)
        
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
        
        # Set properties with validation
        self.name = name
        self.width = width
        self.height = height
        self.image_path = image_path
        self._position = None  # Will be managed by Wall class
        
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
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Width must be a positive number")
        self._width = float(value)
    
    @property
    def height(self) -> float:
        """Get the object's height"""
        return self._height
    
    @height.setter
    def height(self, value: float):
        """Set the object's height with validation"""
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Height must be a positive number")
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
    def position(self):
        """Get the object's current position (x,y coordinates)"""
        return self._position
    
    @position.setter 
    def position(self, value):
        """Set the object's position (should only be called by Wall class)"""
        self._position = value
    
    def get_bounds(self):
        """
        Returns the object's bounding coordinates (x1, y1, x2, y2)
        
        Returns:
            tuple: (left, bottom, right, top) coordinates in inches
            None: If position hasn't been set
        """
        if not self._position:
            return None
        return (
            self._position['x'],
            self._position['y'],
            self._position['x'] + self.width,
            self._position['y'] + self.height
        )
    
    def __str__(self):
        """String representation for debugging"""
        pos_str = f"at ({self._position['x']}, {self._position['y']})" if self._position else "(unpositioned)"
        return f"PermanentObject: {self.name} ({self.width}\" x {self.height}\") {pos_str}"