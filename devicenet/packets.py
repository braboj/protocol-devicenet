# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# System imports
from abc import ABCMeta, abstractmethod
from six import with_metaclass

# Not compatible with Python 3.10 and above
from collections import Iterable

# Project imports
from .addressing import *
from .errors import *
from .definitions import *
from .convert import *

import logging


# TODO:
#   - Fluent interface
#   - Improve method naming
#   - Add parse_data and add_data to the generic packet interface
#   - Refactor the split() method
#   - The split() methods should be in the upper level
#   - Improve documentation
#   - Add a packet builder class
#   - Using CanFrameBasic is a risk in case the CanFrame class is changed in the future
#   - The packets shall only have serialize/deserialize methods
#   - Move the convesion to adapter classes in the network layer\


# ###################################################################################################
# #                                   PACKET INTERFACE
# ###################################################################################################
# class PacketAbc(object):
#
#     def deserialize(self, stream):
#         raise NotImplementedError
#
#     def serialize(self):
#         raise NotImplementedError
#
#     def parse(self):
#         raise NotImplementedError
#
#     def build(self):
#         raise NotImplementedError
#
#     def clear(self):
#         raise NotImplementedError


class CanFrameAbc(with_metaclass(ABCMeta)):

    @abstractmethod
    def __init__(self, **kwargs):
        raise NotImplementedError

    @property
    @abstractmethod
    def extended(self):
        raise NotImplementedError

    @extended.setter
    def extended(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def can_id(self):
        raise NotImplementedError

    @can_id.setter
    def can_id(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def length(self):
        raise NotImplementedError

    @length.setter
    def length(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def data(self):
        raise NotImplementedError

    @data.setter
    def data(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def report(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def rtr(self):
        raise NotImplementedError

    @rtr.setter
    def rtr(self, value):
        raise NotImplementedError


###################################################################################################
#                                   FRAGMENTATION PROTOCOL
###################################################################################################

class FragHeaderMixin(with_metaclass(ABCMeta)):
    """ Mixin class for the fragmentation protocol header byte

    The fragmentation protocol header byte is used to identify the type of the fragment and the
    number of fragments in the message. The fragmentation protocol header byte is used for
    explicit messages only. This class is not intended to be used directly.

    The structure of the fragmentation protocol header byte is as follows:
        - Bits [7, 6] : The fragment type (start=0, middle=1, final=2, ack=3)
        - Bits [5 - 0] : The fragment count

    Args:
        frag_type (int)     : The fragment type (start=0, middle=1, final=2, ack=3)
        frag_count (int)    : The fragment count

    """

    FRAG_TYPE_MASK = 0xC0
    FRAG_TYPE_OFFSET = 6
    FRAG_COUNT_MASK = 0x3F

    def __init__(self, frag_type, frag_count, *args, **kwargs):
        """ Initialize the fragmentation protocol attributes """

        # Initialize the base class (mandatory for mixin classes)
        super(FragHeaderMixin, self).__init__(*args, **kwargs)

        # Bits [7, 6] : The fragment type (start=0, middle=1, final=2, ack=3)
        self.frag_type = frag_type

        # Bits: [5 - 0] : The fragment count
        self.frag_count = frag_count

        # The fragmentation protocol byte
        self.frag_header = 0

    ###############################################################################################

    def validate_frag_type(self):

        # Check whether the value is None
        if self.frag_type is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.frag_type, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.frag_type <= 3:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 3]")

    ###############################################################################################

    def validate_frag_count(self):

        # Check whether the value is None
        if self.frag_count is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.frag_count, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.frag_count <= FRAGMENT.MAX_COUNT:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 63]")

    def validate_frag_header(self):

        # Check the type of the value
        if self.frag_header is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.frag_header, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.frag_header <= 255:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 255]")

    ###############################################################################################

    def get_frag_type(self):

        # Extract the fragment type
        self.frag_type = (self.frag_header & self.FRAG_TYPE_MASK) >> self.FRAG_TYPE_OFFSET

        # Return the current instance
        return self

    ###############################################################################################

    def get_frag_count(self):

        # Extract the fragment count
        self.frag_count = self.frag_header & self.FRAG_COUNT_MASK

        # Return the current instance
        return self

    @abstractmethod
    def get_frag_header(self):
        raise NotImplementedError

    ###############################################################################################

    def set_frag_type(self):

        # Generate the fragmentation protocol byte
        self.frag_header = (self.frag_type << FRAGMENT.TYPE.OFFSET) + self.frag_count

        # Return the current instance
        return self

    ###############################################################################################

    def set_frag_count(self):

        # Generate the fragmentation protocol byte
        self.frag_header = (self.frag_type << FRAGMENT.TYPE.OFFSET) + self.frag_count

        # Return the current instance
        return self

    ###############################################################################################

    @abstractmethod
    def set_frag_header(self):
        """ Generate the fragmentation protocol header byte"""

        raise NotImplementedError


###################################################################################################
#                                   GENERIC DEVICENET PACKET
###################################################################################################

class DeviceNetPacket(object):
    """ Generic DeviceNet Protocol Packet

    The DeviceNet protocol defines a source and a destination address. The source address is the
    MAC address of the device sending the message and the destination address is the MAC address
    of the device receiving the message. Depending on the type of the message the source and
    destination addresses can be encoded in the CAN identifier field of the CAN frame or in the
    explicit message body.

    Packets that inherit from this class are used for explicit messages only such as:
     - Explicit Messages
     - I/O Messages
     - DUPMAC Messages

    For more information see 'The CIP Networks Library, Volume 3, DeviceNet Adaptation of CIP".

    Args:
        group_id (int)      : The message group
        message_id (int)    : The message type
        src_mac (int)       : The MAC of the device sending the packet
        dst_mac (int)       : The MAC of the device receiving the packet
        data (iterable)     : The pure data (no headers)

    Example:
        >>> packet = DeviceNetPacket(
        ...     group_id=1,
        ...     message_id=1,
        ...     src_mac=0,
        ...     dst_mac=1,
        ...     data=[1, 2, 3]
        ... )
        >>> packet.validate()
        >>> packet.build()
        >>> packet.can_header
        0x181

    """

    # Limits and constants
    MAX_PACKET_SIZE = 8
    MAX_CAN_ID = 0x7FF
    MAX_MAC = 0x3F

    # Allowed groups are 1, 2, 3, 4
    VALID_GROUP_ID = range(1, 5)

    # Allowed message IDs are 0x00 - 0x2F
    VALID_MESSAGE_ID = range(0x30)

    def __init__(self,
                 group_id=0,
                 message_id=0,
                 src_mac=0,
                 dst_mac=0,
                 data=()
                 ):

        # CAN-ID part
        self.group_id = group_id
        self.message_id = message_id

        # MAC attributes
        self.src_mac = src_mac
        self.dst_mac = dst_mac

        # Public attributes
        self.can_header = 0
        self.can_data = []
        self.data = list(data)

        # Private attributes
        self._mac_in_can_id = 0
        self._mac_in_message = 0
        self._length = 0
        self._message_header = 0
        self._frag_byte = 0
        self._message_body = []

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

    ###############################################################################################

    def __eq__(self, other):

        if issubclass(type(other), DeviceNetPacket):

            result = (self.can_header == other.can_header)
            result &= (self.can_data == other.can_data)

            result &= (self.group_id == other.group_id)
            result &= (self.message_id == other.message_id)

            result &= (self.data == other.data)
            result &= (self.length == other.length)

        else:
            raise DevNetPacketError("Cannot compare DeviceNet packet with other type")

        return result

    def __ne__(self, other):
        return not self.__eq__(other)

    ###############################################################################################

    @property
    def length(self):
        return len(self.can_data)

    ###############################################################################################

    def validate_group_id(self):

        # Check whether the value is None
        if self.group_id is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.group_id, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif self.group_id not in self.VALID_GROUP_ID:
            raise DevNetPacketError("The value for this attribute must be in the range [1, 4]")

    ###############################################################################################

    def validate_message_id(self):

        # Check whether the value is None
        if self.message_id is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.message_id, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif self.message_id not in self.VALID_MESSAGE_ID:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0x2F]")

    ###############################################################################################
    def validate_src_mac(self):

        # Check whether the value is None
        if self.src_mac is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.src_mac, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.src_mac <= 0x3F:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0x3F]")

    ###############################################################################################

    def validate_dst_mac(self):

        # Check whether the value is None
        if self.dst_mac is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.dst_mac, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.dst_mac <= 0x3F:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0x3F]")

    ###############################################################################################

    def validate_message_data(self):

        # Check the type of the value
        if self.data is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is iterable
        elif not isinstance(self.data, Iterable):
            raise DevNetPacketError("The value for this attribute must be iterable")

        # Check whether the value is in the valid range
        elif not 0 <= len(self.data) <= self.MAX_PACKET_SIZE:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 8]")

    ###############################################################################################

    def validate_can_header(self):

        # Check whether the value is None
        if self.can_header is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.can_header, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.can_header <= 0x7FF:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0x7FF]")

    ###############################################################################################

    def validate_can_data(self):

        # Check whether the value is None
        if self.can_data is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is iterable
        elif not isinstance(self.can_data, Iterable):
            raise DevNetPacketError("The value for this attribute must be iterable")

        # Check whether the value is in the valid range
        elif not 0 <= len(self.can_data) <= 8:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 8]")

    ###############################################################################################

    def get_group_id(self):

        self.group_id = devnet_addr(self.can_header)[0]

        return self

    def get_message_id(self):

        self.message_id = devnet_addr(self.can_header)[1]

        return self

    ###############################################################################################

    def get_src_mac(self):

        # Get the group and message ID
        self.group_id, self.message_id, self._mac_in_can_id = devnet_addr(self.can_header)

        # GROUP 1 or 3
        if self.group_id in (1, 3):
            self.src_mac = self._mac_in_can_id

        # GROUP 2
        elif self.group_id == 2:

            if self.message_id in (BITSTROBE.REQ, EXPLICIT.RSP, UNCONNECTED.RSP):
                self.src_mac = self._mac_in_can_id

            else:
                self.src_mac = self._mac_in_message

        # Other groups
        else:
            raise DevNetPacketError("Cannot parse the source MAC address from the group-ID and message-ID")

    ###############################################################################################

    def get_dst_mac(self):

        # Get the group and message ID
        self.group_id, self.message_id, self._mac_in_can_id = devnet_addr(self.can_header)

        if self.group_id in (1, 3):
            self.dst_mac = self._mac_in_message

        elif self.group_id == 2:

            if self.message_id not in (BITSTROBE.REQ, EXPLICIT.RSP, UNCONNECTED.RSP):
                self.dst_mac = self._mac_in_can_id
            else:
                self.src_mac = self._mac_in_message
        else:
            raise DevNetPacketError("Cannot parse the source MAC address from the group-ID and message-ID")

    ###############################################################################################

    def get_message_data(self):
        """ Parse the packet data from the CAN payload

        The data is the same as the CAN payload and includes all the packet attributes in a single
        sequence of bytes with respect to the packet structure.

        Returns:
            DupMacPacket: The current instance with updated packet data attribute

        """

        # The packet data and the CAN payload are the same
        self.data = self.can_data

        # Return the packet instance
        return self

    ###############################################################################################

    def parse_can_header(self, frame):
        """ Parse the CAN header and extract the group, message and MAC parameters form the CAN-ID.

        Description:
            See Volume 3, Ch.2-2, p.2-4 for more details.

        Args:
            frame (CanFrame) : A CAN frame object

        Returns:
            group_id    (int) : The message group
            message_id  (int) : The message type
            mac         (int) : The MAC of the device encoded in the CAN-ID

        """

        try:
            # Update the devicenet message addressing parameters
            self.group_id, self.message_id, self._mac_in_can_id = devnet_addr(frame.can_id)
            self.can_header = frame.can_id

        except Exception:
            raise DevNetParsingError("Failed to parse CAN header")

        # Return the parsed parameters
        return self

    def parse_can_data(self, frame):

        try:
            # Parse the CAN payload
            self.can_data = frame.data[:]

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def set_group_id(self, value):

        # Store the group ID
        self.group_id = value

        # Update the CAN header
        self.can_header = can_addr(
            msg_group=self.group_id,
            msg_id=self.message_id,
            mac=self._mac_in_can_id
        )

        return self

    ###############################################################################################

    def set_message_id(self, value):

        # Store the message ID
        self.message_id = value

        # Update the CAN header
        self.can_header = can_addr(
            msg_group=self.group_id,
            msg_id=self.message_id,
            mac=self._mac_in_can_id
        )

        return self

    ###############################################################################################

    def set_src_mac(self, value):

        # Store the source MAC
        self.src_mac = value

        # Check whether the source MAC is part of the CAN-ID
        if self.group_id in (1, 3):
            self._mac_in_can_id = self.src_mac

        elif self.group_id == 2:

            if self.message_id in (BITSTROBE.REQ, EXPLICIT.RSP, UNCONNECTED.RSP):
                self._mac_in_can_id = self.src_mac

        # Update the CAN header
        self.can_header = can_addr(
            msg_group=self.group_id,
            msg_id=self.message_id,
            mac=self._mac_in_can_id
        )

        return self

    ###############################################################################################

    def set_dst_mac(self, value):

        # Store the destination MAC
        self.dst_mac = value

        # Check whether the destination MAC is part of the CAN-ID
        if self.group_id in (2,):

            if self.message_id not in (BITSTROBE.REQ, EXPLICIT.RSP, UNCONNECTED.RSP):
                self._mac_in_can_id = self.dst_mac

        # Update the CAN header
        self.can_header = can_addr(
            msg_group=self.group_id,
            msg_id=self.message_id,
            mac=self._mac_in_can_id
        )

        return self

    ###############################################################################################

    def set_message_data(self, data):
        """ Set all the packet data as a sequence of bytes in the CAN payload

        The message data is the same as the CAN payload and includes all the packet attributes in a
        single sequence of bytes with respect to the packet structure.

        Args:
            data (iterable): The serialized packet attributes

        Returns:
            DupMacPacket: The current instance with an updated CAN payload

        """

        try:

            # Store the message data
            self.data = data

            # Update the CAN payload
            self.can_data = data

        # Unexpected errors
        except Exception:
            raise

    ###############################################################################################

    def build_can_header(self):
        """ Generate the CAN header from the current instance state """

        # GROUP 1: Pre-defined Master/Slave Set (Slave to master)
        if self.group_id == MESSAGE.GROUP1.ID:

            self._mac_in_can_id = self.src_mac
            self.can_header = CAN_ID.GROUP1.START
            self.can_header += (self.message_id << CAN_ID.GROUP1.MSG_ID_OFFSET)
            self.can_header += self._mac_in_can_id

        # GROUP 2: Pre-defined Master/Slave Set (Master to slave)
        elif self.group_id == MESSAGE.GROUP2.ID:

            if self.message_id in {BITSTROBE.REQ, EXPLICIT.RSP, UNCONNECTED.RSP}:
                self._mac_in_can_id = self.src_mac
            else:
                self._mac_in_can_id = self.dst_mac

            self.can_header = CAN_ID.GROUP2.START
            self.can_header += (self._mac_in_can_id << CAN_ID.GROUP2.MAC_OFFSET)
            self.can_header += self.message_id

        # GROUP 3: Unconnected Message Manager
        elif self.group_id == MESSAGE.GROUP3.ID:
            self._mac_in_can_id = self.src_mac
            self.can_header = CAN_ID.GROUP3.START
            self.can_header += (self.message_id << CAN_ID.GROUP3.MSG_ID_OFFSET)
            self.can_header += self._mac_in_can_id

        # GROUP 4: Other Messages
        elif self.group_id == MESSAGE.GROUP4.ID:
            self.can_header = CAN_ID.GROUP4.START
            self.can_header += self.message_id

        else:
            # raise DevNetGroupError
            pass

        # Return the current instance
        return self

    ###############################################################################################

    def set_can_data(self, *args):
        """ Generate the CAN payload from the current instance state

        The function generates the CAN payload from the current instance state. The function
        accepts an arbitrary number of arguments. The arguments can be scalar values (int, float)
        or iterable values (array, list, string). The function iterates over the arguments and
        adds the arguments to the CAN payload. The function does not return a value. Instead, it
        updates the CAN payload attribute of the current instance.

        Args:
            args (iterable) : The data to be added to the packet

        Returns:
            self (DeviceNetPacket) : The current packet instance

        """

        payload = []

        for item in args:

            # Check whether the item is iterable
            try:
                iter(item)

            # Add scalar values to the packet (int, float)
            except TypeError:
                payload.append(item)

            # Add iterable values to the packet (array, list, string)
            else:
                payload.extend(item)

        # Store the payload
        self.can_data = payload

        # Return the packet instance
        return self

    ###############################################################################################

    def from_frame(self, frame):
        """ Parse the CAN frame and save the data into the context of the current instance

        Args:
            frame (CanFrameAbc) : A CAN frame object

        Returns:
            self (DeviceNetPacket) : The current packet instance
        """

        try:
            # Parse the CAN header
            self.can_header = frame.can_id

            # Parse the CAN payload
            self.can_data = frame.data

            # Parse the packet
            self.parse()

        except Exception:
            raise DevNetParsingError("Failed to parse CAN frame")

        return self

    ###############################################################################################

    def to_frame(self, frame_class=CanFrameAbc):
        """ Generate a CAN frame from the current instance state

        Returns:
            frame (CanFrameAbc) : A CAN frame object

        """

        # Update the packet instance
        self.build()

        # Create a CAN frame
        frame = frame_class(can_id=self.can_header, data=self.can_data)

        return frame

    ###############################################################################################

    def deserialize(self, stream):

        # Get the CAN header and CAN payload from the data stream
        stream = bytearray(stream)
        self.can_header = bytes_to_integer(stream=stream[:2])
        self.can_data = list(stream[2:])

        # Parse the packet structure
        self.get_group_id()
        self.get_message_id()
        self.get_src_mac()
        self.get_dst_mac()
        self.get_message_data()

        return self

    ###############################################################################################

    def serialize(self):
        """ Serialize the packet into a byte stream

        Returns:
            stream (bytearray) : A byte stream representing the packet

        """

        stream = bytearray()
        stream.extend(integer_to_bytes(value=self.can_header, size=2))
        stream.extend(self.can_data)

        return stream

    # ###############################################################################################
    #
    # def split(self):
    #     """ Split the data into fragments
    #
    #     The function splits the data into fragments. The maximum payload per frame is variable and
    #     depends on the type of the message. For explicit messages the maximum payload is 6 bytes.
    #     For I/O messages the maximum payload is 7 bytes.
    #
    #     Returns:
    #         fragments (list) : A list of CAN frames
    #
    #     """
    #
    #     if isinstance(self, (ExplicitPacket, ExplicitServicePacket)):
    #         data_length = 6
    #         fragment_class = ExplicitFragPacket
    #     else:
    #         data_length = 7
    #         fragment_class = IoFragPacket
    #
    #     fragments = []
    #
    #     # Check whether the maximum payload per frame is exceeded
    #     if self.length > 8:
    #
    #         # Calculate the number of fragments required
    #         frag_count = int(len(self.data) / data_length)
    #
    #         # Check whether the payload is divisible by 8
    #         if len(self.data) % data_length:
    #             frag_count += 1
    #
    #         first_fragment = 0
    #         last_fragment = frag_count - 1
    #
    #         for i in range(frag_count):
    #
    #             start = i * data_length
    #             end = (i + 1) * data_length
    #
    #             block = self.data[start:end]
    #
    #             if i == first_fragment:
    #                 fragment = fragment_class(
    #                     group_id=self.group_id,
    #                     message_id=self.message_id,
    #                     src_mac=self.src_mac,
    #                     dst_mac=self.dst_mac,
    #                     frag_count=i,
    #                     frag_type=FRAGMENT.TYPE.START,
    #                     data=block
    #                 ).build()
    #
    #             elif first_fragment < i < last_fragment:
    #                 fragment = fragment_class(
    #                     group_id=self.group_id,
    #                     message_id=self.message_id,
    #                     src_mac=self.src_mac,
    #                     dst_mac=self.dst_mac,
    #                     frag_count=i,
    #                     frag_type=FRAGMENT.TYPE.MIDDLE,
    #                     data=block
    #                 ).build()
    #
    #             elif i == last_fragment:
    #                 fragment = fragment_class(
    #                     group_id=self.group_id,
    #                     message_id=self.message_id,
    #                     src_mac=self.src_mac,
    #                     dst_mac=self.dst_mac,
    #                     frag_count=i,
    #                     frag_type=FRAGMENT.TYPE.FINAL,
    #                     data=block
    #                 ).build()
    #
    #             else:
    #                 raise DevNetParsingError("Malformed packet")
    #
    #             fragments.append(fragment.to_frame())
    #
    #     else:
    #         fragments.append(self.to_frame())
    #
    #     return fragments

    ###############################################################################################

    def clear(self):

        self.can_header = 0
        self.can_data = []

        return self

    ###############################################################################################

    def build(self):
        """ Update the calculated attributes of the packet

        Returns:
            self (DeviceNetPacket) : A instance of the this class

        """

        self.clear()

        # Build the packet using the current instance state
        self.set_group_id(self.group_id)
        self.set_message_id(self.message_id)
        self.set_src_mac(self.src_mac)
        self.set_dst_mac(self.dst_mac)
        self.set_message_data(self.data)

        return self

    ###############################################################################################

    def parse(self):
        """ Parse the packet and update the calculated attributes of the packet

        The method requires the CAN header and CAN payload to be set by the user. This is done
        either manually or using any kind of deserialization function, e.g. from_frame() or
        deserialize(). The values are then parsed and the current packet instance is updated.

        Returns:
            self (DeviceNetPacket) : A instance of the this class

        """

        self.get_group_id()
        self.get_message_id()
        self.get_src_mac()
        self.get_dst_mac()
        self.get_message_data()

    ###############################################################################################

    def validate(self):
        """ Validate the packet attributes

        This method is optional and can be used to validate the packet attributes. The method
        checks whether the packet attributes are valid. Typically this method is called before a
        call to the build() method. The method raises an exception if the packet attributes are
        invalid.

        Raises:
            DevNetPacketError : The packet attributes are invalid

        Returns:
            self (DeviceNetPacket) : A instance of the this class

        """

        self.validate_can_data()
        self.validate_can_header()
        self.validate_group_id()
        self.validate_message_id()
        self.validate_src_mac()
        self.validate_dst_mac()
        self.validate_message_data()

        return self


