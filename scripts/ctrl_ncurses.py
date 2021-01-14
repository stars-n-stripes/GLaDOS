from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero import Servo, Device
import curses
import argparse
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("--test", nargs="?", const=True, default=False)

LOG_FILE = open("stdout.txt", "w")


def draw_servos(servos, window, twist=-1):
    """
    Draw the servos on the given window, assuming the last servo provided is the
    non-visualized "twist" servo
    :param servos: list of gpiozero Servo objects
    :param window: curses window
    :param twist: index of the 20kg "twist" Servo
    :return:
    """
    assert abs(twist) <= len(servos)
    max_x = curses.COLS
    max_y = curses.LINES

    for i, servo in enumerate(servos):
        if servos[i] == servos[twist]:
            # Hit the twist servo; draw this one horizontally
            #..later
            pass
        else:
            window


def add_title(servo_ctl, servo_ctl_title):
    # - len nonsense is to center the title

    servo_ctl.addstr(1, servo_ctl.getmaxyx()[1] // 2 - len(servo_ctl_title) // 2,
                     servo_ctl_title)


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
    servo_ctl.bkgd(' ', curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)
    # servo_ctl.refresh()
    
    # Draw the current servo levels
    # draw_servos()

    servo_ctl.getch()
    
    




if __name__ == '__main__':
    curses.wrapper(main)