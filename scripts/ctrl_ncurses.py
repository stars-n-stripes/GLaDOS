#!/usr/bin/python3

from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero import Servo, Device
import curses
import argparse
import math
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("--test", nargs="?", const=True, default=False)

# Unicode box
# https://stackoverflow.com/questions/46063974/printing-extended-ascii-characters-in-python
DOUBLE_LEFT_TOP = u'\u2554'
DOUBLE_VERTI_PIPE = u'\u2551'
DOUBLE_LEFT_BOTTOM = u'\u255a'
DOUBLE_RIGHT_TOP = u'\u2557'
DOUBLE_RIGHT_BOTTOM =u'\u255d'
DOUBLE_HORIZ_PIPE = u'\u2550'
DOUBLE_VERTI_PIPE = u'\u2551'
CENTER = u'\u2573'

LOG_FILE = open("stdout.txt", "w")
SERVO_ASCII_3X3  = DOUBLE_LEFT_TOP + DOUBLE_HORIZ_PIPE + DOUBLE_RIGHT_TOP + "\n" + DOUBLE_VERTI_PIPE + CENTER + \
                   DOUBLE_VERTI_PIPE + "\n" + DOUBLE_LEFT_BOTTOM + DOUBLE_HORIZ_PIPE + DOUBLE_RIGHT_BOTTOM
SERVO_ASCII_1X1 = "X"

def draw_vertical_servo_ctl(servo, window, title="Servo"):
    """
    Draw the servos on the given window, filling in the initial value.
    
    :param servo: gpiozero Servo 
    :param window: curses window
    :return:
    """
    # Give the window a title
    add_title(window, title)

    # Create a vertical bar based on the current value of the servo
    # Use the entire height, minus a header/footer and padding on each side
    avail_height, width = window.getmaxyx()
    avail_height -= 1
    midpoint = width // 2

    # Get the current value of the servo as a threshold
    curr_val = servo.value

    for y in range(2, avail_height): #start at two to account for the title
        if y == 2:
            window.addstr(y, midpoint-2, "[{:.2f}]".format(curr_val))
        elif y == avail_height-1:
            window.addstr(y, midpoint-1, "[0]")

        else:
            # Determine whether or not the servo level should fill this bar as much 
            if y / avail_height >= curr_val:
                window.addstr(y, midpoint-1, "[+]")
            else:
                window.addstr(y, midpoint-1, "| |")
    # window.refresh()
            
def draw_horizontal_servo_ctl(servo, window, title="Horizontal Servo"):
    """
    Draws a progress bar similar to draw_vertical_servo, but at a 90 degree offset.
    This will usually be used for the twist servo.
    :param Servo servo: The Servo object to grab a value from
    :param curses.Window window: The window object we will build the horizontal window in
    :param title: The title for the servo controller
    :return:
    """
    # Give the window a title
    add_title(window, title)
    # window.addstr(window.getmaxyx().__str__())

    # Create a horizontal bar based on the current value of the servo
    # Use the entire width, minus a header/footer and padding on each side
    height, avail_width = window.getmaxyx()
    avail_width -= 1
    midpoint = height // 2

    # Get the current value of the servo as a threshold
    curr_val = servo.value
    avail_width -= 4 # Account for headers on left and right
    for x in range(2, avail_width):  # end 4 early to account for headers
        if x == 2:
            window.addstr(midpoint + 1, x,  "[1]".format(curr_val))
        elif x in {2, 3, 4}:
            pass # Would overwrite l72
        elif x == avail_width - 1:
            window.addstr(midpoint + 1, x, "[0]")
            break

        else:
            # Determine whether or not the servo level should fill this bar as much
            if x / avail_width <= curr_val:
                window.addstr(midpoint + 1, x, "|")
            else:
                window.addstr(midpoint + 1, x, " ")
    


def draw_servo(y, x, window, servo, icon=SERVO_ASCII_3X3):
    """
    Draws a servo's location (represented by an ascii icon) on the given window, centered around x, y
    :param y:
    :param x:
    :param window:
    :param servo:
    :return:
    """
    if icon == SERVO_ASCII_3X3:
        xoffset = yoffset = 3
    elif icon == SERVO_ASCII_1X1:
        xoffset = yoffset = 0
    else:
        # Best guess
        xoffset = yoffset = len(icon) // max(icon.count("\n"), 1)

    # window.addstr(str(xoffset) + "/" + str(yoffset))
    # window.addstr(str(x)+ str(y))
    # Curses doesn't work super well with strings that contain newlines
    # window.addstr(max(y-yoffset, 0), max(x-xoffset, 0), icon)
    for line in icon.splitlines(keepends=False):
        window.addstr(y - yoffset, x - xoffset, line)
        yoffset -= 1



