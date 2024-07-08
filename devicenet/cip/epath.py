# coding=utf-8
##############################################################################################
# Author : Daniel Bodurov
##############################################################################################

# coding: utf-8
from __future__ import print_function
from __future__ import print_function

import pprint

BIT_1 = 1       # 0000 0001
BIT_2 = 2       # 0000 0010
BIT_3 = 4       # 0000 0100
BIT_4 = 8       # 0000 1000
BIT_5 = 16      # 0001 0000
BIT_6 = 32      # 0010 0000
BIT_7 = 64      # 0100 0000
BIT_8 = 128     # 1000 0000


def is_bit_set(byte, bit):
    return True if byte & bit else False


class LogicalSegment(object):

    def get_segment_size(self):
        if self.Reserved != 0 or \
                self.ArrayIndex != 0 or \
                self.IndirectArrayIndex != 0 or \
                self.BitIndex != 0 or \
                self.IndirectBitIndex != 0 or \
                self.StructureMemberNumber != 0 or \
                self.StructureMemberHandle != 0:
            return 3
        else:
            return 2

    # TODO: (@Daniel.Bodurov): Refactor because it is extremely unreadable
    # Use some kind of method for this repetevive checking
    def retrieve_data(self, logic_seg):
        if type(logic_seg) is not LogicalSegment:
            pass

        self.ClassID = logic_seg.ClassID if logic_seg.ClassID != 0 else self.ClassID
        self.InstanceID = logic_seg.InstanceID if logic_seg.InstanceID != 0 else self.InstanceID
        self.MemberID = logic_seg.MemberID if logic_seg.MemberID != 0 else self.MemberID
        self.ConnectionPoint = logic_seg.ConnectionPoint if logic_seg.ConnectionPoint != 0 else self.ConnectionPoint
        self.AttributeID = logic_seg.AttributeID if logic_seg.AttributeID != 0 else self.AttributeID
        self.Special = logic_seg.Special if logic_seg.Special != 0 else self.Special
        self.ServiceID = logic_seg.ServiceID if logic_seg.ServiceID != 0 else self.ServiceID
        self.ExtendedLogical = logic_seg.ExtendedLogical if logic_seg.ExtendedLogical != 0 else self.ExtendedLogical
        self.Reserved = logic_seg.Reserved if logic_seg.Reserved != 0 else self.Reserved
        self.ArrayIndex = logic_seg.ArrayIndex if logic_seg.ArrayIndex != 0 else self.ArrayIndex
        self.IndirectArrayIndex = logic_seg.IndirectArrayIndex if logic_seg.IndirectArrayIndex != 0 else self.IndirectArrayIndex
        self.BitIndex = logic_seg.BitIndex if logic_seg.BitIndex != 0 else self.BitIndex
        self.IndirectBitIndex = logic_seg.IndirectBitIndex if logic_seg.IndirectBitIndex != 0 else self.IndirectBitIndex
        self.StructureMemberNumber = logic_seg.StructureMemberNumber if logic_seg.StructureMemberNumber != 0 else self.StructureMemberNumber
        self.StructureMemberHandle = logic_seg.StructureMemberHandle if logic_seg.StructureMemberHandle != 0 else self.StructureMemberHandle

    def __init__(self, data):

        self.ClassID = 0
        self.InstanceID = 0
        self.MemberID = 0
        self.ConnectionPoint = 0
        self.AttributeID = 0
        self.Special = 0
        self.ServiceID = 0
        self.ExtendedLogical = 0

        self.Reserved = 0
        self.ArrayIndex = 0
        self.IndirectArrayIndex = 0
        self.BitIndex = 0
        self.IndirectBitIndex = 0
        self.StructureMemberNumber = 0
        self.StructureMemberHandle = 0

        if data == "":
            return

        first_byte = data[0]

        logical_value = data[1]

        logical_type = ""  # second three bits
        logical_type += ("1" if is_bit_set(first_byte, BIT_5) else "0")
        logical_type += ("1" if is_bit_set(first_byte, BIT_4) else "0")
        logical_type += ("1" if is_bit_set(first_byte, BIT_3) else "0")

        logical_format = ""  # last two bits
        logical_format += ("1" if is_bit_set(first_byte, BIT_2) else "0")
        logical_format += ("1" if is_bit_set(first_byte, BIT_1) else "0")

        if logical_type == "111":  # Extended Logical Type

            extended_logical_type = data[1]
            logical_value = data[2]

            if extended_logical_type == 0 or extended_logical_type > 6:
                self.Reserved = logical_value

            elif extended_logical_type == 1:
                self.ArrayIndex = logical_value

            elif extended_logical_type == 2:
                self.IndirectArrayIndex = logical_value

            elif extended_logical_type == 3:
                self.BitIndex = logical_value

            elif extended_logical_type == 4:
                self.IndirectBitIndex = logical_value

            elif extended_logical_type == 5:
                self.StructureMemberNumber = logical_value

            elif extended_logical_type == 6:
                self.StructureMemberHandle = logical_value

        elif logical_type == "000":
            self.ClassID = logical_value

        elif logical_type == "001":
            self.InstanceID = logical_value

        elif logical_type == "010":
            self.MemberID = logical_value

        elif logical_type == "011":
            self.ConnectionPoint = logical_value

        elif logical_type == "100":
            self.AttributeID = logical_value

        elif logical_type == "101":
            self.Special = logical_value

        elif logical_type == "110":
            self.ServiceID = logical_value


def _decode_all(data):
    segment_list = []

    while True:
        segment = _decode(data)
        if segment is None:
            break

        segment_list.append(segment)
        data = data[segment.get_segment_size():]

    return segment_list


def _decode(data):

    if len(data) > 0:

        first_byte = data[0]

        if first_byte != 0:

            ftb = ""  # first three bits

            ftb += ("1" if is_bit_set(first_byte, BIT_8) else "0")
            ftb += ("1" if is_bit_set(first_byte, BIT_7) else "0")
            ftb += ("1" if is_bit_set(first_byte, BIT_6) else "0")

            if ftb == "000":
                return 0  # PortSegment(data)
            if ftb == "001":
                return LogicalSegment(data)
            if ftb == "010":
                return 0  # NetworkSegment()
            if ftb == "011":
                return 0  # SymbolicSegment()
            if ftb == "100":
                return 0  # DataSegment()
            if ftb == "101":
                return 0  # DataTypeConstructed()
            if ftb == "110":
                return 0  # DataTypeElementary()
            if ftb == "111":
                return 0  # Reserved


def parse(data):
    objects = _decode_all(data)

    log_seg = LogicalSegment("")

    for s in objects:
        if s.__class__.__name__ is LogicalSegment.__name__:
            log_seg.retrieve_data(s)

    return log_seg


if __name__ == "__main__":

    test_stream = [32, 4, 36, 100, 48, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # test_stream = []
    # test_stream = bytearray([0x2c, 0x61, 0x22, 0x33, 0x2a, 0x11, 0x3e, 0x03, 0x37])

    epath = parse(test_stream)

    p = pprint.PrettyPrinter()
    p.pprint(epath.__dict__)

    print(epath.ClassID)
    print(epath.InstanceID)
    print(epath.AttributeID)
