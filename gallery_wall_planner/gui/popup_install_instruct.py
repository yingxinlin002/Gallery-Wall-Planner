import tkinter as tk
from tkinter import ttk
from gallery_wall_planner.gui.app_main import AppMain
from gallery_wall_planner.gui.popup_base import PopupBase
from tkinter import ttk, filedialog, messagebox
import openpyxl
from gallery_wall_planner.utils.export_helpers import (
    save_to_excel,
    save_to_text,
    save_to_word,
    save_to_pdf
)


class InstallInstructionPopup(PopupBase):
    """Popup window for installation instructions"""
    def __init__(self, app_main : AppMain):
        super().__init__(app_main, "Installation Instructions", 400, 500)
        self.load_content()

    def load_content(self):
        """Load the content of the popup window"""
        super().load_content()

        self.artworks = self.app_main.gallery.current_wall.artwork
        self.selected_wall = self.app_main.gallery.current_wall
        # ----------------------------------
        # -------- First Piece Hung --------
        # ----------------------------------
        ttk.Label(self, text="First Piece Hung", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.first_piece_var = tk.StringVar(value=self.artworks[0].name if self.artworks else "")
        for art in self.artworks:
            ttk.Radiobutton(self, text=art.name, variable=self.first_piece_var, value=art.name).pack(anchor="w", padx=30)

        # ------------------------------
        # -------- Wall Measure --------
        # ------------------------------
        ttk.Label(self, text="Wall Measure", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.wall_measure_var = tk.StringVar(value="left")
        ttk.Radiobutton(self, text="From Left Wall", variable=self.wall_measure_var, value="left").pack(anchor="w", padx=30)
        ttk.Radiobutton(self, text="From Right Wall", variable=self.wall_measure_var, value="right").pack(anchor="w", padx=30)

        # --------------------------------
        # -------- Height Measure --------
        # --------------------------------
        ttk.Label(self, text="Height Measure", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.height_measure_var = tk.StringVar(value="floor")
        ttk.Radiobutton(self, text="From Floor", variable=self.height_measure_var, value="floor").pack(anchor="w", padx=30)
        ttk.Radiobutton(self, text="From Ceiling", variable=self.height_measure_var, value="ceiling").pack(anchor="w", padx=30)

        # ---------------------------
        # -------- File Type --------
        # ---------------------------
        ttk.Label(self, text="File Type", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.file_type_var = tk.StringVar(value="word")
        ttk.Radiobutton(self, text="Word", variable=self.file_type_var, value="word").pack(anchor="w", padx=30)
        ttk.Radiobutton(self, text="Excel", variable=self.file_type_var, value="excel").pack(anchor="w", padx=30)
        ttk.Radiobutton(self, text="PDF", variable=self.file_type_var, value="pdf").pack(anchor="w", padx=30)
        ttk.Radiobutton(self, text="Text (No Image)", variable=self.file_type_var, value="text").pack(anchor="w", padx=30)

        # -------------------------
        # -------- Buttons --------
        # -------------------------
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", pady=20)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=10)

        ttk.Button(button_frame, text="Save", command=self.print_and_save).pack(side="right", padx=10)

    def on_close(self):
        """Handle window closing"""
        self.grab_release()
        self.destroy()
        
    def print_and_save(self):
        """Print and save the installation instructions"""
        self.print_measurement_instructions()
        self.save_measurement_instructions()

    def calculate_hang_locations(self):
        """Calculate the hanging locations for each artwork"""
        unsorted_locations = {}
        wall_width = self.selected_wall.width
        wall_height = self.selected_wall.height

        print("\n=== DEBUG: Artwork Positions ===")
        print(f"Wall dimensions: {wall_width}\" wide x {wall_height}\" tall")
        print(f"Measurement reference: From {self.wall_measure_var.get()} wall, from {self.height_measure_var.get()}")
        
        for art in self.artworks:
            # Get bottom-left position
            bottom_left_x = art.position.x
            bottom_left_y = art.position.y
            
            # Calculate center position
            center_x = bottom_left_x + (art.width / 2)
            
            # Calculate top edge (in wall coordinates where 0 is bottom)
            top_edge = bottom_left_y + art.height
            
            # Hanging point is top edge minus hanging point offset
            hang_x = center_x
            hang_y = top_edge - art.hanging_point
            
            print(f"\nArtwork: {art.name}")
            print(f"Size: {art.width}\" x {art.height}\"")
            print(f"Bottom-left position: ({bottom_left_x:.3f}, {bottom_left_y:.3f})")
            print(f"Top edge: {top_edge:.3f}\" from floor")
            print(f"Hanging point offset: {art.hanging_point}\" from top")
            print(f"Calculated nail position: ({hang_x:.3f}, {hang_y:.3f})")
            
            # Adjust based on measurement preferences
            if self.wall_measure_var.get() == "right":
                hang_x = wall_width - hang_x
            if self.height_measure_var.get() == "ceiling":
                hang_y = wall_height - hang_y
                
            print(f"Final hanging point (adjusted): ({hang_x:.3f}, {hang_y:.3f})")
            
            unsorted_locations[art.name] = (hang_x, hang_y)

        print("\n=== END DEBUG ===\n")
        
        # Sort by hang_x ascending, then hang_y descending
        sorted_items = sorted(unsorted_locations.items(), key=lambda kv: (kv[1][0], -kv[1][1]))
        return dict(sorted_items)
    
    def print_measurement_instructions(self):
        """Print the measurement instructions to the console"""
        instructions = self.generate_instruction_lines()
        for line in instructions:
            print(line)

    def save_measurement_instructions(self):
        """Save the measurement instructions to a file"""
        text_lines = self.generate_instruction_lines()
        if not text_lines:
            self.release_top()
            messagebox.showerror("Error", "No instructions to save.")
            self.set_to_top()
            self.on_close()
            return

        # Get the file extension based on selected file type
        extension = self.file_type_var.get()
        file_ext = {
            "excel": ".xlsx",
            "word": ".docx", 
            "pdf": ".pdf",
            "text": ".txt"
        }.get(extension, ".txt")

        # Create default filename using wall name (sanitized to remove special characters)
        wall_name = "".join(c for c in self.selected_wall.name if c.isalnum() or c in (' ', '_')).rstrip()
        default_filename = f"Installation_Instructions_{wall_name}{file_ext}"

        # Set up file dialog with default filename
        filetypes = [
            ("Word Document", "*.docx"),
            ("Excel Spreadsheet", "*.xlsx"),
            ("PDF Document", "*.pdf"),
            ("Text File", "*.txt"),
            ("All Files", "*.*")
        ]
        
        self.release_top()
        filepath = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            initialfile=default_filename,
            filetypes=filetypes,
            title="Save Installation Instructions"
        )
        self.set_to_top()
        
        if not filepath:
            return

        try:
            if extension == "excel":
                save_to_excel(text_lines, filepath)
            elif extension == "word":
                save_to_word(text_lines, filepath)
            elif extension == "pdf":
                save_to_pdf(text_lines, filepath)
            elif extension == "text":
                save_to_text(text_lines, filepath)
            else:
                raise ValueError("Unknown file type selected.")
            self.release_top()
            messagebox.showinfo("Success", f"Instructions saved to {filepath}")
            self.set_to_top()
            self.on_close()
        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to save instructions: {str(e)}")
            traceback.print_exc()  # This prints the full traceback to console
            self.release_top()
            messagebox.showerror("Error", f"Failed to save instructions:\n{e}")
            self.set_to_top()
            self.on_close()

    def generate_instruction_lines(self):
        """Generate the instruction lines for the installation"""
        locations = self.calculate_hang_locations()
        if not locations:
            return []

        wall_ref = self.wall_measure_var.get()
        height_ref = self.height_measure_var.get()
        first_name = self.first_piece_var.get()

        names = list(locations.keys())
        if first_name not in names:
            return ["Error: First piece not found in artwork list."]

        first_index = names.index(first_name)
        instructions = []

        # Add header with general instructions
        instructions.append("GALLERY WALL INSTALLATION INSTRUCTIONS")
        instructions.append("="*50)
        instructions.append(f"Wall: {self.selected_wall.name}")
        instructions.append(f"Total Artworks: {len(self.artworks)}")
        instructions.append(f"Reference Point: From {wall_ref} wall, from {height_ref}")
        instructions.append(f"Starting Piece: {first_name}")
        instructions.append("")
        instructions.append("GENERAL INSTALLATION TIPS:")
        instructions.append("- Use a level to ensure each piece is straight")
        instructions.append("- Mark all hanging points with pencil before starting")
        instructions.append("- Consider using painter's tape to test layout before installing")
        instructions.append("- For heavy pieces, use appropriate wall anchors")
        instructions.append("")
        instructions.append("MEASUREMENT INSTRUCTIONS:")
        instructions.append("="*50)

        # A) Measure from wall/floor to first piece
        first = (first_name, *locations[first_name])
        x_initial = "RIGHT" if wall_ref == "left" else "LEFT"
        y_initial = "UP" if height_ref == "floor" else "DOWN"
        x_dir = "LEFT" if wall_ref == "left" else "RIGHT"
        y_dir = "DOWN" if height_ref == "floor" else "UP"
        adjusted_y = self.selected_wall.height - first[2]
        
        instructions.append(f"1. STARTING POINT - {first[0]}:")
        instructions.append(f"   • From {wall_ref.upper()} wall edge, measure {x_initial} {first[1]:.3f}\"")
        # instructions.append(f"   • From {height_ref.upper()}, measure {y_initial} {first[2]:.3f}\"")
        instructions.append(f"   • From {height_ref.upper()}, measure {y_initial} {adjusted_y:.3f}\"")
        instructions.append(f"   • Mark this point with a pencil - this is your starting nail position")
        instructions.append("")

        # B) Forward pass (first+1 to end)
        step_num = 2  # Starts at 2 because STARTING POINT is always 1
        prev_x, prev_y = first[1], first[2]
        for i in range(first_index + 1, len(names)):
            curr = (names[i], *locations[names[i]])
            dx = abs(curr[1] - prev_x)
            dy = abs(curr[2] - prev_y)
            y_step_dir = "UP" if curr[2] > prev_y else "DOWN"

            instructions.append(f"{step_num}. {curr[0]}:")
            instructions.append(f"   • From {names[i-1]}'s nail position:")
            instructions.append(f"     → Measure {x_initial} {dx:.2f}\"")
            instructions.append(f"     → Measure {y_step_dir} {dy:.2f}\"")
            instructions.append(f"   • Mark this point for {curr[0]}'s nail")
            instructions.append("")
            
            step_num += 1
            prev_x, prev_y = curr[1], curr[2]

        # D) Backward pass (first-1 to start)
        prev_x, prev_y = first[1], first[2]
        for i in range(first_index - 1, -1, -1):
            curr = (names[i], *locations[names[i]])
            dx = abs(curr[1] - prev_x)
            dy = abs(curr[2] - prev_y)
            y_step_dir = "UP" if curr[2] > prev_y else "DOWN"

            instructions.append(f"{step_num}. {curr[0]}:")
            instructions.append(f"   • From {names[i+1]}'s nail position:")
            instructions.append(f"     → Measure {x_dir} {dx:.2f}\"")
            instructions.append(f"     → Measure {y_step_dir} {dy:.2f}\"")
            instructions.append(f"   • Mark this point for {curr[0]}'s nail")
            instructions.append("")
            
            step_num += 1
            prev_x, prev_y = curr[1], curr[2]


        # Final instructions
        instructions.append("FINAL STEPS:")
        instructions.append("="*50)
        instructions.append("- Double check all measurements before installing nails")
        instructions.append("- Install all nails at marked positions")
        instructions.append("- Hang artwork starting with your chosen first piece")
        instructions.append("- Step back periodically to check alignment and spacing")
        instructions.append("- Enjoy your beautifully arranged gallery wall!")
        
        return instructions