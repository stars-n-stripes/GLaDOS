import tkinter as tk     # python 3
# import Tkinter as tk   # python 2

# Based off of a movable token example from
# https://stackoverflow.com/questions/6740855/board-drawing-code-to-move-an-oval/6789351#6789351

class Example(tk.Frame):
    """Illustrate how to drag items on a Tkinter canvas"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # create a canvas
        self.canvas = tk.Canvas(width=200, height=200, background="white")
        # self.canvas.pack(fill="both", expand=True)
        # self.canvas.pack()
        self.controls = tk.Frame(width=400, height=400)
        self.controls.pack(fill="both", expand=True)

        # this data is used to keep track of an
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # create a couple of movable objects
        self.create_token(100, 100, "black")
        self.create_token(200, 100, "black")

        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

        # Create three vertical sliders for the 9g servos
        self.controls.twist = tk.Scale(orient="horizontal")
        self.controls.neck = tk.Scale()
        self.controls.arm = tk.Scale()
        self.controls.head = tk.Scale()
        self.controls.head.pack(side=tk.BOTTOM)
        self.controls.arm.pack(side=tk.BOTTOM)
        self.controls.neck.pack(side=tk.BOTTOM)
        self.controls.twist.pack(side=tk.TOP, expand=True, fill="x")
        # Create a horizontal slider for the 20kg servo


    def create_servoctl(self, x, y, horizontal=False):
        """
        Create a tk scale, place it on the canvas, and associate it with a servo

        """
        o = "horizontal" if horizontal else "vertical"
        self.canvas

    def create_token(self, x, y, color):
        """Create a token at the given coordinate in the given color"""
        self.canvas.create_oval(
            x - 25,
            y - 25,
            x + 25,
            y + 25,
            outline=color,
            fill=color,
            tags=("token",),
        )

    def drag_start(self, event):
        """Begining drag of an object"""
        # record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        """End drag of an object"""
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def drag(self, event):
        """Handle dragging of an object"""
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()