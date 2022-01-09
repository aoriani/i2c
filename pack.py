def assemble_16bits_little_endian(data: [int]) -> int:
    assert len(data) == 2
    result = data[0] & 0xff
    result |= (data[1] & 0xff) << 8
    return result


def assemble_32bits_little_endian(data: [int]) -> int:
    assert len(data) == 4
    result = data[0] & 0xff
    result |= (data[1] & 0xff) << 8
    result |= (data[2] & 0xff) << 16
    result |= (data[3] & 0xff) << 24
    return result
