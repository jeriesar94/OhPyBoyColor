# This class is responsible for parsing gameboy and gameboy color cartridges, it includes the following functions:
# 1. Read binary rom data and store it
# 2. Divide and store ROM data in specified functionality structs (Cartridge headers)

from collections import deque
from cartridge.cartridge_headers import CartridgeInfoStruct
from cartridge.cartridge_headers import HeaderOperations
from cartridge.cartridge_headers import HeaderSize, HeaderMemAddresses


class ROMParser(object):
    def __init__(self, rom_file_path):
        self.__file_path = rom_file_path
        self.__file_data = None
        self.__entry = None
        self.__logo = None
        self.__title = None
        self.__manuf_code = None
        self.__cgb_flag = None
        self.__new_lic_code = None
        self.__sgb_flag = None
        self.__cart_type = None
        self.__rom_size = None
        self.__ram_size = None
        self.__dest_code = None
        self.__old_lic_code = None
        self.__mask_rom_ver = None
        self.__header_chksm = None
        self.__global_chksm = None
        self.__game_data = None

    def parse_file(self):
        with open(self.__file_path, 'rb') as file:
            self.__file_data = file.read()

        self.__entry = self.__file_data[
                       HeaderMemAddresses.ENTRY_POINT: HeaderMemAddresses.ENTRY_POINT + HeaderSize.ENTRY_POINT]
        self.__logo = self.__file_data[HeaderMemAddresses.LOGO: HeaderMemAddresses.LOGO + HeaderSize.LOGO]
        self.__title = self.__file_data[HeaderMemAddresses.TITLE: HeaderMemAddresses.TITLE + HeaderSize.TITLE]
        self.__manuf_code = self.__file_data[
                            HeaderMemAddresses.MANUF_CODE: HeaderMemAddresses.MANUF_CODE + HeaderSize.MANUF_CODE]
        self.__cgb_flag = self.__file_data[
                          HeaderMemAddresses.CGB_FLAG: HeaderMemAddresses.CGB_FLAG + HeaderSize.CGB_FLAG]
        self.__new_lic_code = self.__file_data[
                              HeaderMemAddresses.NEW_LICS_CODE: HeaderMemAddresses.NEW_LICS_CODE + HeaderSize.NEW_LICS_CODE]
        self.__sgb_flag = self.__file_data[
                          HeaderMemAddresses.SGB_FLAG: HeaderMemAddresses.SGB_FLAG + HeaderSize.SGB_FLAG]
        self.__cart_type = self.__file_data[
                           HeaderMemAddresses.CART_TYPE: HeaderMemAddresses.CART_TYPE + HeaderSize.CART_TYPE]
        self.__rom_size = self.__file_data[
                          HeaderMemAddresses.ROM_SIZE: HeaderMemAddresses.ROM_SIZE + HeaderSize.ROM_SIZE]
        self.__ram_size = self.__file_data[
                          HeaderMemAddresses.RAM_SIZE: HeaderMemAddresses.RAM_SIZE + HeaderSize.RAM_SIZE]
        self.__dest_code = self.__file_data[
                           HeaderMemAddresses.DEST_CODE: HeaderMemAddresses.DEST_CODE + HeaderSize.DEST_CODE]
        self.__old_lic_code = self.__file_data[
                              HeaderMemAddresses.OLD_LICS_CODE: HeaderMemAddresses.OLD_LICS_CODE + HeaderSize.OLD_LICS_CODE]
        self.__mask_rom_ver = self.__file_data[
                              HeaderMemAddresses.MASK_ROM_VER_NUM: HeaderMemAddresses.MASK_ROM_VER_NUM + HeaderSize.MASK_ROM_VER_NUM]
        self.__header_chksm = self.__file_data[
                              HeaderMemAddresses.HEADER_CHKSM: HeaderMemAddresses.HEADER_CHKSM + HeaderSize.HEADER_CHKSM]
        self.__global_chksm = self.__file_data[
                              HeaderMemAddresses.GLOBAL_CHKSM: HeaderMemAddresses.GLOBAL_CHKSM + HeaderSize.GLOBAL_CHKSM]
        self.__game_data = self.__file_data[HeaderMemAddresses.GLOBAL_CHKSM + HeaderSize.GLOBAL_CHKSM + 1:]

    @property
    def entry(self):
        return self.__entry

    @property
    def logo(self):
        return self.__logo

    @property
    def title(self):
        return self.__title

    @property
    def manufacture_code(self):
        return self.__manuf_code

    @property
    def cgb(self):
        return self.__cgb_flag

    @property
    def new_license_code(self):
        return self.__new_lic_code

    @property
    def sgb(self):
        return self.__sgb_flag

    @property
    def cart_type(self):
        return self.__cart_type

    @property
    def rom_size(self):
        return self.__rom_size

    @property
    def ram_size(self):
        return self.__ram_size

    @property
    def destination(self):
        return self.__dest_code

    @property
    def old_license_code(self):
        return self.__old_lic_code

    @property
    def mask_rom_version(self):
        return self.__mask_rom_ver

    @property
    def header_checksum(self):
        return self.__header_chksm

    @property
    def global_checksum(self):
        return self.__global_chksm

    @property
    def game_data(self):
        return self.__game_data
