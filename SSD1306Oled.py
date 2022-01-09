from enum import IntEnum

from PyMCP2221A import PyMCP2221A

from I2cDevice import I2cDevice


class SSD1306Oled(I2cDevice):
    class Register(IntEnum):
        COMMAND = 0x00
        DATA = 0x40

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int, ):
        I2cDevice.__init__(self, i2c, address)
    # SSD1306
    # interface.I2C_Write(0x3d, [0x00, 0xAF])
    # interface.I2C_Write(0x3d, [0x00, 0xA6])
    # interface.I2C_Write(0x3d, [0x00, 0x20])
    # interface.I2C_Write(0x3d, [0x00, 0x02])
    # interface.I2C_Write(0x3d, [0x00, 0x8d])
    # interface.I2C_Write(0x3d, [0x00, 0x14])
    # interface.I2C_Write(0x3d, [0x00, 0x10]) #microled skips the first half of the columns
    # interface.I2C_Write(0x3d, [0x00, 0x00])
    # interface.I2C_Write(0x3d, [0x00, 0xB0])
    # for p in range(0,10):
    #     interface.I2C_Write(0x3d, [0x00, 0xB0 + p])
    #     for i in range(0, 127):
    #         interface.I2C_Write(0x3d, [0x40, 0x00])
