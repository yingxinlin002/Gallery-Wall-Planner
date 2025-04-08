from enum import Enum
# I believe the two imports below, def export_snap_line(), and def import_snap_line() should live in wall.py
import json
from types import SimpleNamespace

class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class HorizontalAlignment(Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"

class VerticalAlignment(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class SingleLine:
    def __init__(
        self,
        x=0,
        y=0,
        length=0,
        angle=0,
        snap_to=True,
        moveable=True,
        orientation=Orientation.HORIZONTAL,  # Default is horizontal
        alignment=None,  # Will be set based on orientation
        distance=0.0  # Distance from wall edge (in inches)
    ):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
        self.orientation = orientation  # Use the Orientation enum
        self.distance = distance

        # Set alignment based on orientation
        if orientation == Orientation.HORIZONTAL:
            self.alignment = alignment or HorizontalAlignment.CENTER  # Default to center
        elif orientation == Orientation.VERTICAL:
            self.alignment = alignment or VerticalAlignment.CENTER  # Default to center
        else:
            self.alignment = None # In case of an invalid orientation

    def export_snap_line(self):
        """Export the SingleLine object to a JSON file."""
        file_name = f"{self}_snap_line_export.json"  # Add a .json extension
        with open(file_name, "w") as f:  # Open file in text mode ("w")
            json.dump(self.__dict__, f, indent=4)  # Use json.dump() to write the data as JSON
        print(f"Snap line exported to {file_name}")

def import_snap_line(file_name):
    """Import a SingleLine object from a JSON file."""
    with open(file_name, "r") as f:  # Open the file in read mode
        data = json.load(f)  # Use json.load() to read and parse the JSON data
    return SimpleNamespace(**data)  # Convert the dictionary to a SimpleNamespace object
