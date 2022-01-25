import time

from PyMCP2221A import PyMCP2221A

from I2cDevice import I2cDevice


class PimoroniTrackball(I2cDevice):
    __I2C_ADDRESS = 0x0A

    CHIP_ID = 0xBA11
    VERSION = 1

    REG_LED_RED = 0x00
    REG_LED_GREEN = 0x01
    REG_LED_BLUE = 0x02
    REG_LED_WHITE = 0x03

    REG_LEFT = 0x04
    REG_RIGHT = 0x05
    REG_UP = 0x06
    REG_DOWN = 0x07
    REG_SWITCH = 0x08
    MSK_SWITCH_STATE = 0b10000000

    REG_USER_FLASH = 0xD0
    REG_FLASH_PAGE = 0xF0
    REG_INT = 0xF9
    MSK_INT_TRIGGERED = 0b00000001
    MSK_INT_OUT_EN = 0b00000010
    REG_CHIP_ID_L = 0xFA
    RED_CHIP_ID_H = 0xFB
    REG_VERSION = 0xFC
    REG_I2C_ADDR = 0xFD
    REG_CTRL = 0xFE
    MSK_CTRL_SLEEP = 0b00000001
    MSK_CTRL_RESET = 0b00000010
    MSK_CTRL_FREAD = 0b00000100
    MSK_CTRL_FWRITE = 0b00001000

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int = __I2C_ADDRESS):
        I2cDevice.__init__(self, i2c, address)
        chip_id = self.request16bits(self.REG_CHIP_ID_L)
        assert chip_id == self.CHIP_ID

    def change_address(self, address: int):
        self.write(self.REG_I2C_ADDR, address & 0xff)
        time.sleep(10)

    def enable_interrupt(self, enabled: bool):
        value = self.request8bits(self.REG_INT)
        value = value & ~self.MSK_INT_OUT_EN
        if enabled:
            value = value | self.MSK_INT_OUT_EN
        self.write(self.REG_INT, value)

    def get_interrupt(self):
        # normally you can read the int pin
        return self.request8bits(self.REG_INT) & self.MSK_INT_TRIGGERED

    def set_red(self, red: int):
        self.write(self.REG_LED_RED, red & 0xff)

    def set_green(self, green: int):
        self.write(self.REG_LED_GREEN, green & 0xff)

    def set_blue(self, blue: int):
        self.write(self.REG_LED_BLUE, blue & 0xff)

    def set_white(self, white: int):
        self.write(self.REG_LED_WHITE, white & 0xff)

    def set_rgbw(self, r: int, g: int, b: int, w: int):
        self.write(self.REG_LED_RED, r, g, b, w)

    def get_vectors(self):
        self.write(self.REG_LEFT)
        vectors = self.read(5)
        left = vectors[0]
        right = vectors[1]
        up = vectors[2]
        down = vectors[3]
        state = vectors[4]
        switch = state & ~self.MSK_SWITCH_STATE
        switch_state = (state & self.MSK_SWITCH_STATE) > 0
        return left, right, up, down, switch, switch_state
