from typing import Optional
from gallery_wall_planner.models.structures import Position
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.structures import get_id

class PermanentObject(WallObject):
    """
    Represents a permanent object on a wall (e.g., door, window, switch)
    """
    def __init__(self, name: str = "", width: float = 0, height: float = 0, image_path: Optional[str] = None):
        """
        Initialize a permanent object with basic properties
        
        Args:
            name (str): Name/identifier of the object
            width (float): Width in inches
            height (float): Height in inches
            image_path (str, optional): Path to reference image. Defaults to None.
        """
        # Initialize the parent class
        super().__init__(name, width, height, image_path)
        self._id = get_id("perm_obj"+name+f"width{self.width},height{self.height}")
        
    # All properties are inherited from WallObject
    
    # get_bounds and __str__ are inherited from WallObject