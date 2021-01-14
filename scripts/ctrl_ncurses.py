#!/usr/bin/python3

from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero import Servo, Device
import curses
import argparse
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("--test", nargs="?", const=True, default=False)

LOG_FILE = open("stdout.txt", "w")


def draw_vertical_servo(servo, window, title="Servo"):
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
            window.addstr(y, midpoint-1, "[{:.2f}]".format(curr_val))
        elif y == avail_height-1:
            window.addstr(y, midpoint-1, "[0]")

        else:
            # Determine whether or not the servo level should fill this bar as much 
            if y / avail_height >= curr_val:
                window.addstr(y, midpoint-1, "|=|")
            else:
                window.addstr(y, midpoint-1, "| |")
    # window.refresh()
            
    
    


    
    
    


def add_title(window, title):
    # - len nonsense is to center the title

    window.addstr(1, window.getmaxyx()[1] // 2 - len(title) // 2,
                     title)


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
    draw_vertical_servo(head, h_ctl, "Head Servo")
    draw_vertical_servo(neck,n_ctl, "Neck Servo")
    draw_vertical_servo(arm, a_ctl, "Arm Servo")


    servo_ctl.bkgd(' ', curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)
    # Apply the background colors to all writes that have occured
    servo_ctl.attron(curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)

    servo_ctl.getch()
    

    




if __name__ == '__main__':
    curses.wrapper(main)