###################################################################################################
#                                        EXPLICIT PACKET
###################################################################################################
class ExplicitPacket(DeviceNetPacket):
    """ Explicit packet format

    The packet is used to send explicit messages which exceed the maximum payload of a CAN frame.
    The packet contains the the message header and the message body. The packet is used for
     explicit messages only.

    Packets that inherit from this class are used for explicit messages only such as:
        - Explicit Service Messages
        - Error Messages
        - Unconnected Messages (open, close)
        - Unconnected Message Manager Services (open, close)
        - Device Heartbeat Messages
        - Device Shutdown Messages

    The structure of the packet is as follows:
        - Byte 0    : Fragmentation flag, transaction ID and MAC address (Message Header)
        - Byte 1-7  : Service Data (Message Body)

    Args:
        group_id (int)      : The message group
        message_id (int)    : The message type
        src_mac (int)       : The MAC of the device sending the packet
        dst_mac (int)       : The MAC of the device receiving the packet
        data (iterable)     : The service data

    Example:
        >>> test_packet = ExplicitPacket(group_id=2, message_id=6, src_mac=0, dst_mac=1, data=(1, 2, 3))
        >>> frame = test_packet.to_frame()
        >>> parsed_packet = ExplicitPacket().from_frame(frame)
        >>> assert test_packet == parsed_packet

    """

    def __init__(self,
                 group_id=EXPLICIT.REQ_GROUP,
                 message_id=EXPLICIT.REQ,
                 src_mac=0,
                 dst_mac=0,
                 data=()
                 ):

        # Initialize the base class
        super(ExplicitPacket, self).__init__(
            group_id=group_id,
            message_id=message_id,
            src_mac=src_mac,
            dst_mac=dst_mac,
            data=data
        )

        # Transaction ID
        self.xid = 0

        # Fragmentation flag
        self.frag_flag = 0

    ###############################################################################################

    @property
    def message_header(self):
        return self._message_header

    @message_header.setter
    def message_header(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 0xFF:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFF]")

        self._message_header = value

    ###############################################################################################

    @property
    def message_body(self):
        return self._message_body

    @message_body.setter
    def message_body(self, value):
        self._message_body = value
        self._data = value

    ###############################################################################################
    @property
    def data(self):
        """ Get the data attribute """
        return self._data

    @data.setter
    def data(self, value):
        """ Set the data attribute """

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is iterable
        elif not isinstance(value, Iterable):
            raise DevNetPacketError("The value for this attribute must be iterable")

        # For the explicit packet the data is the message body
        self._message_body = value
        self._data = value

    ###############################################################################################

    def parse_message_header(self, frame, offset=0):

        try:
            # Parse the fragmentation flag
            self.frag_flag = (frame.data[offset] & PACKET.FRAG_FLAG.MASK) >> PACKET.FRAG_FLAG.OFFSET

            # Parse the transaction ID
            self.xid = (frame.data[offset] & PACKET.XID.MASK) >> PACKET.XID.OFFSET

            # Parse the MAC address in the message
            self._mac_in_message = (frame.data[offset] & PACKET.MAC.MASK)

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse fragmentation protocol header byte")

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def parse_message_body(self, frame, offset=1):

        try:
            # Parse the message body
            self.message_body = frame.data[offset:8]

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse fragmentation protocol header byte")

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def generate_message_header(self):
        """ Generate the message header from the current instance state """

        # Generate the message header
        self.message_header = (self.frag_flag << PACKET.FRAG_FLAG.OFFSET)
        self.message_header += (self.xid << PACKET.XID.OFFSET)
        self.message_header += self._mac_in_message

        # Return the packet instance
        return self

    ###############################################################################################

    def generate_message_body(self):

        # Generate the message body
        self.message_body = self.data[:]

        # Return the packet instance
        return self

    ###############################################################################################

    def from_frame(self, frame):
        """ Parse the CAN frame and save the data into the context of the current instance """

        # Parse the packet from the CAN frame
        super(ExplicitPacket, self).from_frame(frame)

        # Parse the packet attributes from the CAN frame payload
        self.parse_message_header(frame, offset=0)
        self.parse_message_body(frame, offset=1)

        return self

    ###############################################################################################

    def build(self):

        self.build_can_header()
        self.generate_message_header()
        self.generate_message_body()

        # Generate the CAN payload
        self.set_can_data(
            self.message_header,
            self.message_body
        )

        return self


