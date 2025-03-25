import json
from types import SimpleNamespace

class Artwork:
    #def __init__(self, title = "", medium = "", height = 0, width = 0, depth = 0, hanging_point = 0, price = 0, nfs = False):
    def __init__(self, name, width, height, depth=0.0, hanging_point=0.0, image_path=None):    
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.hanging_point = float(hanging_point)
        self.image_path = image_path

    def __str__(self):
        return f"{self.name} ({self.width}\" × {self.height}\")"
    
    def export_artwork(self):
        #Temp way to export object to json, can be refined later
        return(json.dumps(self.__dict__))

def import_artwork(art_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    art_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
            