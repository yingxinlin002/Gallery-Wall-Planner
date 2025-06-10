from .base import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    sub = db.Column(db.String(255), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_guest = db.Column(db.Boolean, default=False)  # New field to identify guests
    session_id = db.Column(db.String(36))  # For guest sessions
    
    artworks = db.relationship('Artwork', back_populates='user', lazy=True)
    galleries = db.relationship('Gallery', back_populates='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email or self.sub}>"