# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


###################################################################################################
# CAN IDENTIFIER GROUPS
###################################################################################################

class CAN_ID(object):
    """ CAN Address Distribution by DeviceNet Message Groups """

    class GROUP1(object):
        START = 0
        END = 0x3FF
        MSG_ID_OFFSET = 6
        RANGE = set(range(START, END + 1))

    class GROUP2(object):
        START = 0x400
        END = 0x5FF
        MAC_OFFSET = 3
        RANGE = set(range(START, END + 1))

    class GROUP3(object):
        START = 0x600
        END = 0x7BF
        MSG_ID_OFFSET = 6
        RANGE = set(range(START, END + 1))

    class GROUP4(object):
        START = 0x7C0
        END = 0x7EF
        RANGE = set(range(START, END + 1))

    class INVALID(object):
        START = 0x7F0
        END = 0x7FF
        RANGE = set(range(START, END + 1))


###################################################################################################
# PRE-DEFINED MASTER / SLAVE CONNECTION SET
###################################################################################################

class MESSAGE(object):
    """ DeviceNet Pre-Defined Master/Slave Message Groups

    The CIP Network Library, Volume 3, DeviceNet Adaptation of CIP
        - Chapter 2.2
        - Chapter 3.7

    """

    class GROUP1(object):
        ID = 1
        MPOLL_RSP = 0x0C
        BITSTROBE_RSP = 0x0E
        POLL_RSP = 0x0F
        COS_SLAVE_MESSAGE = 0x0D
        COS_SLAVE_ACK = 0x0F
        CYCLIC_SLAVE_MESSAGE = 0x0D
        CYCLIC_SLAVE_ACK = 0x0F

    class GROUP2(object):
        ID = 2
        DUPMAC = 0x07
        UNCONNECTED_REQ = 0x06
        UNCONNECTED_RSP = 0x03
        EXPLICIT_REQ = 0x04
        EXPLICIT_RSP = 0x03
        BITSTROBE_CMD = 0x00
        MPOLL_CMD = 0x01
        POLL_CMD = 0x05
        COS_MASTER_MESSAGE = 0x05
        COS_MASTER_ACK = 0x02
        CYCLIC_MASTER_MESSAGE = 0x05
        CYCLIC_MASTER_ACK = 0x02

    class GROUP3(object):
        ID = 3
        UNCONNECTED_RSP = 0x05
        UNCONNECTED_REQ = 0x06
        DEVICE_HEARTBEAT_RSP = 0x05
        DEVICE_HEARTBEAT_REQ = 0x06
        DEVICE_SHUTDOWN_RSP = 0x05
        DEVICE_SHUTDOWN_REQ = 0x06
        INVALID = 0x07

    class GROUP4(object):
        ID = 4
        RESERVED = range(0, 0x2C)
        COMM_FAULT_RSP = 0x2C
        COMM_FAULT_REQ = 0x2D
        OFFLINE_OWNERSHIP_RSP = 0x2E
        OFFLINE_OWNERSHIP_REQ = 0x2F

    TAG = {

        GROUP1.MPOLL_RSP: "MULTICAST POLL RESPONSE",
        GROUP1.COS_SLAVE_MESSAGE: "COS / CYCLIC MESSAGE",
        GROUP1.COS_SLAVE_ACK: "COS / CYCLIC SLAVE ACKNOWLEDGE",
        GROUP1.BITSTROBE_RSP: "BITSTROBE RESPONSE",
        GROUP1.POLL_RSP: "POLL/COS/CYCLIC MESSAGE FROM SLAVE",

        GROUP2.BITSTROBE_CMD: "BITSTROBE COMMAND",
        GROUP2.MPOLL_CMD: "MULTICAST POLL COMMAND",
        GROUP2.COS_MASTER_ACK: "COS/CYCLIC MASTER ACKNOWLEDGE",
        GROUP2.EXPLICIT_RSP: "EXPLICIT RESPONSE",
        GROUP2.EXPLICIT_REQ: "EXPLICIT REQUEST",
        GROUP2.POLL_CMD: "POLL/COS/CYCLIC MESSAGE FROM MASTER",
        GROUP2.UNCONNECTED_REQ: "UNCONNECTED REQUEST",
        GROUP2.DUPMAC: "DUPMAC CHECK MESSAGE",

        GROUP3.UNCONNECTED_REQ: "UNCONNECTED EXPLICIT REQUEST",
        GROUP3.UNCONNECTED_RSP: "UNCONNECTED EXPLICIT RESPONSE",
        GROUP3.DEVICE_HEARTBEAT_REQ: "DEVICE HEARTBEAT REQUEST",
        GROUP3.DEVICE_HEARTBEAT_RSP: "DEVICE HEARTBEAT RESPONSE",
        GROUP3.DEVICE_SHUTDOWN_REQ: "DEVICE SHUTDOWN REQUEST",
        GROUP3.DEVICE_SHUTDOWN_RSP: "DEVICE SHUTDOWN RESPONSE",

        GROUP4.COMM_FAULT_REQ: "COMMUNICATION FAULT REQUEST",
        GROUP4.COMM_FAULT_RSP: "COMMUNICATION FAULT RESPONSE",
        GROUP4.OFFLINE_OWNERSHIP_REQ: "OFFLINE OWNERSHIP REQUEST",
        GROUP4.OFFLINE_OWNERSHIP_RSP: "OFFLINE OWNERSHIP RESPONSE"
    }


