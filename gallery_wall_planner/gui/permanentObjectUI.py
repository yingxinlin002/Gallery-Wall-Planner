import tkinter as tk
from tkinter import messagebox, filedialog
from gallery_wall_planner.gui.SelectWallSpaceUI import SelectWallSpaceUI

class PermanentObjectUI:
    def __init__(self, root, return_to_previous):
        self.root = root
        self.return_to_previous = return_to_previous
        self.permanent_objects = []  # Store permanent objects
        self.create_ui()

    def create_ui(self):
        # Clear the current frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Add a title
        tk.Label(self.root, text="Permanent Objects on the Wall", font=("Arial", 24)).pack(pady=20)

        # Ask if there are permanent items
        tk.Label(self.root, text="Is there any permanent items on the wall (e.g., door, light switch)?", font=("Arial", 12)).pack(pady=10)

        # Frame for Yes/No buttons
        yes_no_frame = tk.Frame(self.root)
        yes_no_frame.pack(pady=10)

        # Yes/No buttons
        self.has_permanent_items = tk.BooleanVar(value=False)  # Default to "No"
        tk.Radiobutton(yes_no_frame, text="Yes", variable=self.has_permanent_items, value=True, command=self.show_permanent_item_inputs, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(yes_no_frame, text="No", variable=self.has_permanent_items, value=False, command=self.hide_permanent_item_inputs, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        # Frame for permanent item inputs (hidden by default)
        self.permanent_item_frame = tk.Frame(self.root)
        self.permanent_item_frame.pack(pady=10)

        # Back and Submit buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Back", command=self.return_to_previous, width=15, bg="#69718A", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Submit", command=self.submit, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(side=tk.LEFT, padx=10)

    def show_permanent_item_inputs(self):
        # Clear the frame and add input fields for permanent items
        for widget in self.permanent_item_frame.winfo_children():
            widget.destroy()

        # Name
        tk.Label(self.permanent_item_frame, text="Name:", font=("Arial", 12)).pack(pady=5)
        self.name_entry = tk.Entry(self.permanent_item_frame, font=("Arial", 12))
        self.name_entry.insert(0, "door sign")  # Placeholder text
        self.name_entry.config(fg="grey")
        self.name_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.name_entry, "door sign"))
        self.name_entry.bind("<FocusOut>", lambda event: self.add_placeholder(self.name_entry, "door sign"))
        self.name_entry.pack(pady=5)

        # Width
        tk.Label(self.permanent_item_frame, text="Width (inches):", font=("Arial", 12)).pack(pady=5)
        self.width_entry = tk.Entry(self.permanent_item_frame, font=("Arial", 12))
        self.width_entry.insert(0, "36 inches")  # Placeholder text
        self.width_entry.config(fg="grey")
        self.width_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.width_entry, "36 inches"))
        self.width_entry.bind("<FocusOut>", lambda event: self.add_placeholder(self.width_entry, "36 inches"))
        self.width_entry.pack(pady=5)

        # Height
        tk.Label(self.permanent_item_frame, text="Height (inches):", font=("Arial", 12)).pack(pady=5)
        self.height_entry = tk.Entry(self.permanent_item_frame, font=("Arial", 12))
        self.height_entry.insert(0, "72 inches")  # Placeholder text
        self.height_entry.config(fg="grey")
        self.height_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.height_entry, "72 inches"))
        self.height_entry.bind("<FocusOut>", lambda event: self.add_placeholder(self.height_entry, "72 inches"))
        self.height_entry.pack(pady=5)

        # Image Upload (optional)
        tk.Label(self.permanent_item_frame, text="Upload Image (optional):", font=("Arial", 12)).pack(pady=5)
        self.image_path = tk.StringVar()
        tk.Button(self.permanent_item_frame, text="Browse", command=self.upload_image, width=15, bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(pady=5)

        # Add button to save the permanent item
        tk.Button(self.permanent_item_frame, text="Add Permanent Object", command=self.save_permanent_object, width=20, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5).pack(pady=10)

    def hide_permanent_item_inputs(self):
        # Hide the permanent item input frame
        for widget in self.permanent_item_frame.winfo_children():
            widget.destroy()

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def add_placeholder(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    def upload_image(self):
        # Open a file dialog to upload an image
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path.set(file_path)
            messagebox.showinfo("Success", "Image uploaded successfully!")

    def save_permanent_object(self):
        # Save the permanent object details
        name = self.name_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()
        image = self.image_path.get()

        # Validate inputs
        if name == "door sign" or width == "36 inches" or height == "72 inches":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            width = float(width.replace(" inches", ""))
            height = float(height.replace(" inches", ""))
        except ValueError:
            messagebox.showerror("Error", "Width and height must be numbers.")
            return

        # Add the object to the list
        self.permanent_objects.append({
            "name": name,
            "width": width,
            "height": height,
            "image": image
        })
        messagebox.showinfo("Success", "Permanent object added successfully!")
        self.clear_inputs()

    def clear_inputs(self):
        # Clear the input fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, "door sign")
        self.name_entry.config(fg="grey")
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, "36")
        self.width_entry.config(fg="grey")
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, "72")
        self.height_entry.config(fg="grey")
        self.image_path.set("")

    def submit(self):
        # Handle the final submission
        if self.has_permanent_items.get() and not self.permanent_objects:
            messagebox.showerror("Error", "Please add at least one permanent object.")
            return

        # If "No" is selected, proceed to the next step
        if not self.has_permanent_items.get():
            SelectWallSpaceUI(self.root, self.return_to_previous)
        else:
            messagebox.showinfo("Success", "Wall information submitted successfully!")
            self.return_to_previous()
