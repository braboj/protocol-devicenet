# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject, Attribute
from ..link import *
from ..definitions import *
from ..convert import integer_to_bytes, bytes_to_integer
from ..errors import CipServiceError, CipNoResponseError

# System imports
import logging


#######################################################################################################################
#                                       CONNECTION OBJECT (0x05)
#######################################################################################################################

class ConnectionObject(CipObject):
    """ Connection Object (0x05)

    The Connection Object is used to establish and maintain connections between two nodes in a
    DeviceNet segment. One of the nodes is the master and the other is the slave. The master is
    responsible for initiating the connection and the slave is responsible for responding to the
    connection request.

    Args:
        instance        : Instance ID of the Connection Object
        src_addr        : Source MAC address
        dst_addr        : Destination MAC address
        class_id        : Class ID of the Connection Object
        instance        : Instance ID of the Connection Object
        alloc_choice    : Allocation choice
        ack_sup         : Acknowledge supporession flag
        produce_size    : The size of the data sent by the node
        consume_size    : The size of the data received by the node
        event_handler   : Additional handle for the connection

    Example:
        from Components.devicenet.can.node import CanNode
        from Components.cip.connection import ConnectionObject

        bus = CanNode()
        conn = ExplicitConnection(interface=bus, src_addr=0, dst_addr=1)
        conn.allocate()
        conn.release()

    """

    CLASS_ID = 0x05
    CLASS_DESC = "CONNECTION OBJECT"

    instance_attributes = [
            #          | Type    | ID | Name                    | Size
            Attribute('instance', 1,  'conn_state',             1),
            Attribute('instance', 2,  'conn_type',              1),
            Attribute('instance', 3,  'transport_class',        1),
            Attribute('instance', 4,  'produced_conn_id',       2),
            Attribute('instance', 5,  'consumed_conn_id',       2),
            Attribute('instance', 6,  'initial_com',            1),
            Attribute('instance', 7,  'produced_conn_size',     2),
            Attribute('instance', 8,  'consumed_conn_size',     2),
            Attribute('instance', 9,  'expected_packet_rate',   2),
            Attribute('instance', 10, 'cip_produced_conn_id',   4),
            Attribute('instance', 11, 'cip_consumed_conn_id',   4),
            Attribute('instance', 12, 'timeout_action',         1),
            Attribute('instance', 13, 'produced_path_length',   2),
            Attribute('instance', 14, 'produced_conn_path',     16),
            Attribute('instance', 15, 'consumed_path_length',   2),
            Attribute('instance', 16, 'consumed_conn_path',     16),
            Attribute('instance', 17, 'inhibit_time',           2),
            Attribute('instance', 18, 'timeout_multiplier',     1),
            Attribute('instance', 19, 'binding_list',           16),
            Attribute('instance', 100, 'consume_assembly',      1),
            Attribute('instance', 101, 'produce_assembly',      1),
    ]

    def __init__(self,
                 interface,
                 src_addr,
                 dst_addr,
                 class_id=CONNECTION.ID,
                 instance=CONNECTION.DEFAULT_INSTANCE,
                 alloc_choice=ALLOC.EXPLICIT,
                 ack_sup=False,
                 produce_size=None,
                 consume_size=None,
                 event_handler=None,
                 ):

        super(ConnectionObject, self).__init__(
            interface=interface,
            src_addr=src_addr,
            dst_addr=dst_addr,
            class_id=class_id,
            instance=instance,
            event_handler=event_handler
        )

        self.alloc_choice = alloc_choice

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

        # Initialize parameters
        self.ack_sup = ack_sup
        self._produced_size = produce_size
        self._consumed_size = consume_size

        # Poll time in seconds
        self._sample_rate_ms = 20
        self._poll_time = 0.02

        # self.allocate(ack_sup=ack_sup)

        # Verify if I/O connection sizes are initialized
        # if self._consumed_size is None or self._produced_size is None:
        #     self._consumed_size = self.consumed_conn_size
        #     self._produced_size = self.produced_conn_size

    ###############################################################################################

    @property
    def conn_state(self):
        try:
            data = self.get_attribute(attrib_id=1)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def instance_type(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def transport_class(self):
        try:
            data = self.get_attribute(attrib_id=3)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def produced_conn_id(self):
        try:
            data = self.get_attribute(attrib_id=4)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def consumed_conn_id(self):
        try:
            data = self.get_attribute(attrib_id=5)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def initial_com(self):
        try:
            data = self.get_attribute(attrib_id=6)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def produced_conn_size(self):

        if self._produced_size is None:
            try:
                data = self.get_attribute(attrib_id=7)
                data = bytes_to_integer(data)
                self._produced_size = data
            except (CipServiceError, CipNoResponseError):
                data = None

        else:
            data = self._produced_size

        return data

    ###############################################################################################

    @property
    def consumed_conn_size(self):

        if self._consumed_size is None:
            try:
                data = self.get_attribute(attrib_id=8)
                data = bytes_to_integer(data)
                self._consumed_size = data
            except (CipServiceError, CipNoResponseError):
                data = None
        else:
            data = self._consumed_size

        return data

    ###############################################################################################

    @property
    def expected_packet_rate(self):
        try:
            data = self.get_attribute(attrib_id=9)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    @expected_packet_rate.setter
    def expected_packet_rate(self, value):
        try:
            stream = integer_to_bytes(value, self.get_size("expected_packet_rate"))
            self.set_attribute(attrib_id=9, value=stream)
        except (CipServiceError, CipNoResponseError):
            raise

    ###############################################################################################

    @property
    def cip_produced_conn_id(self):
        try:
            data = self.get_attribute(attrib_id=10)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def cip_consumed_conn_id(self):
        try:
            data = self.get_attribute(attrib_id=11)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def timeout_action(self):
        try:
            data = self.get_attribute(attrib_id=12)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    @timeout_action.setter
    def timeout_action(self, value):
        try:
            stream = integer_to_bytes(value, self.get_size("timeout_action"))
            self.set_attribute(attrib_id=12, value=stream)
        except (CipServiceError, CipNoResponseError):
            raise

    ###############################################################################################

    @property
    def produced_path_length(self):
        try:
            data = self.get_attribute(attrib_id=13)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def produced_conn_path(self):
        try:
            data = self.get_attribute(attrib_id=14)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def consumed_path_length(self):
        try:
            data = self.get_attribute(attrib_id=15)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def consumed_conn_path(self):
        try:
            data = self.get_attribute(attrib_id=16)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def inhibit_time(self):
        try:
            data = self.get_attribute(attrib_id=17)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    @inhibit_time.setter
    def inhibit_time(self, value):
        try:
            stream = integer_to_bytes(value, self.get_size("inhibit_time"))
            self.set_attribute(attrib_id=17, value=stream)
        except (CipServiceError, CipNoResponseError):
            raise

    ###############################################################################################

    @property
    def timeout_multiplier(self):
        try:
            data = self.get_attribute(attrib_id=18)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def binding_list(self):
        try:
            data = self.get_attribute(attrib_id=19)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    ###############################################################################################

    @property
    def consume_assembly(self):
        try:
            data = self.get_attribute(attrib_id=100)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    @consume_assembly.setter
    def consume_assembly(self, value):
        try:
            stream = integer_to_bytes(value, self.get_size("consume_assembly"))
            self.set_attribute(attrib_id=101, value=stream)
        except (CipServiceError, CipNoResponseError):
            raise

    ###############################################################################################

    @property
    def produce_assembly(self):
        try:
            data = self.get_attribute(attrib_id=101)
            data = bytes_to_integer(data)
        except (CipServiceError, CipNoResponseError):
            data = None

        return data

    @produce_assembly.setter
    def produce_assembly(self, value):
        try:
            stream = integer_to_bytes(value, self.get_size("produce_assembly"))
            self.set_attribute(attrib_id=101, value=stream)
        except (CipServiceError, CipNoResponseError):
            raise

    ###############################################################################################

    def is_fragmented(self):

        if self.consumed_conn_size > 8 or self.produced_conn_size > 8:
            fragmented = True
        else:
            fragmented = False

        return fragmented

    ###############################################################################################

    def is_accessible(self):

        if self.transport_class != 0:
            accessible = True
        else:
            accessible = False

        return accessible

    ###############################################################################################

    def read(self, timeout=1):

        data = None

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        resolution = float(self._sample_rate_ms) / 1000
        counter = int(float(timeout) / resolution)

        for i in range(counter):

            # Check I/O connection type and perform operation
            if self.instance == 2:
                data = poll_read(
                    interface=self.interface,
                    master_addr=self.src_addr,
                    slave_addr=self.dst_addr,
                    produced_size=self._produced_size,
                    timeout=resolution
                )
            elif self.instance == 3:
                data = bitstrobe_read(
                    interface=self.interface,
                    master_addr=self.src_addr,
                    slave_addr=self.dst_addr,
                    timeout=resolution
                )
            elif self.instance == 4:
                data = cos_read(
                    interface=self.interface,
                    master_addr=self.src_addr,
                    slave_addr=self.dst_addr,
                    produced_size=self._produced_size,
                    consumed_size=self._consumed_size,
                    ack_data=[],
                    ack_sup=self.ack_sup,
                    timeout=resolution
                )

            # self.log.info("#{0:02X} : {1}".format(i, data))
            if data:
                break

        return data

    ###############################################################################################

    def write(self, data, timeout=1):

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        # Check I/O connection type and perform operation
        if self.instance == 2:
            poll_write(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                consumed_size=self._consumed_size,
                data=data,
            )
        elif self.instance == 3:
            bitstrobe_write(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                data=data,
            )
        elif self.instance == 4:

            # Master uses poll (instance=2) to write to the slave

            if self.ack_sup:
                consumed_size = self.connections[2].consumed_conn_size
                produced_size = 0
            else:
                consumed_size = self.connections[2].consumed_conn_size
                produced_size = self.connections[2].produced_conn_size

            cos_write(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                consumed_size=consumed_size,
                produced_size=produced_size,
                data=data,
                ack_sup=self.ack_sup,
                timeout=timeout
            )

    ###############################################################################################

    def allocate(self, ack_sup=0, wait_time=1):

        self.ack_sup = int(ack_sup) * ALLOC.ACKSUP
        alloc_choice = self.alloc_choice + self.ack_sup
        service_data = (alloc_choice, self.src_addr)

        result = None
        try:
            result = allocate(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                data=service_data,
                wait_time=wait_time
            )

            if result is not None:
                result = 0

        except CipServiceError as error:
            result = error.code

        finally:

            self.connections[self.instance] = self
            if alloc_choice in (ALLOC.COS, ALLOC.COS + ALLOC.ACKSUP, ALLOC.CYCLIC, ALLOC.CYCLIC + ALLOC.ACKSUP):
                poll = ConnectionObject(
                    interface=self.interface,
                    src_addr=self.src_addr,
                    dst_addr=self.dst_addr,
                    instance=2,
                    alloc_choice=ALLOC.POLL
                )
                self.connections[2] = poll

            return result

    ###############################################################################################

    def release(self, wait_time=1):

        alloc_choice = self.alloc_choice

        result = None
        try:
            result = release(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                data=alloc_choice,
                wait_time=wait_time
            )

            if result is not None:
                result = 0

        except CipServiceError as error:
            result = error.code

        finally:

            self._produced_size = None
            self._consumed_size = None

            CipObject.connections[self.instance] = None
            if alloc_choice in (ALLOC.COS, ALLOC.COS + ALLOC.ACKSUP, ALLOC.CYCLIC, ALLOC.CYCLIC + ALLOC.ACKSUP):
                self.connections[2] = None

            return result

    ###############################################################################################

    def report(self):

        # Get the class attibutes report
        super(ConnectionObject, self).report()

        try:
            self.log.info("CONNECTION STATE             = {0}".format(hex(self.conn_state)))
            self.log.info("INSTANCE TYPE                = {0}".format(hex(self.instance_type)))
            self.log.info("TRANSPORT CLASS              = {0}".format(hex(self.transport_class)))
            self.log.info("PRODUCED CONNECTION ID       = {0}".format(hex(self.produced_conn_id)))
            self.log.info("CONSUMED CONNECTION ID       = {0}".format(hex(self.consumed_conn_id)))
            self.log.info("INITIAL COM CHARACTERISTICS  = {0}".format(hex(self.initial_com)))
            self.log.info("PRODUCED CONNECTION SIZE     = {0}".format(self.produced_conn_size))
            self.log.info("CONSUMED CONNECTION SIZE     = {0}".format(self.consumed_conn_size))
            self.log.info("EXPECTED PACKET RATE         = {0}".format(self.expected_packet_rate))
            self.log.info("TIMEOUT ACTION               = {0}".format(self.timeout_action))
            self.log.info("PRODUCED PATH LENGTH         = {0}".format(self.produced_path_length))
            self.log.info("PRODUCED CONNECTION PATH ID  = {0}".format([hex(x) for x in self.produced_conn_path]))
            self.log.info("CONSUMED PATH LENGTH         = {0}".format(self.consumed_path_length))
            self.log.info("CONSUMED CONNECTION PATH ID  = {0}".format([hex(x) for x in self.consumed_conn_path]))
            self.log.info("PRODUCTION INHIBIT TIME      = {0}".format(self.inhibit_time))
            self.log.info("TIMEOUT MULTIPLIER           = {0}".format(self.timeout_multiplier))
            self.log.info("BINDING LIST                 = {0}".format(self.binding_list))

        # Skip the report if the connection is not established
        except TypeError:
            pass


#######################################################################################################################
#                                           EXPLICIT CONNECTION
#######################################################################################################################
class ExplicitConnection(ConnectionObject):

    def __init__(self, interface, src_addr, dst_addr):

        # Initialize the class attributes
        super(ExplicitConnection, self).__init__(
            interface,
            src_addr,
            dst_addr,
            instance=CONNECTION.EXPLICIT,
            alloc_choice=ALLOC.EXPLICIT
        )


#######################################################################################################################
#                                           POLL CONNECTION
#######################################################################################################################
class PollConnection(ConnectionObject):

    def __init__(self, interface, src_addr, dst_addr, produce_size=None, consume_size=None):

        # Initialize the class attributes
        super(PollConnection, self).__init__(
            interface,
            src_addr,
            dst_addr,
            instance=CONNECTION.POLL,
            alloc_choice=ALLOC.POLL,
            produce_size=produce_size,
            consume_size=consume_size
        )

    def read(self, timeout=1):

        data = None
        counter = int(float(timeout) / self._poll_time)

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        for i in range(counter):
            data = poll_read(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                produced_size=self._produced_size,
                timeout=self._poll_time
            )

            # self.log.info("#{0:02X} : {1}".format(i, data))
            if data:
                break

        return data

    def write(self, data, timeout=1):

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        # Check I/O connection type and perform operation
        poll_write(
            interface=self.interface,
            master_addr=self.src_addr,
            slave_addr=self.dst_addr,
            consumed_size=self._consumed_size,
            data=data,
        )


#######################################################################################################################
#                                           BITSTROBE CONNECTION
#######################################################################################################################
class BitstrobeConnection(ConnectionObject):

    def __init__(self, interface, src_addr, dst_addr, produce_size=None, consume_size=None):

        # Initialize the class attributes
        super(BitstrobeConnection, self).__init__(
            interface,
            src_addr,
            dst_addr,
            instance=CONNECTION.BITSTROBE,
            alloc_choice=ALLOC.BITSTROBE,
            produce_size=produce_size,
            consume_size=consume_size
        )

    def read(self, timeout=1):

        data = None
        counter = int(float(timeout) / self._poll_time)

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        for i in range(counter):

            data = bitstrobe_read(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                timeout=self._poll_time
            )

            # self.log.info("#{0:02X} : {1}".format(i, data))
            if data:
                break

        return data

    def write(self, data, timeout=1):

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        bitstrobe_write(
            interface=self.interface,
            master_addr=self.src_addr,
            slave_addr=self.dst_addr,
            data=data,
        )


#######################################################################################################################
#                                           CHANGE-OF-STATE CONNECTION
#######################################################################################################################

class CosConnection(ConnectionObject):

    def __init__(self, interface, src_addr, dst_addr, produce_size=None, consume_size=None, ack_sup=False):

        # Initialize the class attributes
        super(CosConnection, self).__init__(
            interface,
            src_addr,
            dst_addr,
            instance=CONNECTION.COS,
            alloc_choice=ALLOC.COS,
            produce_size=produce_size,
            consume_size=consume_size,
            ack_sup=ack_sup
        )

    def read(self, timeout=1):

        data = None
        counter = int(float(timeout) / self._poll_time)

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        for i in range(counter):

            data = cos_read(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                produced_size=self._produced_size,
                consumed_size=self._consumed_size,
                ack_data=[],
                ack_sup=self.ack_sup,
                timeout=self._poll_time
            )

            # self.log.info("#{0:02X} : {1}".format(i, data))
            if data:
                break

        return data

    def write(self, data, timeout=1):

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        # Master uses poll (instance=2) to write to the slave
        if self.ack_sup:
            consumed_size = self.connections[2].consumed_conn_size
            produced_size = 0
        else:
            consumed_size = self.connections[2].consumed_conn_size
            produced_size = self.connections[2].produced_conn_size

        cos_write(
            interface=self.interface,
            master_addr=self.src_addr,
            slave_addr=self.dst_addr,
            consumed_size=consumed_size,
            produced_size=produced_size,
            data=data,
            ack_sup=self.ack_sup,
            timeout=timeout
        )


#######################################################################################################################
#                                           CYCLIC CONNECTION
#######################################################################################################################

class CyclicConnection(ConnectionObject):

    def __init__(self, interface, src_addr, dst_addr, produce_size=None, consume_size=None, ack_sup=False):

        # Initialize the class attributes
        super(CyclicConnection, self).__init__(
            interface,
            src_addr,
            dst_addr,
            instance=CONNECTION.CYCLIC,
            alloc_choice=ALLOC.CYCLIC,
            produce_size=produce_size,
            consume_size=consume_size,
            ack_sup=ack_sup
        )

    def read(self, timeout=1):

        data = None
        counter = int(float(timeout) / self._poll_time)

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        for i in range(counter):

            data = cos_read(
                interface=self.interface,
                master_addr=self.src_addr,
                slave_addr=self.dst_addr,
                produced_size=self._produced_size,
                consumed_size=self._consumed_size,
                ack_data=[],
                ack_sup=self.ack_sup,
                timeout=self._poll_time
            )

            # self.log.info("#{0:02X} : {1}".format(i, data))
            if data:
                break

        return data

    def write(self, data, timeout=1):

        # Verify if I/O connection sizes are initialized
        if self._consumed_size is None or self._produced_size is None:
            self._consumed_size = self.consumed_conn_size
            self._produced_size = self.produced_conn_size

        # Master uses poll (instance=2) to write to the slave
        if self.ack_sup:
            consumed_size = self.connections[2].consumed_conn_size
            produced_size = 0
        else:
            consumed_size = self.connections[2].consumed_conn_size
            produced_size = self.connections[2].produced_conn_size

        cos_write(
            interface=self.interface,
            master_addr=self.src_addr,
            slave_addr=self.dst_addr,
            consumed_size=consumed_size,
            produced_size=produced_size,
            data=data,
            ack_sup=self.ack_sup,
            timeout=timeout
        )
