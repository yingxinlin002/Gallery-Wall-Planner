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
        raise FileNotFoundError(f"Project file not found: {filepath}")

    with open(filepath, "r") as f:
        project_data = json.load(f)

    print(f"[INFO] Project loaded from {filepath}")
    return project_data
    
def export_project_to_excel(filepath, wall=None, artworks=None, permanent_objects=None):
    """
    Export project data to Excel. Any of wall, artworks, or permanent_objects may be None.

    Args:
        filepath (str): Destination Excel path
        wall (Wall): Wall object
        artworks (list of Artwork): Artwork objects
        permanent_objects (list of PermanentObject): Permanent objects
    """
    def to_visible_wall_data(wall):
        return {
            "Wall Name": wall.name,
            "Width (in)": wall.width,
            "Height (in)": wall.height,
        }

    def to_visible_artwork_data(art):
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
        try:
            d = obj.export()
        except AttributeError:
            d = obj.__dict__
        safe = {}
        for k, v in d.items():
            if isinstance(v, Position):
                safe[k] = {"x": v.x, "y": v.y}
            else:
                safe[k] = v
        return str(safe)

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        if wall:
            wall_data = pd.DataFrame([to_visible_wall_data(wall)])
            wall_data["_internal"] = to_internal_data(wall)
            wall_data.to_excel(writer, sheet_name="Wall", index=False)

        if artworks:
            artworks_data = pd.DataFrame([to_visible_artwork_data(a) for a in artworks])
            artworks_data["_internal"] = [to_internal_data(a) for a in artworks]
            artworks_data.to_excel(writer, sheet_name="Artworks", index=False)

        if permanent_objects:
            perms_data = pd.DataFrame([p.__dict__ for p in permanent_objects])
            perms_data["_internal"] = [to_internal_data(p) for p in permanent_objects]
            perms_data.to_excel(writer, sheet_name="Permanents", index=False)

    print(f"[INFO] Project exported to Excel at {filepath}")

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
    Import available project data from Excel. Will skip missing sheets.

    Returns:
        Tuple of wall, artworks, permanents. Any may be None or empty.
    """
    try:
        data = pd.read_excel(filepath, sheet_name=None)
    except FileNotFoundError:
        raise FileNotFoundError(f"ProjectFileNotFoundError: project excel file not found: {filepath}")

    wall, artworks, permanents = None, [], []

    if "Wall" in data:
        wall_sheet = data["Wall"]
        wall_info = ast.literal_eval(wall_sheet["_internal"][0])
        wall = Wall(
            name=wall_info.get("_name"),
            width=wall_info.get("_width"),
            height=wall_info.get("_height"),
            color=wall_info.get("_color")
        )

    if "Artworks" in data:
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
            a.position = Position(pos["x"], pos["y"])
            artworks.append(a)

    if "Permanents" in data:
        for _, row in data["Permanents"].iterrows():
            perm_info = ast.literal_eval(row["_internal"])
            pos = perm_info.get("_position", {"x": 0, "y": 0})
            p = PermanentObject(
                name=perm_info.get("_name"),
                width=perm_info.get("_width"),
                height=perm_info.get("_height"),
                image_path=perm_info.get("_image_path"),
                orientation=perm_info.get("_orientation", "horizontal"),  # Optional new fields
                category=perm_info.get("_category", None)
            )
            p.position = Position(pos["x"], pos["y"])
            permanents.append(p)

    print(f"[INFO] Project imported from Excel: {filepath}")
    return wall, artworks, permanents

def export_gallery_to_excel(filepath, gallery):
    """
    Export a Gallery object to an Excel file.
    Args:
        filepath (str): Path to save Excel file.
        gallery (Gallery): The gallery object containing multiple walls.
    """
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        for wall in gallery.walls:
            wall_df = pd.DataFrame([{
                "Wall Name": wall.name,
                "Width (in)": wall.width,
                "Height (in)": wall.height,
                "_internal": str(wall.export() if hasattr(wall, "export") else wall.__dict__)
            }])
            wall_df.to_excel(writer, sheet_name=f"{wall.name}_Wall", index=False)

            if wall.artworks:
                artworks_df = pd.DataFrame([{
                    "Name": a.name,
                    "Width": a.width,
                    "Height": a.height,
                    "Hanging Point": a.hanging_point,
                    "Medium": a.medium,
                    "Depth": a.depth,
                    "Photo": a.image_path,
                    "NFS (Y/N)": "Y" if a.nfs else "N",
                    "_internal": str(a.__dict__)
                } for a in wall.artworks])
                artworks_df.to_excel(writer, sheet_name=f"{wall.name}_Artworks", index=False)

            if wall.permanent_objects:
                perms_df = pd.DataFrame([{
                    **{k: v for k, v in po.__dict__.items() if not isinstance(v, Position)},
                    "_internal": str(po.__dict__)
                } for po in wall.permanent_objects])
                perms_df.to_excel(writer, sheet_name=f"{wall.name}_Permanents", index=False)

    print(f"[INFO] Gallery exported to Excel at {filepath}")

from gallery_wall_planner.models.gallery import Gallery  # assuming this exists

def import_gallery_from_excel(filepath):
    """
    Import a Gallery object from an Excel file.
    Args:
        filepath (str): Path to Excel file.
    Returns:
        Gallery: Gallery object reconstructed from the file.
    """
    try:
        data = pd.read_excel(filepath, sheet_name=None)
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    walls = []
    for sheet_name in data:
        if sheet_name.endswith("_Wall"):
            wall_name = sheet_name.replace("_Wall", "")
            wall_info = ast.literal_eval(data[sheet_name]["_internal"][0])
            wall = Wall(
                name=wall_info.get("_name"),
                width=wall_info.get("_width"),
                height=wall_info.get("_height"),
                color=wall_info.get("_color")
            )

            # Artworks
            artworks = []
            art_sheet = data.get(f"{wall_name}_Artworks")
            if art_sheet is not None:
                for _, row in art_sheet.iterrows():
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
                    a.position = Position(pos["x"], pos["y"])
                    artworks.append(a)
            wall.artworks = artworks

            # Permanents
            perms = []
            perm_sheet = data.get(f"{wall_name}_Permanents")
            if perm_sheet is not None:
                for _, row in perm_sheet.iterrows():
                    perm_info = ast.literal_eval(row["_internal"])
                    pos = perm_info.get("_position", {"x": 0, "y": 0})
                    p = PermanentObject(
                        name=perm_info.get("_name"),
                        width=perm_info.get("_width"),
                        height=perm_info.get("_height"),
                        image_path=perm_info.get("_image_path")
                    )
                    p.position = Position(pos["x"], pos["y"])
                    perms.append(p)
            wall.permanent_objects = perms

            walls.append(wall)

    gallery = Gallery(walls=walls)
    print(f"[INFO] Gallery imported from Excel: {filepath}")
    return gallery

# All available methods    
__all__ = [
    "export_project",
    "import_project",
    "export_project_to_excel",
    "import_project_from_excel",
    "export_gallery_to_excel",
    "import_gallery_from_excel"
]
