from enum import IntEnum

from PyMCP2221A import PyMCP2221A

from I2cDevice import I2cDevice


class SparkButton(I2cDevice):
    """
        https://www.sparkfun.com/products/15932
        https://github.com/sparkfun/SparkFun_Qwiic_Button_Arduino_Library
    """
    DEFAULT_ADDRESS = 0x6F
    DEV_ID = 0x5D

    class Register(IntEnum):
        ID = 0x00
        FIRMWARE_MINOR = 0x01
        FIRMWARE_MAJOR = 0x02
        BUTTON_STATUS = 0x03
        INTERRUPT_CONFIG = 0x04
        BUTTON_DEBOUNCE_TIME = 0x05
        PRESSED_QUEUE_STATUS = 0x07
        PRESSED_QUEUE_FRONT = 0x08
        PRESSED_QUEUE_BACK = 0x0C
        CLICKED_QUEUE_STATUS = 0x10
        CLICKED_QUEUE_FRONT = 0x11
        CLICKED_QUEUE_BACK = 0x15
        LED_BRIGHTNESS = 0x19
        LED_PULSE_GRANULARITY = 0x1A
        LED_PULSE_CYCLE_TIME = 0x1B
        LED_PULSE_OFF_TIME = 0x1D
        I2C_ADDRESS = 0x1F

    class EventStatus:
        def __init__(self, status: int):
            self.isEventAvailable = (status & 1) != 0
            self.hasBeenClicked = (status & 2) != 0
            self.hasBeenPressed = (status & 4) != 0

    class EventQueue:
        def __init__(self, button, status_reg: int, queue_front_reg: int, queue_back_reg: int):
            self.button = button
            self.status_reg = status_reg
            self.queue_front_reg = queue_front_reg
            self.queue_back_reg = queue_back_reg

        def is_full(self) -> bool:
            status = self.button.request8bits(self.status_reg)
            return self.Status(status).isFull

        def is_empty(self) -> bool:
            status = self.button.request8bits(self.status_reg)
            return self.Status(status).isEmpty

        def time_since_last_event(self) -> int:
            """
            :return: milliseconds 32 bits. God for 50 days
            """
            return self.button.request32bits(self.queue_front_reg)

        def time_since_first_event(self) -> int:
            """
            :return: milliseconds 32 bits. God for 50 days
            """
            return self.button.request32bits(self.queue_back_reg)

        def pop(self) -> int:
            """
            :return: milliseconds since first button event
            """
            first_event = self.time_since_first_event()
            status = self.button.request8bits(self.status_reg)
            status = status | 1 # set popRequest
            self.button.write(self.status_reg, status)
            return first_event

        class Status:
            def __init__(self, status: int):
                self.popRequest = (status & 1) != 0  # This is bit 0. User mutable, user sets to 1 to pop from queue, we pop from queue and set the bit back to zero.
                self.isEmpty = (status & 2) != 0 # user immutable, returns 1 or 0 depending on whether or not the queue is empty
                self.isFull = (status & 4) != 0

    class Led:
        def __init__(self, button):
            self.button = button

        def turn_off(self):
            self.set_brightness(0)
            self.set_off_time(0)
            self.set_cycle_time(0)

        def set_brightness(self, brightness: int = 0xff):
            """

            :param brightness: 0 to 255
            :return:
            """
            I2cDevice.ensure_8_bits(brightness)
            self.button.write(SparkButton.Register.LED_BRIGHTNESS, brightness)

        def set_cycle_time(self, cycle_time: int):
            I2cDevice.ensure_16_bits(cycle_time)
            self.button.write_16_bits(SparkButton.Register.LED_PULSE_CYCLE_TIME, cycle_time)

        def set_off_time(self, off_time: int):
            I2cDevice.ensure_16_bits(off_time)
            self.button.write_16_bits(SparkButton.Register.LED_PULSE_OFF_TIME, off_time)

        def set_granularity(self, off_time: int):
            I2cDevice.ensure_8_bits(off_time)
            self.button.write(SparkButton.Register.LED_PULSE_GRANULARITY, off_time)

    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int = DEFAULT_ADDRESS):
        I2cDevice.__init__(self, i2c, address)
        self.press_queue = self.EventQueue(self, self.Register.PRESSED_QUEUE_STATUS, self.Register.PRESSED_QUEUE_FRONT,
                                           self.Register.PRESSED_QUEUE_BACK)
        self.click_queue = self.EventQueue(self, self.Register.CLICKED_QUEUE_STATUS, self.Register.CLICKED_QUEUE_FRONT,
                                           self.Register.CLICKED_QUEUE_BACK)
        self.led = self.Led(self)

    # Device Status
    def get_device_id(self) -> int:
        return self.request8bits(self.Register.ID)

    def check_device_id(self) -> bool:
        return SparkButton.DEV_ID == self.get_device_id()

    def get_firmware_version(self) -> (int, int):
        major = self.request8bits(self.Register.FIRMWARE_MAJOR)
        minor = self.request8bits(self.Register.FIRMWARE_MINOR)
        return major, minor

    def set_address(self, new_address: int):
        assert (I2cDevice.is_valid_address(new_address))
        self.write(self.Register.I2C_ADDRESS, new_address)
        self._address = new_address

    def get_address(self) -> int:
        """
        :return: i2c address (8-bits)
        """
        return self._address

    # Button status/config
    def get_button_status(self) -> EventStatus:
        status = self.request8bits(self.Register.BUTTON_STATUS)
        return self.EventStatus(status)

    def clear_event_bits(self):
        self.write(self.Register.BUTTON_STATUS, 0)

    def get_debounce_time(self) -> int:
        """

        :return: debounce time in milliseconds 16 bits
        """
        return self.request16bits(self.Register.BUTTON_DEBOUNCE_TIME)

    def set_debounce_time(self, time: int):
        """

        :param time: debounce in milliseconds
        :return:
        """
        SparkButton.ensure_16_bits(time)
        self.write_16_bits(self.Register.BUTTON_DEBOUNCE_TIME, time)

    # Interrupts
    def set_interrupts(self, clicked: bool, pressed: bool):
        data = (1 if clicked else 0) | (2 if pressed else 0)
        self.write(self.Register.INTERRUPT_CONFIG, data)

    def reset_interrupt_config(self):
        self.write(self.Register.INTERRUPT_CONFIG, 0x3)  # last two bits on
