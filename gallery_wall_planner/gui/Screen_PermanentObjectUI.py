import tkinter as tk
from tkinter import messagebox, filedialog
from gallery_wall_planner.gui.ui_styles import get_ui_styles
from gallery_wall_planner.models.permanentObject import PermanentObject
import re
from gallery_wall_planner.gui.Screen_Base import Screen_Base
from gallery_wall_planner.gui.AppMain import AppMain, ScreenType

class Screen_PermanentObjectUI(Screen_Base):
    def __init__(self, AppMain : AppMain, *args, **kwargs):
        super().__init__(AppMain, *args, **kwargs)
        self.name_entry = None
        self.has_permanent_items = None
        self.wall = AppMain.gallery.current_wall
        self.styles = get_ui_styles()
        self.rdb_add_permanent_object_yes = None
        self.rdb_add_permanent_object_no = None
        self.submit_button = None
        self.home_button = None
        self.add_permanent_object_button = None
        self.browse_button = None

    def load_content(self):

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Fixed top section
        top_frame = tk.Frame(container)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Permanent Objects on the Wall", font=self.styles["title_font"]).pack(pady=20)
        tk.Label(top_frame, text="Is there any permanent items on the wall (e.g., door, light switch)?",
                font=self.styles["label_font"]).pack(pady=10)

        yes_no_frame = tk.Frame(top_frame)
        yes_no_frame.pack(pady=10)

        self.has_permanent_items = tk.BooleanVar(value=False)
        self.rdb_add_permanent_object_yes = tk.Radiobutton(yes_no_frame, text="Yes", variable=self.has_permanent_items, value=True,
                      command=self.show_permanent_item_inputs, font=self.styles["label_font"])
        self.rdb_add_permanent_object_yes.pack(side=tk.LEFT, padx=5)
        self.rdb_add_permanent_object_no = tk.Radiobutton(yes_no_frame, text="No", variable=self.has_permanent_items, value=False,
                      command=self.hide_permanent_item_inputs, font=self.styles["label_font"])
        self.rdb_add_permanent_object_no.pack(side=tk.LEFT, padx=5)

        # Scrollable middle section
        middle_frame = tk.Frame(container)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(middle_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(middle_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_content = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.permanent_item_frame = tk.Frame(self.scrollable_content)
        self.permanent_item_frame.pack(pady=10, fill="x")

        self.object_preview_frame = tk.Frame(self.scrollable_content)
        self.object_preview_frame.pack(pady=10, fill="x")

        # Fixed bottom section
        button_frame = tk.Frame(container)
        button_frame.pack(side="bottom", fill="x", pady=20)

        self.home_button = tk.Button(button_frame, text="Home", command=lambda : self.AppMain.switch_screen(ScreenType.HOME), width=self.styles["button_width"],
                 bg=self.styles["bg_secondary"], fg=self.styles["fg_white"], font=self.styles["button_font"],
                 relief="raised", padx=self.styles["button_padx"], pady=self.styles["button_pady"])
        self.home_button.pack(side=tk.LEFT, padx=10)

        self.submit_button = tk.Button(button_frame, text="Submit", command=self.submit, width=self.styles["button_width"],
                                      bg=self.styles["bg_success"], fg=self.styles["fg_white"], font=self.styles["button_font"],
                                      relief="raised", padx=self.styles["button_padx"], pady=self.styles["button_pady"])
        self.submit_button.pack(side=tk.RIGHT, padx=10)
        self.submit_button.config(state="normal")

    def show_permanent_item_inputs(self):
        for widget in self.permanent_item_frame.winfo_children():
            widget.destroy()

        input_preview_container = tk.Frame(self.permanent_item_frame)
        input_preview_container.pack(fill="both", expand=True)

        # Input fields frame
        input_frame = tk.Frame(input_preview_container)
        input_frame.pack(side="left", padx=20, pady=10)

        # Name field
        tk.Label(input_frame, text="Name:", font=self.styles["label_font"]).pack(pady=5)
        self.name_entry = tk.Entry(input_frame, font=self.styles["label_font"])
        self.name_entry.insert(0, "door sign")
        self.name_entry.config(fg="grey")
        self.name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.name_entry, "door sign"))
        self.name_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.name_entry, "door sign"))
        self.name_entry.pack(pady=5)

        # Width field
        tk.Label(input_frame, text="Width (inches):", font=self.styles["label_font"]).pack(pady=5)
        self.width_entry = tk.Entry(input_frame, font=self.styles["label_font"])
        self.width_entry.insert(0, "36")
        self.width_entry.config(fg="grey")
        self.width_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.width_entry, "36"))
        self.width_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.width_entry, "36"))
        self.width_entry.pack(pady=5)

        # Height field
        tk.Label(input_frame, text="Height (inches):", font=self.styles["label_font"]).pack(pady=5)
        self.height_entry = tk.Entry(input_frame, font=self.styles["label_font"])
        self.height_entry.insert(0, "72")
        self.height_entry.config(fg="grey")
        self.height_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.height_entry, "72"))
        self.height_entry.bind("<FocusOut>", lambda e: self.add_placeholder(self.height_entry, "72"))
        self.height_entry.pack(pady=5)

        # Image upload
        tk.Label(input_frame, text="Upload Image (optional):", font=self.styles["label_font"]).pack(pady=5)
        self.image_path = tk.StringVar()
        self.browse_button = tk.Button(input_frame, text="Browse", command=self.upload_image, width=self.styles["button_width"],
                 bg=self.styles["bg_info"], fg=self.styles["fg_white"], font=self.styles["button_font"],
                 relief="raised", padx=self.styles["button_padx"], pady=self.styles["button_pady"])
        self.browse_button.pack(pady=5)

        # Add button
        self.add_permanent_object_button = tk.Button(input_frame, text="Add Permanent Object", command=self.save_permanent_object,
                 width=20, bg=self.styles["bg_success"], fg=self.styles["fg_white"], font=self.styles["button_font"],
                 relief="raised", padx=self.styles["button_padx"], pady=self.styles["button_pady"])
        self.add_permanent_object_button.pack(pady=10)

        # Preview frame
        preview_frame = tk.Frame(input_preview_container, padx=20, pady=10)
        preview_frame.pack(side="right", fill="both", expand=True)
        self.object_preview_frame = tk.Frame(preview_frame)
        self.object_preview_frame.pack(fill="both", expand=True)
        self.refresh_object_preview()

    def hide_permanent_item_inputs(self):
        for widget in self.permanent_item_frame.winfo_children():
            widget.destroy()
        for widget in self.object_preview_frame.winfo_children():
            widget.destroy()
        self.submit_button.config(state="normal")

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def add_placeholder(self, entry, placeholder):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path.set(file_path)
            messagebox.showinfo("Success", "Image uploaded successfully!")

    def save_permanent_object(self):
        name = self.name_entry.get()
        width = self.width_entry.get()
        height = self.height_entry.get()
        image_path = self.image_path.get()

        if name == "" or width == "" or height == "":
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            width = float(re.sub(r"[^0-9.]", "", width).strip())
            height = float(re.sub(r"[^0-9.]", "", height).strip())

            # Create PermanentObject instance
            permanent_obj = PermanentObject(
                name=name,
                width=width,
                height=height,
                image_path=image_path if image_path else None
            )

            # Add to wall (position will be set in LockObjectsToWall)
            self.wall.add_permanent_object(permanent_obj)

            self.clear_inputs()
            self.refresh_object_preview()
            self.submit_button.config(state="normal")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid dimensions: {str(e)}")

    def refresh_object_preview(self):
        for widget in self.object_preview_frame.winfo_children():
            widget.destroy()

        permanent_objects = self.wall.permanent_objects
        if not permanent_objects:
            tk.Label(self.object_preview_frame, 
                     text="No permanent objects added yet",
                     font=self.styles["label_font"],
                     fg="gray").pack(pady=20)
            return

        tk.Label(self.object_preview_frame, 
                 text="Saved Permanent Objects:",
                 font=self.styles["label_font"]).pack(pady=(0, 10))

        canvas = tk.Canvas(self.object_preview_frame, height=200)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.object_preview_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        objects_container = tk.Frame(canvas)
        canvas.create_window((0, 0), window=objects_container, anchor="nw")

        for index, obj in enumerate(permanent_objects):
            obj_frame = tk.Frame(objects_container)
            obj_frame.pack(fill="x", padx=5, pady=2)

            label_text = f"{obj.name} - {obj.width}\" x {obj.height}\""
            tk.Label(obj_frame, text=label_text, font=self.styles["label_font"]).pack(side="left")

            delete_btn = tk.Button(obj_frame, text="×", 
                                 command=lambda i=index: self.delete_object(i),
                                 font=("Arial", 10, "bold"),
                                 fg="red",
                                 bd=0,
                                 relief="flat",
                                 activeforeground="darkred")
            delete_btn.pack(side="right")

            # Add hover effect
            delete_btn.bind("<Enter>", lambda e, btn=delete_btn: btn.config(fg="darkred"))
            delete_btn.bind("<Leave>", lambda e, btn=delete_btn: btn.config(fg="red"))

    def delete_object(self, index):
        # Get the object to delete
        obj = self.wall.permanent_objects[index]
        self.wall.remove_permanent_object(obj)
        self.refresh_object_preview()

        if not self.wall.permanent_objects and self.has_permanent_items.get():
            self.submit_button.config(state="disabled")

    def clear_inputs(self):
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
        if len(self.wall.permanent_objects) > 0:
            self.AppMain.switch_screen(ScreenType.LOCK_OBJECTS_TO_WALL)
        else:
            self.AppMain.switch_screen(ScreenType.SELECT_WALL_SPACE)
            # if self.has_permanent_items.get():
            #     if not self.wall.get_permanent_objects():
            #         messagebox.showwarning("Missing Data", "You must add at least one permanent object before proceeding.")
            #         return
            #
            #     for widget in self.root.winfo_children():
            #         widget.destroy()
            #     launch_lock_objects_ui(self.root, self.wall)
            # else:
            #     for widget in self.root.winfo_children():
            #         widget.destroy()
            #     SelectWallSpaceUI(self.root, self.return_to_previous)