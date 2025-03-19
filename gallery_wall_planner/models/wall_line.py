import json
from types import SimpleNamespace

class WallLine:
    def __init__(self, x = 0, y = 0, length = 0, angle = 0, snap_to = False, moveable = True):
        self.x_cord = x
        self.y_cord = y
        self.length = length
        self.angle = angle
        self.snap_to = snap_to
        self.moveable = moveable

    def export_wall_line(self):
        #Temp way to export object to json, can be refined later
        return(json.dumps(self.__dict__))

def import_wall_line(wall_line_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    wall_line_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))