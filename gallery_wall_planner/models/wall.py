from __future__ import annotations

import json
from typing import List, Dict, Tuple, Union, Optional, Any

# Use relative imports since we're within the gallery_wall_planner.models package
from .artwork import Artwork
from .permanentObject import PermanentObject
from .wall_line import SingleLine
from .structures import Position

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
        # Initialize private attributes
        self._name = None
        self._width = None
        self._height = None
        self._color = None
        self._artwork = []          # List of Artwork objects
        self._wall_lines = []       # List of decorative lines/markings
        self._permanent_objects: List[PermanentObject] = []  # List of PermanentObject instances
        
        # Set properties with validation
        self.name = name
        self.width = width
        self.height = height
        self.color = color
    
    @property
    def name(self) -> str:
        """Get the wall name"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the wall name with validation"""
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value
    
    @property
    def width(self) -> float:
        """Get the wall width"""
        return self._width
    
    @width.setter
    def width(self, value: float):
        """Set the wall width with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Width must be a number")
        if value <= 0:
            raise ValueError("Width must be positive")
        self._width = float(value)
    
    @property
    def height(self) -> float:
        """Get the wall height"""
        return self._height
    
    @height.setter
    def height(self, value: float):
        """Set the wall height with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Height must be a number")
        if value <= 0:
            raise ValueError("Height must be positive")
        self._height = float(value)
    
    @property
    def color(self) -> str:
        """Get the wall color"""
        return self._color
    
    @color.setter
    def color(self, value: str):
        """Set the wall color with validation"""
        if not isinstance(value, str):
            raise ValueError("Color must be a string")
        self._color = value
    
    @property
    def artwork(self) -> List[Artwork]:
        """Get the list of artwork objects"""
        return self._artwork
    
    @artwork.setter
    def artwork(self, value: List[Artwork]):
        """Set the artwork list with validation"""
        if not isinstance(value, list):
            raise ValueError("Artwork must be a list")
        # Validate that all items are Artwork objects
        for item in value:
            if not isinstance(item, Artwork):
                raise ValueError("All items in artwork list must be Artwork objects")
        self._artwork = value
    
    @property
    def wall_lines(self) -> List[SingleLine]:
        """Get the list of wall lines"""
        return self._wall_lines
    
    @wall_lines.setter
    def wall_lines(self, value: List[SingleLine]):
        """Set the wall lines list with validation"""
        if not isinstance(value, list):
            raise ValueError("Wall lines must be a list")
        # Validate that all items are SingleLine objects
        for item in value:
            if not isinstance(item, SingleLine):
                raise ValueError("All items in wall_lines list must be SingleLine objects")
        self._wall_lines = value
    
    @property
    def permanent_objects(self) -> List[PermanentObject]:
        """Get the list of permanent objects"""
        return self._permanent_objects
    
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
            
        obj.position = Position(x, y)
        self._permanent_objects.append(obj)
        return True
    
    def remove_permanent_object(self, obj: PermanentObject) -> bool:
        """
        Remove a permanent object from the wall
        
        Args:
            obj (PermanentObject): Object instance to remove
            
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
    
    # def get_permanent_objects(self) -> List[Tuple[PermanentObject, Dict[str, float]]]:
    #     """
    #     Get all permanent objects with their positions
        
    #     Returns:
    #         list: Tuples of (PermanentObject, position_dict)
    #     """
    #     return [(obj, obj.position) for obj in self._permanent_objects]
    
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

    def export_to_excel(self, filename: str) -> None:
        """
        Inputs: A wall object and a filename
        Process: Exports all wall and artwork data to excel
        Outputs: An excel sheet with specific wall data and artwork data attached to the wall
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.name
    
        headers = ["Wall Name", "Width", "Height", "Color"]
        ws.append(headers)
        ws.append([self.name, self.width, self.height, self.color])
    
        ws.append([])
        ws.append(["Artwork"])  # Section label
    
        if self.artwork:
            from .artwork import export_to_excel as export_artworks_to_worksheet # Rename imported method to avoid potential naming conflicts
            export_artworks_to_worksheet(ws, self.artwork, start_row=ws.max_row + 1) # Use artwork export method to export full artwork data to wall sheet
    
        wb.save(filename)

    @classmethod
    def import_from_excel(cls, filename: str) -> Wall:
        """
        Inputs: A filename to import from
        Process: Import all wall data and artwork data attached to wall
        Outputs: A wall object containing all relevant artwork, data and metadata
        """
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
    
        name = ws["B2"].value
        width = float(ws["C2"].value)
        height = float(ws["D2"].value)
        color = ws["E2"].value if ws["E2"].value else "White"
    
        wall = cls(name, width, height, color)
    
        for row in ws.iter_rows(min_row=6):
            if row[0].value in (None, "Name"):
                continue
            from .artwork import import_from_excel as import_artwork_from_row # Rename imported metjod to avoid potential naming conflicts 
            artwork = import_artwork_from_row(row, ws.parent) # Use artwork import method to import full artwork data from wall sheet
            if artwork:
                wall.add_artwork(artwork)
    
        return wall
    

    
    def export_wall(self) -> Dict[str, Any]: # I assume we no longer needs these, but have not deleted them as I didn't want to break anyone else's code, please let me know and we can then delete them
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
        
        from gallery_wall_planner.models.permanentObject import PermanentObject
        from gallery_wall_planner.models.structures import Position
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
