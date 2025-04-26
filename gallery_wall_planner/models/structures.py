

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

class Padding:
    def __init__(self, top: int, right: int, bottom: int, left: int):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

class CanvasDimensions:
    def __init__(self, width: int, height: int, margin: int = 50, padding: Padding = None):
        self.width = width
        self.height = height
        self.margin = margin
        self.padding = padding if padding else Padding(0, 0, 0, 0)

class WallPosition:
    
    def __init__(self, wall_left, wall_bottom, wall_right, wall_top):
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
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y