class EXPLICIT(MESSAGE):
    """ Wrapper for the explicit message identifiers """
    REQ_GROUP = MESSAGE.GROUP2.ID
    REQ = MESSAGE.GROUP2.EXPLICIT_REQ
    RSP_GROUP = MESSAGE.GROUP2.ID
    RSP = MESSAGE.GROUP2.EXPLICIT_RSP


class UNCONNECTED(MESSAGE):
    """ Wrapper for the unconnected message identifiers """
    REQ_GROUP = MESSAGE.GROUP2.ID
    REQ = MESSAGE.GROUP2.UNCONNECTED_REQ
    RSP_GROUP = MESSAGE.GROUP2.ID
    RSP = MESSAGE.GROUP2.UNCONNECTED_RSP
    DUPMAC = MESSAGE.GROUP2.DUPMAC


class POLL(MESSAGE):
    """ Wrapper for the poll message identifiers """
    REQ_GROUP = MESSAGE.GROUP2.ID
    REQ = MESSAGE.GROUP2.POLL_CMD
    RSP_GROUP = MESSAGE.GROUP1.ID
    RSP = MESSAGE.GROUP1.POLL_RSP


class BITSTROBE(MESSAGE):
    """ Wrapper for the bitstrobe message identifiers """
    REQ_GROUP = MESSAGE.GROUP2.ID
    REQ = MESSAGE.GROUP2.BITSTROBE_CMD
    RSP_GROUP = MESSAGE.GROUP1.ID
    RSP = MESSAGE.GROUP1.BITSTROBE_RSP


class COS(object):
    """ Wrapper for the COS message identifiers """

    class MASTER(MESSAGE):
        REQ_GROUP = MESSAGE.GROUP2.ID
        REQ = MESSAGE.GROUP2.COS_MASTER_MESSAGE
        RSP_GROUP = MESSAGE.GROUP2.ID
        RSP = MESSAGE.GROUP2.COS_MASTER_ACK

    class SLAVE(MESSAGE):
        REQ_GROUP = MESSAGE.GROUP1.ID
        REQ = MESSAGE.GROUP1.COS_SLAVE_MESSAGE
        RSP_GROUP = MESSAGE.GROUP1.ID
        RSP = MESSAGE.GROUP1.COS_SLAVE_ACK


class CYCLIC(object):
    """ Wrapper for the CYCLIC message identifiers """

    class MASTER(MESSAGE):
        REQ_GROUP = MESSAGE.GROUP2.ID
        REQ = MESSAGE.GROUP2.CYCLIC_MASTER_MESSAGE
        RSP_GROUP = MESSAGE.GROUP2.ID
        RSP = MESSAGE.GROUP2.CYCLIC_MASTER_ACK

    class SLAVE(MESSAGE):
        REQ_GROUP = MESSAGE.GROUP1.ID
        REQ = MESSAGE.GROUP1.CYCLIC_SLAVE_MESSAGE
        RSP_GROUP = MESSAGE.GROUP1.ID
        RSP = MESSAGE.GROUP1.CYCLIC_SLAVE_ACK


##############################################################################################
# SERVICE REQUEST CODES
##############################################################################################

