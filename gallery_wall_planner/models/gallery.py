import openpyxl
from openpyxl.styles import Font, PatternFill

class Gallery:
    # Class-level list to store all walls (replaces shared_state.walls)
    _all_walls = []
    
    def __init__(self, name="Gallery"):
        self.name = name  # Exhibit title
        self.walls = []  # List of Wall objects for this specific gallery

    # Class methods to manage all walls (formerly in shared_state.py)
    @classmethod
    def add_wall(cls, wall):
        cls._all_walls.append(wall)
        
    @classmethod
    def get_walls(cls):
        return cls._all_walls
        
    @classmethod
    def remove_wall(cls, wall):
        cls._all_walls.remove(wall)

    def export_gallery(self, filename="gallery_export.xlsx"):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Artworks"

        # Exhibit title
        ws.merge_cells("A1:I1")
        ws["A1"] = self.name
        ws["A1"].font = Font(size=14, bold=True)
        ws["A1"].fill = PatternFill(start_color="D8BFD8", end_color="D8BFD8", fill_type="solid")  # Purple

        # Define headers and colors
        headers = ["ID", "Name", "Photo", "Medium", "Width", "Height", "Depth", "Value", "NFS"]
        colors = ["ADD8E6", "90EE90", "ADD8E6", "FFFF99", "FFFF99", "FFFF99", "FFFF99", "FA8072", "D8BFD8"]

        # Apply headers
        for col_num, (header, color) in enumerate(zip(headers, colors), start=1):
            cell = ws.cell(row=2, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

        # Populate artwork data
        for wall in self.walls:
            for artwork in wall.artwork:
                ws.append([
                    getattr(artwork, "id", "N/A"),
                    artwork.title,
                    "",  # Placeholder for photos, we can implement later
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