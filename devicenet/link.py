# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Custom libraries
from .packets import *
from .addressing import can_addr

# System libraries
import logging
from functools import partial

log = logging.getLogger("MessageService")
log.addHandler(logging.NullHandler())


# TODO:
#   - Migrate the code base to a new connection class
#   - The to_frame(), from_frame() and split() methods should be moved to producer/consumer classes
#   - Fix bug with writing I/O data without consumption and then explicit request
#   - Rename _fragmented to _is_fragmented, _one_fragment to _is_onefragment, etc.
#   - Add send_dupmac() and recv_dupmac() functions
#   - Add a GUI for the devicenet network (using tkinter, pyqt, etc.)
#   - Split the sending and acknowledge repsonse in cos_write, cos_read

##############################################################################################
# MESSAGING LAYER : Encodes service requests and I/O exchange to the devicenet message format
##############################################################################################

def service_request(
        interface,
        src_addr,
        dst_addr,
        service_code,
        class_id,
        instance_id,
        data=(),
        group_id=2,
        message_id=4,
        wait_time=1,
        event_handler=None
):
    """ Send an explicit request and wait for the explicit response

    Args:
        interface,          : Interface used to send CAN messages
        src_addr,           : Source MAC address
        dst_addr,           : Destination MAC address
        service_code,       : Service code
        class_id,           : Class ID defined by CIP or DeviceNet
        instance_id,        : Instance ID of class
        data=None,          : Attribute ID of class
        group_id=2,         : Default group for explicit messages
        message_id=4,       : Default request message ID for DeviceNet
        wait_time=1,        : Maximum wait time for responses in seconds
        event_handler=None  : Callback for event/indication handling

    Returns:
        response            : Data from the explicit response

    Raises:
        CipError            : On communication problems

    Usage:

        # Create CAN bus interface
        bus = CanNode(device=self.master)

        # Allocate the explcit connection using a partial method of the service request
        # Data is connection-ID (0x01) and allocator address (0x00)
        allocate(
            interface=bus,
            src_addr=self.MASTER_ADDR,
            dst_addr=self.SLAVE_ADDR,
            data=(0x01, 0x00)
        )

        # Send Get_Attibute_Single (0x0E) to Class 0x01 (Identity), Instance 1, Attribute 6
        vendor_id = service_request(
            interface=bus,
            src_addr=self.MASTER_ADDR,
            dst_addr=self.SLAVE_ADDR,
            service_code=0x0E,
            class_id=0x01,
            instance_id=0x01,
            data=(6, )
        )

    """

    # Construct the explicit request packet
    request = ExplicitServicePacket(
        group_id=group_id,
        message_id=message_id,
        src_mac=src_addr,
        dst_mac=dst_addr,
        service_code=service_code,
        class_id=class_id,
        instance_id=instance_id,
        service_data=data,
    ).build()

    try:

        # Start the CAN sniffer
        can_id = can_addr(
            msg_group=EXPLICIT.RSP_GROUP,
            msg_id=EXPLICIT.RSP,
            mac=dst_addr
        )
        interface.start_listen(can_id=[can_id])

        # Send the CAN frame
        send_message(interface, request, explicit=True)

        # Execute callback handler for indications (the handler is provided by the upper layers)
        if event_handler:
            event_handler()

        # Wait for the service request response
        if wait_time:
            response = wait_response(interface, src_addr, dst_addr, service_code, timeout=wait_time)
            interface.stop_listen(can_id=[can_id])

        # In case of no wait time keep the listener active
        else:
            response = []

    except CipError:
        raise

    return response


##############################################################################################

def send_message(interface, message, explicit=True):
    """ Send a devicenet explicit request message on the CAN bus

    Args:
        interface   : CAN interface
        message     : DeviceNet message as CAN data
        explicit    : Explicit or I/O

    """

    # Message shall be fragmented
    if message.length > 8:

        # Generate the fragments
        fragments = message.split()

        for fragment in fragments:

            # Send the fragment
            interface.send(frame=fragment)

            # Wait for the fragment acknowledged response in case of explicit messaging
            if explicit:
                wait_fragment_ack(interface)

    # Message is not fragmented
    else:
        interface.send(frame=message.to_frame())


##############################################################################################

