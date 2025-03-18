import json
from types import SimpleNamespace
class Artwork:
    #Attributes
    title = None
    medium = None
    name = None
    height = None
    width = None
    depth = None
    hanging_point = None
    price = None
    nfs = None
    #Initialize
    def __init__(self, title = "", medium = "", height = 0, width = 0, depth = 0, hanging_point = 0, price = 0, nfs = False):
        self.title = title
        self.height = height
        self.width = width
        self.hanging_point = hanging_point
        self.depth = depth
        self.price = price
        self.nfs = nfs
    #Setters
    def set_medium(self,medium):
        self.medium = medium
    
    def set_title(self,title):
        self.title = title
        
    def set_price(self,price):
        self.price = price

    def set_nfs(self,nfs):
        self.nfs = nfs
        
    def set_height(self, height):
        self.height = height

    def set_width(self, width):
        self.width = width

    def set_depth(self, depth):
        self.depth = depth

    def set_hanging_point(self,hanging_point):
        self.hanging_point = hanging_point

    #Getters
    def get_title(self):
        return(self.title)
        
    def get_price(self):
        return(self.price)

    def get_nfs(self):
        return(self.nfs)

    def get_title(self):
        return(self.title)
    
    def get_height(self):
        return(self.height)

    def get_width(self):
        return(self.width)

    def get_depth(self):
        return(self.depth)

    def get_hanging_point(self):
        return(self.hanging_point)

    def export_artwork(self):
        #Temp way to export object to json, can be refined later
        return(json.dumps(self.__dict__))

def import_artwork(art_name, file_name):
    #TEMP: Replace later with the menu input
    with open(file_name, "rb") as f:
        data = f.read()
    art_name = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
            