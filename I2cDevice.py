from PyMCP2221A import PyMCP2221A

from pack import assemble_16bits_little_endian, assemble_32bits_little_endian


class I2cDevice:
    def __init__(self, i2c: PyMCP2221A.PyMCP2221A, address: int):
        self.__i2c = i2c
        self._address = address

    def write(self, command: int, *args: int):
        self.__i2c.I2C_Write(self._address, [command, *args])

    def read(self, size: int) -> [int]:
        return self.__i2c.I2C_Read(self._address, size)

    def write_16_bits(self, command: int, value: int):
        self.__i2c.I2C_Write(self._address, [command,  *I2cDevice.explode_16bits(value)])

    def request(self, command: int, response_size: int) -> [int]:
        self.__i2c.I2C_Write(self._address, [command])
        return self.__i2c.I2C_Read(self._address, response_size)

    def request8bits(self, command) -> int:
        return self.request(command, 2)[0]

    # TODO Make endianess explicit
    def request16bits(self, command) -> int:
        return assemble_16bits_little_endian(self.request(command, 2))

    # TODO Make endianess explicit
    def request32bits(self, command) -> int:
        return assemble_32bits_little_endian(self.request(command, 4))

    @staticmethod
    def is_valid_address(address: int) -> bool:
        return 0x08 <= address <= 0x77

    @staticmethod
    def ensure_16_bits(integer: int):
        assert (integer & ~0xFFFF == 0)

    @staticmethod
    def ensure_8_bits(integer: int):
        assert (integer & ~0xFF == 0)

    @staticmethod
    def explode_16bits(value: int) -> [int]:
        result = [0]*2
        result[0] = value & 0xff
        result[1] = (value & 0xff00) >> 8
        return result
