# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from .definitions import *
from .cip.identity import IdentityObject
from .cip.mr import MessageRouterObject
from .cip.devnet import DeviceNetObject
from .cip.connection import ConnectionObject
from .cip.ack_handler import AcknowledgeHandler
from .cip.mns import ModuleNetworkStatus
from .cip.assembly import AssemblyObject
from .cip.dummy import DummyObject
from .cip.base import CipObject

import logging

# TODO: Refactoring tasks
#   - Add a collection that stores the CIP classes (e.g. IdentityObject, DeviceNetObject, etc.) -> Profiles
#       - Profile with generic CIP objects (Generic Device Profile)
#       - Profile with generic and Hilscher specific objects
#       - Profile with generic, Hilscher specific and test objects
#   - The node constructor uses the object collection to instantiate the objects (profile instantiation)
#   - Add support to add and remove objects dynamically (e.g. node.add_object("obj_name", object))
#   - Improve the update of src_addr, dst_addr and the event_handler using the object collection
#   - Improve comments and documentation


class DevNetCipNode(object):
    """ Class representing a standard CIP node with some pre-defined CIP objects.

    This class represent a standard communication adapter profile. According to the CIP
    specification each profile requires a certain set of objects.

    Example:

        can = CanNode(device=...)
        node = CipNode(bus=can, src_addr=0, self.dst_addr=1, event_handler=None)

        # Allocate explicit connection
        node.explicit.allocate()

        # Access slave's objects through the bus
        print(node.identity.mac)
        print(node.devnet.mac)

        # Allocate an I/O connection
        node.poll.allocate()
        print(node.poll.conn_state)

        # Release the explicit connection
        node.explicit.release()

    """

    def __init__(self,
                 bus=None,                          # Bus interface
                 src_addr=0,                        # DeviceNet Master Address
                 dst_addr=1,                        # DeviceNet Slave Address
                 produce_size=8,                    # Size of the produce buffer
                 consume_size=8,                    # Size of the consume buffer
                 event_handler=None                 # Event handler
                 ):

        # Initialize logger
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        # CAN interface
        self.bus = bus

        # DeviceNet parameters
        self._src_addr = src_addr
        self._dst_addr = dst_addr
        self._produce_size = produce_size
        self._consume_size = consume_size

        # Event handler method
        self._event_handler = event_handler

        # Identity Object (Class 0x01, Instance 0x01)
        self.identity = IdentityObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler
        )

        # Message Router Object (Class 0x02, Instance 0x01)
        self.mr = MessageRouterObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler
        )

        # DeviceNet Object (Class 0x03, Instance 0x01)
        self.devnet = DeviceNetObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler
        )

        # Connection Class Object (Class 0x05, Instance 0x00)
        self.connection_class = CipObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            class_id=0x05,
            instance=0,
            event_handler=event_handler,
        )

        # Explicit Connection Object (Class 0x05, Instance 0x01)
        self.explicit = ConnectionObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler,
            alloc_choice=ALLOC.EXPLICIT
        )

        # Poll Connection Object (Class 0x05, Instance 0x02)
        self.poll = ConnectionObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=2,
            event_handler=event_handler,
            alloc_choice=ALLOC.POLL
        )

        # Bitstrobe Connection Object (Class 0x05, Instance 0x03)
        self.bitstrobe = ConnectionObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=3,
            event_handler=event_handler,
            alloc_choice=ALLOC.BITSTROBE
        )

        # COS Connection Object (Class 0x05, Instance 0x04)
        self.cos = ConnectionObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=4,
            event_handler=event_handler,
            alloc_choice=ALLOC.COS
        )

        # CYCLIC Connection Object (Class 0x05, Instance 0x04)
        self.cyclic = ConnectionObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=4,
            event_handler=event_handler,
            alloc_choice=ALLOC.CYCLIC
        )

        # MPOLL Connection Object (Class 0x05, Instance 0x05)
        self.mpoll = ConnectionObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=5,
            event_handler=event_handler,
            alloc_choice=ALLOC.MPOLL
        )

        # ACK Handler Object (Class 0x2B, Instance 0x01)
        self.ack_handler = AcknowledgeHandler(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler,
        )

        # MNS Object (Class 0x404, Instance 0x01)
        self.mns = ModuleNetworkStatus(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler,
        )

        # Assembly Consumer Object (Class 0x4, Instance 0x100)
        self.consumer = AssemblyObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=100,
            event_handler=event_handler,
        )

        # Assembly Producer Object (Class 0x4, Instance 0x101)
        self.producer = AssemblyObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=101,
            event_handler=event_handler,
        )

        # DummyObject for test purposes
        self.dummy = DummyObject(
            interface=bus,
            src_addr=src_addr,
            dst_addr=dst_addr,
            instance=1,
            event_handler=event_handler,
        )

    ##############################################################################################

    @property
    def dst_addr(self):
        """ Destination address getter """
        return self._dst_addr

    @dst_addr.setter
    def dst_addr(self, value):
        """ Destination address setter """

        # Notify CIP objects about the address change
        self.identity.dst_addr = value
        self.mr.dst_addr = value
        self.devnet.dst_addr = value
        self.explicit.dst_addr = value
        self.poll.dst_addr = value
        self.bitstrobe.dst_addr = value
        self.cos.dst_addr = value
        self.cyclic.dst_addr = value
        self.mpoll.dst_addr = value
        self.ack_handler.dst_addr = value
        self.mns.dst_addr = value
        self.dummy.dst_addr = value
        self.consumer.dst_addr = value
        self.producer.dst_addr = value

        # Save new value
        self._dst_addr = value

    ##############################################################################################

    @property
    def src_addr(self):
        """ Source address getter """
        return self._src_addr

    @src_addr.setter
    def src_addr(self, value):
        """ Source address setter """

        # TODO: Pack the followiung statements in a handler method
        #   The handler method shall iterate all the objects from the profile
        #   add call an update method.

        # Notify CIP objects about the address change
        self.identity.src_addr = value
        self.mr.src_addr = value
        self.devnet.src_addr = value
        self.explicit.src_addr = value
        self.poll.src_addr = value
        self.bitstrobe.src_addr = value
        self.cos.src_addr = value
        self.cyclic.src_addr = value
        self.mpoll.src_addr = value
        self.ack_handler.src_addr = value
        self.mns.src_addr = value
        self.dummy.src_addr = value
        self.consumer.src_addr = value
        self.producer.src_addr = value

        # Save new value
        self._src_addr = value

    ##############################################################################################

    @property
    def event_handler(self):
        """ Event handler method getter """
        return self._event_handler

    @event_handler.setter
    def event_handler(self, value):
        """ Event handler method setter """

        # TODO: Pack the followiung statements in a handler method
        #   The handler method shall iterate all the objects from the profile
        #   add call an update method.

        # Notify CIP objects about the event handler change
        self.identity.event_handler = value
        self.mr.event_handler = value
        self.devnet.event_handler = value
        self.explicit.event_handler = value
        self.poll.event_handler = value
        self.bitstrobe.event_handler = value
        self.cos.event_handler = value
        self.cyclic.event_handler = value
        self.mpoll.event_handler = value
        self.ack_handler.event_handler = value
        self.mns.event_handler = value
        self.dummy.event_handler = value
        self.consumer.event_handler = value
        self.producer.event_handler = value

        # Save new value
        self._event_handler = value

    ##############################################################################################

    def allocate(self, alloc_choice):
        """ Allocate connections according to the allocation choice."""

        try:
            # Scan allocation choice byte and populate connection list
            if (alloc_choice & ALLOC.EXPLICIT) >> 0:
                CipObject.connections[1] = self.explicit

            if (alloc_choice & ALLOC.POLL) >> 1:
                CipObject.connections[2] = self.poll

            if (alloc_choice & ALLOC.BITSTROBE) >> 2:
                CipObject.connections[3] = self.bitstrobe

            if (alloc_choice & ALLOC.MPOLL) >> 3:
                CipObject.connections[5] = self.mpoll

            if (alloc_choice & ALLOC.COS) >> 4:
                CipObject.connections[4] = self.cos
                CipObject.connections[2] = self.poll

            if (alloc_choice & ALLOC.CYCLIC) >> 5:
                CipObject.connections[4] = self.cyclic
                CipObject.connections[2] = self.poll

            if (alloc_choice & ALLOC.ACKSUP) >> 6:
                CipObject.connections[4].ack_sup = 1

            # Allocate all connections
            self.devnet.allocate(alloc_choice=alloc_choice)

        except Exception as e:
            self.log.error(e)
            raise

    ##############################################################################################

    def release(self, alloc_choice=None, wait_time=1):
        """ Release connections according to the allocation choice."""

        try:
            # Custom release procedure
            if alloc_choice is not None:
                self.devnet.release(alloc_choice)

            # Default release procedure
            else:

                # Release all connections
                for connection in CipObject.connections.values():
                    connection.release(wait_time=wait_time) if connection else None

                # CipObject.connections = dict.fromkeys(range(1, 6), None)
                # self.bus.stop_listen()

            # Flush all pending packets
            self.bus.flush()

        except Exception as e:
            self.log.error(e)
            raise

    ##############################################################################################

    def report(self):
        """ Report on all profile objects """

        # TODO: Iterate over the objects in a profile

        self.identity.report()
        self.mr.report()
        self.devnet.report()
        self.explicit.report()
        self.poll.report()
        self.bitstrobe.report()
        self.cos.report()
        self.cyclic.report()
        self.ack_handler.report()
        self.mns.report()
        self.consumer.report()
        self.producer.report()
