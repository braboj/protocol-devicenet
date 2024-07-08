# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from .definitions import ERROR


class DevNetError(Exception):
    """ Generic DeviceNet Protocol Error """
    pass


class DevNetParsingError(DevNetError):
    """ The DeviceNet message could not be parsed """
    pass


class DevNetPacketError(DevNetError):
    """ The DeviceNet packet has an invalid attribute value """
    pass


class DevNetGroupError(DevNetError):
    """ The DeviceNet Messaging Group is not valid """
    pass


class CipError(Exception):

    def __init__(self, error_code=None):
        Exception.__init__(self)

        if error_code:
            self.message = "{0} ({1})".format(self.__class__.__name__, error_code)
        else:
            self.message = self.__class__.__name__

        self.code = error_code

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class CipServiceError(CipError):

    def __init__(self, *args, **kwargs):
        super(CipServiceError, self).__init__(*args, **kwargs)

        if args:
            error_code = args[0]
        else:
            error_code = kwargs[str("error_code")]

        err_hex = "0x{0:02X}".format(error_code)
        self.message = "{0} ({1})".format(ERROR.TAG[error_code], err_hex)


class CipNoResponseError(CipError):
    def __init__(self, *args, **kwargs):
        super(CipNoResponseError, self).__init__(*args, **kwargs)
        self.message = "Not responding or wrong CAN identifier"


class CipFragmentResponseError(CipError):
    def __init__(self, *args, **kwargs):
        super(CipFragmentResponseError, self).__init__(*args, **kwargs)
        self.message = "Fragmet acknowledge packet is malformed"


class CipFragmentMissing(CipError):
    def __init__(self, *args, **kwargs):
        super(CipFragmentMissing, self).__init__(*args, **kwargs)
        self.message = "Missing fragment detected"


def test_errors():

    # Test generic CIP Error
    try:
        raise CipError(14)

    except Exception as e:
        print(e)

    # Test service CIP Error
    try:
        raise CipServiceError(error_code=14)

    except Exception as e:
        print(e)


if __name__ == "__main__":
    test_errors()
