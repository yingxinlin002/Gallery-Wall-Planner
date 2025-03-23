import json
from types import SimpleNamespace

class Wall:
    def __init__(self, name, width, height, color = "White"):
        self.name = name
        self.width = width
        self.height = height
        self.color = color

        self.artwork = []
        self.wall_lines = []

    def export_wall(self):
        #TODO: way to export object to json, can be refined later
        return(json.dumps(self.__dict__))
    
    def toString(self):
        return f"Wall: {self.name}, {self.width}, {self.height}, {self.color}"
        
def import_wall(wall_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    wall_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))