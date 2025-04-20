class MeasurementLinesManager:
    def __init__(self, canvas, wall_ref):
        """
        Manages measurement lines and text for draggable artwork.
        Args:
            canvas: The Tkinter canvas where lines and text are drawn.
            wall_ref: Reference to the VirtualWall instance.
        """
        self.canvas = canvas
        self.wall_ref = wall_ref
        self.measurement_lines = []
        self.measurement_texts = []

    def clear_measurement_lines(self):
        """Remove all measurement lines and text."""
        for line in self.measurement_lines:
            self.canvas.delete(line)
        for text in self.measurement_texts:
            self.canvas.delete(text)
        self.measurement_lines = []
        self.measurement_texts = []

    def draw_measurement_lines(self, x1, y1, x2, y2):
        """Draw measurement lines and distances for the artwork."""
        # Clear existing measurement lines and texts
        self.clear_measurement_lines()

        # Convert to canvas coordinates
        cx1 = self.wall_ref.wall_left + x1 * self.wall_ref.scale
        cy1 = self.wall_ref.canvas_height - (self.wall_ref.wall_bottom + y2 * self.wall_ref.scale)
        cx2 = self.wall_ref.wall_left + x2 * self.wall_ref.scale
        cy2 = self.wall_ref.canvas_height - (self.wall_ref.wall_bottom + y1 * self.wall_ref.scale)

        # Wall boundaries
        wall_top = self.wall_ref.canvas_height - (self.wall_ref.wall_bottom + self.wall_ref.wall_height * self.wall_ref.scale)

        # Left measurement line
        line = self.canvas.create_line(
            self.wall_ref.wall_left, cy1, cx1, cy1,
            fill="gray", dash=(2, 2), width=1
        )
        self.measurement_lines.append(line)

        # Left distance text
        dist = x1
        text = self.canvas.create_text(
            (self.wall_ref.wall_left + cx1) / 2, cy1 - 10,
            text=f"{dist:.1f}\"",
            fill="black"
        )
        self.measurement_texts.append(text)

        # Right measurement line
        line = self.canvas.create_line(
            cx2, cy1, self.wall_ref.wall_right, cy1,
            fill="gray", dash=(2, 2), width=1
        )
        self.measurement_lines.append(line)

        # Right distance text
        dist = self.wall_ref.wall_width - x2
        text = self.canvas.create_text(
            (cx2 + self.wall_ref.wall_right) / 2, cy1 - 10,
            text=f"{dist:.1f}\"",
            fill="black"
        )
        self.measurement_texts.append(text)

        # Top measurement line
        line = self.canvas.create_line(
            cx1, wall_top, cx1, cy1,
            fill="gray", dash=(2, 2), width=1
        )
        self.measurement_lines.append(line)

        # Top distance text
        dist = self.wall_ref.wall_height - y2
        text = self.canvas.create_text(
            cx1 + 10, (wall_top + cy1) / 2,
            text=f"{dist:.1f}\"",
            fill="black"
        )
        self.measurement_texts.append(text)

        # Bottom measurement line
        line = self.canvas.create_line(
            cx1, cy2, cx1, self.wall_ref.canvas_height - self.wall_ref.wall_bottom,
            fill="gray", dash=(2, 2), width=1
        )
        self.measurement_lines.append(line)

        # Bottom distance text
        dist = y1
        text = self.canvas.create_text(
            cx1 + 10, (cy2 + self.wall_ref.canvas_height - self.wall_ref.wall_bottom) / 2,
            text=f"{dist:.1f}\"",
            fill="black"
        )
        self.measurement_texts.append(text)