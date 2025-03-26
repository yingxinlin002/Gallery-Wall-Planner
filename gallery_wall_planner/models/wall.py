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

    def add_artwork(self, artwork):
        self.artwork.append(artwork)

    def remove_artwork(self, artwork):
        if artwork in self.artwork:
            self.artwork.remove(artwork)
            return True
        return False

    def get_artwork_by_name(self, name):
        for art in self.artwork:
            if art.name == name:
                return art
        return None

    def export_wall(self):
        #Temp way to export object to json, can be refined later
        with open(f"{self.name}_wall_export", "wb") as f:
            f.write(json.dumps(self.__dict__))
    
    def toString(self):
        return f"Wall: {self.name}, {self.width}, {self.height}, {self.color}"
        
def import_wall(wall_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    wall_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

def __str__(self):  # Added to allow degubbing. Following should be mostly readable: print(str(wall))
        return f"Wall(Name: {self.name}, Width: {self.width}, Height: {self.height}, Color: {self.color})"
