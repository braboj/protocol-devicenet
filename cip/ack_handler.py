# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from .base import CipObject, Attribute
from ..errors import CipServiceError
from ..convert import bytes_to_integer, integer_to_bytes

# System imports
import logging


##############################################################################################
# ACKNOWLEDGE HANDLER OBJECT (0x2B)
##############################################################################################

class AcknowledgeHandler(CipObject):

    """
    The Acknowledge Handler Object is used to manage the reception of message acknowledgments. This
    object communicates with a message producing Application Object within a device. The Acknowledge
    Handler Object notifies the producing application of acknowledge reception, acknowledge timeouts,
    and production retry limit.
    """

    CLASS_ID = 0x2B
    CLASS_DESC = "ACKNOWLEDGE HANDLER OBJECT"

    instance_attributes = [
            #          | Type    | ID | Name                        | Size
            Attribute('instance', 1,  'ack_timer',                  2),
            Attribute('instance', 2,  'retry_limit',                1),
            Attribute('instance', 3,  'cos_prod_instance',          2),
            Attribute('instance', 4,  'ack_list_size',              1),
            Attribute('instance', 5,  'ack_list',                   16),
            Attribute('instance', 6,  'ack_path_list_size',         1),
            Attribute('instance', 7,  'ack_path_list',              16),
    ]

    def __init__(self, *args, **kwargs):
        super(AcknowledgeHandler, self).__init__(class_id=0x2B, *args, **kwargs)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

    ##########################################################################################

    @property
    def ack_timer(self):
        try:
            data = self.get_attribute(attrib_id=1)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @ack_timer.setter
    def ack_timer(self, value):
        stream = integer_to_bytes(value, self.get_size("ack_timer"))
        self.set_attribute(attrib_id=1, value=stream)

    ##########################################################################################

    @property
    def retry_limit(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    @retry_limit.setter
    def retry_limit(self, value):
        stream = value
        self.set_attribute(attrib_id=2, value=stream)

    ##########################################################################################

    @property
    def cos_prod_instance(self):
        try:
            data = self.get_attribute(attrib_id=3)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def ack_list_size(self):
        try:
            data = self.get_attribute(attrib_id=4)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def ack_list(self):
        try:
            data = self.get_attribute(attrib_id=5)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def ack_path_list_size(self):
        try:
            data = self.get_attribute(attrib_id=6)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def ack_path_list(self):
        try:
            data = self.get_attribute(attrib_id=7)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    def report(self):
        super(AcknowledgeHandler, self).report()

        try:
            self.log.info("REVISION                 = {0}".format(self.revision))
            self.log.info("ACKNOWLEDGE TIMER        = {0}".format(self.ack_timer))
            self.log.info("RETRY LIMIT              = {0}".format(self.retry_limit))
            self.log.info("COS PRODUCING INSTANCE   = {0}".format(self.cos_prod_instance))
            self.log.info("ACK LIST SIZE            = {0}".format(self.ack_list_size))
            self.log.info("ACK LIST                 = {0}".format(self.ack_list))
            self.log.info("ACK PATH LIST SIZE       = {0}".format(self.ack_path_list_size))
            self.log.info("ACK PATH LIST            = {0}".format(self.ack_path_list))

        except TypeError:
            pass
