# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject, Attribute
from ..errors import CipServiceError
from ..convert import bytes_to_integer

# System imports
import logging


##############################################################################################
# MODULE AND NETWORK STATUS (0x404)
##############################################################################################


class ModuleNetworkStatus(CipObject):

    """
    The DeviceNet Object is used to provide the configuration and status of a physical attachment to DeviceNet. A
    product must support one (and only one) DeviceNet Object per physical network attachment
    """

    CLASS_ID = 0x404
    CLASS_DESC = "MODULE AND NETWORK STATUS OBJECT"

    instance_attributes = [
            #          | Type    | ID | Name                        | Size
            Attribute('instance', 1,  'module_status',              4),
            Attribute('instance', 2,  'network_status',             4),
    ]

    def __init__(self, *args, **kwargs):
        super(ModuleNetworkStatus, self).__init__(class_id=0x404, *args, **kwargs)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())

        self.attributes.extend(self.instance_attributes)

    ##########################################################################################

    @property
    def module_status(self):
        try:
            data = self.get_attribute(attrib_id=1)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    @property
    def network_status(self):
        try:
            data = self.get_attribute(attrib_id=2)
            data = bytes_to_integer(data)
        except CipServiceError:
            data = None

        return data

    ##########################################################################################

    def report(self):
        super(ModuleNetworkStatus, self).report()

        try:
            self.log.info("MODULE STATUS            = {0}".format(hex(self.module_status)))
            self.log.info("NETWORK STATUS           = {0}".format(hex(self.network_status)))

        except TypeError:
            pass
