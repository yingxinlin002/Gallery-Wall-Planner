import tkinter as tk
from gallery.gui.ui_styles import get_ui_styles


class CollapsibleMenu(tk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent,  *args, **kwargs)
        self.parent_ui = parent
        self.title = title
        self.is_expanded = True
        self.styles = get_ui_styles()
        self.sidebar_visible = True
        self.sidebar_animation_running = False
        self.toggle_btn = None
        self.content_frame = None
        self.menu_frame = None
        self.header = None
        self.sidebar_width = 300
        self.menu_frame = None


    def load_content(self):
        # Control panel with initial width
        self.content_frame = tk.Frame(self,
                                    width=self.sidebar_width,
                                    bg="#f0f0f0")
        self.content_frame.pack(side="left", fill="y")
        self.content_frame.pack_propagate(False)  # Prevent children from changing width

        # Toggle button with improved styling
        self.toggle_btn = tk.Button(self,
                                  text="◀",
                                  command=self.toggle_sidebar,
                                  bg="#e0e0e0",
                                  fg="black",
                                  bd=1,
                                  relief="raised",
                                  font=("Arial", 10),
                                  width=3)
        self.toggle_btn.pack(side="right", fill="y")

        if self.title != "":
            header = tk.Frame(self.content_frame, bg="#e0e0e0")
            header.pack(fill="x")
            tk.Label(header,
                   text=self.title,
                   font=self.styles["label_font"],
                   bg="#e0e0e0").pack(side="left", padx=5)

        self.menu_frame = tk.Frame(self.content_frame, bg="#e0e0e0", bd=1, relief="raised")
        self.menu_frame.pack(fill="x", pady=2)

    def animate_sidebar(self, target_width):
        """Smoothly animate the sidebar width change"""
        if self.sidebar_animation_running:
            return
            
        self.sidebar_animation_running = True
        
        current_width = self.content_frame.winfo_width()
        step = 15  # Pixels to move each frame
        direction = 1 if target_width > current_width else -1
        
        def update_animation():
            nonlocal current_width
            current_width += step * direction
            
            # Check if we've reached or passed the target
            if (direction == 1 and current_width >= target_width) or \
            (direction == -1 and current_width <= target_width):
                current_width = target_width
                self.content_frame.config(width=current_width)
                self.sidebar_animation_running = False
                self.finalize_sidebar_state()
                return
            
            self.content_frame.config(width=current_width)
            self.after(10, update_animation)  # Changed from self.root.after to self.after
        
        update_animation()

    def finalize_sidebar_state(self):
        """Final adjustments after animation completes"""
        if self.sidebar_visible:
            self.toggle_btn.config(text="◀")
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(side="right", fill="y")
        else:
            self.toggle_btn.config(text="▶")
            self.toggle_btn.pack_forget()
            self.toggle_btn.pack(side="left", fill="y")

    def toggle_sidebar(self):
        """Toggle sidebar visibility with animation"""
        if self.sidebar_animation_running:
            return
            
        if self.sidebar_visible:
            self.animate_sidebar(0)
        else:
            self.animate_sidebar(self.sidebar_width)
        
        self.sidebar_visible = not self.sidebar_visible
