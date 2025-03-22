import tkinter as tk
from tkinter import font
from gallery_wall_planner.gui.NewExhibitUI import NewGalleryUI


def create_home_menu():
    """Create the home menu with buttons."""
    for widget in root.winfo_children():
        widget.destroy()

    # Add the title label
    tk.Label(root, text="Gallery Wall Planner", font=("Arial", 24)).pack(pady=50)

    # Add the buttons
    tk.Button(root, text="New Exhibit", command=lambda: NewGalleryUI(root, create_home_menu), width=20, bg="#5F3FCA",
              fg="white", font=button_font, relief="raised", padx=10, pady=5).pack(pady=10)
    tk.Button(root, text="Load Exhibit", command=load_exhibit, width=20, bg="#5F3FCA", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=10)
    tk.Button(root, text="Quit", command=quit_application, width=20, bg="#69718A", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=10)


def load_exhibit():
    """Placeholder function for the Load Exhibit functionality."""
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text="Existing Exhibits", font=("Arial", 24)).pack(pady=50)
    tk.Button(root, text="Back to Home", command=create_home_menu, width=20, bg="#FF9800", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=20)


def quit_application():
    """Quit the application."""
    root.destroy()


# Create the main application window
root = tk.Tk()
root.title("Gallery Wall Planner")
root.geometry("1024x768")

# Define a custom font for the buttons
button_font = font.Font(family="Helvetica", size=12, weight="bold")

# Create the home menu
create_home_menu()

# Start the main event loop
root.mainloop()
