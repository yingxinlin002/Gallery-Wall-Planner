import tkinter as tk
from tkinter import ttk
from gallery_wall_planner.gui.app_main import AppMain
from tkinter import ttk, filedialog, messagebox
import openpyxl
from gallery_wall_planner.utils.export_helpers import (
    save_to_excel,
    save_to_text,
    save_to_word,
    save_to_pdf
)


def open_install_instruct_popup(root, selected_wall, artwork_items):
    InstallInstructionPopup(root, selected_wall, artwork_items)


class InstallInstructionPopup(tk.Toplevel):
    def __init__(self, root, selected_wall, artworks):
        super().__init__(root)
        self.selected_wall = selected_wall
        self.artworks = artworks

        # Make the window stay on top
        self.attributes("-topmost", True)

        self.geometry("400x500")
        self.title("Installation Instructions")

        # Make sure window stays on top while it's open
        self.transient(root)  # Set as transient window of parent
        self.grab_set()       # Grab all events to this window
        # When window closes, release the grab
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # ----------------------------------
        # -------- First Piece Hung --------
        # ----------------------------------
        ttk.Label(self, text="First Piece Hung", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(10, 0))
        self.first_piece_var = tk.StringVar(value=artworks[0].name if artworks else "")
        for art in artworks:
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

        def on_save():
            self.print_measurement_instructions()
            self.save_measurement_instructions()

        ttk.Button(button_frame, text="Save", command=on_save).pack(side="right", padx=10)

    def on_close(self):
        """Handle window closing"""
        self.grab_release()
        self.destroy()
        
    def print_and_save(self):
        self.print_measurement_instructions()
        self.save_measurement_instructions()

    def calculate_hang_locations(self):
        unsorted_locations = {}
        wall_width = self.selected_wall.width
        wall_height = self.selected_wall.height


        for art in self.artworks:
            # Get position from Artwork object directly (using WallObject's position property)
            x1 = art.position.x
            x2 = art.position.x + art.width
            y_top = art.position.y + art.height  # Top edge of artwork
            hang_height = art.hanging_point  # Using hanging_point from Artwork class

            # Calculate hanging coordinates
            hang_x = (x1 + x2) / 2  # Center of artwork
            hang_y = y_top - hang_height  # Hanging point position

            # Adjust based on measurement preferences
            if self.wall_measure_var.get() == "right":
                hang_x = wall_width - hang_x
            if self.height_measure_var.get() == "ceiling":
                hang_y = wall_height - hang_y

            unsorted_locations[art.name] = (hang_x, hang_y)

        # Sort by hang_x ascending, then hang_y descending
        sorted_items = sorted(unsorted_locations.items(), key=lambda kv: (kv[1][0], -kv[1][1]))
        return dict(sorted_items)

    def print_measurement_instructions(self):
        locations = self.calculate_hang_locations()
        if not locations:
            return

        wall_ref = self.wall_measure_var.get()
        height_ref = self.height_measure_var.get()
        first_name = self.first_piece_var.get()

        names = list(locations.keys())
        if first_name not in names:
            print("Error: First piece not found in artwork list.")
            return

        first_index = names.index(first_name)

        # A) Measure from wall/floor to first piece
        first = (first_name, *locations[first_name])
        x_initial = "RIGHT" if wall_ref == "left" else "LEFT"
        y_initial = "UP" if height_ref == "floor" else "DOWN"
        x_dir = "LEFT" if wall_ref == "left" else "RIGHT"
        y_dir = "DOWN" if height_ref == "floor" else "UP"
        print(f"FROM {wall_ref.upper()} WALL measure {x_initial} {first[1]:.2f}. FROM {height_ref.upper()} measure {y_initial} {first[2]:.2f}")

        # B) Forward pass (first+1 to end)
        prev_x, prev_y = first[1], first[2]
        for i in range(first_index + 1, len(names)):
            curr = (names[i], *locations[names[i]])
            dx = abs(curr[1] - prev_x)
            dy = abs(curr[2] - prev_y)
            if curr[2] > prev_y:
              print(f"FROM {names[i-1]} measure {x_initial} {dx:.2f}, and {y_initial} {dy:.2f}")
            else:
              print(f"FROM {names[i-1]} measure {x_initial} {dx:.2f}, and {y_dir} {dy:.2f}")
            prev_x, prev_y = curr[1], curr[2]

        # D) Backward pass (first-1 to start)
        prev_x, prev_y = first[1], first[2]
        for i in range(first_index - 1, -1, -1):
            curr = (names[i], *locations[names[i]])
            dx = (curr[1] - prev_x)
            dy = (curr[2] - prev_y)
            if curr[2] < prev_y:
                print(f"FROM {names[i+1]} measure {x_dir} {abs(dx):.2f}, and {y_dir} {abs(dy):.2f}")
            else:
                print(f"FROM {names[i+1]} measure {x_dir} {abs(dx):.2f}, and {y_initial} {abs(dy):.2f}")
            prev_x, prev_y = curr[1], curr[2]

        # E) Final message
        print("ALL ART SHOULD BE HUNG")


    def save_measurement_instructions(self):
        text_lines = self.generate_instruction_lines()
        if not text_lines:
            messagebox.showerror("Error", "No instructions to save.")
            return

        filetypes = [("All Files", "*.*")]
        extension = self.file_type_var.get()
        initial_ext = {"excel": ".xlsx", "word": ".docx", "pdf": ".pdf", "text": ".txt"}.get(extension, ".txt")
        filepath = filedialog.asksaveasfilename(defaultextension=initial_ext, filetypes=filetypes)
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
            messagebox.showinfo("Success", f"Instructions saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save instructions:\n{e}")
