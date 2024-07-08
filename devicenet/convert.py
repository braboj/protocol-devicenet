# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


def integer_to_bytes(value, size, endianess='little'):
    """A helper function to convert integer values to a list of bytes.

    Parameters:
        value: Integer to be converted to bytes
        size: Size of desired output list of bytes
        endianess: Layout of the output list of bytes

    Returns:
        List of bytes

    Usage:

        from Components.utils.convert import integer_to_bytes

        stream = integer_to_bytes(value=0xAABBCCDD, size=4, endianess="little")
        # Output will be [0xDD, 0xCC, 0xBB, 0xAA]

        stream = integer_to_bytes(value=0xAABBCCDD, size=4, endianess="big")
        # Output will be [0xAA, 0xBB, 0xCC, 0xDD]

    """

    # Initialize
    stream = [0] * size

    # Convert
    for i in range(0, size):
        result = value >> i*8 & 0xFF
        stream[i] = result

    return stream if endianess == 'little' else stream[::-1]


def bytes_to_integer(stream, endianess='little'):
    """A helper function to convert bytes to an integer value.

    Parameters:
        stream: List of bytes to be converted to an integer value
        endianess: Layout of the input list of bytes

    Returns:
        Numeric value

    Usage:

        from Components.utils.convert import bytes_to_integer

        stream = bytes_to_integer(stream=[0xDD, 0xCC, 0xBB, 0xAA], endianess="little")
        # Output will be 0xAABBCCDD

        stream = integer_to_bytes(stream=[0xDD, 0xCC, 0xBB, 0xAA], endianess="big")
        # Output will be 0xDDCCBBAA

    """

    result = 0

    # Revert stream if little-endian layout chosen
    stream = stream if endianess == 'big' else stream[::-1]

    # Convert
    for b in stream:
        result = result * 256 + int(b)

    return result


def string_to_bytes(value):
    """A helper function to convert UTF-8 string to bytes with length prefix.

    Parameters:
        value: UTF-8 string to be converted to bytes

    Returns:
        List of bytes

    Usage:

        from Components.utils.convert import string_to_bytes

        stream = string_to_bytes(value="Hello")
        # Output is [4, 84, 101, 115, 116]

    """

    stream = bytearray(value, encoding='utf-8')
    stream = list(stream)
    length = len(stream)
    stream.insert(0, length)
    if len(stream) > 255:
        stream = stream[:255]

    return stream


def bytes_to_string(stream):
    """A helper function to bytes UTF-8 whereas the first byte is the length prefix.

    Parameters:
        stream: List of input bytes to be converted to a string value

    Returns:
       UTF-8 string

    Usage:

        from Components.utils.convert import bytes_to_string

        stream = bytes_to_string(stream=[4, 84, 101, 115, 116])
        # Output is "Test"

    """

    stream = list(stream)
    length = stream.pop(0)
    stream = stream[:length]
    result = bytearray(stream).decode('utf-8')
    result = result.rstrip("\u0000")
    return result


def to_list(value):
    """A helper function to convert any data type to a list.

    Parameters:
        value: Any data type to be converted to a list

    Returns:
       List

    Usage:

        from Components.utils.convert import to_list

        test_value = 1
        output = to_list(value=test_value)
        # Output is [1]

    """

    result = []

    try:
        result = list(value)
    except TypeError:
        result.append(value)

    return result


def main():
    # 01: Convert integer to bytes
    test_value = 0xAABBCCDD
    output = integer_to_bytes(value=test_value, size=4, endianess="little")
    assert output == [0xDD, 0xCC, 0xBB, 0xAA]

    # 02: Convert bytes to integer
    test_stream = [0xDD, 0xCC, 0xBB, 0xAA]
    output = bytes_to_integer(stream=test_stream, endianess="little")
    assert output == 0xAABBCCDD

    # 03: Encode string to bytes (appends length prefix)
    test_string = "Test"
    output = string_to_bytes(value=test_string)
    assert output == [4, ord('T'), ord('e'), ord('s'), ord('t')]

    # 04: Parse string from bytes (removes length prefix)
    test_stream = [4, ord('T'), ord('e'), ord('s'), ord('t')]
    output = bytes_to_string(stream=test_stream)
    assert output == "Test"

    # 05: Convert integer to list
    test_value = 1
    output = to_list(value=test_value)
    assert output == [1]

    # 06: Convert float to list
    test_value = 1.0
    output = to_list(value=test_value)
    assert output == [1.0]

    # 07: Convert complex to list
    test_value = 1j
    output = to_list(value=test_value)
    assert output == [1j]

    # 08: Convert tuple to list
    test_value = (1, )
    output = to_list(value=test_value)
    assert output == [1]

    # 09: Convert list to list
    test_value = [1, 2]
    output = to_list(value=test_value)
    assert output == [1, 2]

    # 10: Print docstring
    print(80*"#")
    print(integer_to_bytes.__doc__)

    print(80*"#")
    print(bytes_to_integer.__doc__)

    print(80*"#")
    print(string_to_bytes.__doc__)

    print(80*"#")
    print(bytes_to_string.__doc__)

    print(80*"#")
    print(to_list.__doc__)


if __name__ == "__main__":
    main()

