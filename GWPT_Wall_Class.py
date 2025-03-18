import json
from types import SimpleNamespace
class Wall:
    #Attributes
    name = None
    width = None
    height = None
    color = "White" #Default is white, not required to change
    #Initialize
    def __init__(name, width, height, color = "White"):
        self.name = name
        self.width = width
        self.height = height
        self.color = color
    #Setters
    def set_name(self, name):
        self.name = name
        
    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_color(self, color):
        self.color = color

    #Getters
    def get_name(self):
        return(self.name)
        
    def get_width(self):
        return(self.width)

    def get_height(self):
        return(self.height)

    def get_color(self):
        return(self.color)

    def export_wall(self):
        #Temp way to export object to json, can be refined later
        return(json.dumps(self.__dict__))
        
def import_wall(wall_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    wall_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))