def wait_response(interface, src_addr, dst_addr, service_code, timeout=1):
    """ Wait for a devicenet explicit response message on the CAN bus

    Args:
        interface       : CAN interface
        src_addr        : Source MAC address
        dst_addr        : Destination MAC address
        service_code    : Expected service code
        timeout         : Time to wait for a response (set to 0 to deactivate waiting)

    Usage:

        # Create CAN bus interface
        bus = CanNode(device=self.master)

        # Allocate the explcit connection using a partial method of the service request
        # Data is connection-ID (0x01) and allocator address (0x00)
        allocate(
            interface=bus,
            src_addr=self.MASTER_ADDR,
            dst_addr=self.SLAVE_ADDR,
            data=(0x01, 0x00)
        )

        # Send Get_Attribute_All (0x01) to the Class 0x01 (Identity), Instance 1
        service_request(
            interface=bus,
            src_addr=0,
            dst_addr=1,
            service_code=0x01,
            class_id=0x01,
            instance_id=1,
            data=[],
            group_id=EXPLICIT.REQ_GROUP,
            message_id=EXPLICIT.REQ,
            wait_time=0
        )

        # Wait for slave's response on the bus
        response = wait_response(
            interface=self.bus,
            src_addr=self.MasterAddr,
            dst_addr=self.SlaveAddr,
            service_code=SERVICE.GET_ATTR_ALL,
        )

    """

    # The service data is stored in this list
    result = []

    while True:

        msg_in = interface.recv(timeout=timeout)

        # Message arrived within timeout
        if msg_in:
            response = ExplicitServicePacket().from_frame(msg_in)

        # Slave didn't respond
        else:
            raise CipNoResponseError

        # Response detected
        if response.service_code == service_code:

            # Non-fragmented consumption
            if not _fragmented(response):
                result = response.service_data
                break

            # Fragmented consumption consisting of one fragment
            elif _one_fragment(response):
                result = response.service_data
                break

            elif _start_fragment(response):
                ack_fragment(interface, src_addr, dst_addr, 0x00)
                result.extend(response.service_data)
                result.extend(read_fragment(interface, src_addr, dst_addr, explicit=True))
                break

            # Error in consumption (middle, last fragment came first)
            else:
                continue

        # Check slave's response on requests with service codes having the R/R flag set
        elif _bad_service(service_code) and not _error(response):
            raise CipServiceError(ERROR.INVALID_REPLY_RECEIVED)

        # Error response from slave on service request
        elif _error(response):
            error = response.service_data[0]
            raise CipServiceError(error)

    return result


############################################################################################

def read_fragment(interface, src_addr, dst_addr, explicit=True, timeout=1):
    """ Read fragmented explicit and I/O fragmented

    Args:
        interface   : CAN interface
        src_addr    : Source MAC address
        dst_addr    : Destination MAC address
        explicit    : Explicit or I/O message
        timeout     : Time to wait for a response (set to 0 to deactivate waiting)

    """

    stream = []
    prev_counter = 0
    # queue = []

    while True:

        msg_in = interface.recv(timeout=timeout)
        # queue.append(msg_in)

        # Check type of fragmentation and parse CAN message
        if msg_in:
            if explicit:
                response = ExplicitFragPacket().from_frame(msg_in)
            else:
                response = IoFragPacket().from_frame(msg_in)
        else:
            break

        counter_diff = (response.frag_count - prev_counter)

        # Duplicate fragment received, re-acknowledge
        if counter_diff == 0:
            if explicit:
                ack_fragment(interface, src_addr, dst_addr, response.frag_count)
            else:
                stream.extend(response.data)

        # Next fragment
        elif counter_diff == 1:
            stream.extend(response.data)
            if explicit:
                ack_fragment(interface, src_addr, dst_addr, response.frag_count)
            prev_counter = response.frag_count

        # Error occurred during defragmentation
        elif counter_diff > 1:
            log.warning("WARNING : Missing fragment detected!")

        # Exit
        if _final_fragment(response):
            break

    result = stream if stream else None
    return result


############################################################################################

def wait_fragment_ack(interface):
    """ Wait for the fragment acknowledged response

    Args:
        interface   : CAN interface

    """

    msg_in = None
    for i in range(2):
        msg_in = interface.recv(timeout=1)
        if msg_in:
            response = ExplicitFragAckPacket().from_frame(msg_in)
            if response.ack_status != 0:
                raise CipFragmentResponseError
            break
        else:
            continue

    if not msg_in:
        raise CipNoResponseError


