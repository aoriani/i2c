from PyMCP2221A import PyMCP2221A

from I2cDevice import I2cDevice


class SparkLedStick(I2cDevice):
    """
        https://www.sparkfun.com/products/14783
        https://github.com/sparkfun/SparkFun_Qwiic_LED_Stick_Arduino_Library
    """
    __I2C_ADDRESS = 0x23

    # Hardware supports adding more leds, hence the  this command
    COMMAND_CHANGE_ADDRESS = 0xC7
    COMMAND_CHANGE_LED_LENGTH = 0x70
    COMMAND_WRITE_SINGLE_LED_COLOR = 0x71
    COMMAND_WRITE_ALL_LED_COLOR = 0x72
    COMMAND_WRITE_SINGLE_LED_BRIGHTNESS = 0x76
    COMMAND_WRITE_ALL_LED_BRIGHTNESS = 0x77
    COMMAND_WRITE_ALL_LED_OFF = 0x78

    # It seem they need to be called together to work nice
    COMMAND_WRITE_RED_ARRAY = 0x73
    COMMAND_WRITE_GREEN_ARRAY = 0x74
    COMMAND_WRITE_BLUE_ARRAY = 0x75

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int = __I2C_ADDRESS):
        I2cDevice.__init__(self, i2c, address)

    def __write_color_array(self, array_command: int, offset: int, array: [int]):
        # The microcontroller for the strip does not support more than 16 bytes
        assert (len(array) <= 12)
        self.write(array_command, len(array), offset, *array)

    def turn_off_all_leds(self):
        self.write(SparkLedStick.COMMAND_WRITE_ALL_LED_OFF)

    def set_led_color(self, led: int, red: int, green: int, blue: int):
        assert (0 <= led <= 9)
        self.write(SparkLedStick.COMMAND_WRITE_SINGLE_LED_COLOR, led + 1, red, green, blue)

    def set_all_leds_color(self, red: int, green: int, blue: int):
        self.write(SparkLedStick.COMMAND_WRITE_ALL_LED_COLOR, red, green, blue)

    def set_all_leds_brightness(self, brightness: int):
        assert (0 <= brightness <= 31)
        self.write(SparkLedStick.COMMAND_WRITE_ALL_LED_BRIGHTNESS, brightness)

    def set_led_brightness(self, led: int, brightness: int):
        assert (0 <= led <= 9)
        assert (0 <= brightness <= 31)
        self.write(SparkLedStick.COMMAND_WRITE_SINGLE_LED_BRIGHTNESS, led + 1, brightness)

    def change_address(self, new_address: int):
        assert (I2cDevice.is_valid_address(new_address))
        self.write(SparkLedStick.COMMAND_CHANGE_ADDRESS, new_address)
        self._address = new_address

    def set_led_red_array(self, start: int, values: [int]):
        self.__write_color_array(SparkLedStick.COMMAND_WRITE_RED_ARRAY, start, values)

    def set_led_green_array(self, start: int, values: [int]):
        self.__write_color_array(SparkLedStick.COMMAND_WRITE_GREEN_ARRAY, start, values)

    def set_led_blue_array(self, start: int, values: [int]):
        self.__write_color_array(SparkLedStick.COMMAND_WRITE_BLUE_ARRAY, start, values)
