import json
from types import SimpleNamespace
class Wall_lines:
    #Attributes
    x_cord = None
    y_cord = None
    length = None
    angle = None
    snap_to = None
    moveable = None
    #Initialize
    def __init__(self, x = 0, y = 0, length = 0, angle = 0, snap_to = False, moveable = True):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable
    
    #Setters
    def set_x(self, x):
        self.x_cord = x

    def set_y(self, y):
        self.y_cord = y

    def set_length(self, length):
        self.length = length

    def set_angle(self, angle):
        self.angle = angle

    def set_snap(self, snap_to):
        self.snap_to = snap_to

    def set_move(self, moveable):
        self.moveable = movable
    #Getters
    def get_x(self):
        return(self.x_cord)

    def get_y(self):
        return(self.y_cord)

    def get_length(self):
        return(self.length)

    def get_angle(self):
        return(self.angle)

    def get_snap(self):
        return(self.snap_to)

    def get_move(self):
        return(self.moveable)

    def export_wall_line(self):
        #Temp way to export object to json, can be refined later
        return(json.dumps(self.__dict__))

def import_wall_line(wall_line_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    wall_line_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))