##############################################################################################

def ack_fragment(interface, src_addr, dst_addr, frag_count, frag_status=0, frag_type=3):
    """ Acknowledge a received fragment

    Args:
        interface   : CAN interface
        src_addr    : Source MAC address
        dst_addr    : Destination MAC address
        frag_count  : Fragmentation counter
        frag_status : Fragmentation status
        frag_type   : Fragment type

    """

    acknowledge = ExplicitFragAckPacket(
        src_mac=src_addr,
        dst_mac=dst_addr,
        frag_count=frag_count,
        frag_type=frag_type,
        ack_status=frag_status
    ).build()

    msg_out = acknowledge.to_frame()
    interface.send(frame=msg_out)


##############################################################################################

def bitstrobe_write(interface, master_addr, slave_addr, data):
    """ Send a bitstrobe message

    Args:
        interface   : CAN interface
        master_addr : Master address
        slave_addr  : Slave address
        data        : Data to send

    Raises:
        Exception   : On unexpected exceptions

    """

    command = IoPacket(
        group_id=BITSTROBE.REQ_GROUP,
        message_id=BITSTROBE.REQ,
        src_mac=master_addr,
        dst_mac=slave_addr,
        data=data
    ).build()

    # Start listeners
    can_id = can_addr(
        msg_group=BITSTROBE.RSP_GROUP,
        msg_id=BITSTROBE.RSP,
        mac=slave_addr
    )
    interface.start_listen(can_id=[can_id])

    try:
        interface.send(frame=command.to_frame())

    except Exception as error:
        log.error(error)
        raise


##############################################################################################

def bitstrobe_read(interface, master_addr, slave_addr, timeout=1):
    """ Receive a bitstrobe message

    Args:
        interface   : CAN interface
        master_addr : Master address
        slave_addr  : Slave address
        timeout     : Time to wait for a response (set to 0 to deactivate waiting)

    Raises:
        Exception   : On unexpected exceptions

    Returns:
        result      : Data from the received bitstrobe message

    """

    # Calculate the CAN ID for the response
    can_id = can_addr(
        msg_group=BITSTROBE.RSP_GROUP,
        msg_id=BITSTROBE.RSP,
        mac=slave_addr
    )

    try:

        # Receive response
        result = None
        message = interface.recv(can_id=can_id, timeout=timeout)
        if message:
            response = IoPacket(master_addr, slave_addr).from_frame(message)
            result = response.data

        # Stop listeners
        interface.stop_listen()

    except Exception as error:
        log.error(error)
        raise

    return result


##############################################################################################

def poll_write(interface, master_addr, slave_addr, consumed_size, data):
    """ Send a poll message

    Args:
        interface       : CAN interface
        master_addr     : Master address
        slave_addr      : Slave address
        consumed_size   : The data size consumed by the node
        data            : Data to send

    Raises:
        Exception   : On unexpected exceptions

    """

    # Start listeners here in case of fragmented messages in quick succession
    can_id = can_addr(
        msg_group=POLL.RSP_GROUP,
        msg_id=POLL.RSP,
        mac=slave_addr
    )
    interface.start_listen(can_id=[can_id])

    try:

        command = IoPacket(
            group_id=POLL.REQ_GROUP,
            message_id=POLL.REQ,
            src_mac=master_addr,
            dst_mac=slave_addr,
            data=data
        ).build()

        # Check if fragmentation is required
        fragmentation = (consumed_size > 8)
        data_size = len(data)

        # Send multiple frames with the fragmentation protocol
        if fragmentation and data_size >= 8:
            # command.data = (0,) + tuple(command.data)
            send_message(interface, command, explicit=False)

        # Send a single frame with the fragmentation protocol
        elif fragmentation and data_size < 8:
            command.data = (FRAGMENT.MAX_COUNT,) + tuple(command.data)
            interface.send(frame=command.to_frame())

        # Send a non-fragmented can frame
        else:
            interface.send(frame=command.to_frame())

    except Exception as error:
        log.error(error)
        raise


##############################################################################################

