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
from .wall_line import WallLine

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
    
def _project_to_excel(filepath, wall=None, artworks=None, permanent_objects=None):
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

        if artwork:
            artworks_data = pd.DataFrame([to_visible_artwork_data(a) for a in artwork])
            artworks_data["_internal"] = [to_internal_data(a) for a in artwork]
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

    artworks_data = pd.DataFrame([to_visible_artwork_data(a) for a in artwork])
    artworks_data["_internal"] = [to_internal_data(a) for a in artwork]

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
    print(f"[INFO] Starting export of gallery: {gallery.name} to {filepath}")
    
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        # 1. Ensure at least one sheet exists
        pd.DataFrame({"Export status": ["Initialized"]}).to_excel(writer, sheet_name="ExportInfo", index=False)

        # 2. Export walls
        for wall in gallery.walls:
            print(f"[INFO] Processing wall: {wall.name}")
            try:
                # Export artworks
                if hasattr(wall, "artwork"):
                    artworks = [a.to_dict() for a in wall.artwork]
                elif hasattr(wall, "artworks"):
                    artworks = [a.to_dict() for a in wall.artwork]
                else:
                    print(f"[WARN] Wall '{wall.name}' has no 'artwork' or 'artworks' attribute.")
                    artworks = []

                df_artworks = pd.DataFrame(artworks)
                if df_artworks.empty:
                    df_artworks = pd.DataFrame([{"info": "No artworks"}])
                df_artworks.to_excel(writer, sheet_name=f"{wall.name[:28]} - Art", index=False)
                print(f"[OK] Artworks for wall '{wall.name}' written.")

                # Export wall lines
                lines = [l.to_dict() for l in getattr(wall, "wall_lines", [])]
                df_lines = pd.DataFrame(lines)
                if df_lines.empty:
                    df_lines = pd.DataFrame([{"info": "No wall lines"}])
                df_lines.to_excel(writer, sheet_name=f"{wall.name[:28]} - Lines", index=False)
                print(f"[OK] Wall lines for wall '{wall.name}' written.")

                # Export permanent objects
                perms = [p.to_dict() for p in getattr(wall, "permanent_objects", [])]
                df_perms = pd.DataFrame(perms)
                if df_perms.empty:
                    df_perms = pd.DataFrame([{"info": "No permanent objects"}])
                df_perms.to_excel(writer, sheet_name=f"{wall.name[:28]} - Perm", index=False)
                print(f"[OK] Permanent objects for wall '{wall.name}' written.")

            except Exception as e:
                print(f"[ERROR] Failed to export data for wall '{wall.name}': {e}")

        print(f"[DONE] Export completed to {filepath}")


from gallery_wall_planner.models.gallery import Gallery  # assuming this exists

def import_gallery_from_excel(filepath):
    print(f"[INFO] Importing gallery from {filepath}")
    xls = pd.ExcelFile(filepath)
    gallery = Gallery(name="Imported Gallery")

    walls = {}
    for sheet in xls.sheet_names:
        print(f"[INFO] Reading sheet: {sheet}")
        try:
            df = xls.parse(sheet)
            if df.empty:
                print(f"[WARN] Sheet '{sheet}' is empty, skipping.")
                continue

            if " - Art" in sheet:
                wall_name = sheet.replace(" - Art", "")
                if df.columns.tolist() == ["info"] and "No artworks" in df["info"].values:
                    print(f"[INFO] Placeholder sheet for artworks on '{wall_name}', skipping.")
                    continue
                walls.setdefault(wall_name, Wall(name=wall_name)).artworks = [
                    Artwork.from_dict(row) for _, row in df.iterrows()
                ]
                print(f"[OK] Loaded artworks for wall '{wall_name}'.")

            elif " - Lines" in sheet:
                wall_name = sheet.replace(" - Lines", "")
                if df.columns.tolist() == ["info"] and "No wall lines" in df["info"].values:
                    print(f"[INFO] Placeholder sheet for wall lines on '{wall_name}', skipping.")
                    continue
                walls.setdefault(wall_name, Wall(name=wall_name)).wall_lines = [
                    WallLine.from_dict(row) for _, row in df.iterrows()
                ]
                print(f"[OK] Loaded wall lines for wall '{wall_name}'.")

            elif " - Perm" in sheet:
                wall_name = sheet.replace(" - Perm", "")
                if df.columns.tolist() == ["info"] and "No permanent objects" in df["info"].values:
                    print(f"[INFO] Placeholder sheet for permanent objects on '{wall_name}', skipping.")
                    continue
                walls.setdefault(wall_name, Wall(name=wall_name)).permanent_objects = [
                    PermanentObject.from_dict(row) for _, row in df.iterrows()
                ]
                print(f"[OK] Loaded permanent objects for wall '{wall_name}'.")

        except Exception as e:
            print(f"[ERROR] Failed to load sheet '{sheet}': {e}")

    gallery.walls = list(walls.values())
    print(f"[DONE] Finished importing gallery with {len(gallery.walls)} walls.")
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
