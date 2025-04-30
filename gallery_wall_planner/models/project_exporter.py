# project_exporter.py

import json
import os
import ast
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import SheetFormatProperties
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanent_object import PermanentObject
from gallery_wall_planner.models.structures import Position

def export_project(filepath, wall, permanent_objects, layout):
    """
    Save the current project data (wall, permanent objects, layout) into a JSON file.
    
    Args:
        filepath (str): Path to save the JSON file.
        wall (Wall): The Wall object.
        permanent_objects (list): List of permanent objects (dicts).
        layout (dict): Dictionary of layout positions keyed by object names.
    """
    project_data = {
        "wall": wall.export() if hasattr(wall, 'export') else wall.__dict__,  # fallback if export() is not defined
        "permanent_objects": permanent_objects,
        "layout": layout
    }
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w") as f:
        json.dump(project_data, f, indent=4)
    print(f"[INFO] Project saved to {filepath}")

def import_project(filepath):
    """
    Load a project from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file.
    
    Returns:
        dict: Dictionary containing wall, permanent_objects, and layout.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r") as f:
        project_data = json.load(f)

    print(f"[INFO] Project loaded from {filepath}")
    return project_data
def export_project_to_excel(filepath, wall, artworks, permanent_objects):
    """
    Load project from excel file

    Args: 
          filepath (str): Path to excel file, wall (wall obj), artworks (artwork objects),
                          permanent_objects (permanent objects)
    Returns:
            Nothing, just prints where the excel file was saved
    """
    def to_visible_wall_data(wall):
        # Prepares walls for export
        return {
            "Wall Name": wall.name,
            "Width (in)": wall.width,
            "Height (in)": wall.height,
        }

    def to_visible_artwork_data(art):
        # Prepares artwork for export
        return {
            "Name": art.name,
            "Width": art.width,
            "Height": art.height,
            "Hanging Point": art.hanging_point,
            "Medium": art.medium,
            "Depth": art.depth,
            "Photo": art.image_path,
            "NFS (Y/N)": "Y" if art.nfs else "N"
        }

    def to_internal_data(obj):
        # PRepares the _internal data for export
        safe = {}
        for k, v in obj.__dict__.items():
            if isinstance(v, Position):
                safe[k] = {"x": v.x, "y": v.y}
            else:
                safe[k] = v
        return str(safe)
    # Store data in pandas dataframe
    wall_data = pd.DataFrame([to_visible_wall_data(wall)])
    wall_data["_internal"] = to_internal_data(wall)

    artworks_data = pd.DataFrame([to_visible_artwork_data(a) for a in artworks])
    artworks_data["_internal"] = [to_internal_data(a) for a in artworks]

    perms_data = pd.DataFrame([p.__dict__ for p in permanent_objects])
    perms_data["_internal"] = [to_internal_data(p) for p in permanent_objects]
    # Write pandas dataframe to excel using openpyxl
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        wall_data.to_excel(writer, sheet_name="Wall", index=False)
        artworks_data.to_excel(writer, sheet_name="Artworks", index=False)
        perms_data.to_excel(writer, sheet_name="Permanents", index=False)

    print(f"[INFO] Project exported to Excel at {filepath}")

def import_project_from_excel(filepath):
    """
    Args:
         filepath (str): Path to excel file
    Returns:
            wall, artwork and permanent object data as class objects
    """
    try:
        data = pd.read_excel(filepath, sheet_name=None)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: excel file with specific name or path not found: {filepath}")

    # ----------- WALL -----------
    # Parses all wall data from excel
    wall_sheet = data["Wall"]
    wall_info = ast.literal_eval(wall_sheet["_internal"][0])
    # print("[DEBUG] Parsed wall_info:", wall_info)
    wall = Wall(
        name=wall_info.get("_name"),
        width=wall_info.get("_width"),
        height=wall_info.get("_height"),
        color=wall_info.get("_color")
    )

    # ----------- ARTWORKS -----------
    # Parses all artwork data from excel
    artworks = []
    for _, row in data["Artworks"].iterrows():
        art_info = ast.literal_eval(row["_internal"])
        pos = art_info.get("_position", {"x": 0, "y": 0})
        a = Artwork(
            name=art_info.get("_name"),
            width=art_info.get("_width"),
            height=art_info.get("_height"),
            image_path=art_info.get("_image_path"),
            medium=art_info.get("_medium"),
            depth=art_info.get("_depth"),
            hanging_point=art_info.get("_hanging_point"),
            price=art_info.get("_price", 0.0),
            nfs=art_info.get("_nfs", False),
            notes=art_info.get("_notes", "")
        )
        # Get position data
        a.position = Position(pos["x"], pos["y"])
        artworks.append(a)

    # ----------- PERMANENT OBJECTS -----------
    # Parse permanent object data from excel 
    permanents = []
    for _, row in data["Permanents"].iterrows():
        perm_info = ast.literal_eval(row["_internal"])
        pos = perm_info.get("_position", {"x": 0, "y": 0})
        p = PermanentObject(
            name=perm_info.get("_name"),
            width=perm_info.get("_width"),
            height=perm_info.get("_height"),
            image_path=perm_info.get("_image_path")
        )
        p.position = Position(pos["x"], pos["y"])
        permanents.append(p)

    print(f"[INFO] Project imported from Excel: {filepath}")
    return wall, artworks, permanents
# All available methods    
__all__ = [
    "export_project",
    "import_project",
    "export_project_to_excel",
    "import_project_from_excel"
]
