from enum import IntEnum

from PyMCP2221A import PyMCP2221A

from I2cDevice import I2cDevice


class SSD1306Oled(I2cDevice):
    """
        https://github.com/sparkfun/Qwiic_OLED_Base_Py/blob/main/qwiic_oled_base/qwiic_oled_base.py
        https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
    """

    class Register(IntEnum):
        COMMAND = 0x00
        DATA = 0x40

    class Commands(IntEnum):
        SETCONTRAST = 0x81
        DISPLAYALLONRESUME = 0xA4
        DISPLAYALLON = 0xA5
        NORMALDISPLAY = 0xA6
        INVERTDISPLAY = 0xA7
        DISPLAYOFF = 0xAE
        DISPLAYON = 0xAF
        SETDISPLAYOFFSET = 0xD3
        SETCOMPINS = 0xDA
        SETVCOMDESELECT = 0xDB
        SETDISPLAYCLOCKDIV = 0xD5
        SETPRECHARGE = 0xD9
        SETMULTIPLEX = 0xA8
        SETLOWCOLUMN = 0x00
        SETHIGHCOLUMN = 0x10
        SETSTARTLINE = 0x40
        MEMORYMODE = 0x20
        COMSCANINC = 0xC0
        COMSCANDEC = 0xC8
        SEGREMAP = 0xA0
        CHARGEPUMP = 0x8D
        EXTERNALVCC = 0x01
        SWITCHCAPVCC = 0x02
        #  Scroll
        ACTIVATESCROLL = 0x2F
        DEACTIVATESCROLL = 0x2E
        SETVERTICALSCROLLAREA = 0xA3
        RIGHTHORIZONTALSCROLL = 0x26
        LEFTHORIZONTALSCROLL = 0x27
        VERTICALRIGHTHORIZONTALSCROLL = 0x29
        VERTICALLEFTHORIZONTALSCROLL = 0x2A

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int, width: int, height: int):
        I2cDevice.__init__(self, i2c, address)
        self.width = width
        self.height = height

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

    def init(self):
        self.write(self.Register.COMMAND, self.Commands.DISPLAYOFF)  # 0xAE

        self.write(self.Register.COMMAND, self.Commands.SETDISPLAYCLOCKDIV)  # 0xD5
        self.write(self.Register.COMMAND, 0x80)  # the suggested ratio 0x80

        self.write(self.Register.COMMAND, self.Commands.SETMULTIPLEX)  # 0xA8
        self.write(self.Register.COMMAND, self.height - 1)

        self.write(self.Register.COMMAND, self.Commands.SETDISPLAYOFFSET)  # 0xD3
        self.write(self.Register.COMMAND, 0x0)  # no offset

        self.write(self.Register.COMMAND, self.Commands.SETSTARTLINE | 0x0)  # line #0

        self.write(self.Register.COMMAND, self.Commands.CHARGEPUMP)  # enable charge pump
        self.write(self.Register.COMMAND, 0x14)

        self.write(self.Register.COMMAND, self.Commands.NORMALDISPLAY)  # 0xA6
        self.write(self.Register.COMMAND, self.Commands.DISPLAYALLONRESUME)  # 0xA4

        self.write(self.Register.COMMAND, self.Commands.SEGREMAP | 0x1)
        self.write(self.Register.COMMAND, self.Commands.COMSCANDEC)

        self.write(self.Register.COMMAND, self.Commands.SETCOMPINS)  # 0xDA
        if self.width * self.height // 8 == 512:
            self.write(self.Register.COMMAND, 0x02)  # rect (128x32 OLED modules)
        else:
            self.write(self.Register.COMMAND, 0x12)  # square and large (64x48 or 128x64 OLED modules)

        self.write(self.Register.COMMAND, self.Commands.SETCONTRAST)  # 0x81
        self.write(self.Register.COMMAND, 0x8F)

        self.write(self.Register.COMMAND, self.Commands.SETPRECHARGE)  # 0xd9
        self.write(self.Register.COMMAND, 0x22)

        self.write(self.Register.COMMAND, self.Commands.SETVCOMDESELECT)  # 0xDB
        self.write(self.Register.COMMAND, 0x30)

        self.write(self.Register.COMMAND, self.Commands.DISPLAYON)  # --turn on oled panel
        self.clear()

    def set_page_address(self, pageAddress):
        """
            Set SSD1306 page address.
            :param pageAddress: The page address command and address
            :return: No return value
        """

        # self.write(self.Register.COMMAND, 0xb0|pageAddress)

        self.write(self.Register.COMMAND, 0x22)
        self.write(self.Register.COMMAND, (pageAddress & (self.height - 1)))
        self.write(self.Register.COMMAND, self.height - 1)

    # ----------------------------------------------------
    # Send column address command and address to the SSD1306 OLED controller.
    def set_column_address(self, colAddress):
        """
            Set SSD1306 column address.
            :param colAddress: The column address command and address
            :return: No return value
        """

        if self.width * self.height // 8 == 384:
            self.write(self.Register.COMMAND, (0x10 | (colAddress >> 4)) + 0x02)
            self.write(self.Register.COMMAND, (0x0f & colAddress))
        else:
            self.write(self.Register.COMMAND, 0x21)
            self.write(self.Register.COMMAND, (colAddress & (self.width - 1)))
            self.write(self.Register.COMMAND, self.width - 1)

    @staticmethod
    def __chunks(lst: [int], n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def clear(self):
        for i in range(8):
            self.set_page_address(i)
            self.set_column_address(0)
            # pylint: disable=unused-variable
            data = [0x0]*self.width
            for chunk in SSD1306Oled.__chunks(data, 59):
                self.write(self.Register.DATA, *chunk)

    def set_normal(self):
        self.write(self.Register.COMMAND, self.Commands.NORMALDISPLAY)

    def set_inverted(self):
        self.write(self.Register.COMMAND, self.Commands.INVERTDISPLAY)

    def set_contrast(self, value: int):
        assert (0 <= value <= 255)
        self.write(self.Register.COMMAND, self.Commands.SETCONTRAST)
        self.write(self.Register.COMMAND, value)

    def send_display_data(self, data: [int]):
        chunks = SSD1306Oled.__chunks(data, 59)
        for chunk in chunks:
            self.write(self.Register.DATA, *chunk)

    def stop_scroll(self):
        self.write(self.Register.COMMAND, self.Commands.DEACTIVATESCROLL)

    def horizontal_scroll(self, start_page: int, stop_page, right: bool = True):
        assert (start_page <= stop_page)

        self.stop_scroll()

        self.write(self.Register.COMMAND, self.Commands.RIGHTHORIZONTALSCROLL if right else self.Commands.LEFTHORIZONTALSCROLL)
        self.write(self.Register.COMMAND, 0x00)
        self.write(self.Register.COMMAND, start_page & 0xff)
        self.write(self.Register.COMMAND, 0x7) #speed ?
        self.write(self.Register.COMMAND, stop_page & 0xff)
        self.write(self.Register.COMMAND, 0x00)
        self.write(self.Register.COMMAND, 0xff)
        self.write(self.Register.COMMAND, self.Commands.ACTIVATESCROLL)

    def flip_vertical(self, flip: bool):
        self.write(self.Register.COMMAND, self.Commands.COMSCANINC if flip else self.Commands.COMSCANDEC)

    def flip_horizontal(self, flip: bool):
        self.write(self.Register.COMMAND, self.Commands.SEGREMAP | (0x0 if flip else 0x1))


