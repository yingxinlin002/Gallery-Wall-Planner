import tkinter as tk
import math

class PointDistanceApp:
    def __init__(self, master):
        self.master = master
        master.title("Point Distance Calculator")

        self.canvas = tk.Canvas(master, width=400, height=300, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.point1 = None
        self.point2 = None
        self.distance_label = tk.Label(master, text="Distance: ")
        self.distance_label.pack()

    def on_click(self, event):
        x, y = event.x, event.y
        if self.point1 is None:
            self.point1 = (x, y)
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")
        elif self.point2 is None:
            self.point2 = (x, y)
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue")
            self.calculate_distance()
            self.point1 = None
            self.point2 = None
        else:
            self.point1 = (x, y)
            self.point2 = None
            self.canvas.delete("all")
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")
            self.distance_label.config(text="Distance: ")
            
    def calculate_distance(self):
        x1, y1 = self.point1
        x2, y2 = self.point2
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        self.distance_label.config(text=f"Distance: {distance:.2f}")

root = tk.Tk()
app = PointDistanceApp(root)
root.mainloop()