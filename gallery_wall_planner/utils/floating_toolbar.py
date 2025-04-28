import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

class FloatingToolbar:
    def __init__(self, parent_canvas: tk.Canvas, 
                 on_edit_callback: Callable[[], None], 
                 on_lock_toggle_callback: Callable[[], None]):
        """
        Initialize the floating toolbar with edit and lock/unlock functionality.

        Args:
            parent_canvas: The canvas where the toolbar will appear
            on_edit_callback: Function to call when edit button is clicked
            on_lock_toggle_callback: Function to call when lock button is clicked
        """
        self.parent_canvas = parent_canvas
        self._visible = False
        self._x = 0
        self._y = 0
        
        # Create toolbar frame with shadow effect
        self.toolbar_frame = tk.Frame(
            parent_canvas,
            bg="#f0f0f0",
            bd=1,
            relief="raised",
            padx=2,
            pady=2
        )
        
        # Add subtle shadow
        self.shadow = tk.Frame(
            parent_canvas,
            bg="#c0c0c0",
            bd=0
        )
        
        # Configure buttons with consistent styling
        button_style = {
            'bg': "#e0e0e0",
            'fg': "black",
            'font': ("Arial", 10),
            'activebackground': "#d0d0d0",
            'padx': 10,
            'pady': 5,
            'relief': "flat",
            'borderwidth': 1
        }
        
        # Lock/Unlock button
        self.lock_button = tk.Button(
            self.toolbar_frame,
            text="🔓 Lock/Unlock",
            command=on_lock_toggle_callback,
            **button_style
        )
        self.lock_button.pack(side="left", padx=2)
        
        # Edit button
        self.edit_button = tk.Button(
            self.toolbar_frame,
            text="✏️ Edit",
            command=on_edit_callback,
            **button_style
        )
        self.edit_button.pack(side="left", padx=2)
        
        # Close button
        self.close_button = tk.Button(
            self.toolbar_frame,
            text="×",
            command=self.hide,
            bg="#f0f0f0",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=6,
            pady=1,
            borderwidth=0,
            activebackground="#e0e0e0"
        )
        self.close_button.pack(side="right")
        
        # Initially hidden
        self.hide()

    @property
    def visible(self) -> bool:
        """Return whether the toolbar is currently visible."""
        return self._visible

    @property
    def position(self) -> tuple[int, int]:
        """Return the current position of the toolbar."""
        return (self._x, self._y)

    def show(self, x: int, y: int) -> None:
        """
        Show the toolbar at the specified coordinates.
        
        Args:
            x: X coordinate relative to parent canvas
            y: Y coordinate relative to parent canvas
        """
        # Adjust position to keep toolbar fully visible
        canvas_width = self.parent_canvas.winfo_width()
        canvas_height = self.parent_canvas.winfo_height()
        
        # Estimate toolbar size (update after first show)
        toolbar_width = 200  # Initial estimate
        toolbar_height = 40
        
        # Adjust position if near edges
        x = min(max(x, 10), canvas_width - toolbar_width - 10)
        y = min(max(y, 10), canvas_height - toolbar_height - 10)
        
        # Show shadow first
        self.shadow.place(
            x=x+2,
            y=y+2,
            width=toolbar_width,
            height=toolbar_height
        )
        
        # Show main toolbar
        self.toolbar_frame.place(x=x, y=y)
        self._x = x
        self._y = y
        self._visible = True
        
        # Update actual size after first show
        self.toolbar_frame.update_idletasks()
        toolbar_width = self.toolbar_frame.winfo_width()
        toolbar_height = self.toolbar_frame.winfo_height()

    def hide(self) -> None:
        """Hide the toolbar and its shadow."""
        self.toolbar_frame.place_forget()
        self.shadow.place_forget()
        self._visible = False

    def update_lock_button(self, is_locked: bool) -> None:
        """Update the lock button appearance based on current state."""
        if is_locked:
            self.lock_button.config(text="🔒 Locked", bg="#ffcccc")
        else:
            self.lock_button.config(text="🔓 Unlocked", bg="#e0e0e0")