import json
import os
from types import SimpleNamespace
from enum import Enum, auto
from typing import Union

class WallLine:
    def __init__(self, x=0, y=0, length=0, angle=0, snap_to=False, moveable=True):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable

    def export_wall_line(self):
        #Temp way to export object to json, can be refined later
        with open(f"{self}wall_line_export", "wb") as f:
            f.write(json.dumps(self.__dict__))


class LineOrientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class LineAlignment(Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class SingleLine:
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        length: float = 0,
        angle: float = 0,
        snap_to: bool = True,
        moveable: bool = True,
        orientation: Union[LineOrientation, str] = LineOrientation.HORIZONTAL,
        alignment: Union[LineAlignment, str] = LineAlignment.CENTER,
        distance: float = 0.0               # Distance from wall edge (in inches)
    ):
        # Initialize private attributes
        self._x_cord = None
        self._y_cord = None
        self._length = None
        self._angle = None
        self._snap_to = None
        self._moveable = None
        self._orientation = None
        self._alignment = None
        self._distance = None
        
        # Set properties with validation
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
        self.orientation = orientation
        self.alignment = alignment
        self.distance = distance
        
    @property
    def x_cord(self) -> float:
        """Get the x-coordinate of the line"""
        return self._x_cord
    
    @x_cord.setter
    def x_cord(self, value: float):
        """Set the x-coordinate of the line with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("X-coordinate must be a number")
        self._x_cord = float(value)
    
    @property
    def y_cord(self) -> float:
        """Get the y-coordinate of the line"""
        return self._y_cord
    
    @y_cord.setter
    def y_cord(self, value: float):
        """Set the y-coordinate of the line with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Y-coordinate must be a number")
        self._y_cord = float(value)
    
    @property
    def length(self) -> float:
        """Get the length of the line"""
        return self._length
    
    @length.setter
    def length(self, value: float):
        """Set the length of the line with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Length must be a number")
        if value < 0:
            raise ValueError("Length cannot be negative")
        self._length = float(value)
    
    @property
    def angle(self) -> float:
        """Get the angle of the line"""
        return self._angle
    
    @angle.setter
    def angle(self, value: float):
        """Set the angle of the line with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Angle must be a number")
        # Normalize angle to be between 0 and 360
        self._angle = float(value) % 360
    
    @property
    def snap_to(self) -> bool:
        """Get the snap_to property of the line"""
        return self._snap_to
    
    @snap_to.setter
    def snap_to(self, value: bool):
        """Set the snap_to property of the line with validation"""
        if not isinstance(value, bool):
            raise ValueError("Snap-to must be a boolean")
        self._snap_to = value
    
    @property
    def moveable(self) -> bool:
        """Get the moveable property of the line"""
        return self._moveable
    
    @moveable.setter
    def moveable(self, value: bool):
        """Set the moveable property of the line with validation"""
        if not isinstance(value, bool):
            raise ValueError("Moveable must be a boolean")
        self._moveable = value
    
    @property
    def orientation(self) -> LineOrientation:
        """Get the orientation of the line"""
        return self._orientation
    
    @orientation.setter
    def orientation(self, value: Union[LineOrientation, str]):
        """Set the orientation of the line with validation"""
        if isinstance(value, LineOrientation):
            self._orientation = value
        elif isinstance(value, str):
            try:
                self._orientation = LineOrientation(value)
            except ValueError:
                raise ValueError(f"Invalid orientation value: {value}. Must be one of {[o.value for o in LineOrientation]}")
        else:
            raise ValueError("Orientation must be a LineOrientation enum or a valid string value")
    
    @property
    def alignment(self) -> LineAlignment:
        """Get the alignment of the line"""
        return self._alignment
    
    @alignment.setter
    def alignment(self, value: Union[LineAlignment, str]):
        """Set the alignment of the line with validation"""
        if isinstance(value, LineAlignment):
            self._alignment = value
        elif isinstance(value, str):
            try:
                self._alignment = LineAlignment(value)
            except ValueError:
                raise ValueError(f"Invalid alignment value: {value}. Must be one of {[a.value for a in LineAlignment]}")
        else:
            raise ValueError("Alignment must be a LineAlignment enum or a valid string value")
    
    @property
    def distance(self) -> float:
        """Get the distance of the line from the wall edge"""
        return self._distance
    
    @distance.setter
    def distance(self, value: float):
        """Set the distance of the line from the wall edge with validation"""
        if not isinstance(value, (int, float)):
            raise ValueError("Distance must be a number")
        if value < 0:
            raise ValueError("Distance cannot be negative")
        self._distance = float(value)

    def export_snap_line(self, directory: str = "") -> str:
        """Export snap line to a JSON file
        
        Args:
            directory (str, optional): Directory to save the file. Defaults to current directory.
            
        Returns:
            str: Path to the exported file
        """
        # Create a dictionary with public properties
        export_dict = {
            'x_cord': self.x_cord,
            'y_cord': self.y_cord,
            'length': self.length,
            'angle': self.angle,
            'snap_to': self.snap_to,
            'moveable': self.moveable,
            'orientation': self.orientation.value,  # Convert enum to string
            'alignment': self.alignment.value,      # Convert enum to string
            'distance': self.distance
        }
        
        # Generate a safe file name
        safe_name = f"line_{int(self.x_cord)}_{int(self.y_cord)}"
        file_path = os.path.join(directory, f"{safe_name}_snap_line_export.json")
        
        # Export to JSON
        with open(file_path, "w") as f:
            f.write(json.dumps(export_dict))
            
        return file_path


def import_wall_line(file_name):
    """Import a wall line object from JSON file."""
    with open(file_name, "r") as f:
        data = f.read()
    obj = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
    
    # Convert string values back to enum instances if needed
    if hasattr(obj, 'orientation'):
        obj.orientation = LineOrientation(obj.orientation)
    if hasattr(obj, 'alignment'):
        obj.alignment = LineAlignment(obj.alignment)
    
    return obj
