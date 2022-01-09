from enum import IntEnum

from PyMCP2221A import PyMCP2221A

from I2cDevice import I2cDevice


class SSD1327Oled(I2cDevice):
    class Register(IntEnum):
        COMMAND = 0x00
        DATA = 0x40

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int, ):
        I2cDevice.__init__(self, i2c, address)
    #
    # init_seq_1327 = [
    #     0xae,
    #     0x81, 0x80,
    #     0xa0, 0x53,
    #     0x51,
    #     0xA1, 0x00,
    #     0xA2, 0x00,
    #     0xa6,
    #     0xA8, 0x7F,
    #     0xB1, 0x11,
    #     0xb3, 0x00,
    #     0xAB, 0x01,
    #     0xB6, 0x04,
    #     0xBE, 0x0F,
    #     0xBC, 0x08,
    #     0xD5, 0x62,
    #     0xFD, 0x12,
    #     0xA4, 0xaf,
    #     0x75, 0x00, 0x7f,
    #     0x15, 0x0, 0x3f
    # ]
    # for cmd in init_seq_1327:
    #     interface.I2C_Write(0x3c, [0x00, cmd])
    #
    # buffer = [0x40] + ([0x33]*32)
    # for cmd in range(0, 8192//32):
    #     interface.I2C_Write(0x3c, buffer)