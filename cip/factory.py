# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject
from .identity import IdentityObject
from .devnet import DeviceNetObject
from .assembly import AssemblyObject
from .connection import ConnectionObject
from .ack_handler import AcknowledgeHandler
from .mns import ModuleNetworkStatus

# System imports
import logging


class CipFactory(object):
    """ Class used to generate an object from Class-ID.

    The factory class takes some generic parameters like interface, source and
    destinationa addresses and the factory method "create" then produces the
    desired object with class-ID and instance-ID.

    Example:

        # Create CAN bus interface
        can = CanNode(device=...)

        # Initialize CIP object factory
        factory = CipFactory(interface=can, src_addr=0, dst_addr=1)

        # Create explicit connection object from class ID and instance ID
        connection = factory.create(class_id=0x05, instance_id=1)
        connection.allocate()
        connection.report()

        # Create identity object from class and instance ID
        identity = factory.create(class_id=0x01, instance_id=1)
        identity.report()

        # Create devnet object from class and instance ID
        devnet = factory.create(class_id=0x03, instance_id=1)
        devnet.report()

    """

    def __init__(self, interface, src_addr, dst_addr):

        self.interface = interface
        self.src_addr = src_addr
        self.dst_addr = dst_addr

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

    def create(self, class_id, instance_id):

        # TODO: Convert if-then-else to a dynamic structure for easier scaling
        #   Loop throught registered objects (potential metaclass usecase)
        #   for cip_object in objects:
        #       if class_id == obj.CLASS_ID:
        #           result = cip_obj(...)

        if class_id == IdentityObject.CLASS_ID:
            cip_object = IdentityObject(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                instance=instance_id
            )

        elif class_id == DeviceNetObject.CLASS_ID:
            cip_object = DeviceNetObject(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                instance=instance_id
            )

        elif class_id == AssemblyObject.CLASS_ID:
            cip_object = AssemblyObject(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                instance=instance_id
            )

        elif class_id == ConnectionObject.CLASS_ID:
            cip_object = ConnectionObject(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                instance=instance_id
            )

        elif class_id == AcknowledgeHandler.CLASS_ID:
            cip_object = AcknowledgeHandler(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                instance=instance_id
            )

        elif class_id == ModuleNetworkStatus.CLASS_ID:
            cip_object = ModuleNetworkStatus(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                instance=instance_id
            )

        elif class_id:
            cip_object = CipObject(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=class_id,
                instance=instance_id
            )

        else:
            cip_object = None

        return cip_object


if __name__ == "__main__":

    factory = CipFactory(interface=None, src_addr=0, dst_addr=1)
    explicit = factory.create(class_id=5, instance_id=1)

    for attrib in dir(explicit):
        print(attrib)