class SERVICE(object):
    """ Standard Service Codes defined by the DeviceNet Protocol """

    # Service Code Constants
    RANGE = range(0, 128)
    SUPPORTED = list(range(0x1, 0x0B)) + [0x0D, 0x0E] + [0x10, 0x11] + list(range(0x14, 0x1D))
    RESERVED = [0, 0x0B, 0x0C, 0x0F, 0x12, 0x13, ] + list(range(0x1D, 0x20))

    GET_ATTR_ALL = 0x01
    SET_ATTR_ALL = 0x02
    GET_ATTR_LIST = 0x03
    SET_ATTR_LIST = 0x04
    RESET = 0x05
    START = 0x06
    STOP = 0x07
    CREATE = 0x08
    DELETE = 0x09
    MULT_PACKETS = 0x0A
    APPLY_ATTR = 0x0D
    GET_ATTR_SINGLE = 0x0E
    SET_ATTR_SINGLE = 0x10
    FIND_NEXT_INST = 0x11
    ERROR = 0x14
    RESTORE = 0x15
    SAVE = 0x16
    NOP = 0x17
    GET_MEMBER = 0x18
    SET_MEMBER = 0x19
    INSERT_MEMBER = 0x1A
    REMOVE_MEMBER = 0x1B
    GROUP_SYNC = 0x1C
    GET_CONN_POINT_MEMBER_LIST = 0x1D
    ALLOCATE = 0x4B
    RELEASE = 0x4C
    LAST_VALID_CODE = 0x7F

    # Sample payload for a subset of the supported services
    PAYLOAD = {
        GET_ATTR_ALL: (),
        SET_ATTR_ALL: (1, 0xFF),
        GET_ATTR_LIST: (1, 1),
        SET_ATTR_LIST: (1, 1, 1),
        RESET: (),
        START: (),
        STOP: (),
        CREATE: (),
        DELETE: (),
        MULT_PACKETS: (),
        APPLY_ATTR: (),
        GET_ATTR_SINGLE: (1, ),
        SET_ATTR_SINGLE: (1, 1),
        FIND_NEXT_INST: (1, ),
        ERROR: (),
        RESTORE: (),
        SAVE: (),
        NOP: (),
        GET_MEMBER: (1, 1),
        SET_MEMBER: (1, 1, 1),
        INSERT_MEMBER: (1, 1),
        REMOVE_MEMBER: (1, ),
        GROUP_SYNC: (),
        GET_CONN_POINT_MEMBER_LIST: (),
        ALLOCATE: (0x1, 00),
        RELEASE: (0x1, ),
        LAST_VALID_CODE: ()
    }


##############################################################################################
# PACKET CONSTANTS
##############################################################################################

class PACKET(object):
    """ Explicit Service Request/Response Packet Constants """

    # FRAGMENTATION
    class FRAG_FLAG(object):
        MASK = 0x80
        OFFSET = 7

    # EXPLCIT PACKET
    class XID(object):
        MASK = 0x40
        OFFSET = 6

    # EXPLCIT PACKET
    class MAC(object):
        MASK = 0x3F
        OFFSET = 0

    # EXPLCIT PACKET
    class SERVICE(object):
        MASK = 0x7F
        OFFSET = 0

    # EXPLCIT PACKET, DUPMAC
    class RSP_FLAG(object):
        MASK = 0x80
        OFFSET = 7

    # DUPMAC
    class PHYSICAL_PORT(object):
        MASK = 0x7F
        OFFSET = 0

##############################################################################################
# FRAGMENTATION PROTOCOL CONSTANTS
##############################################################################################

class FRAGMENT(object):
    """ DeviceNet Fragmentation Protocol Packet Constants """

    class TYPE (object):
        MASK = 0xC0
        OFFSET = 6
        START = 0x00
        MIDDLE = 0x01
        FINAL = 0x02
        ACK = 0x03

    # Fragmentation enabled or disabled
    ENABLED = 1

    # Fragment counter is 7 bits
    MAX_COUNT = 0x3F

    # Constant Descriptors
    TAG = {
        TYPE.START: "First fragment",
        TYPE.MIDDLE: "Middle fragment",
        TYPE.FINAL: "Final fragment",
        TYPE.ACK: "Acknowledge response to a fragment"
    }


###################################################################################################
# IDENTITY
###################################################################################################

class IDENTITY(object):
    """ Identity Object from the CIP Standard """

    ID = 0x01
    DEFAULT_INSTANCE = 0x01

    # Status bits
    NOT_OWNED = 0
    NOT_CONFIGURED = 0
    OWNED = 0x00000001
    CONFIGURED = 0x00000004

    # Extended status 1
    EXT_UNKNOWN = 0
    EXT_ALL_SET = 0x000000f0
    EXT_UPDATE = 0x00000010
    EXT_IO_CONN_MISSING = 0x00000030
    EXT_IO_CONN_FAULT = 0x00000020
    EXT_IO_CONN_IDLE = 0x00000070
    EXT_IO_CONN_RUN = 0x00000060
    EXT_MAJOR_FAULT = 0x00000050
    EXT_BAD_CFG_FILE = 0x00000040

    # Minor / Major Bits
    MINOR_RECOV_FAULT = 0x00000100
    MINOR_UNRECOV_FAULT = 0x00000200
    MAJOR_RECOV_FAULT = 0x00000400
    MAJOR_UNRECOV_FAULT = 0x00000800


