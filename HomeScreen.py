import tkinter as tk
from tkinter import messagebox, font


def new_exhibit():
    # Create a popup window for new exhibit options
    popup = tk.Toplevel(root)
    popup.title("New Exhibit")
    popup.geometry("300x150")

    # Function to handle the "Start from Scratch" option
    def start_from_scratch():
        messagebox.showinfo("New Exhibit", "Starting a new exhibit from scratch.")
        popup.destroy()

    # Function to handle the "Load from an Existing Wall" option
    def load_from_existing():
        messagebox.showinfo("New Exhibit", "Loading from an existing wall.")
        popup.destroy()

    # Add buttons to the popup window
    tk.Button(popup, text="Start from Scratch", command=start_from_scratch, width=20, bg="#B95CF4", fg="white",
              font=button_font, relief="raised", padx=10, pady=5).pack(pady=10)
    tk.Button(popup, text="Load from an Existing Wall", command=load_from_existing, width=20, bg="#B95CF4", fg="white",
              font=button_font, relief="raised", padx=10, pady=5).pack(pady=10)


def load_exhibit():
    # Clear the current frame and load the existing exhibits page
    for widget in root.winfo_children():
        widget.destroy()

    # Add a label for the existing exhibits page
    tk.Label(root, text="Existing Exhibits", font=("Arial", 24)).pack(pady=50)

    # Add a back button to return to the home menu
    tk.Button(root, text="Back to Home", command=create_home_menu, width=20, bg="#7D7098", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=20)


def quit_application():
    root.destroy()


def create_home_menu():
    # Clear the current frame and create the home menu
    for widget in root.winfo_children():
        widget.destroy()

    # Add the title label
    tk.Label(root, text="Gallery Wall Planner", font=("Arial", 24)).pack(pady=50)

    # Styling the buttons
    tk.Button(root, text="New Exhibit", command=new_exhibit, width=20, bg="#B95CF4", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=10)
    tk.Button(root, text="Load Exhibit", command=load_exhibit, width=20, bg="#B95CF4", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=10)
    tk.Button(root, text="Quit", command=quit_application, width=20, bg="#B95CF4", fg="white", font=button_font,
              relief="raised", padx=10, pady=5).pack(pady=10)


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
