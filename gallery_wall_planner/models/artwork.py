import json
from types import SimpleNamespace

class Artwork:
    def __init__(self, name = "", medium = "", height = 0, width = 0, depth = 0, hanging_point = 0, price = 0, nfs = False, image_path = "", notes = ""):
        self.name = name
        self.medium = medium
        self.height = height
        self.width = float(width)
        self.depth = float(depth)
        self.hanging_point = float(hanging_point)
        self.price = float(price)
        self.nfs = nfs
        self.image_path = image_path
        self.notes = notes

    def __str__(self):
        #return all info about the artwork
        return f"Name: {self.name}\nMedium: {self.medium}\nHeight: {self.height}\nWidth: {self.width}\nDepth: {self.depth}\nHanging Point: {self.hanging_point}\nPrice: {self.price}\nNFS: {self.nfs}\nImage Path: {self.image_path}\nNotes: {self.notes}"
    
    def export_artwork(self):
        #Temp way to export object to json, can be refined later
        with open(f"{self.title}_artwork_export", "wb") as f:
            f.write(json.dumps(self.__dict__))

def import_artwork(art_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    art_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
            
