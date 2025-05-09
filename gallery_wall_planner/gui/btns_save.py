import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gallery_wall_planner.gui.app_main import AppMain

from gallery_wall_planner.models import project_exporter



class BTNSSave(ttk.Frame):
    def __init__(self, parent, app_main: AppMain, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.save_btn = None
        self.save_as_btn = None
        self.app_main: AppMain = app_main

    def load_content(self):
        self.save_btn = tk.Button(self, text="Save", command=self.save, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5)
        self.save_btn.pack(pady=10, side="left")

        if self.app_main.save_file_path is not None:
            self.add_save_as_button()

    def save(self):
        print("Save")
        if self.app_main.save_file_path is not None:
            try:
                project_exporter.export_gallery_to_excel(self.app_main.save_file_path, self.app_main.gallery)
                print(f"[INFO] Project saved to {self.app_main.save_file_path}")
                messagebox.showinfo("Success", "Project saved successfully")
            except Exception as e:
                print(f"[ERROR] Could not save project: {str(e)}")
                messagebox.showerror("Error", f"Could not save project:\n{str(e)}")
        else:
            self.save_as()

    def save_as(self):
        print("Save As")
        try:
            file_path = filedialog.asksaveasfilename(
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if file_path:
                # Ensure file_path ends with .xlsx extension
                if not file_path.lower().endswith('.xlsx'):
                    file_path += '.xlsx'
                try:
                    project_exporter.export_gallery_to_excel(file_path, self.app_main.gallery)
                    self.app_main.save_file_path = file_path
                    print(f"[INFO] Project saved to {file_path}")
                    messagebox.showinfo("Success", "Project saved successfully")
                    if self.save_as_btn is None:
                        self.add_save_as_button()
                except Exception as e:
                    print(f"[ERROR] Could not save project: {str(e)}")
                    messagebox.showerror("Error", f"Could not save project:\n{str(e)}")
        except Exception as e:
            import traceback
            print(f"[ERROR] Could not browse files: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Could not browse files:\n{str(e)}")
        
    def add_save_as_button(self):
        self.save_as_btn = tk.Button(self, text="Save As", command=self.save_as, width=15, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief="raised", padx=10, pady=5)
        self.save_as_btn.pack(pady=10, side="right")
        