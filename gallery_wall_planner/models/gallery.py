import openpyxl
from openpyxl.styles import Font, PatternFill

class Gallery:
    # Class-level list to store all walls (replaces shared_state.walls)
    _all_walls = []
    
    def __init__(self, name="Gallery"):
        self.name = name  # Exhibit title
        self.walls = []  # List of Wall objects for this specific gallery

    # Class methods to manage all walls
    @classmethod
    def add_wall(cls, wall):
        cls._all_walls.append(wall)
        
    @classmethod
    def get_walls(cls):
        return cls._all_walls
        
    @classmethod
    def remove_wall(cls, wall):
        cls._all_walls.remove(wall)

    @classmethod
    def get_wall_by_name(cls, name):
        """Find a wall by its name"""
        for wall in cls._all_walls:
            if wall.name == name:
                return wall
        return None

    @classmethod
    def add_artwork_to_wall(cls, wall_name, artwork):
        wall = cls.get_wall_by_name(wall_name)
        if wall:
            wall.add_artwork(artwork)
            return True
        return False
    

    @classmethod
    def remove_artwork_from_wall(cls, wall_name, artwork):
        """
        Remove an artwork from a specific wall
        Args:
            wall_name: Name of the wall to remove artwork from
            artwork: Artwork object to remove
        Returns:
            bool: True if successful, False if wall not found or artwork not in wall
        """
        wall = cls.get_wall_by_name(wall_name)
        if wall:
            return wall.remove_artwork(artwork)
        return False

    def export_gallery(self, filename="gallery_export.xlsx"):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Artworks"

        # Exhibit title
        ws.merge_cells("A1:I1")
        ws["A1"] = self.name
        ws["A1"].font = Font(size=14, bold=True)
        ws["A1"].fill = PatternFill(start_color="D8BFD8", end_color="D8BFD8", fill_type="solid")

        # Define headers and colors
        headers = ["ID", "Name", "Photo", "Medium", "Width", "Height", "Depth", "Value", "NFS"]
        colors = ["ADD8E6", "90EE90", "ADD8E6", "FFFF99", "FFFF99", "FFFF99", "FFFF99", "FA8072", "D8BFD8"]

        # Apply headers
        for col_num, (header, color) in enumerate(zip(headers, colors), start=1):
            cell = ws.cell(row=2, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

        # Populate artwork data
        art_counter = 0 # Counter to track id's
        for wall in self.walls:
            for artwork in wall.artwork:
                art_counter += 1
                ws.append([
                    getattr(artwork, "id", art_counter),
                    artwork.title,
                    "",  # Placeholder for photos
                    artwork.medium,
                    artwork.width,
                    artwork.height,
                    artwork.depth,
                    artwork.price,
                    artwork.nfs
                ])

        # Adjust column width
        for col in ws.iter_cols(min_row=2, max_row=ws.max_row):
            max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

        # Save the excel file
        wb.save(filename)
        print(f"Gallery exported to {filename}")

    @classmethod
    def import_gallery(cls, filename="gallery_export.xlsx"):
        wb = openpyxl.load_workbook(filename)
        ws = wb["Artworks"]

        # Read the exhibit title
        exhibit_name = ws["A1"].value or "Imported Exhibit"

        # Create a new Gallery object
        gallery = cls(name=exhibit_name)

        # Create a generic wall to hold artworks (since Excel currently does not store wall info)
        imported_wall = Wall(name="Imported Wall", width=0, height=0)

        # Read the artwork data from row 3 onwards
        for row in ws.iter_rows(min_row=3, values_only=True):
            if not any(row):  # Skip empty rows
                continue

            # Extract values based on the expected column order
            art_id, title, _, medium, width, height, depth, price, nfs = row

            #Create Artwork objects
            artwork = Artwork(
                title=title or "",
                medium=medium or "",
                width=width or 0,
                height=height or 0,
                depth=depth or 0,
                price=price or 0,
                nfs=bool(nfs)
            )
            setattr(artwork, "id", art_id)  # Set the ID manually (not part of Artwork class by default as usually not needed)

            # Add to the imported wall
            imported_wall.artwork.append(artwork)

        # Add the wall to the gallery
        gallery.walls.append(imported_wall)

        print(f"Gallery '{gallery.name}' imported successfully with {len(imported_wall.artwork)} artworks.")
        return gallery
