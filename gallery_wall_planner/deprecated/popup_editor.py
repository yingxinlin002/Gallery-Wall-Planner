import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, filedialog
import os

def open_popup_editor(
    root,
    item_index,
    item_data,  # This is now our prepared dictionary
    obstacles,
    obstacle_names,
    layout_items,
    items,
    item_buttons,
    canvas,
    scale,
    wall_left,
    wall_bottom,
    canvas_height,
    move_item_to_canvas,
    check_all_collisions,
    enforce_boundaries,
    popup_windows,
):
    if item_index in popup_windows:
        popup_windows[item_index].destroy()

    # Use the provided item_data dictionary directly
    item_name = item_data["Name"]
    pos = {"x": item_data["x"], "y": item_data["y"]}
    width_val = item_data["Width"]
    height_val = item_data["Height"]
    
    bl = (pos["x"], pos["y"])
    center = (bl[0] + width_val / 2, bl[1] + height_val / 2)
    tl = (bl[0], bl[1] + height_val)
    tr = (bl[0] + width_val, bl[1] + height_val)
    br = (bl[0] + width_val, bl[1])

    def recalc_from_center(new_center):
        cx, cy = new_center
        w = float(width_var.get())
        h = float(height_var.get())
        bl_new = (cx - w / 2, cy - h / 2)
        tl_new = (bl_new[0], bl_new[1] + h)
        tr_new = (bl_new[0] + w, bl_new[1] + h)
        br_new = (bl_new[0] + w, bl_new[1])
        return bl_new, tl_new, tr_new, br_new, new_center

    popup = Toplevel(root)
    popup.title(f"Edit {item_name}")
    popup.geometry("300x400")

    content_frame = ttk.Frame(popup)
    content_frame.pack(expand=True)
    content_frame.grid_columnconfigure(0, weight=1)

    print(f"Opening popup for item_index={item_index}, data={item_data}")

    name_var = tk.StringVar(master=popup)
    width_var = tk.DoubleVar(master=popup)
    height_var = tk.DoubleVar(master=popup)


    name_var.set(item_data["Name"])
    width_var.set(width_val)
    height_var.set(height_val)

    popup_windows[item_index] = popup

    bl_var = tk.StringVar(master=popup)
    tl_var = tk.StringVar(master=popup)
    tr_var = tk.StringVar(master=popup)
    br_var = tk.StringVar(master=popup)
    center_var = tk.StringVar(master=popup)



    # bl_var = tk.StringVar(master=popup, value=f"{bl[0]:.2f}, {bl[1]:.2f}")
    # tl_var = tk.StringVar(master=popup, value=f"{tl[0]:.2f}, {tl[1]:.2f}")
    # tr_var = tk.StringVar(master=popup, value=f"{tr[0]:.2f}, {tr[1]:.2f}")
    # br_var = tk.StringVar(master=popup, value=f"{br[0]:.2f}, {br[1]:.2f}")
    # center_var = tk.StringVar(master=popup, value=f"{center[0]:.2f}, {center[1]:.2f}")

    def update_popup_fields():
        if popup.winfo_exists():
            pos = {"x": items[item_index].x, "y": items[item_index].y}
            new_bl = (pos["x"], pos["y"])
            try:
                h = float(height_var.get())
                w = float(width_var.get())
            except (tk.TclError, ValueError):
                print(f"[WARNING] Invalid height or width value for item '{item_name}' — skipping update")
                return

            new_tl = (new_bl[0], new_bl[1] + h)
            new_tr = (new_bl[0] + w, new_bl[1] + h)
            new_br = (new_bl[0] + w, new_bl[1])
            new_center = (new_bl[0] + w / 2, new_bl[1] + h / 2)
            bl_var.set(f"{new_bl[0]:.2f}, {new_bl[1]:.2f}")
            tl_var.set(f"{new_tl[0]:.2f}, {new_tl[1]:.2f}")
            tr_var.set(f"{new_tr[0]:.2f}, {new_tr[1]:.2f}")
            br_var.set(f"{new_br[0]:.2f}, {new_br[1]:.2f}")
            center_var.set(f"{new_center[0]:.2f}, {new_center[1]:.2f}")
            popup.update_idletasks()
            popup.update()


    items[item_index].update_popup_fields = update_popup_fields
    update_popup_fields()
    
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # The ability to edit physical properties is currently breaking the ability to track location while using drag and drop
    # These buttons are being hidden, and if we have time to come back and attempt to repair the connection we can add them back in
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # edit_button = ttk.Button(content_frame, text="Edit Physical Object")
    # save_button = ttk.Button(content_frame, text="Save Changes to Object")
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    ttk.Label(content_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
    name_entry = ttk.Entry(content_frame, textvariable=name_var, justify="center", state="readonly")
    name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Width:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
    width_entry = ttk.Entry(content_frame, textvariable=width_var, justify="center", state="readonly")
    width_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Height:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
    height_entry = ttk.Entry(content_frame, textvariable=height_var, justify="center", state="readonly")
    height_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

    # def enable_editing():
    #     name_entry.config(state="normal")
    #     width_entry.config(state="normal")
    #     height_entry.config(state="normal")
    #     edit_button.config(state="disabled")
    #     save_button.config(state="normal")

    # def apply_physical_changes():
    #     new_name = name_var.get().strip()
    #     try:
    #         new_width = float(width_var.get())
    #         new_height = float(height_var.get())
    #     except ValueError:
    #         messagebox.showerror("Error", "Width and Height must be numeric values")
    #         return

    #     if new_width <= 0 or new_height <= 0:
    #         messagebox.showerror("Error", "Width and Height must be greater than zero")
    #         return

    #     new_bl_x = center[0] - new_width / 2
    #     new_bl_y = center[1] - new_height / 2
    #     old_name = items[item_index].name
    #     item_obj = items[item_index]
    #     update_func = item_obj.update_popup_fields

    #     obstacles[item_index]["Name"] = new_name
    #     obstacles[item_index]["Width"] = new_width
    #     obstacles[item_index]["Height"] = new_height

    #     layout_items[new_name] = {"x": new_bl_x, "y": new_bl_y}
    #     if new_name != old_name:
    #         layout_items.pop(old_name, None)

    #     item_buttons[item_index].config(text=new_name)

    #     item_obj.name = new_name
    #     item_obj.width = new_width
    #     item_obj.height = new_height
    #     item_obj.x = new_bl_x
    #     item_obj.y = new_bl_y

    #     item_obj.update_popup_fields = update_func
    #     item_obj.update_popup_fields()
    #     move_item_to_canvas(item_index)
    #     check_all_collisions()
    #     items[item_index].update_popup_fields = update_popup_fields

    #     name_entry.config(state="disabled")
    #     width_entry.config(state="disabled")
    #     height_entry.config(state="disabled")
    #     save_button.config(state="disabled")
    #     edit_button.config(state="normal")

    # edit_button.config(command=enable_editing, state="normal")
    # save_button.config(command=apply_physical_changes, state="disabled")
    # edit_button.grid(row=3, column=0, pady=10, padx=5)
    # save_button.grid(row=3, column=1, pady=10, padx=5)

    ttk.Separator(content_frame, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)


    ttk.Label(content_frame, text="Bottom Left:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
    bl_entry = ttk.Entry(content_frame, textvariable=bl_var, justify="center")
    bl_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Top Left:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
    tl_entry = ttk.Entry(content_frame, textvariable=tl_var, justify="center")
    tl_entry.grid(row=6, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Top Right:").grid(row=7, column=0, sticky="e", padx=5, pady=2)
    tr_entry = ttk.Entry(content_frame, textvariable=tr_var, justify="center")
    tr_entry.grid(row=7, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Bottom Right:").grid(row=8, column=0, sticky="e", padx=5, pady=2)
    br_entry = ttk.Entry(content_frame, textvariable=br_var, justify="center")
    br_entry.grid(row=8, column=1, sticky="w", padx=5, pady=2)

    ttk.Label(content_frame, text="Center (editable):").grid(row=9, column=0, sticky="e", padx=5, pady=2)
    center_entry = ttk.Entry(content_frame, textvariable=center_var, justify="center")
    center_entry.grid(row=9, column=1, sticky="w", padx=5, pady=2)

    def update_coordinates(source_field):
        try:
            new_x, new_y = map(float, eval(f"{source_field}_var").get().split(','))
            w = float(width_var.get())
            h = float(height_var.get())

            if source_field == "bl":
                new_bl = (new_x, new_y)
            elif source_field == "tl":
                new_bl = (new_x, new_y - h)
            elif source_field == "tr":
                new_bl = (new_x - w, new_y - h)
            elif source_field == "br":
                new_bl = (new_x - w, new_y)
            elif source_field == "center":
                new_bl = (new_x - w / 2, new_y - h / 2)

            new_bl = enforce_boundaries(new_bl[0], new_bl[1], w, h)
            new_tl = (new_bl[0], new_bl[1] + h)
            new_tr = (new_bl[0] + w, new_bl[1] + h)
            new_br = (new_bl[0] + w, new_bl[1])
            new_center = (new_bl[0] + w / 2, new_bl[1] + h / 2)

            bl_var.set(f"{new_bl[0]:.2f}, {new_bl[1]:.2f}")
            tl_var.set(f"{new_tl[0]:.2f}, {new_tl[1]:.2f}")
            tr_var.set(f"{new_tr[0]:.2f}, {new_tr[1]:.2f}")
            br_var.set(f"{new_br[0]:.2f}, {new_br[1]:.2f}")
            center_var.set(f"{new_center[0]:.2f}, {new_center[1]:.2f}")

            layout_items[item_name] = {"x": new_bl[0], "y": new_bl[1]}
            items[item_index].x = new_bl[0]
            items[item_index].y = new_bl[1]
            move_item_to_canvas(item_index)
            check_all_collisions()
        except ValueError:
            pass

    bl_entry.bind("<FocusOut>", lambda e: update_coordinates("bl"))
    tl_entry.bind("<FocusOut>", lambda e: update_coordinates("tl"))
    tr_entry.bind("<FocusOut>", lambda e: update_coordinates("tr"))
    br_entry.bind("<FocusOut>", lambda e: update_coordinates("br"))
    center_entry.bind("<FocusOut>", lambda e: update_coordinates("center"))

    def save_popup():
        try:
            cx_str, cy_str = center_var.get().split(',')
            new_center = (float(cx_str.strip()), float(cy_str.strip()))
        except Exception:
            messagebox.showerror("Error", "Center must be entered as 'x, y'")
            return

        w = float(width_var.get())
        h = float(height_var.get())
        new_bl, new_tl, new_tr, new_br, new_center = recalc_from_center(new_center)
        corrected_x, corrected_y = enforce_boundaries(new_bl[0], new_bl[1], w, h)
        corrected_bl = (corrected_x, corrected_y)
        corrected_tl = (corrected_bl[0], corrected_bl[1] + h)
        corrected_tr = (corrected_bl[0] + w, corrected_bl[1] + h)
        corrected_br = (corrected_bl[0] + w, corrected_bl[1])
        corrected_center = (corrected_bl[0] + w / 2, corrected_bl[1] + h / 2)

        bl_var.set(f"{corrected_bl[0]:.2f}, {corrected_bl[1]:.2f}")
        tl_var.set(f"{corrected_tl[0]:.2f}, {corrected_tl[1]:.2f}")
        tr_var.set(f"{corrected_tr[0]:.2f}, {corrected_tr[1]:.2f}")
        br_var.set(f"{corrected_br[0]:.2f}, {corrected_br[1]:.2f}")

        layout_items[item_name] = {"x": corrected_bl[0], "y": corrected_bl[1]}
        items[item_index].x = corrected_bl[0]
        items[item_index].y = corrected_bl[1]
        move_item_to_canvas(item_index)
        check_all_collisions()
        popup.on_close()

    ttk.Button(content_frame, text="Save", command=save_popup).grid(row=18, column=0, columnspan=2, pady=10)

    # Final rebind to ensure drag-drop has the latest reference
    items[item_index].update_popup_fields = update_popup_fields
    update_popup_fields()

# Note: This implementation assumes `items` is initialized externally
# and `items[item_index].update_popup_fields` can be safely assigned here.
# If modularizing further, consider passing a handler or item reference directly instead.
