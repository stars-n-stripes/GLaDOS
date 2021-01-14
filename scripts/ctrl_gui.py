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
        self.canvas.pack()
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

        self.create_servoctl()





    def create_servoctl(self):
        """
        Create a tk scale, place it on the canvas, and associate it with a servo
        Also create all three servos - we don't want to be able to instantiate any more/less than 3

        """
        # Create three vertical sliders for the 9g servos
        # Create a horizontal slider for the 20kg servo
        self.controls.twist = tk.Scale(orient="horizontal")
        self.controls.neck = tk.Scale()
        self.controls.arm = tk.Scale()
        self.controls.head = tk.Scale()
        self.controls.head.pack(side=tk.LEFT)
        self.controls.arm.pack(side=tk.LEFT)
        self.controls.neck.pack(side=tk.LEFT)
        self.controls.twist.pack(side=tk.TOP, expand=True, fill="x")

        # Build three ovals
        # Head
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        self.head_oval = self.canvas.create_oval(
            x=c_width/4,
            y=c_height/4,
            outline="black",
            fill="white",
            tags=("servogui")
        )
        self.neck_oval = self.canvas.create_oval(
            x=c_width/3,
            y=c_height/3,
            outline="black",
            fill="white",
            tags=("servogui")
        )
        self.arm_oval = self.canvas.create_oval(
            x=3*c_width/2,
            y=3*c_height/2,
            outline="black",
            fill="white",
            tags=("servogui")
        )


        # Add connecting lines
        self.head_neck_line = self.canvas.create_line(
            c_width/4,
            c_height/4,
            c_width / 3,
            c_height / 3,
            fill="black"
        )
        self.neck_arm_line = self.canvas.create_line(
            x=c_width/3,
            y=c_height/3,
            fill="black"
        )



    def create_token(self, x, y, color, tag=None):
        """Create a token at the given coordinate in the given color"""
        t = ("token", tag) if tag else ("token")
        self.canvas.create_oval(
            x - 25,
            y - 25,
            x + 25,
            y + 25,
            outline=color,
            fill=color,
            tags=t
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
    def console_servo(self,value, servo="no_name"):
        print(servo, ": ", value)

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()