def add_title(window, title):
    # - len nonsense is to center the title

    window.addstr(1, window.getmaxyx()[1] // 2 - len(title) // 2,
                     title)


def draw_servo_chain(servo_dict, window):
    """
    Draw the servos in a list as a chain resembling GLaDOS' arm on the provided window
    :param dict servo_dict: Dictonary of servo objects, with the following names:
                        "arm"
                        "head"
                        "neck"
    :param window: The Window object to draw the servos on
    :return:
    """
    # Place the arm servo in the center of the window
    # Save the center of the arm servo
    ay, ax = window.getmaxyx()
    ax = ax // 2
    ay = ay // 2

    draw_servo(ay, ax, window, servo_dict["arm"])

    # Place the neck servo on the same vertical as the arm servo, shifting it down based on the arm servo's value
    # Save where it ends up

    nx = ax // 2
    # asin will return 90 degrees for 1 (full ext), 0 deg for 0 (no ext)
    #TODO: Start here
    angle_between = - math.asin(servo_dict["arm"].value())

    # Place the head servo on the same vertical as the neck.


def main(stdscr):
    args = parser.parse_args()
    print(args.test)
    if args.test:
        Device.pin_factory = MockFactory(pin_class=MockPWMPin)
        # Build the Servos
        head = Servo(17)
        neck = Servo(18)
        arm = Servo(20)
        twist = Servo(21)
    else:
        # Build the Servos
        head = Servo(17)
        neck = Servo(18)
        arm = Servo(20)
        twist = Servo(21)

    servos = [head, neck, arm, twist]
    # Debug
    head.value = 0.33
    neck.value = 0.66
    arm.value = 0.5
    twist.value = 0.75

    
    # Start up the curses
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(False)

    # Create a new window
    begin_x = 0
    begin_y = 0
    height = curses.LINES -1
    width = curses.COLS // 2 - 1
    servo_view = curses.newwin(height, width, begin_y, begin_x)

    # Add another window for the servo control and create a border for it
    servo_ctl = curses.newwin(curses.LINES - 1, width + 1, 0, width + 1)
    # servo_ctl.border()
    t_ctl = servo_ctl.derwin(3 * height // 4 + 1, 0)
    a_ctl = servo_ctl.derwin(3 * height // 4-2, width // 3, 3, 0)
    h_ctl = servo_ctl.derwin(3 * height // 4-2, width // 3 + 1, 3, width // 3 + 1)
    n_ctl = servo_ctl.derwin(3 * height // 4-2, width // 3, 3, 2 * width // 3 +2)

    # n_ctl = servo_ctl.derwin()
    # a_ctl = servo_ctl.derwin()
    # t_ctl = servo_ctl.derwin()
    a_ctl.border()
    h_ctl.border()
    t_ctl.border()
    n_ctl.border()

    # place titles
    servo_ctl_title = "[GLaDOS Servo Control v0.1]"

    add_title(servo_ctl, servo_ctl_title)
    add_title(servo_view, "[Current Servo Positions]")

    servo_ctl.refresh()

    # Add a border around the GLaDOS view
    servo_view.border()
    servo_view.refresh()

    # Create a white/blue background for the servo control
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_CYAN)
    # servo_view.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
    # servo_view.addstr(1,1, "This is not blue")
    # servo_view.getch()
    # servo_ctl.refresh()
    
    # Draw the current servo levels
    draw_vertical_servo_ctl(head, h_ctl, "Head Servo")
    draw_vertical_servo_ctl(neck, n_ctl, "Neck Servo")
    draw_vertical_servo_ctl(arm, a_ctl, "Arm Servo")
    draw_horizontal_servo_ctl(twist, t_ctl, "Twist Servo")

    # Draw the ASCIIART servo
    # draw_servo(10,10,servo_view, head)
    draw_servo_chain({"arm": arm, "head": head, "neck": neck}, servo_view)
    servo_ctl.bkgd(' ', curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)
    # Apply the background colors to all writes that have occured
    servo_ctl.attron(curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)
    servo_view.refresh()
    servo_ctl.getch()


    




if __name__ == '__main__':
    curses.wrapper(main)