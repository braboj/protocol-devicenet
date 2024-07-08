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

class MessageRouterObject(CipObject):

    """ Message Router Class

    The Message Router Object provides a messaging connection point through which a Client
    may address a service to any object class or instance residing in the physical device.

    Instance Attributes
        1. Structure of supported classes and the supported instances of these classes
        2. Maximum number of connections
        3. Number of connections currently used
        4. A list of the connection ID's of the currently active connections

    """

    CLASS_ID = 0x02
    CLASS_DESC = "MESSAGE ROUTER"

    instance_attributes = [
            #          | Type    | ID | Name                | Size
            Attribute('instance', 2,  'available',        2),
    ]

    def __init__(self, *args, **kwargs):
        super(MessageRouterObject, self).__init__(class_id=0x02, *args, **kwargs)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

    ##########################################################################################

    @property
    def num_available(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except CipError:
            data = None

        return data

    ##########################################################################################

    def report(self):
        super(MessageRouterObject, self).report()

        try:
            self.log.info("CONNECTIONS AVAILABLE    = {0}".format(self.num_available))

        except TypeError:
            pass
