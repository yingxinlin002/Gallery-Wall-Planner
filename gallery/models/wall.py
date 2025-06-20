from __future__ import annotations
from typing import List, Dict, Optional
from .base import db

class Wall(db.Model):
    __tablename__ = 'wall'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    exhibit_id = db.Column(db.Integer, db.ForeignKey('exhibits.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    color = db.Column(db.String(32))
    
    # Relationships
    permanent_objects = db.relationship('PermanentObject', backref='wall', lazy=True, cascade='all, delete-orphan')
    artworks = db.relationship('Artwork', backref='wall', lazy=True, cascade='all, delete-orphan')
    snap_lines = db.relationship('SingleLine', backref='wall', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, name: str, width: float, height: float, color: str = "White", exhibit_id: Optional[int] = None):
        self.name = name
        self.width = width
        self.height = height
        self.color = color
        self.exhibit_id = exhibit_id

    def add_permanent_object(self, name: str, width: float, height: float, 
                           x: float = 0, y: float = 0, image_path: Optional[str] = None):
        from .permanent_object import PermanentObject
        obj = PermanentObject(
            name=name,
            width=width,
            height=height,
            x=x,
            y=y,
            image_path=image_path,
            wall_id=self.id
        )
        db.session.add(obj)
        return obj

    def get_permanent_objects(self) -> List[Dict]:
        return [{
            'id': obj.id,
            'name': obj.name,
            'width': obj.width,
            'height': obj.height,
            'x': obj.x,
            'y': obj.y,
            'image_path': obj.image_path
        } for obj in self.permanent_objects]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "color": self.color,
        }

    def __repr__(self):
        return f"<Wall {self.name} ({self.width}x{self.height})>"