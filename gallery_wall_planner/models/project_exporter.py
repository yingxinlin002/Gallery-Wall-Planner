# project_exporter.py

import json
import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import SheetFormatProperties
from gallery_wall_planner.models.wall import Wall
from gallery_wall_planner.models.artwork import Artwork
from gallery_wall_planner.models.permanentObject import PermanentObject
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
    Export the current project (wall, artworks, permanent objects) into a single Excel file.

    Args:
        filepath (str): Path to save the Excel file.
        wall (Wall): Wall object.
        artworks (list of Artwork): List of Artwork instances.
        permanent_objects (list of PermanentObject): List of PermanentObject instances.
    """
    wall_data = {
        "Name": [wall.name],
        "Width": [wall.width],
        "Height": [wall.height],
        "Color": [wall.color],
        "_internal": [str(vars(wall))]  # store all internal data invisibly
    }

    artworks_data = []
    for art in artworks:
        row = {
            "Name": art.name,
            "Width": art.width,
            "Height": art.height,
            "Hanging Point": art.hanging_point,
            "Medium": getattr(art, 'medium', ''),
            "Depth": getattr(art, 'depth', ''),
            "Photo": art.image_path or '',
            "NFS (Y/N)": 'Y' if getattr(art, 'nfs', False) else 'N',
            "_internal": str(vars(art))
        }
        artworks_data.append(row)

    perm_data = []
    for obj in permanent_objects:
        row = {
            "Name": obj.name,
            "Width": obj.width,
            "Height": obj.height,
            "Photo": obj.image_path or '',
            "_internal": str(vars(obj))
        }
        perm_data.append(row)

    with pd.ExcelWriter(filepath) as writer:
        pd.DataFrame(wall_data).to_excel(writer, sheet_name="Wall", index=False)
        pd.DataFrame(artworks_data).to_excel(writer, sheet_name="Artworks", index=False)
        pd.DataFrame(perm_data).to_excel(writer, sheet_name="PermanentObjects", index=False)

    print(f"[INFO] Project exported to Excel at {filepath}")


def import_project_from_excel(filepath): # Currently does not work, I plan to fix this Friday morning as I cannot figure out why it will not work properly, I would gladly accept help on this. 
    """
    Import a project from an Excel file and create wall, artworks, and permanent objects.

    Args:
        filepath (str): Path to the Excel file.

    Returns:
        tuple: (Wall object, list of Artwork objects, list of PermanentObject objects)
    """
    data = pd.read_excel(filepath, sheet_name=None)

    # ----------- WALL -----------
    wall_sheet = data["Wall"]
    
    try:
        raw_internal = wall_sheet["_internal"].dropna().iloc[0]
        wall_info = ast.literal_eval(raw_internal)
    except Exception as e:
        raise ValueError(f"Failed to parse wall info from _internal column: {e}")
    
    name = wall_info.get("name") # For some reason this refuses to grab the value of the name, I suspect it has similar issues for other attributes. 
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"Invalid or missing wall name: {name}")
    
    wall = Wall(
        name=name,
        width=wall_info.get("width", 0),
        height=wall_info.get("height", 0),
        color=wall_info.get("color", "#ffffff"),
    )

    # ----------- ARTWORKS -----------
    artworks = []
    for _, row in data["Artworks"].iterrows():
        art_info = ast.literal_eval(row["_internal"])
        artwork = Artwork(
            name=art_info.get("name"),
            width=art_info.get("width"),
            height=art_info.get("height"),
            hanging_point=art_info.get("hanging_point", 0),
            medium=art_info.get("medium", ""),
            depth=art_info.get("depth", 0),
            nfs=art_info.get("nfs", False),
        )
        artwork.image_path = art_info.get("image_path", None)
        if "position" in art_info:
            pos = art_info["position"]
            artwork.position = Position(pos["x"], pos["y"])
        artworks.append(artwork)

    # ----------- PERMANENT OBJECTS -----------
    permanent_objects = []
    for _, row in data["PermanentObjects"].iterrows():
        perm_info = ast.literal_eval(row["_internal"])
        obj = PermanentObject(
            name=perm_info.get("name"),
            width=perm_info.get("width"),
            height=perm_info.get("height"),
        )
        obj.image_path = perm_info.get("image_path", None)
        if "position" in perm_info:
            pos = perm_info["position"]
            obj.position = Position(pos["x"], pos["y"])
        permanent_objects.append(obj)

    print(f"[INFO] Project imported successfully from {filepath}")
    return wall, artworks, permanent_objects
