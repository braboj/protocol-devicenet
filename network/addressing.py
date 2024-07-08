# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from ..errors import DevNetGroupError


def can_addr(msg_group, msg_id, mac):
    """Generates valid CAN address based on devicenet message identifier fields

    Parameters:
        msg_group: Message group
        msg_id: Message ID
        mac: Source or Destination MAC

    Returns:
        CAN-ID

    Usage:
        from Components.utils.devnet import can_addr

        can_addr = (msg_group=2, msg_id=4, mac=0)
        # Output is 1038 (0x40C)

    """

    # Perform input check
    if msg_group not in range(1, 5):
        raise DevNetGroupError

    elif msg_group == 1 and msg_id not in range(0, 16):
        raise DevNetGroupError

    elif msg_group == 2 and msg_id not in range(0, 8):
        raise DevNetGroupError

    elif msg_group == 3 and msg_id not in range(0, 7):
        raise DevNetGroupError

    elif msg_id not in range(0, 64):
        raise DevNetGroupError

    elif mac not in range(0, 64):
        raise DevNetGroupError

    # Generate CAN header
    if msg_group == 1:
        can_id = (msg_id << 6) + mac

    elif msg_group == 2:
        can_id = 0x400 + (mac << 3) + msg_id

    elif msg_group == 3:
        can_id = 0x600 + (msg_id << 6) + mac

    elif msg_group == 4:
        can_id = 0x7C0 + msg_id

    else:
        raise DevNetGroupError

    return can_id


def devnet_addr(can_id):
    """ Generates devicenet identifiers from CAN-ID

    Parameters:
        can_id: CAN identifier from the CAN frame

    Returns:
        tuple(msg_group, msg_id, mac)

    Usage:
        from Components.utils.devnet import devnet_addr

        output = devnet_addr(can_id=0x40B)
        # Output is (2, 3, 1) -> Group 2, Message-ID 3, Source MAC 1
    """

    group_id = 0
    message_id = 0
    mac = 0

    # Volume 3, p. 2-4
    group_01 = set(range(0, 0x400))
    group_02 = set(range(0x400, 0x600))
    group_03 = set(range(0x600, 0x7C0))
    group_04 = set(range(0x7C0, 0x7F0))

    # Parse message group
    if can_id in group_01:
        group_id = 1

    elif can_id in group_02:
        group_id = 2

    elif can_id in group_03:
        group_id = 3

    elif can_id in group_04:
        group_id = 4

    # Parse message-id and MAC address
    if group_id == 1:
        message_id = (can_id & 0x3C0) >> 6
        mac = (can_id & 0x03F)

    elif group_id == 2:
        message_id = (can_id & 0x007)
        mac = (can_id & 0x1F8) >> 3

    elif group_id == 3:
        message_id = (can_id & 0x1C0) >> 6
        mac = (can_id & 0x03F)

    elif group_id == 4:
        message_id = (can_id & 0x03F)

    return group_id, message_id, mac


def main():
    # Address used by master for explicit request message (MAC is destination address)
    output = can_addr(msg_group=2, msg_id=4, mac=1)
    assert output == 0x40C

    # Address used by slave to respond to explicit requests (MAC is source address)
    devnet_id = devnet_addr(0x40B)
    assert devnet_id == (2, 3, 1)

    print("#"*80)
    print(can_addr.__doc__)
    print("#"*80)
    print(devnet_addr.__doc__)
    print("#"*80)


if __name__ == "__main__":
    main()