###################################################################################################
#                                      EXPLICIT SERVICE REQUEST PACKET
###################################################################################################

class ExplicitServicePacket(FragHeaderMixin, ExplicitPacket):
    """ Explicit service packet format

    The general structure of the packet is as follows:
        - Byte 0    : Fragmentation flag, transaction ID and MAC address (Message Header)
        - Byte 1    : Service header (Request/Response flag and service code)
        - Byte 2-7  : Service Data (Message Body)

    For request messages with body format 0 the packet structure is as follows:
        - Byte 2    : Class ID (Message Body)
        - Byte 3    : Instance ID (Message Body)
        - Byte 4-7  : Service Data (Message Body)

    For request messages with body format 1 the packet structure is as follows:
        - Byte 2    : Class ID (Message Body)
        - Byte 3-4  : Instance ID (Message Body)
        - Byte 5-7  : Service Data (Message Body)

    For request messages with body format 2 the packet structure is as follows:
        - Byte 2-3  : Class ID (Message Body)
        - Byte 4-5  : Instance ID (Message Body)
        - Byte 6-7  : Service Data (Message Body)

    For request messages with body format 3 the packet structure is as follows:
        - Byte 2-3  : Class ID (Message Body)
        - Byte 4    : Instance ID (Message Body)
        - Byte 5-7  : Service Data (Message Body)

    For request messages with body format 4 the packet structure is as follows:
        - Byte 2    : Path length (Message Body)
        - Byte 3    : Path (Message Body)
        - Byte 4-7  : Service Data (Message Body)

    Args:
        group_id (int)          : The message group
        message_id (int)        : The message type
        src_mac (int)           : The MAC of the device sending the packet
        dst_mac (int)           : The MAC of the device receiving the packet
        packet_type (int)       : The packet type (request=0, response=1)
        service_code (int)      : The service code
        class_id (int)          : The class ID
        instance_id (int)       : The instance ID
        path_length (int)       : The path length
        path (iterable)         : The path
        service_data (iterable) : The service data
        body_format (int)       : The message body format

    Example:
        >>> test_packet = ExplicitServicePacket(group_id=2, message_id=6, src_mac=0, dst_mac=1, body_format=0)
        >>> frame = test_packet.to_frame()
        >>> parsed_packet = ExplicitServicePacket().from_frame(frame)
        >>> assert test_packet == parsed_packet

    """

    __REQUEST = 0
    __RESPONSE = 1

    __BODY_FORMAT_8_8 = 0
    __BODY_FORMAT_8_16 = 1
    __BODY_FORMAT_16_16 = 2
    __BODY_FORMAT_16_8 = 3
    __BODY_FORMAT_EPATH = 4

    def __init__(self,
                 group_id=EXPLICIT.REQ_GROUP,
                 message_id=EXPLICIT.REQ,
                 src_mac=0,
                 dst_mac=0,
                 packet_type=0,
                 service_code=0,
                 class_id=0,
                 instance_id=0,
                 path_length=0,
                 path=(),
                 service_data=(),
                 body_format=0
                 ):

        # Initialize the base class
        super(ExplicitServicePacket, self).__init__(
            group_id=group_id,
            message_id=message_id,
            src_mac=src_mac,
            dst_mac=dst_mac,
            frag_type=FRAGMENT.TYPE.START,
            frag_count=0,
        )

        # The message body format (0-4)
        self._body_format = body_format

        # Request(0) or Response(1)
        self.packet_type = packet_type

        # Service header combines the R/R flag (request/response) and the service code
        self._service_header = 0

        # Service code (max 7 bits)
        self._service_code = service_code

        # Service data (max 4 bytes)
        self._service_data = service_data

        # Message body format 0-3 (max 4 bytes)
        self._class_id = class_id
        self._instance_id = instance_id

        # Message body format 4 (max 2 bytes)
        self._path_length = path_length
        self._path = path

    ###############################################################################################
    @property
    def body_format(self):
        return self._body_format

    @body_format.setter
    def body_format(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 4:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 4]")

        self._body_format = value

    ###############################################################################################
    @property
    def rr_flag(self):
        return self.packet_type

    @rr_flag.setter
    def rr_flag(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 1:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 1]")

        self.packet_type = value

    ###############################################################################################

    @property
    def service_code(self):
        return self._service_code

    @service_code.setter
    def service_code(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 0x7F:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0x7F]")

        self._service_code = value

    ###############################################################################################

    @property
    def class_id(self):
        return self._class_id

    @class_id.setter
    def class_id(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 0xFFFF:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFFFF]")

        self._class_id = value

    ###############################################################################################

    @property
    def instance_id(self):
        return self._instance_id

    @instance_id.setter
    def instance_id(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 0xFFFF:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFFFF]")

        self._instance_id = value

    ###############################################################################################

    @property
    def service_header(self):
        return self._service_header

    @service_header.setter
    def service_header(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 0xFF:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFF]")

        self._service_header = value

    ###############################################################################################

    @property
    def service_data(self):
        return self._service_data

    @service_data.setter
    def service_data(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is iterable
        elif not isinstance(value, Iterable):
            raise DevNetPacketError("The value for this attribute must be iterable")

        self._service_data = value

    ###############################################################################################

    def is_request(self):
        return self.rr_flag == self.__REQUEST

    def is_response(self):
        return self.rr_flag == self.__RESPONSE

    ###############################################################################################

    def parse_service_header(self, frame, offset=1):
        """ Parse the service header byte """

        try:
            self.service_header = frame.data[offset]
            self.rr_flag = (self.service_header & PACKET.RSP_FLAG.MASK) >> PACKET.RSP_FLAG.OFFSET
            self.service_code = self.service_header & PACKET.SERVICE.MASK

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse service header byte")

        # Unexpected errors
        except Exception:
            raise

        return self

    ###############################################################################################

    def parse_message_body(self, frame, offset=1):
        """ Parse the packet body and save the data into the context of the current instance"""

        try:
            # Parse the message body
            self.message_body = frame.data[offset:8]

            # Service header
            self.rr_flag = (self.message_body[0] & PACKET.RSP_FLAG.MASK) >> PACKET.RSP_FLAG.OFFSET
            self.service_code = self.message_body[0] & PACKET.SERVICE.MASK

            # The packet type is is request
            if self.rr_flag == self.__REQUEST:
                self.src_mac = self._mac_in_message
                self.dst_mac = self._mac_in_can_id

                # Body format 0: 8-bit class ID, 8-bit instance ID, 5 bytes service data
                self.class_id = self.message_body[1]
                self.instance_id = self.message_body[2]
                self.service_data = self.message_body[3:8]

                # TODO: Body format 1: 8-bit class ID, 16-bit instance ID, 4 bytes service data
                # TODO: Body format 2: 16-bit class ID, 16-bit instance ID, 3 bytes service data
                # TODO: Body format 3: 16-bit class ID, 8-bit instance ID, 4 bytes service data

            # The packet type is response
            else:
                self.src_mac = self._mac_in_can_id
                self.dst_mac = self._mac_in_message
                self.service_data = self.message_body[1:8]

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse message body")

        # Unexpected error
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def generate_service_header(self):
        self.service_header = (self.rr_flag << PACKET.RSP_FLAG.OFFSET)
        self.service_header += self.service_code
        return self

    ###############################################################################################

    def generate_message_body(self):
        """ Generate the message body from the current instance state """

        # Generate the service code byte
        self.generate_service_header()

        # Check whether the service data is iterable
        if not isinstance(self.service_data, Iterable):
            self.service_data = [self.service_data]

        # Generate the message body
        body = [self.service_header, self.class_id, self.instance_id]
        body.extend(self.service_data)

        # Store the message body
        self.message_body = body

        # Return the packet instance
        return self

    ###############################################################################################

    def from_frame(self, frame):
        """ Parse the CAN frame and save the data into the context of the current instance """

        # Parse the packet from the CAN frame
        super(ExplicitServicePacket, self).from_frame(frame)

        # Parse the packet attributes from the CAN frame payload
        self.parse_message_header(frame, offset=0)

        # The packet is fragmented
        if self.frag_flag:
            self.get_frag_header()
            self.parse_message_body(frame, offset=2)

        # The packet is not fragmented
        else:
            self.parse_message_body(frame, offset=1)

        # Return the packet instance
        return self

    def get_frag_header(self):
        """ Parse the fragmentation protocol header byte

        Returns:
            self (DeviceNetPacket) : The current packet instance

        """

        try:

            # Store the fragmentation protocol header
            self.frag_header = self.can_data[1]

            # Parse the fragmentation protocol header
            self.get_frag_type()
            self.get_frag_count()

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse fragmentation protocol header byte")

        # Unexpected errors
        except Exception:
            raise

        # Return the current instance
        return self

    def set_frag_header(self):
        """ Generate the fragmentation protocol header byte"""

        # Generate the fragmentation protocol byte
        self.frag_header = (self.frag_type << self.FRAG_TYPE_OFFSET) + self.frag_count

        # self.can_data[1] = self.frag_header

        # Return the current instance
        return self

    ###############################################################################################

    def build(self):

        # Generate the packet attributes
        self.generate_message_header()
        self.generate_message_body()

        # Generate the CAN header and payload
        self.build_can_header()
        self.set_can_data(
            self.message_header,
            self.message_body
        )

        return self

    ###############################################################################################

    def split(self):
        """ Split the data into fragments

        The function splits the data into fragments. The maximum payload per frame is variable and
        depends on the type of the message. For explicit messages the maximum payload is 6 bytes.
        For I/O messages the maximum payload is 7 bytes.

        Returns:
            fragments (list) : A list of CAN frames

        """

        data_length = 6
        fragments = []

        # Check whether the maximum payload per frame is exceeded
        if self.length > 8:

            # Calculate the number of fragments required
            frag_count = int(len(self.data) / data_length)

            # Check whether the payload is divisible by 8
            if len(self.data) % data_length:
                frag_count += 1

            first_fragment = 0
            last_fragment = frag_count - 1

            for i in range(frag_count):

                start = i * data_length
                end = (i + 1) * data_length

                block = self.data[start:end]

                if i == first_fragment:
                    fragment = ExplicitFragPacket(
                        group_id=self.group_id,
                        message_id=self.message_id,
                        src_mac=self.src_mac,
                        dst_mac=self.dst_mac,
                        frag_count=i,
                        frag_type=FRAGMENT.TYPE.START,
                        data=block
                    ).build()

                elif first_fragment < i < last_fragment:
                    fragment = ExplicitFragPacket(
                        group_id=self.group_id,
                        message_id=self.message_id,
                        src_mac=self.src_mac,
                        dst_mac=self.dst_mac,
                        frag_count=i,
                        frag_type=FRAGMENT.TYPE.MIDDLE,
                        data=block
                    ).build()

                elif i == last_fragment:
                    fragment = ExplicitFragPacket(
                        group_id=self.group_id,
                        message_id=self.message_id,
                        src_mac=self.src_mac,
                        dst_mac=self.dst_mac,
                        frag_count=i,
                        frag_type=FRAGMENT.TYPE.FINAL,
                        data=block
                    ).build()

                else:
                    raise DevNetParsingError("Malformed packet")

                fragments.append(fragment.to_frame())

        else:
            fragments.append(self.to_frame())

        return fragments


###################################################################################################
#                                        EXPLICIT FRAGMENTED PACKET
###################################################################################################

class ExplicitFragPacket(FragHeaderMixin, ExplicitPacket):
    """ Explicit fragmentation packet format

    The packet is used to send explicit messages which exceed the maximum payload of a CAN frame.
    The packet contains the fragmentation header, the message header and the message body.

    The following rules apply for fragmented messages:
        - The fragmentation flag (FRAG) is set to FRAGMENTED (0x01) for all fragments.
        - The fragmentation type is set to FRAGMENT_TYPE_START (0x00) for the first fragment
        - The fragmentation type is set to FRAGMENT_TYPE_MIDDLE (0x01) for all fragments in between
        - The fragmentation type is set to FRAGMENT_TYPE_FINAL (0x02) for the last fragment.
        - The fragmentation count is set to the fragment number
        - The message body contains the service data

    The structure of the acknowledge response is as follows:
        - Byte 0    : Fragmentation flag, transaction ID and MAC address (Message Header)
        - Byte 1    : Fragment type and fragment count (Fragment Header)
        - Byte 2-7  : Service Data (Message Body)

    Args:
        group_id (int)      : The message group
        message_id (int)    : The message type
        src_mac (int)       : The MAC of the device sending the packet
        dst_mac (int)       : The MAC of the device receiving the packet
        frag_count (int)    : The fragment count
        frag_type (int)     : The fragment type
        data (iterable)     : The service data

    Example:
        >>> test_packet = ExplicitFragPacket(
        ...     group_id=2,
        ...     message_id=3,
        ...     src_mac=0,
        ...     dst_mac=1,
        ...     data=(1, 2, 3)
        ... )
        >>> frame = test_packet.to_frame()
        >>> parsed_packet = ExplicitFragPacket().from_frame(frame)
        >>> assert test_packet == parsed_packet

    """

    def __init__(self,
                 group_id=EXPLICIT.REQ_GROUP,
                 message_id=EXPLICIT.REQ,
                 src_mac=0,
                 dst_mac=0,
                 frag_count=0,
                 frag_type=FRAGMENT.TYPE.MIDDLE,
                 data=()
                 ):
        # Initialize the base class
        super(ExplicitFragPacket, self).__init__(
            group_id=group_id,
            message_id=message_id,
            src_mac=src_mac,
            dst_mac=dst_mac,
            frag_count=frag_count,
            frag_type=frag_type,
            data=data
        )

        # Fragmentation attributes
        self.frag_flag = 1
        self.frag_type = frag_type
        self.frag_count = frag_count

    def get_frag_header(self):
        """ Parse the fragmentation protocol header byte

        Returns:
            self (DeviceNetPacket) : The current packet instance

        """

        try:

            # Store the fragmentation protocol header
            self.frag_header = self.can_data[1]

            # Parse the fragmentation protocol header
            self.get_frag_type()
            self.get_frag_count()

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse fragmentation protocol header byte")

        # Unexpected errors
        except Exception:
            raise

        # Return the current instance
        return self

    def set_frag_header(self):
        """ Generate the fragmentation protocol header byte"""

        # Generate the fragmentation protocol byte
        self.frag_header = (self.frag_type << self.FRAG_TYPE_OFFSET) + self.frag_count

        # self.can_data[1] = self.frag_header

        # Return the current instance
        return self

    ###############################################################################################

    def from_frame(self, frame):
        # Parse the CAN frame attributes
        self.parse_can_header(frame)
        self.parse_can_data(frame)

        # Parse the packet attributes from the CAN frame payload
        self.parse_message_header(frame, offset=0)
        self.get_frag_header()
        self.parse_message_body(frame, offset=2)

        # Return the packet instance
        return self

    ###############################################################################################

    def build(self):
        self.build_can_header()
        self.generate_message_header()
        self.set_frag_header()
        self.set_message_data(self.data)

        # Generate the CAN payload
        self.set_can_data(
            self.message_header,
            self.frag_header,
            self.message_body
        )

        return self


###################################################################################################
#                                     EXPLICIT FRAGMENTED ACKNOWLEDGE PACKET
###################################################################################################

class ExplicitFragAckPacket(ExplicitFragPacket):
    """ Acknowledge response for fragmented messages

    The acknowledge response is sent by the receiver of a fragmented message to the sender of
    the message. The packet contains the acknowledge status of the message together with the
    fragment counter. The fragment type is set to FRAGMENT_TYPE_ACK (0x03).

    The structure of the acknowledge response is as follows:
        - Byte 0: Fragmentation flag, transaction ID and MAC address (Message Header)
        - Byte 1: Fragment type and fragment count (Fragment Header)
        - Byte 2: Acknowledge status (Message Body)

    Args:
        group_id (int)      : The message group
        message_id (int)    : The message type
        src_mac (int)       : The MAC of the device sending the packet
        dst_mac (int)       : The MAC of the device receiving the packet
        frag_count (int)    : The fragment count
        frag_type (int)     : The fragment type
        ack_status (int)    : The acknowledge status

    Example:
        >>> expected_packet = ExplicitFragAckPacket(
        ...     group_id=2,
        ...     message_id=3,
        ...     src_mac=0,
        ...     dst_mac=1,
        ...     frag_count=0,
        ...     frag_type=FRAGMENT.TYPE.ACK,
        ...     ack_status=0
        ... )
        >>>
        >>> frame = expected_packet.to_frame()
        >>> obtained_packet = ExplicitFragAckPacket().from_frame(frame)
        >>> assert expected_packet == obtained_packet

    """

    def __init__(self,
                 group_id=EXPLICIT.REQ_GROUP,
                 message_id=EXPLICIT.REQ,
                 src_mac=0,
                 dst_mac=0,
                 frag_count=0,
                 frag_type=FRAGMENT.TYPE.ACK,
                 ack_status=0
                 ):

        # Call the base class constructor
        super(ExplicitFragAckPacket, self).__init__(
            group_id=group_id,
            message_id=message_id,
            src_mac=src_mac,
            dst_mac=dst_mac,
            frag_count=frag_count,
            frag_type=frag_type,
            data=[ack_status, ]
        )

        self._ack_status = ack_status

    ###############################################################################################
    @property
    def ack_status(self):
        return self._ack_status

    @ack_status.setter
    def ack_status(self, value):

        # Check whether the value is None
        if value is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(value, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= value <= 0xFF:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFF]")

        self._ack_status = value

    ###############################################################################################

    def from_frame(self, frame):

        # Parse the CAN frame
        super(ExplicitFragAckPacket, self).from_frame(frame)

        # Validate the packet type
        self.validate()

        # Return the packet instance
        return self

    ###############################################################################################

    def validate(self):

        # Check that received fragment is of type ACK
        if self.frag_type != FRAGMENT.TYPE.ACK:
            raise DevNetParsingError("Malformed fragment acknowledge packet")

        # Too much data received
        elif self.ack_status == 0x01:
            raise DevNetParsingError("Too much data received")

        # Unknown status code
        elif self.ack_status in range(0x02, 0x100):
            raise DevNetParsingError("Unknown status code")


###################################################################################################
#                                                  I/O PACKET
###################################################################################################

class IoPacket(DeviceNetPacket):
    """ I/O message format

    The structure of the I/O message is as follows:
        - Byte 0-7: I/O data

    Args:
        group_id (int)      : The message group
        message_id (int)    : The message type
        src_mac (int)       : The MAC of the device sending the packet
        dst_mac (int)       : The MAC of the device receiving the packet
        data (iterable)     : The I/O data

    Example:
        >>> expected_packet = IoPacket(
        >>>     group_id=2,
        >>>     message_id=0,
        >>>     src_mac=0,
        >>>     dst_mac=1,
        >>>     data=(1, 2, 3, 4, 5, 6, 7)
        >>> ).build()
        >>>
        >>> can_frame = expected_packet.to_frame()
        >>> obtained_packet = IoPacket().from_frame(can_frame)
        >>> assert expected_packet == obtained_packet

    """

    DATA_OFFSET = 0

    def __init__(self,
                 group_id=0,
                 message_id=0,
                 src_mac=0,
                 dst_mac=0,
                 data=()
                 ):

        # Call the base class constructor
        super(IoPacket, self).__init__(
            group_id=group_id,
            message_id=message_id,
            src_mac=src_mac,
            dst_mac=dst_mac,
            data=data)

        # Update the packet data
        self.data = list(data)

    ###############################################################################################

    def parse_data(self, frame, offset=0):

        try:
            # Update the CAN payload
            self.can_data = frame.data[offset:]

            # Update the I/O data
            self.data = self.can_data[:]

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def from_frame(self, frame):

        # Parse the CAN header
        self.parse_can_header(frame)

        # Parse the CAN payload
        self.parse_can_data(frame)

        # Parse the I/O data
        self.parse_data(frame)

        # Return the packet instance
        return self

    ###############################################################################################

    def split(self):
        """ Split the data into fragments

        The function splits the data into fragments. The maximum payload per frame is variable and
        depends on the type of the message. For explicit messages the maximum payload is 6 bytes.
        For I/O messages the maximum payload is 7 bytes.

        Returns:
            fragments (list) : A list of CAN frames

        """

        data_length = 7
        fragments = []

        # Check whether the maximum payload per frame is exceeded
        if self.length > 8:

            # Calculate the number of fragments required
            frag_count = int(len(self.data) / data_length)

            # Check whether the payload is divisible by 8
            if len(self.data) % data_length:
                frag_count += 1

            first_fragment = 0
            last_fragment = frag_count - 1

            for i in range(frag_count):

                start = i * data_length
                end = (i + 1) * data_length

                block = self.data[start:end]

                if i == first_fragment:
                    fragment = IoFragPacket(
                        group_id=self.group_id,
                        message_id=self.message_id,
                        src_mac=self.src_mac,
                        dst_mac=self.dst_mac,
                        frag_count=i,
                        frag_type=FRAGMENT.TYPE.START,
                        data=block
                    )
                    fragment.build()

                elif first_fragment < i < last_fragment:
                    fragment = IoFragPacket(
                        group_id=self.group_id,
                        message_id=self.message_id,
                        src_mac=self.src_mac,
                        dst_mac=self.dst_mac,
                        frag_count=i,
                        frag_type=FRAGMENT.TYPE.MIDDLE,
                        data=block
                    )
                    fragment.build()

                elif i == last_fragment:
                    fragment = IoFragPacket(
                        group_id=self.group_id,
                        message_id=self.message_id,
                        src_mac=self.src_mac,
                        dst_mac=self.dst_mac,
                        frag_count=i,
                        frag_type=FRAGMENT.TYPE.FINAL,
                        data=block
                    )
                    fragment.build()

                else:
                    raise DevNetParsingError("Malformed packet")

                fragments.append(fragment.to_frame())

        else:
            fragments.append(self.to_frame())

        return fragments

    ###############################################################################################

    def build(self):

        # Generate the CAN header
        self.build_can_header()

        # Generate the CAN payload
        self.set_can_data(
            self.data
        )

        # Return the packet instance
        return self


###################################################################################################
#                                              I/O FRAGMENTED PACKET
###################################################################################################

class IoFragPacket(FragHeaderMixin, IoPacket):
    """ I/O fragmented message format

    The structure of the I/O message is as follows:
        - Byte 0    : Fragmentation protocol header
        - Byte 1-7  : I/O data

    Args:
        group_id (int)      : The message group
        message_id (int)    : The message type
        src_mac (int)       : The MAC of the device sending the packet
        dst_mac (int)       : The MAC of the device receiving the packet
        data (iterable)     : The I/O data
        frag_count (int)    : The fragment count
        frag_type (int)     : The fragment type

    Example:
        >>> expected_packet = IoFragPacket(
        >>>     group_id=2,
        >>>     message_id=0,
        >>>     src_mac=0,
        >>>     dst_mac=1,
        >>>     frag_type=0,
        >>>     frag_count=1,
        >>>     data=(1, 2, 3, 4, 5, 6, 7)
        >>> ).build()
        >>>
        >>> can_frame = expected_packet.to_frame()
        >>> obtained_packet = IoFragPacket().from_frame(can_frame)
        >>> assert expected_packet == obtained_packet

    """

    def __init__(self,
                 group_id=0,
                 message_id=0,
                 src_mac=0,
                 dst_mac=0,
                 frag_count=0,
                 frag_type=0,
                 data=()
                 ):
        # Call the base class constructor
        super(IoFragPacket, self).__init__(
            group_id=group_id,
            message_id=message_id,
            src_mac=src_mac,
            dst_mac=dst_mac,
            data=data,
            frag_type=frag_type,
            frag_count=frag_count,
        )

    ###############################################################################################

    def from_frame(self, frame):
        """ Parse the CAN frame and save the data into the context of the current instance

        Args:
            frame (CanFrameAbc) : A CAN frame object

        Returns:
            self (DeviceNetPacket) : The current packet instance
        """

        # Parse the CAN header
        self.can_header = frame.can_id

        # Parse the CAN payload
        self.can_data = frame.data

        # Parse the packet
        self.parse()

        return self

    ###############################################################################################

    def get_frag_header(self):
        """ Parse the fragmentation protocol header byte

        Returns:
            self (DeviceNetPacket) : The current packet instance

        """

        try:

            # Store the fragmentation protocol header
            self.frag_header = self.can_data[0]

            # Parse the fragmentation protocol header
            self.get_frag_type()
            self.get_frag_count()

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse fragmentation protocol header byte")

        # Unexpected errors
        except Exception:
            raise

        # Return the current instance
        return self

    ###############################################################################################

    def set_frag_type(self, value):

        # Calculate the fragment type bits
        frag_type = value << self.FRAG_TYPE_OFFSET

        # Update the fragment header
        self.frag_header = frag_type + (self.frag_count & self.FRAG_COUNT_MASK)

        # Update the CAN payload
        self.can_data[0] = self.frag_header

        # # Generate the fragmentation protocol byte
        # self.frag_header = (self.frag_type << FRAGMENT.TYPE.OFFSET) + self.frag_count

        # Return the current instance
        return self

    ###############################################################################################

    def set_frag_count(self, value):

        frag_count = value & self.FRAG_COUNT_MASK
        self.frag_header = (self.frag_type << self.FRAG_TYPE_OFFSET) + frag_count

        self.can_data[0] = self.frag_header

        # Generate the fragmentation protocol byte
        # self.frag_header = (self.frag_type << FRAGMENT.TYPE.OFFSET) + self.frag_count

        # Return the current instance
        return self

    def set_frag_header(self):
        """ Generate the fragmentation protocol header byte"""

        # Generate the fragmentation protocol byte
        self.frag_header = (self.frag_type << self.FRAG_TYPE_OFFSET) + self.frag_count

        self.can_data.extend([self.frag_header, ])

        # Return the current instance
        return self

    ###############################################################################################

    def get_app_data(self):

        self.data = self.can_data[1:]

        return self

    def set_app_data(self, data):

        self.data = data
        self.can_data.extend(self.data)

        return self

    def clear(self):

        self.can_header = 0
        self.can_data = [0, ]

    ###############################################################################################

    def build(self):

        # Clear previous values for the CAN header and payload
        self.clear()

        # Generate the CAN header and payload
        self.set_group_id(self.group_id)
        self.set_message_id(self.message_id)
        self.set_src_mac(self.src_mac)
        self.set_dst_mac(self.dst_mac)
        self.set_frag_type(self.frag_type)
        self.set_frag_count(self.frag_count)
        self.set_app_data(self.data)

        return self

    ###############################################################################################

    def parse(self):

        self.get_group_id()
        self.get_message_id()
        self.get_src_mac()
        self.get_dst_mac()
        self.get_frag_header()
        self.get_app_data()

        return self


###################################################################################################
#                               DUPMAC REQUEST AND RESPONSE PACKET
###################################################################################################

class DupMacPacket(DeviceNetPacket):
    """ Duplicate MAC packet format with fluent interface

    The structure of the duplicate MAC packet is as follows:
        - Byte 0    : RR flag (bit 7) and phycial port (bits 0-6)
        - Byte 1-2  : Vendor ID
        - Byte 3-6  : Serial number

    The packet is broadcast to all devices on the network. If the MAC address of the device matches
    the MAC address in the packet, the device will respond with a duplicate MAC response packet. If
    the MAC address does not match, the listening device will ignore the packet. The requesting
    device will assume that the MAC address is not in use after 2 attempts without a response.

    The difference between the request and response packet is that the response packet has the RR
    flag set to 1. If the requesting device receives a response packet, it will assume that the MAC
    address is in use and will not use it.

    Args:
        dst_mac (int)           : The MAC of the device receiving the packet
        rr_flag (int)           : The request/response flag (0=request, 1=response)
        physical_port (int)     : The physical port
        vendor_id (int)         : The vendor ID
        serial_number (int)     : The serial number

    Example:
        >>> # Use the constructor to build the packet
        >>> packet = DupMacPacket(
        >>>     group_id=2,
        >>>     message_id=6,
        >>>     src_mac=0,
        >>>     dst_mac=1,
        >>>     physical_port=1,
        >>>     vendor_id=0x1234,
        >>>     serial_number=0x12345678
        >>> ).build()
        >>>
        >>> # Convert and parse the packet to/from a CAN frame
        >>> can_frame = packet.to_frame()
        >>> parsed_packet = DupMacPacket().from_frame(can_frame)
        >>> assert packet == parsed_packet
        >>>
        >>> # Use the fluent interface to build the packet
        >>> packet = (
        >>>     DupMacPacket()
        >>>     .set_dst_mac(1)
        >>>     .set_rr_flag(0)
        >>>     .set_physical_port(1)
        >>>     .set_vendor_id(0x1234)
        >>>     .set_serial_number(0x12345678)
        >>>     .validate()
        >>>     .build()
        >>> )
        >>>
        >>> # Access the packet attributes
        >>> assert packet.data == [0x81, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12]
        >>>
        >>> # Build the packet from data
        >>> packet = (
        >>>     DupMacPacket()
        >>>     .set_dst_mac(1)
        >>>     .set_message_data([0x81, 0x34, 0x12, 0x78, 0x56, 0x34, 0x12])
        >>>     .build()
        >>> )
        >>>
        >>> # Access the packet attributes
        >>> assert packet.rr_flag == 1
        >>> assert packet.physical_port == 1
        >>> assert packet.vendor_id == 0x1234
        >>> assert packet.serial_number == 0x12345678

    """

    # RR flag (bit 7) from byte 0
    RR_FLAG_OFFSET = 0
    RR_FLAG_MASK = 0x80

    # Physical port (bits 0-6) from byte 0
    PHY_PORT_OFFSET = 0
    PHY_PORT_MASK = 0x7F
    PHY_PORT_SIZE = 1

    # Vendor ID (bits 0-15) from byte 1-2
    VENDOR_ID_OFFSET = 1
    VENDOR_ID_MASK = 0xFFFF
    VENDOR_ID_SIZE = 2

    # Serial number (bits 0-31) from byte 3-6
    SERIAL_NUMBER_OFFSET = 3
    SERIAL_NUMBER_MASK = 0xFFFFFFFF
    SERIAL_NUMBER_SIZE = 4

    # Data size (in bytes)
    PACKET_SIZE = 7

    def __init__(self,
                 dst_mac=0,
                 rr_flag=0,
                 physical_port=0,
                 vendor_id=0,
                 serial_number=0,
                 ):

        # Initialize the base class
        super(DupMacPacket, self).__init__(
            group_id=MESSAGE.GROUP2.ID,
            message_id=MESSAGE.GROUP2.DUPMAC,
            dst_mac=dst_mac,
            data=[0, ] * self.PACKET_SIZE,
        )

        # Initialzize the instance state
        self.rr_flag = rr_flag
        self.physical_port = physical_port
        self.vendor_id = vendor_id
        self.serial_number = serial_number

    ###############################################################################################

    def validate_message_data(self):

        PACKET_SIZE = self.PHY_PORT_SIZE + self.VENDOR_ID_SIZE + self.SERIAL_NUMBER_SIZE

        # Check if the data is None
        if self.data is None:
            raise DevNetPacketError("The data cannot be None")

        # Check if the data is iterable
        elif not isinstance(self.data, Iterable):
            raise DevNetPacketError("The data must be iterable")

        # Check the data length
        elif len(self.data) != PACKET_SIZE:
            raise DevNetPacketError("The data length must be {} bytes".format(PACKET_SIZE))

        return self

    ###############################################################################################

    def validate_rr_flag(self):
        """ Validate the request/response flag

        The request/response flag must be an integer in the range [0, 1]

        Raises:
            DevNetPacketError: If the value is not valid

        """

        # Check whether the value is None
        if self.rr_flag is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.rr_flag, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.rr_flag <= 1:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 1]")

    ###############################################################################################

    def validate_physical_port(self):
        """ Validate the physical port

        The physical port must be an integer in the range [0, 0x7F]

        Raises:
            DevNetPacketError: If the value is not valid

        """

        # Check whether the value is None
        if self.physical_port is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.physical_port, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.physical_port <= self.PHY_PORT_MASK:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFF]")

    ###############################################################################################

    def validate_vendor_id(self):
        """ Validate the vendor ID

        The vendor ID must be an integer in the range [0, 0xFFFF]

        Raises:
            DevNetPacketError: If the value is not valid

        """

        # Check whether the value is None
        if self.vendor_id is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.vendor_id, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.vendor_id <= self.VENDOR_ID_MASK:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFFFF]")

    ###############################################################################################

    def validate_serial_number(self):
        """ Validate the serial number

        The serial number must be an integer in the range [0, 0xFFFFFFFF]

        Raises:
            DevNetPacketError: If the value is not valid

        """

        # Check whether the value is None
        if self.serial_number is None:
            raise DevNetPacketError("The value for this attribute cannot be None")

        # Check whether the value is an integer
        elif not isinstance(self.serial_number, int):
            raise DevNetPacketError("The value for this attribute must be an integer")

        # Check whether the value is in the valid range
        elif not 0 <= self.serial_number <= self.SERIAL_NUMBER_MASK:
            raise DevNetPacketError("The value for this attribute must be in the range [0, 0xFFFFFFFF]")

    ###############################################################################################

    def get_dst_mac(self):
        """ Parse the destination MAC address from the CAN header

        Returns:
            DupMacPacket: The current instance with an updated destination MAC address

        """

        self.group_id, self.message_id, self.dst_mac = devnet_addr(self.can_header)

        return self

    ###############################################################################################

    def get_rr_flag(self):
        """ Parse the RR flag from the CAN payload

        Returns:
            DupMacPacket: The current instance with an updated rr_flag attribute

        """
        try:
            # Get the numeric value of the RR flag
            value = self.can_data[self.RR_FLAG_OFFSET]

            # Convert to a boolean value (0, 1)
            self.rr_flag = (value & self.RR_FLAG_MASK) >> PACKET.RSP_FLAG.OFFSET

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse RR flag")

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################
    def get_physical_port(self):
        """ Parse the physical port from the CAN payload

        Returns:
            DupMacPacket: The current instance with an updated physical port attribute

        """

        # Parse the physical port (1 byte)
        try:
            value = self.can_data[self.PHY_PORT_OFFSET]
            self.physical_port = value & PACKET.PHYSICAL_PORT.MASK

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse physical port")

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def get_vendor_id(self):
        """ Parse the vendor ID from the CAN payload

        Returns:
            DupMacPacket: The current instance with updated vendor ID attribute

        """

        # Parse the vendor ID (2 bytes)
        try:
            start = self.VENDOR_ID_OFFSET
            end = start + self.VENDOR_ID_SIZE
            self.vendor_id = bytes_to_integer(self.can_data[start:end])

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse vendor ID")

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def get_serial_number(self):
        """ Parse the serial number from the CAN payload

        Returns:
            DupMacPacket: The current instance with an updated serial number attribute

        """

        # Parse the serial number (4 bytes)
        try:
            start = self.SERIAL_NUMBER_OFFSET
            end = start + self.SERIAL_NUMBER_SIZE
            self.serial_number = bytes_to_integer(self.can_data[start:end])

        # The frame data is malformed (wrong pocket type)
        except IndexError:
            raise DevNetParsingError("Failed to parse serial number")

        # Unexpected errors
        except Exception:
            raise

        # Return the packet instance
        return self

    ###############################################################################################

    def set_dst_mac(self, value):
        """ Add the destination MAC address to the CAN header

        Args:
            value (int): The destination MAC address

        Returns:
            DupMacPacket: The current instance with an updated CAN header

        """

        # Update the CAN header
        self.can_header = can_addr(MESSAGE.GROUP2.ID, MESSAGE.GROUP2.DUPMAC, value)

        return self

    ###############################################################################################

    def set_rr_flag(self, value):
        """" Set the RR flag in the CAN payload

        Args:
            value (int): The RR flag value

        Returns:
            DupMacPacket: The current instance with an updated CAN payload

        """

        try:

            # Update the RR flag attribute
            self.rr_flag = value

            # Ensure the value is either 0 or 1
            value = int(value > 0)

            # Calculate the bit position of the RR flag from the mask
            n = self.RR_FLAG_MASK.bit_length() - 1

            # Keep the last 7 bits and set only the RR flag bit
            rr_bit = value << n
            other_bits = self.data[self.RR_FLAG_OFFSET] & ~self.RR_FLAG_MASK

            # Update the CAN payload
            self.data[self.RR_FLAG_OFFSET] = other_bits | rr_bit

        # Unexpected errors
        except Exception:
            raise

        return self

    ###############################################################################################

    def set_physical_port(self, value):
        """" Set the physical port in the CAN payload

        Args:
            value (int): The physical port value

        Returns:
            DupMacPacket: The current instance with an updated CAN payload

        """

        try:

            # Set the physical port attribute
            self.physical_port = value

            # Update the packet data
            other_bits = self.data[self.PHY_PORT_OFFSET] & ~self.PHY_PORT_MASK
            phy_bits = (value & self.PHY_PORT_MASK)

            # Update the CAN payload
            self.data[self.PHY_PORT_OFFSET] = other_bits | phy_bits

        # Unexpected errors
        except Exception:
            raise

        return self

    ###############################################################################################

    def set_vendor_id(self, value):
        """ Set the vendor ID in the CAN payload

        Args:
            value (int): The vendor ID value

        Returns:
            DupMacPacket: The current instance with an updated CAN payload

        """

        try:

            # Set the vendor ID attribute
            self.vendor_id = value

            # Calculate the start and end index
            start = self.VENDOR_ID_OFFSET
            end = start + self.VENDOR_ID_SIZE

            # Update the packet data
            new_value = integer_to_bytes(value=self.vendor_id, size=2)

            # Update the CAN payload
            self.data[start:end] = new_value

        # Unexpected errors
        except Exception:
            raise

        return self

    ###############################################################################################

    def set_serial_number(self, value):
        """ Set the serial number in the CAN payload

        Args:
            value (int): The serial number value

        Returns:
            DupMacPacket: The current instance with an updated CAN payload

        """

        try:
            # Set the serial number attribute
            self.serial_number = value

            # Calculate the start and end index
            start = self.SERIAL_NUMBER_OFFSET
            end = start + self.SERIAL_NUMBER_SIZE

            # Update the packet data
            new_value = integer_to_bytes(value=self.serial_number, size=4)

            # Update the CAN payload
            self.data[start:end] = new_value

        # Unexpected errors
        except Exception:
            raise

        return self

    ###############################################################################################

    def build(self):
        """ Generate the CAN frame object from the current instance state """

        self.clear()

        # Update the current instance
        self.set_dst_mac(self.dst_mac)
        self.set_rr_flag(self.rr_flag)
        self.set_physical_port(self.physical_port)
        self.set_vendor_id(self.vendor_id)
        self.set_serial_number(self.serial_number)
        self.set_can_data(*self.data)

        # Return the packet instance
        return self

    ###############################################################################################

    def parse(self):
        """ Parse the packet structure from the CAN payload

        Returns:
            DupMacPacket: The current instance

        """

        # Parse the packet data
        self.get_dst_mac()
        self.get_rr_flag()
        self.get_physical_port()
        self.get_vendor_id()
        self.get_serial_number()

        # Return the packet instance
        return self

    def validate(self):

        # Check whether the vendor ID is valid
        self.validate_rr_flag()
        self.validate_physical_port()
        self.validate_vendor_id()
        self.validate_serial_number()
        self.validate_message_data()

        return self
