from typing import Optional
from gallery_wall_planner.models.structures import Position
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.models.structures import get_id
from typing import override

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
        
    def to_dict(self):
    # Helper for exporter.py export
        return {
            "name": self.name,
            "image_path": self.image_path,
            "position": self.position,
            "width": self.width,
            "height": self.height
            # Add any other relevant attributes here
        }

    @staticmethod
    def from_dict(data):
        # Helper for exporter.py import
        return PermanentObject(
            # position = data.get("position", (0,0)), So I don't actually know how we initialize this attribute, so for now I'll disable it. 
            width=data.get("width", 0),
            height=data.get("height", 0),
            name=data.get("name", ""),
            image_path = data.get("image_path", None)
        )

    @override
    def _get_id(self):
        return get_id("perm_obj"+self.name+f"width{self.width},height{self.height}")
        
