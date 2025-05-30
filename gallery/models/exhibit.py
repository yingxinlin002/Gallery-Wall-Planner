import openpyxl
from openpyxl.styles import Font, PatternFill
from typing import List, Optional
from .base import db
from .artwork import Artwork

class Gallery(db.Model):
    __tablename__ = 'galleries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    
    # Relationships
    walls = db.relationship('Wall', backref='gallery', lazy=True, cascade='all, delete-orphan')
    unplaced_artworks = db.relationship('Artwork', 
                                      primaryjoin='and_(Artwork.wall_id==None, Artwork.gallery_id==Gallery.id)',
                                      backref='gallery',
                                      lazy=True)

    def __init__(self, name: str = "Gallery"):
        self.name = name

    def add_wall(self, name: str, width: float, height: float, color: str = "White") -> "Wall":
        """Add a new wall to the gallery"""
        from .wall import Wall
        wall = Wall(name=name, width=width, height=height, color=color, gallery_id=self.id)
        db.session.add(wall)
        return wall

    def get_walls(self) -> list["Wall"]:
        """Get all walls in this gallery"""
        return self.walls

    def get_wall_by_name(self, name: str) -> "Wall | None":
        """Find a wall by its name"""
        from .wall import Wall
        return Wall.query.filter_by(name=name, gallery_id=self.id).first()

    def remove_wall(self, wall_id: int) -> bool:
        """Remove a wall from the gallery"""
        wall = Wall.query.get(wall_id)
        if wall and wall.gallery_id == self.id:
            db.session.delete(wall)
            return True
        return False

    def add_unplaced_artwork(self, title: str, medium: str = "", width: float = 0, 
                            height: float = 0, depth: float = 0, price: float = 0,
                            nfs: bool = False, notes: str = "") -> Artwork:
        """Add artwork that isn't placed on any wall"""
        artwork = Artwork(
            title=title,
            medium=medium,
            width=width,
            height=height,
            depth=depth,
            price=price,
            nfs=nfs,
            notes=notes,
            gallery_id=self.id
        )
        db.session.add(artwork)
        return artwork

    def get_unplaced_artworks(self) -> List[Artwork]:
        """Get all artworks not placed on any wall"""
        return self.unplaced_artworks

    def place_artwork(self, artwork_id: int, wall_id: int) -> bool:
        """Move artwork from unplaced to a specific wall"""
        artwork = Artwork.query.get(artwork_id)
        wall = Wall.query.get(wall_id)
        
        if artwork and wall and artwork.gallery_id == self.id and wall.gallery_id == self.id:
            artwork.wall_id = wall_id
            return True
        return False

    def unplace_artwork(self, artwork_id: int) -> bool:
        """Remove artwork from a wall and make it unplaced"""
        artwork = Artwork.query.get(artwork_id)
        if artwork and artwork.gallery_id == self.id:
            artwork.wall_id = None
            return True
        return False

    def export_to_excel(self, filename: str = "gallery_export.xlsx") -> str:
        """Export gallery data to Excel file"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Artworks"

        # Add wall information
        for wall in self.walls:
            ws.append([wall.name, wall.width, wall.height, wall.color])
        ws.append([])  # Empty row before gallery title

        # Gallery title
        ws.append([self.name])
        title_row = ws.max_row
        ws.merge_cells(start_row=title_row, start_column=1, end_row=title_row, end_column=10)
        title_cell = ws.cell(row=title_row, column=1)
        title_cell.font = Font(size=14, bold=True)
        title_cell.fill = PatternFill(start_color="D8BFD8", end_color="D8BFD8", fill_type="solid")
        
        ws.append([])  # Empty row before headers
        
        # Column headers
        headers = ["ID", "Name", "Photo", "Medium", "Width", "Height", "Depth", "Value", "NFS", "Notes"]
        colors = ["ADD8E6", "90EE90", "ADD8E6", "FFFF99", "FFFF99", "FFFF99", "FFFF99", "FA8072", "D8BFD8", "FFFFFF"]
        
        header_row = ws.max_row + 1
        for col_num, (header, color) in enumerate(zip(headers, colors), start=1):
            cell = ws.cell(row=header_row, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

        # Add placed artworks
        art_counter = 0
        for wall in self.walls:
            for artwork in wall.artworks:
                art_counter += 1
                ws.append([
                    artwork.id or art_counter,
                    artwork.title,
                    "",
                    artwork.medium,
                    artwork.width,
                    artwork.height,
                    artwork.depth,
                    artwork.price,
                    artwork.nfs,
                    artwork.notes
                ])

        # Add unplaced artworks section
        ws.append([])
        ws.append(["Unplaced Artwork"])
        ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=10)
        title_cell = ws.cell(row=ws.max_row, column=1)
        title_cell.font = Font(size=12, bold=True)
        title_cell.fill = PatternFill(start_color="F0E68C", end_color="F0E68C", fill_type="solid")

        # Add headers again for unplaced artwork
        header_row = ws.max_row + 1
        for col_num, (header, color) in enumerate(zip(headers, colors), start=1):
            cell = ws.cell(row=header_row, column=col_num, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

        # Add unplaced artworks
        for artwork in self.unplaced_artworks:
            art_counter += 1
            ws.append([
                artwork.id or art_counter,
                artwork.title,
                "",
                artwork.medium,
                artwork.width,
                artwork.height,
                artwork.depth,
                artwork.price,
                artwork.nfs,
                artwork.notes
            ])

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[col[0].column_letter].width = adjusted_width

        wb.save(filename)
        return filename

    @classmethod
    def import_from_excel(cls, filename: str = "gallery_export.xlsx") -> 'Gallery':
        """Import gallery data from Excel file"""
        try:
            wb = openpyxl.load_workbook(filename)
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {filename}")

        ws = wb["Artworks"]
        gallery = cls()

        # Read wall information
        row_idx = 1
        while ws.cell(row=row_idx, column=1).value:
            wall_name = ws.cell(row=row_idx, column=1).value
            wall_width = float(ws.cell(row=row_idx, column=2).value)
            wall_height = float(ws.cell(row=row_idx, column=3).value)
            wall_color = ws.cell(row=row_idx, column=4).value or "White"
            gallery.add_wall(name=wall_name, width=wall_width, height=wall_height, color=wall_color)
            row_idx += 1
        
        # Skip empty rows and get gallery name
        row_idx += 1
        gallery.name = ws.cell(row=row_idx, column=1).value or "Imported Gallery"
        row_idx += 2  # Skip empty row and headers

        reading_unplaced = False
        current_wall = gallery.walls[-1] if gallery.walls else None

        for row in ws.iter_rows(min_row=row_idx, values_only=True):
            if not any(row):
                continue
            if row[0] == "Unplaced Artwork":
                reading_unplaced = True
                continue
            if row[0] == "ID":  # Skip header rows
                continue

            # Create artwork from row data
            art_id, title, _, medium, width, height, depth, price, nfs, notes = row
            artwork_data = {
                'title': title or "",
                'medium': medium or "",
                'width': float(width or 0),
                'height': float(height or 0),
                'depth': float(depth or 0),
                'price': float(price or 0),
                'nfs': bool(nfs),
                'notes': notes or "",
                'gallery_id': gallery.id
            }

            if reading_unplaced:
                gallery.add_unplaced_artwork(**artwork_data)
            elif current_wall:
                artwork = Artwork(**artwork_data, wall_id=current_wall.id)
                db.session.add(artwork)

        return gallery

    def __repr__(self):
        return f"<Gallery {self.name} ({len(self.walls)} walls, {len(self.unplaced_artworks)} unplaced artworks)>"