###################################################################################################
# MESSAGE_ROUTER
###################################################################################################

class MESSAGE_ROUTER(object):
    """ Message Router from the CIP Standard """

    ID = 0x02
    DEFAULT_INSTANCE = 0x01


###################################################################################################
# DEVICENET
###################################################################################################

class DEVICENET(object):
    """ DeviceNet Object from the CIP Standard """

    ID = 0x03
    DEFAULT_INSTANCE = 0x01


###################################################################################################
# ASSEMBLY
###################################################################################################

class ASSEMBLY(object):
    """ Assembly Object from the CIP Standard """

    ID = 0x04
    DEFAULT_INSTANCE = 0x01


###################################################################################################
# CONNECTION
###################################################################################################

class CONNECTION(object):
    """ Connection Object from the CIP Standard """

    ID = 0x05
    DEFAULT_INSTANCE = 0x01
    EXPLICIT = DEFAULT_INSTANCE
    POLL = 0x02
    BITSTROBE = 0x03
    COS = 0x04
    CYCLIC = 0x04


###################################################################################################
# USER OBJECT
###################################################################################################

class ACK_HANDLER(object):
    """ Ack Handler Object """

    ID = 0x2B
    DEFAULT_INSTANCE = 0x01


###################################################################################################
# USER OBJECT
###################################################################################################

class DUMMY(object):
    """ User Object """

    ID = 0xAB
    DEFAULT_INSTANCE = 0x01


###################################################################################################
# MNS
###################################################################################################

class IO_MAPPING(object):
    """ Hilscher  Object """

    ID = 0x402
    DEFAULT_INSTANCE = 0x01


##############################################################################################
# ALLOCATION INFO
##############################################################################################

class ALLOC(object):

    EXPLICIT = 0x01
    POLL = 0x02
    BITSTROBE = 0x04
    MPOLL = 0x08
    COS = 0x10
    CYCLIC = 0x20
    ACKSUP = 0x40
    RESERVED = 0x80

    TAG = {
        EXPLICIT: "Explicit",
        POLL: "Polled I/O",
        BITSTROBE: "Bit-strobed I/O",
        MPOLL: "Multi-polled I/O",
        COS: "Change-of-State I/O",
        CYCLIC: "Cyclic I/O",
        ACKSUP: "Acknowledge Suppression",
        RESERVED: "Reserved allocation bit"
    }


##############################################################################################
# CONNECTION STATES
##############################################################################################

class STATE(object):
    """ Connection States """

    NONE = None
    CONFIG = 1
    WAIT_ID = 2
    ESTABLISHED = 3
    TIMEDOUT = 4
    DEFERRED = 5
    CLOSING = 6

    TAG = {
        NONE: "NONE-EXISTENT",
        CONFIG: "CONFIGURING",
        WAIT_ID: "WAITING_ID",
        ESTABLISHED: "ESTABLISED",
        TIMEDOUT: "TIMED_OUT",
        DEFERRED: "DEREFERRED_DELETE",
        CLOSING: "CLOSING"
    }


##############################################################################################
# CONNECTION TIMEOUT ACTIONS
##############################################################################################

class TIMEOUT(object):
    """ Connection timeout actions defined by the DeviceNet protocol"""

    TIMED_OUT = 0
    AUTO_DELETE = 1
    AUTO_RESET = 2
    DEFERRED = 3

    TAG = {
        TIMED_OUT: "TIME_OUT",
        AUTO_DELETE: "AUTO_DELETE",
        AUTO_RESET: "AUTO_RESET",
        DEFERRED: "DEFERRED_DELETE"
    }


##############################################################################################
# CIP ERRORS
##############################################################################################

