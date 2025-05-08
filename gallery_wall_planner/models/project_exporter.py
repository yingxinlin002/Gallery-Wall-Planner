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
from .wall_line import SingleLine
from gallery_wall_planner.models.gallery import Gallery


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

    def import_gallery_from_excel(filepath):
        print(f"[INFO] Importing gallery from {filepath}")
        xls = pd.ExcelFile(filepath)
        gallery = Gallery(name="Imported Gallery")
    
        walls = {}
    
        # Load wall metadata first
        if "Walls" in xls.sheet_names:
            df_walls = xls.parse("Walls")
            for _, row in df_walls.iterrows():
                name = row["name"]
                width = float(row["width"])
                height = float(row["height"])
                color = row.get("color", "#FFFFFF")
                walls[name] = Wall(name=name, width=width, height=height, color=color)
        else:
            print("[WARN] No 'Walls' sheet found. Walls will use default dimensions.")
    
        # Now process each wall's data
        for sheet in xls.sheet_names:
            print(f"[INFO] Reading sheet: {sheet}")
            df = xls.parse(sheet)
            if df.empty:
                print(f"[WARN] Sheet '{sheet}' is empty, skipping.")
                continue
    
            if " - Art" in sheet:
                wall_name = sheet.replace(" - Art", "")
                if df.columns.tolist() == ["info"] and "No artworks" in df["info"].values:
                    continue
                if wall_name in walls:
                    walls[wall_name].artwork = [Artwork.from_dict(row) for _, row in df.iterrows()]
                    print(f"[OK] Loaded artworks for wall '{wall_name}'.")
                else:
                    print(f"[ERROR] Wall '{wall_name}' not found in Walls sheet.")
    
            elif " - Lines" in sheet:
                wall_name = sheet.replace(" - Lines", "")
                if df.columns.tolist() == ["info"] and "No wall lines" in df["info"].values:
                    continue
                if wall_name in walls:
                    walls[wall_name].wall_lines = [SingleLine.from_dict(row) for _, row in df.iterrows()]
                    print(f"[OK] Loaded wall lines for wall '{wall_name}'.")
                else:
                    print(f"[ERROR] Wall '{wall_name}' not found in Walls sheet.")
    
            elif " - Perm" in sheet:
                wall_name = sheet.replace(" - Perm", "")
                if df.columns.tolist() == ["info"] and "No permanent objects" in df["info"].values:
                    continue
                if wall_name in walls:
                    walls[wall_name].permanent_objects = [PermanentObject.from_dict(row) for _, row in df.iterrows()]
                    print(f"[OK] Loaded permanent objects for wall '{wall_name}'.")
                else:
                    print(f"[ERROR] Wall '{wall_name}' not found in Walls sheet.")
    
        gallery.walls = list(walls.values())
        print(f"[DONE] Imported gallery with {len(gallery.walls)} walls.")
        return gallery



def export_gallery_to_excel(filepath: str, gallery: Gallery):
    print(f"[INFO] Exporting gallery to {filepath}")
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')

    # Sheet: ExportInfo
    pd.DataFrame([{"Export status": "Initialized"}]).to_excel(writer, index=False, sheet_name="ExportInfo")

    # NEW Sheet: Walls
    wall_rows = []
    for wall in gallery.walls:
        wall_rows.append({
            "name": wall.name,
            "width": wall.width,
            "height": wall.height,
            "color": wall.color
        })
    pd.DataFrame(wall_rows).to_excel(writer, index=False, sheet_name="Walls")

    # Export each wall's elements
    for wall in gallery.walls:
        # Artwork
        if wall.artwork:
            pd.DataFrame([a.to_dict() for a in wall.artwork]).to_excel(
                writer, index=False, sheet_name=f"{wall.name} - Art"
            )
        else:
            pd.DataFrame([{"info": "No artworks"}]).to_excel(
                writer, index=False, sheet_name=f"{wall.name} - Art"
            )

        # Wall Lines
        if wall.wall_lines:
            pd.DataFrame([l.to_dict() for l in wall.wall_lines]).to_excel(
                writer, index=False, sheet_name=f"{wall.name} - Lines"
            )
        else:
            pd.DataFrame([{"info": "No wall lines"}]).to_excel(
                writer, index=False, sheet_name=f"{wall.name} - Lines"
            )

        # Permanent Objects
        if wall.permanent_objects:
            pd.DataFrame([p.to_dict() for p in wall.permanent_objects]).to_excel(
                writer, index=False, sheet_name=f"{wall.name} - Perm"
            )
        else:
            pd.DataFrame([{"info": "No permanent objects"}]).to_excel(
                writer, index=False, sheet_name=f"{wall.name} - Perm"
            )

    writer.close()
    print("[DONE] Finished exporting gallery.")


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
                # Load wall metadata first
            if "Walls" in xls.sheet_names:
                df_walls = xls.parse("Walls")
                for _, row in df_walls.iterrows():
                    name = row["name"]
                    width = float(row["width"])
                    height = float(row["height"])
                    color = row.get("color", "#FFFFFF")
                    walls[name] = Wall(name=name, width=width, height=height, color=color)
            else:
                print("[WARN] No 'Walls' sheet found. Walls will use default dimensions.")

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
                    SingleLine.from_dict(row) for _, row in df.iterrows()
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
