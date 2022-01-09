from time import sleep

from PyMCP2221A import PyMCP2221A
from typing import Tuple

from I2cDevice import I2cDevice


class Neotrellis(I2cDevice):
    """
        # https://github.com/nagius/neotrellis
        # https://learn.adafruit.com/adafruit-seesaw-atsamd09-breakout/using-the-seesaw-platform
    """
    DEFAULT_I2C_ADDR = 0x2E
    # SeeSaw hardware ID
    HW_ID_CODE = 0x55

    # Status section
    STATUS_BASE = 0x00
    STATUS_SWRST = 0x7F
    STATUS_HW_ID = 0x01
    STATUS_VERSION = 0x02

    DEFAULT_PIXEL_NUMBER = 16
    NEOPIXEL_BASE = 0x0E
    NEOPIXEL_STATUS = 0x00
    NEOPIXEL_PIN = 0x01
    NEOPIXEL_SPEED = 0x02
    NEOPIXEL_BUF_LENGTH = 0x03
    NEOPIXEL_BUF = 0x04
    NEOPIXEL_SHOW = 0x05

    KEYPAD_BASE = 0x10
    KEYPAD_STATUS = 0x00
    KEYPAD_EVENT = 0x01
    KEYPAD_INTENSET = 0x02
    KEYPAD_INTENCLR = 0x03
    KEYPAD_COUNT = 0x04
    KEYPAD_FIFO = 0x10

    KEY_HIGH = 0  # Key is pressed
    KEY_LOW = 1  # Key is released
    KEY_RELEASED = 2  # Key is falling edge
    KEY_PRESSED = 3  # Key is rising edge

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int = DEFAULT_I2C_ADDR):
        I2cDevice.__init__(self, i2c, address)
        assert (self.software_reset())
        # Led init
        self.write(self.NEOPIXEL_BASE, self.NEOPIXEL_PIN, 3)
        # Big endian for 16 bits
        self.write(self.NEOPIXEL_BASE, self.NEOPIXEL_BUF_LENGTH, 0, 3 * 16)

        # Keypad init
        # enable interruption

    def get_version(self) -> int:
        self.write(self.STATUS_BASE, self.STATUS_VERSION)
        # Version is big-endian
        data = self.read(4)
        version = (data[3] & 0xFF)
        version |= (data[2] & 0xFF) << 8
        version |= (data[1] & 0xFF) << 16
        version |= (data[0] & 0xFF) << 24
        return version

    def get_hardware_id(self) -> int:
        self.write(self.STATUS_BASE, self.STATUS_HW_ID)
        return self.read(1)[0]

    def software_reset(self) -> bool:
        self.write(self.STATUS_BASE, self.STATUS_SWRST, 0xFF)
        sleep(0.5)
        return True if (self.get_hardware_id() == self.HW_ID_CODE) else False

    def set_pixel(self, pixel: int, red: int, green: int, blue: int):
        assert (0 <= pixel <= 15)
        self.write(self.NEOPIXEL_BASE,
                   self.NEOPIXEL_BUF,
                   0, pixel * 3,  # address
                   green & 0xff, red & 0xff, blue & 0xff)
        self.write(self.NEOPIXEL_BASE, self.NEOPIXEL_SHOW)

    def set_pixels(self, start_pixel: int, *colors: Tuple[int, int, int]):
        assert (0 <= start_pixel <= 15)
        assert (start_pixel + len(colors) <= 16)
        reordered_colors = [(g & 0xff, r & 0xff, b & 0xff) for (r, g, b) in colors]
        list_of_colors = list(sum(reordered_colors, ()))
        self.write(self.NEOPIXEL_BASE,
                   self.NEOPIXEL_BUF,
                   0, start_pixel * 3,  # address
                   *list_of_colors)
        self.write(self.NEOPIXEL_BASE, self.NEOPIXEL_SHOW)

    def get_events_count(self):
        self.write(self.KEYPAD_BASE, self.KEYPAD_COUNT)
        return self.read(1)[0]

    def enable_interrupt(self):
        self.write(self.KEYPAD_BASE, self.KEYPAD_INTENSET, 0x01)

    def disable_interrupt(self):
        self.write(self.KEYPAD_BASE, self.KEYPAD_INTENCLR, 0x01)

    def set_event(self, key, edge, enabled: bool):
        setting = (1 << (edge + 1)) | (1 if enabled else 0)
        self.write(self.KEYPAD_BASE, self.KEYPAD_EVENT, key, setting)

    def set_event(self, key, edge, enabled: bool):
        assert (0 <= key <= 15)
        key = (key // 4) * 8 + (key % 4)
        setting = (1 << (edge + 1)) | (1 if enabled else 0)
        self.write(self.KEYPAD_BASE, self.KEYPAD_EVENT, key, setting)

    def fetch_events(self, count: int):
        self.write(self.KEYPAD_BASE, self.KEYPAD_FIFO)
        events = self.read(count)
        def get_edge(v): return v & 0x3

        def get_key(v):
            key_raw = (v >> 2) & 0x3F
            return (key_raw // 8) * 4 + (key_raw % 8)

        return [(get_key(v), get_edge(v)) for v in events]