def poll_read(interface, master_addr, slave_addr, produced_size, timeout=1):
    """ Receive a poll message

    Args:
        interface       : CAN interface
        master_addr     : Master address
        slave_addr      : Slave address
        produced_size   : The data size produced by the node
        timeout         : Time to wait for a response (set to 0 to deactivate waiting)

    Raises:
        Exception   : On unexpected exceptions

    Returns:
        result      : Data from the received poll message

    """

    # Calculate the CAN ID for the response
    can_id = can_addr(
        msg_group=POLL.RSP_GROUP,
        msg_id=POLL.RSP,
        mac=slave_addr
    )

    result = None
    try:

        # Receive response
        if produced_size > 8:
            result = read_fragment(interface, master_addr, slave_addr, explicit=False, timeout=timeout)
        else:
            message = interface.recv(can_id=can_id, timeout=timeout)
            if message:
                response = IoPacket(master_addr, slave_addr).from_frame(message)
                result = response.data

        # Stop listeners
        interface.stop_listen()

    except Exception as error:
        log.error(error)
        raise

    return result


##############################################################################################

def cos_write(interface, master_addr, slave_addr, consumed_size, produced_size, data, ack_sup, timeout=1):
    """ Send a COS/CYCLIC message

    Args:
        interface       : CAN interface
        master_addr     : Master address
        slave_addr      : Slave address
        produced_size   : The data size produced by the node
        consumed_size   : The data size consumed by the node
        ack_sup         : Acknowledge suppression flag
        data            : Data to send
        timeout         : Time to wait for a response (set to 0 to deactivate waiting)

    Raises:
        Exception   : On unexpected exceptions

    Returns:
        result      : Data from the acknowledge message

    """

    result = None

    try:

        # Create COS message from the master
        command = IoPacket(
            group_id=COS.MASTER.REQ_GROUP,
            message_id=COS.MASTER.REQ,
            src_mac=master_addr,
            dst_mac=slave_addr,
            data=data
        ).build()

        # Start listener for ACK response from the slave
        can_id = can_addr(
            msg_group=COS.SLAVE.RSP_GROUP,
            msg_id=COS.SLAVE.RSP,
            mac=slave_addr
        )
        interface.start_listen(can_id=[can_id])

        # Send command
        fragmentation = (consumed_size > 8)
        data_size = len(data)

        if fragmentation and data_size >= 8:
            send_message(interface, command, explicit=False)

        elif fragmentation and data_size < 8:
            command.data = (FRAGMENT.MAX_COUNT,) + tuple(command.data)
            interface.send(frame=command.to_frame())

        else:
            interface.send(frame=command.to_frame())

        # Receive ACK from slave
        if not ack_sup:

            if produced_size > 8:
                result = read_fragment(interface, master_addr, slave_addr, explicit=False)
            else:
                message = interface.recv(timeout=timeout)
                if message:
                    response = IoPacket(master_addr, slave_addr).from_frame(message)
                    result = response.data
                else:
                    raise CipNoResponseError

        # Stop listeners
        interface.stop_listen()

    except Exception as error:
        log.error(error)
        raise

    return result


##############################################################################################

def cos_read(interface, master_addr, slave_addr, consumed_size, produced_size, ack_data, ack_sup, timeout=1):
    """ Receive a COS/CYCLIC message

    Args:
        interface       : CAN interface
        master_addr     : Master address
        slave_addr      : Slave address
        produced_size   : The data size produced by the node
        consumed_size   : The data size consumed by the node
        ack_sup         : Acknowledge suppression flag
        ack_data        : Data to send in the acknowledgment cos message
        timeout         : Time to wait for a response (set to 0 to deactivate waiting)

    Raises:
        Exception   : On unexpected exceptions

    Returns:
        result      : Data from the cos message

    """

    result = None
    try:

        # Start listeners for messages from the slave
        can_id = can_addr(
            msg_group=COS.SLAVE.REQ_GROUP,
            msg_id=COS.SLAVE.REQ,
            mac=slave_addr
        )
        interface.start_listen(can_id=[can_id])

        # Wait for COS messages
        if produced_size > 8:
            result = read_fragment(interface, master_addr, slave_addr, explicit=False, timeout=timeout)
        else:
            message = interface.recv(timeout=timeout)
            if message:
                response = IoPacket(master_addr, slave_addr).from_frame(message)
                result = response.data

        # Send ACK to slave
        if result and not ack_sup:

            # Create packet
            response = IoPacket(
                group_id=COS.MASTER.RSP_GROUP,
                message_id=COS.MASTER.RSP,
                src_mac=master_addr,
                dst_mac=slave_addr,
                data=ack_data
            ).build()

            # Send response
            fragmentation = (consumed_size > 8)
            data_size = len(ack_data)

            # Signal start of multi-fragmentation and counter set to 0
            if fragmentation and data_size >= 8:
                send_message(interface, response, explicit=False)

            # Signal single fragment message by setting the fragment counter to MAX_COUNT
            elif fragmentation and data_size < 8:
                response.data = (FRAGMENT.MAX_COUNT,) + tuple(response.data)
                interface.send(frame=response.to_frame())

            else:
                interface.send(frame=response.to_frame())

        # Stop listeners
        interface.stop_listen()

    except Exception:
        raise

    return result


