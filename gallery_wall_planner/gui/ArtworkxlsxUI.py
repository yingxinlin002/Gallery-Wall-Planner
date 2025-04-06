import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import webbrowser
from pathlib import Path
from PIL import Image, ImageTk  # Requires Pillow package

class ArtworkxlsxUI:
    def __init__(self, root, return_to_editor, selected_wall):
        self.root = root
        self.return_to_editor = return_to_editor
        self.selected_wall = selected_wall
        self.styles = self.get_ui_styles()
        self.init_styles(root)
        
        # Set up paths
        self.base_dir = Path(__file__).parent
        self.sample_xlsx_path = self.base_dir / "Sample_xlsx_Format.xlsx"
        self.sample_image_path = self.base_dir / "sample_xlsx_format.png"
        
        # Initialize image variables
        self.original_image = None
        self.image_tk = None
        
        self.create_ui()
        self.center_window()

    def get_ui_styles(self):
        """Return UI styles dictionary"""
        return {
            "title_font": ("Arial", 24),
            "label_font": ("Arial", 12),
            "button_font": ("Helvetica", 12, "bold"),
            "button_padx": 10,
            "button_pady": 5,
            "button_width": 15,
            "bg_primary": "#5F3FCA",  # Purple
            "bg_secondary": "#69718A",  # Gray
            "bg_success": "#4CAF50",   # Green
            "bg_info": "#2196F3",      # Blue
            "small_font": ("Arial", 10),
            "fg_white": "white"
        }

    def init_styles(self, root):
        """Initialize ttk styles"""
        style = ttk.Style(root)
        style.theme_use("clam")
        
        # Configure button styles
        style.configure("Primary.TButton",
                       background=self.styles["bg_primary"],
                       foreground=self.styles["fg_white"],
                       font=self.styles["button_font"],
                       padding=(self.styles["button_padx"], self.styles["button_pady"]))
        
        style.configure("Secondary.TButton",
                       background=self.styles["bg_secondary"],
                       foreground=self.styles["fg_white"],
                       font=self.styles["button_font"])
        
        style.configure("Info.TButton",
                       background=self.styles["bg_info"],
                       foreground=self.styles["fg_white"],
                       font=self.styles["button_font"])

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 800  # Default width
        height = 700  # Default height
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_ui(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Back button
        back_button = ttk.Button(header_frame,
                               text="← Back to Editor",
                               command=self.return_to_editor,
                               style="Secondary.TButton")
        back_button.pack(side="left", padx=10)
        
        # Title
        title_label = ttk.Label(header_frame,
                              text="Add Artwork from xlsx File",
                              style="Header.TLabel",
                              font=self.styles["title_font"])
        title_label.pack(side="left", padx=20)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Instructions
        instructions = ttk.Label(content_frame,
                               text="Please prepare an xlsx file with your artwork information using the format shown below:",
                               font=self.styles["label_font"],
                               wraplength=600,
                               justify="left")
        instructions.pack(pady=(0, 15), anchor="w")
        
        # Download sample button
        download_btn = ttk.Button(content_frame,
                                text="Download Sample xlsx File",
                                command=self.download_sample,
                                style="Info.TButton")
        download_btn.pack(pady=(0, 15))
        
        # Image display frame
        self.setup_image_display(content_frame)
        
        # Upload section
        upload_frame = ttk.Frame(content_frame)
        upload_frame.pack(fill="x", pady=(20, 15))
        
        ttk.Label(upload_frame,
                 text="Upload your xlsx file:",
                 font=self.styles["label_font"]).pack(side="left", padx=5)
        
        self.file_entry = ttk.Entry(upload_frame, width=40)
        self.file_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        browse_btn = ttk.Button(upload_frame,
                              text="Browse...",
                              command=self.browse_file,
                              style="Secondary.TButton")
        browse_btn.pack(side="left", padx=5)
        
        # Import button
        import_btn = ttk.Button(content_frame,
                              text="Import Artwork",
                              command=self.import_artwork,
                              style="Primary.TButton")
        import_btn.pack(pady=(15, 0))
        
        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_image_display(self, parent):
        """Set up the image display area with canvas and scrollbars"""
        # Container frame
        self.image_container = ttk.Frame(parent)
        self.image_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self.image_container, bg="white", highlightthickness=0)
        self.h_scroll = ttk.Scrollbar(self.image_container, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = ttk.Scrollbar(self.image_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.image_container.grid_rowconfigure(0, weight=1)
        self.image_container.grid_columnconfigure(0, weight=1)
        
        # Load the image
        self.load_sample_image()

    def load_sample_image(self):
        """Load and display the sample image"""
        try:
            # Load image using Pillow for better handling
            self.original_image = Image.open(str(self.sample_image_path))
            self.update_image_display()
        except Exception as e:
            print(f"Error loading sample image: {e}")
            self.canvas.create_text(50, 50, 
                                  text="Sample xlsx format image not found",
                                  fill="gray", anchor="nw")
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def update_image_display(self):
        """Update the image display based on current window size"""
        if not self.original_image:
            return
            
        # Get available space for the image
        canvas_width = self.image_container.winfo_width() - 20
        canvas_height = self.image_container.winfo_height() - 20
        
        if canvas_width <= 1 or canvas_height <= 1:
            return  # Window not ready yet
            
        # Calculate new size maintaining aspect ratio
        img_width, img_height = self.original_image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Resize image
        resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(resized_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Show/hide scrollbars as needed
        self.h_scroll.grid_remove()
        self.v_scroll.grid_remove()
        if new_width > canvas_width:
            self.h_scroll.grid()
        if new_height > canvas_height:
            self.v_scroll.grid()

    def on_window_resize(self, event):
        """Handle window resize event"""
        if event.widget == self.root:
            self.update_image_display()

    def download_sample(self):
        """Handle download sample button click"""
        try:
            if self.sample_xlsx_path.exists():
                # Try different methods for different OS
                try:
                    os.startfile(str(self.sample_xlsx_path))  # Windows
                except:
                    webbrowser.open(f"file://{str(self.sample_xlsx_path)}")  # Mac/Linux
                messagebox.showinfo("Success", "Sample xlsx file opened successfully!")
            else:
                messagebox.showerror("Error", f"Sample file not found at:\n{str(self.sample_xlsx_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open sample file:\n{str(e)}")

    def browse_file(self):
        """Handle file browsing"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def import_artwork(self):
        """Handle artwork import"""
        file_path = self.file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an xlsx file first")
            return
        
        try:
            # Here you would add code to actually parse the xlsx file
            # For now, just show a success message
            messagebox.showinfo("Success", f"Artwork imported from:\n{file_path}")
            self.return_to_editor()
        except Exception as e:
            messagebox.showerror("Error", f"Could not import artwork:\n{str(e)}")