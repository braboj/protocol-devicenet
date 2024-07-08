# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject, Attribute
from ..errors import CipServiceError
from ..convert import bytes_to_integer
from ..link import get_member, set_member

# System imports
import logging


##############################################################################################
# ASSEMBLY OBJECT (0x04)
##############################################################################################

class AssemblyObject(CipObject):

    """
    The Assembly Object binds attributes of multiple objects, which allows data to or from each
    object to be sent or received over a single connection. Assembly objects can be used to bind
    input data or output data. The terms ”input” and ”output” are defined from the network’s point
    of view. An input will produce data on the network and an output will consume data from the
    network.
    """

    CLASS_ID = 0x04
    CLASS_DESC = "ASSEMBLY OBJECT"

    instance_attributes = [
            #          | Type    | ID | Name                        | Size
            Attribute('instance', 1,  'member_list_size',           2),
            Attribute('instance', 2,  'member_list',                2),
            Attribute('instance', 3,  'data',                       254),
            Attribute('instance', 4,  'size',                       2),
            Attribute('instance', 5,  'member_list_signature',      4),
    ]

    def __init__(self, *args, **kwargs):
        super(AssemblyObject, self).__init__(class_id=0x04, *args, **kwargs)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

    ##########################################################################################

    @property
    def member_list_size(self):
        try:
            data = self.get_attribute(attrib_id=1)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def member_list(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @member_list.setter
    def member_list(self, value):
        stream = value
        self.set_attribute(attrib_id=2, value=stream)

    ##########################################################################################

    @property
    def data(self):
        try:
            data = self.get_attribute(attrib_id=3)

        except CipServiceError:
            data = None

        return data

    @data.setter
    def data(self, value):
        stream = value
        self.set_attribute(attrib_id=3, value=stream)

    ##########################################################################################

    @property
    def size(self):
        try:
            data = self.get_attribute(attrib_id=4)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def member_list_signature(self):
        try:
            data = self.get_attribute(attrib_id=5)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    def get_member(self, member_id=0):

        try:
            data = get_member(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=self.class_id,
                instance_id=self.instance,
                data=member_id,
            )

        except CipServiceError:
            raise

        return data

    ##########################################################################################

    def set_member(self, member_id=0, member_data=None):

        member_data = [] if member_data is None else [member_data]
        service_data = [member_id] + member_data

        try:
            set_member(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                class_id=self.class_id,
                instance_id=self.instance,
                data=service_data,
            )

        except CipServiceError:
            raise

    ##########################################################################################

    def report(self):
        super(AssemblyObject, self).report()

        try:
            self.log.info("REVISION                 = {0}".format(self.revision))
            self.log.info("MEMBER LIST SIZE         = {0}".format(self.member_list_size))
            self.log.info("MEMBER LIST              = {0}".format(self.member_list))
            self.log.info("DATA                     = {0}".format(self.data))
            self.log.info("SIZE                     = {0}".format(self.size))
            self.log.info("MEMBER LIST SIGNATURE    = {0}".format(self.member_list_signature))

        except TypeError:
            pass
