from __future__ import annotations

import json
from typing import List, Dict, Tuple, Union, Optional, Any

# Use relative imports since we're within the gallery_wall_planner.models package
from .artwork import Artwork
from .permanentObject import PermanentObject
from .wall_line import WallLine

class Wall:
    def __init__(self, name: str, width: float, height: float, color: str = "White"):
        """
        Represents a wall with artwork and permanent objects
        
        Args:
            name (str): Wall identifier
            width (float): Width in inches
            height (float): Height in inches
            color (str, optional): Wall color. Defaults to "White".
        """
        self.name = name
        self.width = width
        self.height = height
        self.color = color
        self.artwork = []          # List of Artwork objects
        self.wall_lines = []       # List of decorative lines/markings
        self._permanent_objects = []  # List of PermanentObject instances
    
    def add_permanent_object(self, obj: PermanentObject, x: Optional[float] = None, y: Optional[float] = None) -> bool:
        """
        Add a permanent object to the wall with optional position
        
        Args:
            obj (PermanentObject): The object to add
            x (float, optional): Left position in inches. Defaults to centered.
            y (float, optional): Bottom position in inches. Defaults to 12" from bottom.
        
        Returns:
            bool: True if added successfully
        """
        if not isinstance(obj, PermanentObject):
            raise ValueError("Can only add PermanentObject instances")
            
        # Set default position if not specified
        if x is None:
            x = self.width/2 - obj.width/2  # Center horizontally
        if y is None:
            y = self.height - obj.height - 12  # 12" from bottom
            
        # Validate position
        if x < 0 or (x + obj.width) > self.width:
            raise ValueError("Object would extend beyond wall width")
        if y < 0 or (y + obj.height) > self.height:
            raise ValueError("Object would extend beyond wall height")
            
        obj.position = {'x': x, 'y': y}
        self._permanent_objects.append(obj)
        return True
    
    def remove_permanent_object(self, obj: Union[PermanentObject, str]) -> bool:
        """
        Remove a permanent object from the wall
        
        Args:
            obj (PermanentObject or str): Object instance or name to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if isinstance(obj, str):
            # Find by name
            for permanent_obj in self._permanent_objects:
                if permanent_obj.name == obj:
                    self._permanent_objects.remove(permanent_obj)
                    return True
            return False
        else:
            if obj in self._permanent_objects:
                self._permanent_objects.remove(obj)
                return True
            return False
    
    def get_permanent_objects(self) -> List[Tuple[PermanentObject, Dict[str, float]]]:
        """
        Get all permanent objects with their positions
        
        Returns:
            list: Tuples of (PermanentObject, position_dict)
        """
        return [(obj, obj.position) for obj in self._permanent_objects]
    
    def get_permanent_object_by_name(self, name: str) -> Optional[PermanentObject]:
        """
        Find a permanent object by name
        
        Args:
            name (str): Object name to find
            
        Returns:
            PermanentObject: Found object or None
        """
        for obj in self._permanent_objects:
            if obj.name == name:
                return obj
        return None
    
    # Existing artwork methods (unchanged)
    def add_artwork(self, artwork: Artwork) -> None:
        """Add artwork to the wall"""
        self.artwork.append(artwork)
    
    def remove_artwork(self, artwork: Artwork) -> bool:
        """Remove artwork from the wall"""
        if artwork in self.artwork:
            self.artwork.remove(artwork)
            return True
        return False
    
    def get_artwork_by_name(self, name: str) -> Optional[Artwork]:
        """Find artwork by name"""
        for art in self.artwork:
            if art.name == name:
                return art
        return None
    
    def export_wall(self) -> Dict[str, Any]:
        """
        Export wall data to JSON format
        
        Returns:
            dict: Contains all wall data including artwork and permanent objects
        """
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'color': self.color,
            'artwork': [art.__dict__ for art in self.artwork],
            'wall_lines': self.wall_lines,
            'permanent_objects': [
                {
                    'name': obj.name,
                    'width': obj.width,
                    'height': obj.height,
                    'image_path': obj.image_path,
                    'position': obj.position
                }
                for obj in self._permanent_objects
            ]
        }
    
    def save_to_file(self, filename: str) -> None:
        """Save wall data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.export_wall(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> Wall:
        """Load wall data from JSON file"""
        with open(filename) as f:
            data = json.load(f)
        
        wall = cls(data['name'], data['width'], data['height'], data['color'])
        wall.wall_lines = data.get('wall_lines', [])
        
        # Recreate permanent objects
        for obj_data in data.get('permanent_objects', []):
            obj = PermanentObject(
                obj_data['name'],
                obj_data['width'],
                obj_data['height'],
                obj_data.get('image_path')
            )
            wall.add_permanent_object(obj, obj_data['position']['x'], obj_data['position']['y'])
        
        # Note: Artwork recreation would need similar handling
        # but requires your Artwork class implementation
        
        return wall
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return (f"Wall(Name: {self.name}, Size: {self.width}\" x {self.height}\", "
                f"Color: {self.color}, Artwork: {len(self.artwork)} items, "
                f"Permanent Objects: {len(self._permanent_objects)} items)")