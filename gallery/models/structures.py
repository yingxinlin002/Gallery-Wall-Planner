from enum import Enum
from typing import Optional
from .base import db

def get_id(input: str) -> str:
    """Generate a simple hash from the input string.
    
    Args:
        input: String to hash
        
    Returns:
        A simple hash string
    """
    hash_value = sum(ord(c) * (i + 1) for i, c in enumerate(input))
    return f"{hash_value:x}"[-8:].zfill(8)

class MeasureFrom(Enum):
    EDGES = "edges"
    CENTER = "center"

class MeasureHorizontal(Enum):
    LEFT = "left"
    RIGHT = "right"

class MeasureVertical(Enum):
    TOP = "top"
    BOTTOM = "bottom"

class Padding(db.Model):
    __tablename__ = 'paddings'
    
    id = db.Column(db.Integer, primary_key=True)
    top = db.Column(db.Integer, nullable=False, default=0)
    right = db.Column(db.Integer, nullable=False, default=0)
    bottom = db.Column(db.Integer, nullable=False, default=0)
    left = db.Column(db.Integer, nullable=False, default=0)
    
    def __init__(self, top: int = 0, right: int = 0, bottom: int = 0, left: int = 0):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        
    def to_dict(self) -> dict:
        return {
            'top': self.top,
            'right': self.right,
            'bottom': self.bottom,
            'left': self.left
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Padding':
        return cls(
            top=data.get('top', 0),
            right=data.get('right', 0),
            bottom=data.get('bottom', 0),
            left=data.get('left', 0)
        )

class CanvasDimensions(db.Model):
    __tablename__ = 'canvas_dimensions'
    
    id = db.Column(db.Integer, primary_key=True)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    margin = db.Column(db.Integer, default=50)
    padding_id = db.Column(db.Integer, db.ForeignKey('paddings.id'))
    padding = db.relationship('Padding', uselist=False)
    
    def __init__(self, width: int, height: int, margin: int = 50, padding: Optional[Padding] = None):
        self.width = width
        self.height = height
        self.margin = margin
        self.padding = padding if padding else Padding()
        
    def to_dict(self) -> dict:
        return {
            'width': self.width,
            'height': self.height,
            'margin': self.margin,
            'padding': self.padding.to_dict() if self.padding else None
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'CanvasDimensions':
        padding_data = data.get('padding')
        padding = Padding.from_dict(padding_data) if padding_data else None
        return cls(
            width=data['width'],
            height=data['height'],
            margin=data.get('margin', 50),
            padding=padding
        )

class WallPosition(db.Model):
    __tablename__ = 'wall_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    wall_left = db.Column(db.Float, nullable=False)
    wall_top = db.Column(db.Float, nullable=False)
    wall_right = db.Column(db.Float, nullable=False)
    wall_bottom = db.Column(db.Float, nullable=False)
    
    def __init__(self, wall_left: float, wall_top: float, wall_right: float, wall_bottom: float):
        self.wall_left = wall_left
        self.wall_top = wall_top
        self.wall_right = wall_right
        self.wall_bottom = wall_bottom
        
    @property
    def width(self) -> float:
        return self.wall_right - self.wall_left
        
    @property
    def height(self) -> float:
        return self.wall_bottom - self.wall_top
        
    def to_dict(self) -> dict:
        return {
            'wall_left': self.wall_left,
            'wall_top': self.wall_top,
            'wall_right': self.wall_right,
            'wall_bottom': self.wall_bottom
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'WallPosition':
        return cls(
            wall_left=data['wall_left'],
            wall_top=data['wall_top'],
            wall_right=data['wall_right'],
            wall_bottom=data['wall_bottom']
        )

class Position(db.Model):
    __tablename__ = 'positions'
    
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
        
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
        
    def to_dict(self) -> dict:
        return {'x': self.x, 'y': self.y}
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        return cls(x=data['x'], y=data['y'])