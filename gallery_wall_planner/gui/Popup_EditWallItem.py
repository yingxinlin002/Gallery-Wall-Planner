
from gallery_wall_planner.gui.Popup_Base import Popup_Base
from gallery_wall_planner.models.wall_object import WallObject
from gallery_wall_planner.gui.AppMain import AppMain

class Popup_EditWallItem(Popup_Base):
    def __init__(self, AppMain : AppMain, parent_ui: 'Screen_Base', WallObject : WallObject, *args, **kwargs):
        super().__init__(AppMain, "Edit Wall Item", 300, 150, *args, **kwargs)
        self.WallObject = WallObject
        from gallery_wall_planner.gui.Screen_Base import Screen_Base
        self.parent_ui: Screen_Base = parent_ui
        self.load_content()
        

    def load_content(self):
        pass