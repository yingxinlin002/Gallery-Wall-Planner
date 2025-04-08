import json
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
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
        self.orientation = orientation if isinstance(orientation, LineOrientation) else LineOrientation(orientation)
        self.alignment = alignment if isinstance(alignment, LineAlignment) else LineAlignment(alignment)
        self.distance = distance

    def export_snap_line(self):
        #Temp way to export object to json, can be refined later
        export_dict = self.__dict__.copy()
        # Convert enum values to their string representation for JSON serialization
        export_dict['orientation'] = self.orientation.value
        export_dict['alignment'] = self.alignment.value
        with open(f"{self}_snap_line_export", "wb") as f:
            f.write(json.dumps(export_dict))


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
