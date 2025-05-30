from typing import Optional, Dict
from .wall_object import WallObject
from .base import db

class PermanentObject(WallObject):
    __tablename__ = 'permanent_object'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    x = db.Column(db.Float, default=0.0)
    y = db.Column(db.Float, default=0.0)
    image_path = db.Column(db.String(256))
    wall_id = db.Column(db.Integer, db.ForeignKey('wall.id'))

    def __init__(self, name: str, width: float, height: float, 
                 x: float = 0, y: float = 0, image_path: Optional[str] = None,
                 wall_id: Optional[int] = None):
        self.name = name
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.image_path = image_path
        self.wall_id = wall_id

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'x': self.x,
            'y': self.y,
            'image_path': self.image_path,
            'wall_id': self.wall_id
        }

    def __repr__(self):
        return f"<PermanentObject {self.name} ({self.width}x{self.height})>"