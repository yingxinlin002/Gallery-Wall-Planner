import json
import re
import os
from types import SimpleNamespace
from typing import Optional

class Artwork:
    def __init__(self, name: str = "", medium: str = "", height: float = 0, width: float = 0, depth: float = 0, hanging_point: float = 0, price: float = 0, nfs: bool = False, image_path: str = "", notes: str = ""):
        # Initialize private attributes
        self._name = None
        self._medium = None
        self._height = None
        self._width = None
        self._depth = None
        self._hanging_point = None
        self._price = None
        self._nfs = None
        self._image_path = None
        self._notes = None
        
        # Set properties with validation
        self.name = name
        self.medium = medium
        self.height = height
        self.width = width
        self.depth = depth
        self.hanging_point = hanging_point
        self.price = price
        self.nfs = nfs
        self.image_path = image_path
        self.notes = notes
        
    @property
    def name(self) -> str:
        """Get the artwork's name"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set the artwork's name with validation"""
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        self._name = value
    
    @property
    def medium(self) -> str:
        """Get the artwork's medium"""
        return self._medium
    
    @medium.setter
    def medium(self, value: str):
        """Set the artwork's medium with validation"""
        if not isinstance(value, str):
            raise ValueError("Medium must be a string")
        self._medium = value
    
    @property
    def height(self) -> float:
        """Get the artwork's height"""
        return self._height
    
    @height.setter
    def height(self, value: float):
        """Set the artwork's height with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Height must be a number")
        if value < 0:
            raise ValueError("Height cannot be negative")
        self._height = float(value)
    
    @property
    def width(self) -> float:
        """Get the artwork's width"""
        return self._width
    
    @width.setter
    def width(self, value: float):
        """Set the artwork's width with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Width must be a number")
        if value < 0:
            raise ValueError("Width cannot be negative")
        self._width = float(value)
    
    @property
    def depth(self) -> float:
        """Get the artwork's depth"""
        return self._depth
    
    @depth.setter
    def depth(self, value: float):
        """Set the artwork's depth with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Depth must be a number")
        if value < 0:
            raise ValueError("Depth cannot be negative")
        self._depth = float(value)
    
    @property
    def hanging_point(self) -> float:
        """Get the artwork's hanging point"""
        return self._hanging_point
    
    @hanging_point.setter
    def hanging_point(self, value: float):
        """Set the artwork's hanging point with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Hanging point must be a number")
        if value < 0:
            raise ValueError("Hanging point cannot be negative")
        self._hanging_point = float(value)
    
    @property
    def price(self) -> float:
        """Get the artwork's price"""
        return self._price
    
    @price.setter
    def price(self, value: float):
        """Set the artwork's price with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Price must be a number")
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = float(value)
    
    @property
    def nfs(self) -> bool:
        """Get the artwork's not-for-sale status"""
        return self._nfs
    
    @nfs.setter
    def nfs(self, value: bool):
        """Set the artwork's not-for-sale status with validation"""
        if not isinstance(value, bool):
            raise ValueError("NFS must be a boolean")
        self._nfs = value
    
    @property
    def image_path(self) -> str:
        """Get the artwork's image path"""
        return self._image_path
    
    @image_path.setter
    def image_path(self, value: str):
        """Set the artwork's image path with validation"""
        if not isinstance(value, str):
            raise ValueError("Image path must be a string")
        self._image_path = value
    
    @property
    def notes(self) -> str:
        """Get the artwork's notes"""
        return self._notes
    
    @notes.setter
    def notes(self, value: str):
        """Set the artwork's notes with validation"""
        if not isinstance(value, str):
            raise ValueError("Notes must be a string")
        self._notes = value

    def __str__(self):
        #return all info about the artwork
        return f"Name: {self.name}\nMedium: {self.medium}\nHeight: {self.height}\nWidth: {self.width}\nDepth: {self.depth}\nHanging Point: {self.hanging_point}\nPrice: {self.price}\nNFS: {self.nfs}\nImage Path: {self.image_path}\nNotes: {self.notes}"
    
    def export_artwork(self, directory: str = "") -> str:
        """Export artwork to a JSON file
        
        Args:
            directory (str, optional): Directory to save the file. Defaults to current directory.
        """
        # Preprocess name to make it a valid filename
        # Replace spaces and special characters with underscores
        safe_name = re.sub(r'[^\w\-\.]', '_', self.name)
        # Remove multiple consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        # Default to 'artwork' if name is empty after processing
        if not safe_name:
            safe_name = "artwork"
            
        # Create the full file path
        file_path = os.path.join(directory, f"{safe_name}_artwork_export.json")
        
        # Export to JSON
        with open(file_path, "w") as f:
            f.write(json.dumps(self.__dict__))
            
        return file_path

def import_artwork(art_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    art_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
            
