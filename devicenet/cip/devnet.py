# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject, Attribute
from ..link import allocate, release
from ..errors import CipServiceError
from ..convert import bytes_to_integer, integer_to_bytes


# System imports
import logging


##############################################################################################
# DEVICENET OBJECT (0x03)
##############################################################################################


class DeviceNetObject(CipObject):

    """
    The DeviceNet Object is used to provide the configuration and status of a physical attachment to DeviceNet. A
    product must support one (and only one) DeviceNet Object per physical network attachment
    """

    CLASS_ID = 0x03
    CLASS_DESC = "DEVICENET OBJECT"

    instance_attributes = [
            #          | Type    | ID | Name                        | Size
            Attribute('instance', 1,  'mac',                        1),
            Attribute('instance', 2,  'baudrate',                   1),
            Attribute('instance', 3,  'busoff_interrupt',           1),
            Attribute('instance', 4,  'bussoff_counter',            1),
            Attribute('instance', 5,  'alloc_info',                 2),
            Attribute('instance', 6,  'mac_switch_changed',         1),
            Attribute('instance', 7,  'baudrate_switch_changed',    2),
            Attribute('instance', 8,  'mac_switch_value',           1),
            Attribute('instance', 9,  'baudrate_switch_value',      1),
            Attribute('instance', 10, 'quick_connect',              1),
            Attribute('instance', 11, 'safety_network_number',      2),
            Attribute('instance', 12, 'diagnostic_counters',        34),
            Attribute('instance', 13, 'active_node_table',          8),
    ]

    def __init__(self, *args, **kwargs):
        super(DeviceNetObject, self).__init__(class_id=0x03, *args, **kwargs)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

    ##########################################################################################

    @property
    def mac(self):
        try:
            data = self.get_attribute(attrib_id=1)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @mac.setter
    def mac(self, value):
        stream = integer_to_bytes(value, self.get_size("mac"))
        self.set_attribute(attrib_id=1, value=stream)

    ##########################################################################################

    @property
    def baudrate(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @baudrate.setter
    def baudrate(self, value):
        stream = integer_to_bytes(value, self.get_size("baudrate"))
        self.set_attribute(attrib_id=2, value=stream)

    ##########################################################################################

    @property
    def busoff_interrupt(self):
        try:
            data = self.get_attribute(attrib_id=3)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @busoff_interrupt.setter
    def busoff_interrupt(self, value):
        stream = integer_to_bytes(value, self.get_size("busoff_interrupt"))
        self.set_attribute(attrib_id=3, value=stream)

    ##########################################################################################

    @property
    def busoff_counter(self):
        try:
            data = self.get_attribute(attrib_id=4)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @busoff_counter.setter
    def busoff_counter(self, value):
        try:
            stream = integer_to_bytes(value, self.get_size("busoff_counter"))
            self.set_attribute(attrib_id=4, value=stream)
        except CipServiceError:
            pass

    ##########################################################################################

    @property
    def alloc_info(self):
        try:
            data = self.get_attribute(attrib_id=5)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def mac_switch_changed(self):
        try:
            data = self.get_attribute(attrib_id=6)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @mac_switch_changed.setter
    def mac_switch_changed(self, value):
        stream = integer_to_bytes(value, self.get_size("mac_switch_changed"))
        self.set_attribute(attrib_id=6, value=stream)

    ##########################################################################################

    @property
    def baudrate_switch_changed(self):
        try:
            data = self.get_attribute(attrib_id=7)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @baudrate_switch_changed.setter
    def baudrate_switch_changed(self, value):
        stream = integer_to_bytes(value, self.get_size("baudrate_switch_changed"))
        self.set_attribute(attrib_id=7, value=stream)

    ##########################################################################################

    @property
    def mac_switch_value(self):
        try:
            data = self.get_attribute(attrib_id=8)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @mac_switch_value.setter
    def mac_switch_value(self, value):
        stream = integer_to_bytes(value, self.get_size("mac_switch_value"))
        self.set_attribute(attrib_id=8, value=stream)

    ##########################################################################################

    @property
    def baudrate_switch_value(self):
        try:
            data = self.get_attribute(attrib_id=9)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @baudrate_switch_value.setter
    def baudrate_switch_value(self, value):
        stream = integer_to_bytes(value, self.get_size("baudrate_switch_value"))
        self.set_attribute(attrib_id=9, value=stream)

    ##########################################################################################

    def allocate(self, alloc_choice=0x01, alloc_mac=None, wait_time=1):

        alloc_mac = self.src_addr if not alloc_mac else alloc_mac

        result = None
        try:
            result = allocate(
                interface=self.interface,
                src_addr=self.src_addr,
                dst_addr=self.dst_addr,
                data=(alloc_choice, alloc_mac),
                wait_time=wait_time
            )

            if result is not None:
                result = 0

        except CipServiceError as e:
            result = e.code

        finally:
            return result

    ##########################################################################################

    def release(self, alloc_choice=0x01, wait_time=1):

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

        except CipServiceError as e:
            result = e.code

        finally:
            return result

    ##########################################################################################

    def report(self):
        super(DeviceNetObject, self).report()

        try:
            self.log.info("REVISION                 = {0}".format(hex(self.revision)))
            self.log.info("MAC-ID                   = {0}".format(hex(self.mac)))
            self.log.info("BAUDRATE                 = {0}".format(hex(self.baudrate)))
            self.log.info("BUSOFF COUNTER           = {0}".format(self.busoff_counter))
            self.log.info("ALLOC INFO               = {0}".format(self.alloc_info))
            self.log.info("MAC SWITCH CHANGED       = {0}".format(self.mac_switch_changed))
            self.log.info("BAUDRATE SWITCH CHANGED  = {0}".format(self.baudrate_switch_changed))
            self.log.info("MAC SWITCH VALUE         = {0}".format(self.mac_switch_value))
            self.log.info("BAUDRATE SWITCH VALUE    = {0}".format(self.baudrate_switch_value))

        except TypeError:
            pass
