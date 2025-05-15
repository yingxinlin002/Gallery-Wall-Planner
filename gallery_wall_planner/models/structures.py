
from enum import Enum

def get_id(input: str) -> str:
    """Generate a simple hash from the input string.
    
    Args:
        input: String to hash
        
    Returns:
        A simple hash string
    """
    # Use a simple hash algorithm - sum of character codes multiplied by position
    hash_value = sum(ord(c) * (i + 1) for i, c in enumerate(input))
    # Convert to a hex string and take the last 8 characters
    return f"{hash_value:x}"[-8:].zfill(8)

class MeasureFrom(Enum):
    """Enum representing measurement options for the gallery wall."""
    EDGES = "edges"
    CENTER = "center"

class MeasureHorizontal(Enum):
    """Enum representing horizontal measurement options."""
    LEFT = "left"
    RIGHT = "right"

class MeasureVertical(Enum):
    """Enum representing vertical measurement options."""
    TOP = "top"
    BOTTOM = "bottom"

class Padding:
    """Class representing padding values."""
    def __init__(self, top: int, right: int, bottom: int, left: int):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

class CanvasDimensions:
    """Class representing the dimensions of a canvas."""
    def __init__(self, width: int, height: int, margin: int = 50, padding: Padding = None):
        self.width = width
        self.height = height
        self.margin = margin
        self.padding = padding if padding else Padding(0, 0, 0, 0)

class WallPosition:
    """Class representing the position of a wall in a gallery."""
    def __init__(self, wall_left, wall_top, wall_right, wall_bottom):
        self._wall_left = wall_left
        self._wall_bottom = wall_bottom
        self._wall_right = wall_right
        self._wall_top = wall_top

    @property
    def wall_left(self):
        return self._wall_left

    @property
    def wall_bottom(self):
        return self._wall_bottom

    @property
    def wall_right(self):
        return self._wall_right

    @property
    def wall_top(self):
        return self._wall_top

    
#class Bounds:


class Position:
    """Class representing a 2D position with x and y coordinates."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"