# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

# Framework imports
from .base import CipObject

# System imports
import logging


##############################################################################################
# USER OBJECT
##############################################################################################


class DummyObject(CipObject):

    """ Dummy object class used to test specific functionality of the product """

    CLASS_ID = 0xAB
    CLASS_DESC = "USER OBJECT CLASS"

    def __init__(self, *args, **kwargs):
        super(DummyObject, self).__init__(class_id=0xAB, *args, **kwargs)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.addHandler(logging.NullHandler())
