# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from ..errors import CipServiceError
from ..link import reset, get_attr_single, set_attr_single, get_attr_all
from ..convert import bytes_to_integer, integer_to_bytes

# System imports
import logging
import collections


##########################################################################################
# CIP OBJECT BASE CLASS
##########################################################################################


Attribute = collections.namedtuple("Attribute", ['type', 'id', 'name', 'size'])


class CipObject(object):
    """ Class representing a CIP object

    This class will allow the developer to create CIP objects and easily scale the required
    attributes and services. There are two use cases for the class:

    A) Define a class which inherits the CipObject and extends the attributes list in
    the constructor. Each attribute then will be accessed using properties. This use case is
    usually used to implement objects from the protocol specification(identity, connection, etc.)

    Example:

        class IdentityObject(CipObject):

            CLASS_ID = 0x01
            CLASS_DESC = "IDENTITY OBJECT"

            instance_attributes = [
                    #          | Type    | ID | Name                | Size
                    # .....
                    Attribute('instance', 7,  'product_name',       32),
            ]

            def __init__(self, *args, **kwargs):
                super(IdentityObject, self).__init__(*args, **kwargs)
                self.attributes.extend(self.instance_attributes)

            @property
            def product_name(self):
                try:
                    data = self.get_attribute(attrib_id=7)
                    data = convert.bytes_to_string(data)
                except CipServiceError:
                    data = None

                return data

            @product_name.setter
            def product_name(self, value):
                try:
                    stream = convert.string_to_bytes(value)
                    self.set_attribute(attrib_id=7, value=stream)
                except CipServiceError:
                    raise

        # Create bus interface
        bus = CanNode(device=...)

        # Create identity object
        identity = IdentityObject(interface=bus, src_addr=0, dst_addr=1)

        # Access identity object through properties
        identity.product_name = "Hilscher"
        print(identity.product_name)

    B) Create a CIP object and extend the attributes dynamically. This use case is usually
    used to implement user objects, which are not specified in the protocol documentation.
    The attributes will be accessed by service calls.

    Example:

        from Components.cip.base import CipBase
        from Components.cip.base import Attribute

        # Create user object
        user_object = CipObject(interface=bus,
                        src_addr=self.MASTER_ADDR,
                        dst_addr=self.SLAVE_ADDR,
                        class_id=0x55,
                        instance=0x55)

        # Append an instance attribute dynamically
        user_object.attributes.append(
            Attribute(type='instance',
                      id=0x55,
                      name='my_attrib',
                      size=1)
        )

        # Update object
        user_object.update()

        # Access object's attributes through services
        user_object.set_attribute(attribute_id=0x55, value=0xAA)

    """

    CLASS_DESC = ""

    class_attributes = [
        #         | Type    | ID    | Name                  | Size
        Attribute("class",      0,  "none",                 0),
        Attribute("class",      1,  "revision",             2),
        Attribute("class",      2,  "max_instance",         2),
        Attribute("class",      3,  "num_instance",         2),
        Attribute("class",      4,  "opt_attrib_list",      255),
        Attribute("class",      5,  "opt_service_list",     255),
        Attribute("class",      6,  "last_class_attrib",    2),
        Attribute("class",      7,  "last_instance_attrib", 2),
        Attribute('instance',   0,  'none',                 0),
    ]

    # TODO: This is a workaround for the connection tracking. It should be implemented in a more
    #  generic way in the future, e.g. be a part of the DeviceNetNode class.

    # Connection mapping (instance -> connection type)
    connections = {
        1: None,
        2: None,
        3: None,
        4: None,
        5: None
    }

    ##########################################################################################

    def __init__(self,
                 interface,             # CAN bus interface class
                 src_addr,              # DeviceNet source address
                 dst_addr,              # DeviceNet destination address
                 class_id=0,            # Class-ID
                 instance=1,            # Instance-ID
                 event_handler=None     # Event handler (e.g for remanent storage)
                 ):

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        # Devicenet attributes
        self.interface = interface
        self.src_addr = src_addr
        self.dst_addr = dst_addr

        # CIP attributes
        self.class_id = class_id
        self.instance = instance
        self.attributes = self.class_attributes[:]

        # Initialize and event handler in case the user needs a callback function
        self.event_handler = self.default_handler if event_handler is None else event_handler

    ##########################################################################################

    @property
    def revision(self):
        try:
            data = self.get_attribute(attrib_id=1, instance_id=0)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @revision.setter
    def revision(self, value):
        stream = integer_to_bytes(value, self.get_size("revision"))
        self.set_attribute(attrib_id=12, value=stream)

    ##########################################################################################

    @property
    def max_instance(self):
        try:
            data = self.get_attribute(attrib_id=2, instance_id=0)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @max_instance.setter
    def max_instance(self, value):
        stream = integer_to_bytes(value, self.get_size("max_instance"))
        self.set_attribute(attrib_id=2, value=stream)

    ##########################################################################################

    @property
    def num_instance(self):
        try:
            data = self.get_attribute(attrib_id=3, instance_id=0)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @num_instance.setter
    def num_instance(self, value):
        stream = integer_to_bytes(value, self.get_size("num_instance"))
        self.set_attribute(attrib_id=3, value=stream)

    ##########################################################################################

    @property
    def last_class_attrib(self):
        try:
            data = self.get_attribute(attrib_id=6, instance_id=0)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @last_class_attrib.setter
    def last_class_attrib(self, value):
        stream = integer_to_bytes(value, self.get_size("last_class_attrib"))
        self.set_attribute(attrib_id=6, value=stream)

    ##########################################################################################

    @property
    def last_instance_attrib(self):
        try:
            data = self.get_attribute(attrib_id=7, instance_id=0)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @last_instance_attrib.setter
    def last_instance_attrib(self, value):
        stream = integer_to_bytes(value, self.get_size("last_instance_attrib"))
        self.set_attribute(attrib_id=7, value=stream)

    ##########################################################################################

    def get_attribute_all(self, instance_id=1, wait_time=1):

        # Initialize instance ID
        if instance_id is None:
            instance_id = self.instance

        try:
            data = get_attr_all(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=self.class_id,
                instance_id=instance_id,
                wait_time=wait_time,
            )

        except CipServiceError as e:
            raise e

        return data

    ##########################################################################################

    def reset(self, instance_id=None, reset_type=None, wait_time=1):
        try:

            # Initialize instance-id
            if instance_id is None:
                instance_id = self.instance
            else:
                instance_id = instance_id

            # Convert reset type to raw bytes
            if reset_type is None:
                reset_type = []
            elif not isinstance(reset_type, list):
                reset_type = integer_to_bytes(value=reset_type, size=1)

            data = reset(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=self.class_id,
                instance_id=instance_id,
                data=reset_type,
                wait_time=wait_time,
                event_handler=self.event_handler
            )

            data = 0 if len(data) == 0 else data

        except CipServiceError as e:
            data = e.code

        return data

    ##########################################################################################

    def get_attribute(self, attrib_id, instance_id=None, wait_time=1):

        # Initialize instance ID
        if instance_id is None:
            instance_id = self.instance

        try:
            data = get_attr_single(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=self.class_id,
                instance_id=instance_id,
                data=attrib_id,
                wait_time=wait_time
            )

        except CipServiceError as e:
            raise e

        return data

    ##########################################################################################

    def set_attribute(self, attrib_id, value, instance_id=None, attrib_type="instance", wait_time=1):

        # Initialize instance ID
        if not instance_id:
            instance_id = self.instance

        # Check if value is iterable
        try:
            iter(value)

        # Convert number to stream of bytes
        except TypeError:
            size = self.get_size(attrib_id=attrib_id, attrib_type=attrib_type)
            value = integer_to_bytes(value=value, size=size)

        # Check if value is list and convert
        else:
            if not isinstance(value, list):
                value = [value]

        # Convert attribute ID to list
        if not isinstance(attrib_id, list):
            attrib_id = [attrib_id]

        # Send CIP request
        try:
            response = set_attr_single(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=self.class_id,
                instance_id=instance_id,
                data=attrib_id + value,
                wait_time=wait_time,
                event_handler=self.event_handler
            )

        except CipServiceError as e:
            raise e

        return response

    ##########################################################################################

    def get_size(self, attrib_id, attrib_type="instance"):

        result = 0

        # Attribute ID is integer (attribute index)
        if isinstance(attrib_id, int):
            for element in self.attributes:
                if (attrib_id == element.id) and (attrib_type == element.type):
                    result = element.size
                    break

        # Attribute ID is string (attribute name)
        elif isinstance(attrib_id, bytes) or isinstance(attrib_id, str):
            for element in self.attributes:
                if attrib_id == element.name:
                    result = element.size
                    break

        return result

    ##########################################################################################

    def default_handler(self):
        pass

    ##########################################################################################

    def update(self):
        for attrib in self.attributes:
            if not hasattr(self, attrib.name) and attrib.type == "instance":
                setattr(self, attrib.name, 0)

    ##########################################################################################

    def report(self):
        self.log.info("+" * 80)
        self.log.info("{0} (0x{1:02X}) : INSTANCE [{2}]".format(
            self.CLASS_DESC, self.class_id, self.instance)
        )
        self.log.info("+" * 80)


if __name__ == "__main__":
    o = CipObject(interface=None, src_addr=0, dst_addr=1)
    print(o.get_size(attrib_id=1, attrib_type="class"))
