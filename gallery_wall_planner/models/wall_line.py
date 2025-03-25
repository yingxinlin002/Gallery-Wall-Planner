import json
from types import SimpleNamespace

class WallLine:
    def __init__(self, x=0, y=0, length=0, angle=0, snap_to=False, moveable=True):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable

    def export_wall_line(self):
        return json.dumps(self.__dict__)


class SingleLine:
    def __init__(
        self,
        x=0,
        y=0,
        length=0,
        angle=0,
        snap_to=True,
        moveable=True,
        orientation="horizontal",  # "horizontal" or "vertical"
        alignment="center",        # Alignment point on artwork
        distance=0.0               # Distance from wall edge (in inches)
    ):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
        self.orientation = orientation
        self.alignment = alignment
        self.distance = distance

    def export_snap_line(self):
        return json.dumps(self.__dict__)


def import_wall_line(file_name):
    """Import a wall line object from JSON file."""
    with open(file_name, "r") as f:
        data = f.read()
    return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
