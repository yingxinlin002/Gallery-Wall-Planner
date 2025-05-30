from __future__ import annotations
from enum import Enum
from typing import Union, Optional, List
from .structures import get_id
from .base import db

class HorizontalAlignment(Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"

class VerticalAlignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    @classmethod
    def alignment_options(cls, orientation: Orientation) -> Union[List[HorizontalAlignment], List[VerticalAlignment]]:
        if orientation == Orientation.HORIZONTAL:
            return [HorizontalAlignment.TOP, HorizontalAlignment.CENTER, HorizontalAlignment.BOTTOM]
        elif orientation == Orientation.VERTICAL:
            return [VerticalAlignment.LEFT, VerticalAlignment.CENTER, VerticalAlignment.RIGHT]
        return []

class SingleLine(db.Model):
    __tablename__ = 'single_lines'
    
    id = db.Column(db.String(32), primary_key=True)
    x_cord = db.Column(db.Float, nullable=False, default=0.0)
    y_cord = db.Column(db.Float, nullable=False, default=0.0)
    length = db.Column(db.Float, nullable=False, default=0.0)
    angle = db.Column(db.Float, nullable=False, default=0.0)
    snap_to = db.Column(db.Boolean, nullable=False, default=True)
    moveable = db.Column(db.Boolean, nullable=False, default=True)
    orientation = db.Column(db.Enum(Orientation), nullable=False)
    alignment = db.Column(db.String(20), nullable=False)  # Stores either Horizontal or Vertical alignment
    distance = db.Column(db.Float, nullable=False, default=0.0)
    wall_id = db.Column(db.Integer, db.ForeignKey('wall.id'))

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        length: float = 0,
        angle: float = 0,
        snap_to: bool = True,
        moveable: bool = True,
        orientation: Orientation = Orientation.HORIZONTAL,
        alignment: Union[HorizontalAlignment, VerticalAlignment] = HorizontalAlignment.CENTER,
        distance: float = 0.0,
        wall_id: Optional[int] = None
    ):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
        self.orientation = orientation
        self.alignment = alignment.value  # Store enum value
        self.distance = distance
        self.wall_id = wall_id
        self.id = get_id(f"line_x{self.x_cord}_y{self.y_cord}_len{self.length}_ang{self.angle}")

    def __str__(self):
        return f"Line {self.orientation.value} {self.distance}"

    @property
    def alignment_enum(self) -> Union[HorizontalAlignment, VerticalAlignment]:
        """Get the alignment as the appropriate enum type"""
        if self.orientation == Orientation.HORIZONTAL:
            return HorizontalAlignment(self.alignment)
        return VerticalAlignment(self.alignment)

    @alignment_enum.setter
    def alignment_enum(self, value: Union[HorizontalAlignment, VerticalAlignment]):
        """Set the alignment from enum"""
        if isinstance(value, (HorizontalAlignment, VerticalAlignment)):
            self.alignment = value.value

    def approximate_equal(self, other: SingleLine) -> bool:
        """Check if two SingleLine objects are approximately equal"""
        return (self.orientation == other.orientation and 
                self.alignment == other.alignment and 
                abs(self.distance - other.distance) < 0.001)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'x_cord': self.x_cord,
            'y_cord': self.y_cord,
            'length': self.length,
            'angle': self.angle,
            'snap_to': self.snap_to,
            'moveable': self.moveable,
            'orientation': self.orientation.value,
            'alignment': self.alignment,
            'distance': self.distance,
            'wall_id': self.wall_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> SingleLine:
        """Create from dictionary"""
        orientation = Orientation(data.get("orientation", "horizontal"))
        
        # Determine the alignment enum type based on orientation
        alignment_str = data.get("alignment", "center")
        if orientation == Orientation.HORIZONTAL:
            alignment = HorizontalAlignment(alignment_str)
        else:
            alignment = VerticalAlignment(alignment_str)
    
        return cls(
            x=data.get("x_cord", 0),
            y=data.get("y_cord", 0),
            length=data.get("length", 0),
            angle=data.get("angle", 0),
            snap_to=data.get("snap_to", True),
            moveable=data.get("moveable", True),
            orientation=orientation,
            alignment=alignment,
            distance=data.get("distance", 0.0),
            wall_id=data.get("wall_id")
        )