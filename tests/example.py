import tkinter as tk

class GalleryPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Gallery Planner")

        # Create a canvas
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw guide lines (snap lines)
        self.snap_lines = [100, 200, 300, 400, 500]
        for line in self.snap_lines:
            self.canvas.create_line(line, 0, line, 400, fill="lightgray", dash=(2, 2))  # Vertical lines
            self.canvas.create_line(0, line, 600, line, fill="lightgray", dash=(2, 2))  # Horizontal lines

        # Create a draggable artwork (rectangle)
        self.artwork = self.canvas.create_rectangle(50, 50, 150, 150, fill="blue", tags="draggable")

        # Bind mouse events
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag)

        self.offset_x = 0
        self.offset_y = 0
        self.snap_threshold = 8  # Pixels within which snapping occurs

    def on_press(self, event):
        """Store the initial offset when clicking the artwork."""
        x1, y1, x2, y2 = self.canvas.coords("draggable")
        self.offset_x = event.x - x1
        self.offset_y = event.y - y1

    def on_drag(self, event):
        """Move the artwork while dragging and apply snapping in real-time."""
        x, y = event.x - self.offset_x, event.y - self.offset_y
        
        # Find closest snapping positions
        snap_x = min(self.snap_lines, key=lambda line: abs(line - x))
        snap_y = min(self.snap_lines, key=lambda line: abs(line - y))

        # Apply snapping if within threshold
        if abs(snap_x - x) < self.snap_threshold:
            x = snap_x
        if abs(snap_y - y) < self.snap_threshold:
            y = snap_y

        # Move the rectangle to the new snapped position
        self.canvas.coords("draggable", x, y, x + 100, y + 100)

if __name__ == "__main__":
    root = tk.Tk()
    app = GalleryPlanner(root)
    root.mainloop()