from typing import Optional
from .structures import Position
from .base import db

class WallObject(db.Model):
    """
    Base class for objects that can be placed on a wall (artwork, permanent objects)
    This class contains common properties and methods shared between Artwork and PermanentObject classes.
    """
    __tablename__ = 'wall_objects'
    __abstract__ = True  # This makes it a base class for inheritance
    
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(256))
    x_position = db.Column(db.Float, default=0.0)  # X coordinate on wall
    y_position = db.Column(db.Float, default=0.0)  # Y coordinate on wall
    
    def __init__(self, name: str, width: float, height: float, image_path: Optional[str] = None):
        """
        Initialize a wall object with basic properties
        
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
        self.id = self._get_id()
    
    def _get_id(self) -> str:
        """Generate a unique ID for this object"""
        from .structures import get_id
        return get_id(f"wall_obj_{self.name}_width{self.width}_height{self.height}")

    @property
    def position(self) -> Position:
        """Get the object's current position as a Position object"""
        return Position(self.x_position, self.y_position)
    
    @position.setter
    def position(self, value: Position):
        """Set the object's position from a Position object"""
        if not isinstance(value, Position):
            raise ValueError("Position must be a Position object")
        self.x_position = value.x
        self.y_position = value.y

    def get_bounds(self) -> tuple:
        """
        Returns the object's bounding coordinates (x1, y1, x2, y2)
        
        Returns:
            tuple: (left, bottom, right, top) coordinates in inches
        """
        return (
            self.x_position,
            self.y_position,
            self.x_position + self.width,
            self.y_position + self.height
        )
    
    def overlaps_with(self, other: 'WallObject') -> bool:
        """
        Check if this wall object overlaps with another wall object
        
        Args:
            other (WallObject): Another wall object to check for overlap
            
        Returns:
            bool: True if the objects overlap, False otherwise
        """
        # Get bounds of both objects
        ax1, ay1, ax2, ay2 = self.get_bounds()
        bx1, by1, bx2, by2 = other.get_bounds()
        
        # Check for overlap
        return not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
    
    def to_dict(self) -> dict:
        """Convert object to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'image_path': self.image_path,
            'position': {'x': self.x_position, 'y': self.y_position}
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WallObject':
        """Create object from dictionary"""
        return cls(
            name=data['name'],
            width=float(data['width']),
            height=float(data['height']),
            image_path=data.get('image_path')
        )

    def __repr__(self):
        """String representation for debugging"""
        return (f"<{self.__class__.__name__} {self.name} "
                f"({self.width}x{self.height}) at "
                f"({self.x_position},{self.y_position})>")