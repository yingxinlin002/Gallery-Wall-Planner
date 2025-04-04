class PermanentObject:
    def __init__(self, name, width, height, image_path=None):
        """
        Represents a permanent object on a wall (e.g., door, window, switch)
        
        Args:
            name (str): Name/identifier of the object
            width (float): Width in inches
            height (float): Height in inches
            image_path (str, optional): Path to reference image. Defaults to None.
        """
        self.name = name
        self.width = width
        self.height = height
        self.image_path = image_path
        self._position = None  # Will be managed by Wall class
        
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