# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from PyMCP2221A import PyMCP2221A

from Neotrellis import Neotrellis
from SparkButton import SparkButton
from SparkLedStick import SparkLedStick
import time


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    interface = PyMCP2221A.PyMCP2221A()
    interface.I2C_Init()

    print("   0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F  ")
    for i in range(0x00, 0x7F):
        if i % 16 == 0 and i > 0:
            print("   {:02X}".format(i - 1))

        if interface.I2C_Read(i, 1) != -1:
            print('  {:02X}'.format(i), end='')
        else:
            print('  --', end='')
        # time.sleep(0.1)

    print("")

    neo = Neotrellis(interface)
    neo.software_reset()
    neo.enable_interrupt()

    neo.set_event(0, neo.KEY_PRESSED, True)
    neo.set_event(1, neo.KEY_PRESSED, True)
    neo.set_event(2, neo.KEY_PRESSED, True)
    neo.set_event(3, neo.KEY_PRESSED, True)
    neo.set_event(4, neo.KEY_PRESSED, True)
    neo.set_event(15, neo.KEY_PRESSED, True)
    print(neo.get_events_count())

    while True:
        count = neo.get_events_count()
        print(count)
        if count > 0:
            print()
            key = neo.fetch_events(1)[0][0]
            neo.set_pixel(key, 255,255,255)

    # button = SparkButton(interface)
    # print(button.get_button_status().isEventAvailable)
    # print(button.get_button_status().hasBeenPressed)
    # print(button.get_button_status().hasBeenClicked)
    # button.led.set_brightness(75)
    # button.led.set_cycle_time(2500)
    # button.led.set_off_time(0)
    # button.led.set_granularity(1)
    # button.set_debounce_time(10)
    # print(button.get_debounce_time())
    #
    # button.clear_event_bits()
