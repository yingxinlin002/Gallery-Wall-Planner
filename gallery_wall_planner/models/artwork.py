import json
from types import SimpleNamespace

class Artwork:
    def __init__(self, title = "", medium = "", height = 0, width = 0, depth = 0, hanging_point = 0, price = 0, nfs = False):
        self.title = title
        self.height = height
        self.width = width
        self.hanging_point = hanging_point
        self.depth = depth
        self.price = price
        self.nfs = nfs

    def export_artwork(self):
        #Temp way to export object to json, can be refined later
        return(json.dumps(self.__dict__))

def import_artwork(art_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    art_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
            