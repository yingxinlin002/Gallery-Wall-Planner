# project_exporter.py

import json
import os

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
