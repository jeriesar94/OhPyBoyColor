from dataclasses import dataclass, field

from typing import List


class HeaderMemAddresses(object):
    ENTRY_POINT = 0x100
    LOGO = 0x104
    TITLE = 0x134
    MANUF_CODE = 0x13F
    CGB_FLAG = 0x143
    NEW_LICS_CODE = 0x144
    SGB_FLAG = 0x146
    CART_TYPE = 0x147
    ROM_SIZE = 0x148
    RAM_SIZE = 0x149
    DEST_CODE = 0x14A
    OLD_LICS_CODE = 0x14B
    MASK_ROM_VER_NUM = 0x14C
    HEADER_CHKSM = 0x14D
    GLOBAL_CHKSM = 0x14E


class HeaderSize(object):
    ENTRY_POINT = 4
    LOGO = 48
    TITLE = 16
    MANUF_CODE = 4
    CGB_FLAG = 1
    NEW_LICS_CODE = 2
    SGB_FLAG = 1
    CART_TYPE = 1
    ROM_SIZE = 1
    RAM_SIZE = 1
    DEST_CODE = 1
    OLD_LICS_CODE = 1
    MASK_ROM_VER_NUM = 1
    HEADER_CHKSM = 1
    GLOBAL_CHKSM = 2


@dataclass
class CartridgeInfoStruct:
    size: int
    start_addr: int
    data: List[bytes] = field(default_factory=list)


class HeaderOperations(object):
    @staticmethod
    def get_next_header(header_info: CartridgeInfoStruct):
        return header_info.start_addr + header_info.size