##############################################################################################
# HELPERS
##############################################################################################

def _fragmented(response):
    """ Check whether the response is fragmented """
    result = (response.frag_flag == FRAGMENT.ENABLED)
    return result


def _one_fragment(response):
    """ Check whether the response is fragmented and consisting of only one fragment """
    result = (response.frag_type == FRAGMENT.TYPE.START) and \
             (response.frag_count == FRAGMENT.MAX_COUNT)

    return result


def _start_fragment(response):
    """ Check whether this is the first fragmented packet of the response """
    result = (response.frag_type == FRAGMENT.TYPE.START) and \
             (response.frag_count == 0x00)

    return result


def _middle_fragment(response):
    """ Check whether this is a middle fragmented packet of the response """
    result = (response.frag_type == FRAGMENT.TYPE.MIDDLE) and \
             (0 < response.frag_count < FRAGMENT.MAX_COUNT)

    return result


def _final_fragment(response):
    """ Check whether this is the last fragmented packet of the response """
    result = (response.frag_type == FRAGMENT.TYPE.FINAL) or \
             (response.frag_count == FRAGMENT.MAX_COUNT)

    return result


def _bad_service(service_code):
    """ Check validity of the service request code """
    result = (service_code > SERVICE.LAST_VALID_CODE)
    return result


def _error(response):
    """ Check whether the response from the slave is an error """
    result = (response.service_code == SERVICE.ERROR)
    return result


##############################################################################################
# COMMON SERVICES
##############################################################################################

get_attr_all = partial(
    service_request,
    service_code=SERVICE.GET_ATTR_ALL,
    group_id=EXPLICIT.REQ_GROUP,
    message_id=EXPLICIT.REQ
)

reset = partial(
    service_request,
    service_code=SERVICE.RESET,
    group_id=EXPLICIT.REQ_GROUP,
    message_id=EXPLICIT.REQ
)

get_attr_single = partial(
    service_request,
    service_code=SERVICE.GET_ATTR_SINGLE,
    group_id=EXPLICIT.REQ_GROUP,
    message_id=EXPLICIT.REQ
)

set_attr_single = partial(
    service_request,
    service_code=SERVICE.SET_ATTR_SINGLE,
    group_id=EXPLICIT.REQ_GROUP,
    message_id=EXPLICIT.REQ
)

get_member = partial(
    service_request,
    service_code=SERVICE.GET_MEMBER,
    group_id=EXPLICIT.REQ_GROUP,
    message_id=EXPLICIT.REQ
)

set_member = partial(
    service_request,
    service_code=SERVICE.SET_MEMBER,
    group_id=EXPLICIT.REQ_GROUP,
    message_id=EXPLICIT.REQ
)

##############################################################################################
# OBJECT SPECIFIC SERVICES
##############################################################################################

allocate = partial(
    service_request,
    service_code=SERVICE.ALLOCATE,
    group_id=UNCONNECTED.REQ_GROUP,
    message_id=UNCONNECTED.REQ,
    class_id=DEVICENET.ID,
    instance_id=DEVICENET.DEFAULT_INSTANCE
)

release = partial(
    service_request,
    service_code=SERVICE.RELEASE,
    group_id=UNCONNECTED.REQ_GROUP,
    message_id=UNCONNECTED.REQ,
    class_id=DEVICENET.ID,
    instance_id=DEVICENET.DEFAULT_INSTANCE
)
