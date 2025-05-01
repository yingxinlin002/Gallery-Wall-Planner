
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk
import os
import webbrowser
from gallery_wall_planner.gui.screen_base import ScreenBase
from gallery_wall_planner.gui.app_main import AppMain, ScreenType
from gallery_wall_planner.gui.ui_styles import get_ui_styles


class ScreenArtworkxlsxUI(ScreenBase):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.styles = get_ui_styles()
        self.init_styles()
        
        # Store current window size before making changes
        # self.original_geometry = self.root.geometry()
        
        # Initialize widget references
        self.image_container = None
        self.canvas = None
        self.h_scroll = None
        self.v_scroll = None
        self.file_entry = None
        
        # Set up paths
        self.base_dir = Path(__file__).parent
        self.sample_xlsx_path = self.base_dir / "Sample_xlsx_Format.xlsx"
        self.sample_image_path = self.base_dir / "sample_xlsx_format.png"
        
        # Initialize image variables
        self.original_image = None
        self.image_tk = None
        
    # TODO: Move this to a shared module
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

    # TODO: Move this to a shared module
    def init_styles(self):
        """Initialize ttk styles"""
        style = ttk.Style(self.AppMain.root)
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

    def load_content(self):
        # Prevent window from resizing during UI creation
        # self.root.withdraw()
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Back button
        back_button = ttk.Button(header_frame,
                               text="← Back to Editor",
                               command=lambda: self.AppMain.switch_screen(ScreenType.EDITOR),
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
        
        # # Restore original window size and position
        # self.root.deiconify()
        # self.root.geometry(self.original_geometry)
        
        # # Bind window resize event
        # self.root.bind("<Configure>", self.on_window_resize)

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
            if not self.sample_image_path.exists():
                raise FileNotFoundError(f"Sample image not found at {self.sample_image_path}")
            
            # Load image using Pillow for better handling
            self.original_image = Image.open(str(self.sample_image_path))
            self.update_image_display()
        except Exception as e:
            print(f"Error loading sample image: {e}")
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                self.canvas.create_text(50, 50, 
                                      text="Sample xlsx format image not found",
                                      fill="gray", anchor="nw")
                self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def update_image_display(self):
        """Update the image display based on current window size"""
        try:
            # Check if we have everything we need
            if (not hasattr(self, 'original_image') or 
                not self.original_image or 
                not hasattr(self, 'image_container') or 
                not self.image_container.winfo_exists()):
                return
                
            # Get container dimensions (returns 1 if window not ready)
            container_width = self.image_container.winfo_width()
            container_height = self.image_container.winfo_height()
            
            # Skip if container isn't ready yet
            if container_width <= 1 or container_height <= 1:
                return
                
            # Calculate available space (subtract scrollbar sizes if visible)
            canvas_width = container_width - 20
            canvas_height = container_height - 20
            
            # Ensure we have positive dimensions
            if canvas_width <= 0 or canvas_height <= 0:
                return
                
            # Get original image dimensions
            img_width, img_height = self.original_image.size
            
            # Calculate new size maintaining aspect ratio
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width = max(1, int(img_width * ratio))
            new_height = max(1, int(img_height * ratio))
            
            # Resize image
            resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
            self.image_tk = ImageTk.PhotoImage(resized_image)
            
            # Update canvas if it exists
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
                self.canvas.config(scrollregion=(0, 0, new_width, new_height))
                
                # Manage scrollbars
                self.update_scrollbars(new_width, new_height, canvas_width, canvas_height)
                
        except Exception as e:
            # Only print errors that aren't about initialization
            if "height and width must be > 0" not in str(e):
                print(f"Error updating image display: {e}")

    def update_scrollbars(self, img_width, img_height, container_width, container_height):
        """Update scrollbar visibility based on content size"""
        if not hasattr(self, 'h_scroll') or not hasattr(self, 'v_scroll'):
            return
            
        if img_width > container_width and self.h_scroll.winfo_exists():
            self.h_scroll.grid()
        else:
            self.h_scroll.grid_remove()
            
        if img_height > container_height and self.v_scroll.winfo_exists():
            self.v_scroll.grid()
        else:
            self.v_scroll.grid_remove()

    def on_window_resize(self, event):
        """Handle window resize events with debounce"""
        if not hasattr(self, 'resize_pending'):
            self.resize_pending = False
            
        if not self.resize_pending:
            self.resize_pending = True
            self.root.after(200, self.handle_delayed_resize)

    def handle_delayed_resize(self):
        """Handle the actual resize after a short delay"""
        self.resize_pending = False
        try:
            if (hasattr(self, 'image_container') and 
                self.image_container.winfo_exists() and 
                hasattr(self, 'original_image') and 
                self.original_image):
                self.update_image_display()
        except Exception as e:
            print(f"Error handling delayed resize: {e}")

    def download_sample(self):
        """Handle download sample button click"""
        try:
            if not self.sample_xlsx_path.exists():
                raise FileNotFoundError(f"Sample file not found at {self.sample_xlsx_path}")
            
            # Try different methods for different OS
            try:
                os.startfile(str(self.sample_xlsx_path))  # Windows
            except:
                webbrowser.open(f"file://{str(self.sample_xlsx_path)}")  # Mac/Linux
            messagebox.showinfo("Success", "Sample xlsx file opened successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open sample file:\n{str(e)}")

    def browse_file(self):
        """Handle file browsing"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if file_path and hasattr(self, 'file_entry') and self.file_entry.winfo_exists():
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not browse files:\n{str(e)}")

    def import_artwork(self):
        """Handle artwork import"""
        try:
            if not hasattr(self, 'file_entry') or not self.file_entry.winfo_exists():
                raise ValueError("File entry widget not available")
                
            file_path = self.file_entry.get()
            if not file_path:
                raise ValueError("Please select an xlsx file first")
            
            # TODO: Add code to parse xlsx file
            # Here you would add code to actually parse the xlsx file
            # For now, just show a success message
            messagebox.showinfo("Success", f"Artwork imported from:\n{file_path}")
            self.AppMain.switch_screen(ScreenType.EDITOR)
        except Exception as e:
            messagebox.showerror("Error", f"Could not import artwork:\n{str(e)}")
