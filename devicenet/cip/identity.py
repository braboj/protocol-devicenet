# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject, Attribute
from ..errors import *
from ..convert import *

# System imports
import logging


##############################################################################################
# IDENTITY OBJECT (0x01)
##############################################################################################

class IdentityObject(CipObject):

    """
    This object provides identification of and general information about the device and optionally its subsystems.
    Instance one (1) of the Identity Object shall be present in all devices. Instance one (1) shall identify the
    whole device. It alone shall be used for electronic keying, by applications wishing to determine what nodes are
    on the network and to match an EDS with a product on the network.

    Other instances are optional. They may be provided by a device to give additional information about a device,
    such as its embedded components and/or subsystems. Instances greater than one (1) that are used to report the
    revision of embedded components shall be assigned the Embedded Component (0xC8) device type. See section 6-44
    Embedded Component for attribute and service requirements for this purpose.
    """

    CLASS_ID = 0x01
    CLASS_DESC = "IDENTITY OBJECT"

    instance_attributes = [
            #          | Type    | ID | Name                | Size
            Attribute('instance', 1,  'vendor',             2),
            Attribute('instance', 2,  'device_type',        2),
            Attribute('instance', 3,  'product_code',       2),
            Attribute('instance', 4,  'revision',           2),
            Attribute('instance', 5,  'status',             2),
            Attribute('instance', 6,  'serial',             4),
            Attribute('instance', 7,  'product_name',       32),
    ]

    def __init__(self, *args, **kwargs):
        super(IdentityObject, self).__init__(class_id=0x01, *args, **kwargs)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

    ##########################################################################################

    @property
    def vendor(self):
        try:
            data = self.get_attribute(attrib_id=1)
            data = bytes_to_integer(data)
        except CipError:
            data = None

        return data

    @vendor.setter
    def vendor(self, value):
        stream = integer_to_bytes(value, self.get_size("vendor"))
        self.set_attribute(attrib_id=1, value=stream)

    ##########################################################################################

    @property
    def device_type(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @device_type.setter
    def device_type(self, value):
        stream = integer_to_bytes(value, self.get_size("device_type"))
        self.set_attribute(attrib_id=2, value=stream)

    ##########################################################################################

    @property
    def product_code(self):
        try:
            data = self.get_attribute(attrib_id=3)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @product_code.setter
    def product_code(self, value):
        stream = integer_to_bytes(value, self.get_size("product_code"))
        self.set_attribute(attrib_id=3, value=stream)

    ##########################################################################################

    @property
    def revision(self):
        try:
            data = self.get_attribute(attrib_id=4)
        except CipServiceError:
            data = None

        return data

    @revision.setter
    def revision(self, value):
        stream = integer_to_bytes(value, self.get_size("revision"))
        self.set_attribute(attrib_id=4, value=stream)

    ##########################################################################################

    @property
    def status(self):
        try:
            data = self.get_attribute(attrib_id=5)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @status.setter
    def status(self, value):
        stream = integer_to_bytes(value, self.get_size("status"))
        self.set_attribute(attrib_id=5, value=stream)

    ##########################################################################################

    @property
    def serial(self):
        try:
            data = self.get_attribute(attrib_id=6)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @serial.setter
    def serial(self, value):
        stream = integer_to_bytes(value, self.get_size("serial"))
        self.set_attribute(attrib_id=6, value=stream)

    ##########################################################################################

    @property
    def product_name(self):
        try:
            data = self.get_attribute(attrib_id=7)
            data = bytes_to_string(data)
        except CipServiceError:
            data = None

        return data

    @product_name.setter
    def product_name(self, value):
        try:
            stream = string_to_bytes(value)
            self.set_attribute(attrib_id=7, value=stream)
        except CipServiceError:
            raise

    ##########################################################################################

    def report(self):
        super(IdentityObject, self).report()

        try:
            self.log.info("VENDOR ID    = {0}".format(self.vendor))
            self.log.info("DEVICE TYPE  = {0}".format(self.device_type))
            self.log.info("PRODUCT CODE = {0}".format(self.product_code))
            self.log.info("REVISION     = {0}".format(self.revision))
            self.log.info("STATUS       = {0}".format(self.status))
            self.log.info("SERIAL       = {0}".format(self.serial))
            self.log.info("PRODUCT NAME = {0}".format(self.product_name))

        except TypeError:
            pass