class ERROR(object):

    COMM_PROBLEM = 0x01
    RESOURCE_UNAVAILABLE = 0x02
    INVALID_PARAM_VALUE = 0x03
    PATH_SEGMENT_ERROR = 0x04
    PATH_DEST_UNKNOWN = 0x05
    PARTIAL_TRANSFER = 0x06
    CONNECTION_LOST = 0x07
    SERVICE_NOT_SUPPORTED = 0x08
    INVALID_ATTRIB_VALUE = 0x09
    ATTRIBUTE_LIST_ERROR = 0x0A
    ALREADY_IN_REQUESTED_STATE = 0x0B
    OBJECT_STATE_CONFLICT = 0x0C
    OBJECT_ALREADY_EXISTS = 0x0D
    ATTRIBUTE_NOT_SETTABLE = 0x0E
    PRIVILEGE_VIOLATION = 0x0F
    DEVICE_STATE_CONFLICT = 0x10
    REPLY_DATA_TOO_LARGE = 0x11
    FRAGMENTATION_OF_PRIMITIVE_VALUE = 0x12
    NOT_ENOUGH_DATA = 0x13
    ATTRIBUTE_NOT_SUPPORTED = 0x14
    TOO_MUCH_DATA = 0x15
    OBJECT_INSTANCE_NOT_EXISTANT = 0x16
    SERVICE_FRAGMENTATION_OUT_OF_SEQUENCE = 0x17
    NO_STORED_ATTRIBUTE_DATA = 0x18
    STORE_OPERATION_FAILURE = 0x19
    ROUTING_FAILURE_REQUEST_TOO_LARGE = 0x1A
    ROUTING_FAILURE_RESPONSE_TOO_LARGE = 0x1B
    MISSING_ATTRIBUTE_LIST_ENTRY = 0x1C
    INVALID_ATTRIB_VALUE_LIST = 0x1D
    EMBEDDED_SERVICE_ERROR = 0x1E
    VENDOR_ERROR = 0x1F
    INVALID_PARAMETER = 0x20
    WRITE_ONCE_VALUE_ALREADY_WRITTEN = 0x21
    INVALID_REPLY_RECEIVED = 0x22
    BUFFER_OVERFLOW = 0x23
    MESSAGE_FORMAT_ERROR = 0x24
    KEY_FAILURE_IN_PATH = 0x25
    PATH_SIZE_INVALID = 0x26
    UNEXPECTED_ATTRIBUTE_IN_LIST = 0x27
    INVALID_MEMBER_ID = 0x28
    MEMBER_NOT_SETTABLE = 0x29
    GROUP_2_ONLY_SERVER_FAILURE = 0x2A
    UNKNOWN_MODBUS_ERROR = 0x2B
    ATTRIBUTE_NOT_GETTABLE = 0x2C
    INSTANCE_NOT_DELETABLE = 0x2D
    SERVICE_NOT_SUPPORTED_FOR_PATH = 0x2E

    TAG = {
        None: "Slave is not responding",
        0x00: "SUCCESS",
        0x01: "Communication related problem",
        0x02: "Resource unavailable",
        0x03: "Invalid parameter value",
        0x04: "Path segment error",
        0x05: "Path destination unknown",
        0x06: "Partial transfer",
        0x07: "Connection lost",
        0x08: "Service not supported",
        0x09: "Invalid attribute value",
        0x0A: "Attribute list error",
        0x0B: "Already in requested mode/state",
        0x0C: "Object state conflict",
        0x0D: "Object already exists",
        0x0E: "Attribute not settable",
        0x0F: "Privilege violation",
        0x10: "Device state conflict",
        0x11: "Reply data too large",
        0x12: "Fragmentation of a primitive value",
        0x13: "Not enough data",
        0x14: "Attribute not supported",
        0x15: "Too much data",
        0x16: "Object instance does not exist",
        0x17: "Service fragmentation out of sequence",
        0x18: "No stored attribute data",
        0x19: "Store operation failure",
        0x1A: "Routing failure, request packet too large",
        0x1B: "Routing failure, response packet too large",
        0x1C: "Missing attribute list entry data",
        0x1D: "Invalid attribute value list",
        0x1E: "Embedded service error",
        0x1F: "Vendor specific error",
        0x20: "Invalid parameter",
        0x21: "Write-once value or medium already written",
        0x22: "Invalid Reply Received",
        0x23: "Buffer Overflow",
        0x24: "Message Format Error",
        0x25: "Key failure in path",
        0x26: "Path size invalid",
        0x27: "Unexpected attribute in list",
        0x28: "Invalid Member ID",
        0x29: "Member not settable",
        0x2A: "Group 2 only server general failure",
        0x2B: "Unknown Modbus Error",
        0x2C: "Attribute not gettable",
        0x2D: "Instance not Deletable",
        0x2E: "Service not supported for specified path 1",
    }
