from __future__ import annotations
from enum import Enum
# I believe the two imports below, def export_snap_line(), and def import_snap_line() should live in wall.py
import json
import os
from types import SimpleNamespace
from enum import Enum, auto
from typing import Union, Optional, List
from models.structures import get_id

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
        else:
            return []




class SingleLine:
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        length: float = 0,
        angle: float = 0,
        snap_to: bool = True,
        moveable: bool = True,
        orientation: Orientation = Orientation.HORIZONTAL,
        alignment: Union[HorizontalAlignment,VerticalAlignment] = HorizontalAlignment.CENTER,
        distance: float = 0.0               # Distance from wall edge (in inches)
    ):
        # Initialize private attributes
        self._x_cord: float = None
        self._y_cord: float = None
        self._length: float = None
        self._angle: float = None
        self._snap_to: bool = None
        self._moveable: bool = None
        self._orientation: Orientation = None
        self._alignment: Union[HorizontalAlignment,VerticalAlignment] = None
        self._distance: float = None

        # Set properties with validation
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
        self.orientation = orientation  # Use the Orientation enum
        self.alignment = alignment
        self.distance = distance

        self._id = get_id("line"+f"x{self.x_cord},y{self.y_cord},length{self.length},angle{self.angle},snap_to{self.snap_to},moveable{self.moveable},orientation{self.orientation},alignment{self.alignment},distance{self.distance}")

    def __str__(self):
        return f"Line {self.orientation.value} {self.distance}"

    @property
    def id(self) -> str:
        """Get the line id"""
        return self._id

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
    def orientation(self) -> Orientation:
        """Get the orientation of the line"""
        return self._orientation

    @orientation.setter
    def orientation(self, value: Orientation):
        """Set the orientation of the line with validation"""
        if isinstance(value, Orientation):
            self._orientation = value
 

    @property
    def alignment(self) -> Union[HorizontalAlignment,VerticalAlignment]:
        return self._alignment

    @alignment.setter
    def alignment(self, value: Union[HorizontalAlignment,VerticalAlignment]):
        self._alignment = value

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

    def approximate_equal(self, other: SingleLine) -> bool:
        """Check if two SingleLine objects are approximately equal"""
        return self.orientation == other.orientation and self.alignment == other.alignment and abs(self.distance - other.distance) < 0.001

    def to_dict(self):
        # Helper for import/export in project_exporter.py
        return {
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
    try:
        with open(file_name, "r") as f:
            data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"WallLineJsonNotFound: wall line json with specific name or path not found: {file_name}")
    obj = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

    # Convert string values back to enum instances if needed
    if hasattr(obj, 'orientation'):
        obj.orientation = Orientation(obj.orientation)
    if hasattr(obj, 'alignment'):
        obj.alignment = LineAlignment(obj.alignment)

    return obj
