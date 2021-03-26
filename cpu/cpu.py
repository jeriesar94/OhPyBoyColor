# This class represents the emulated CPU of the Gameboy Color
# All processes relating to the operation of the CPU will be part of this class
# This includes:
# Clock timing,
# Instructions fetch and execute,
# Instructions translation,
# and CPU register and peripherals representation

import time
from cartridge.parser import ROMParser

class RegisterConstants(object):
    HIGH = 0
    LOW = 1

class GameBoyColorCPU(object):
    def __init__(self, game_data):
        #########################################################
        #                                                       #
        #                       Registers                       #
        #                                                       #
        #########################################################
        # 16 Bit Accumulator & Flags Register: [[A: HI], [F: LO]]
        # Flag Register (F: LO 8 bits):
        # [ Z(7) | N(6) | H(5) | C(4) | Not Used(3-0) ]
        self.__AF = [0x00, 0b00000000]
        # 16 Bit BC Register: [[HI], [LO]]
        self.__BC = [0x00, 0x00]
        # 16 Bit DE: [[HI], [LO]]
        self.__DE = [0x00, 0x00]
        # 16 Bit HL: [[HI], [LO]]
        self.__HL = [0x00, 0x00]
        # 16 Bit Stack Pointer Register
        self.__SP = 0x00
        # 16 Bit Program Counter/Pointer Register
        self.__PC = 0x00

        # CPU Frequency (MHz)
        self.__freq_mhz = 8.4
        self.__cpu_time = 1 / (self.__freq_mhz * 1e6)
        self.__ticks = 0
        self.__game_data = game_data
        self.__opcode_table = {
            0x00: self.nop,
            0x01: self.ld_16bit_bc,
            0x02: self.ld_8bit_bc_a,
            0x03: self.inc_16bit_bc,
            0x04: self.inc_8bit_b,
            0x05: self.dec_8bit_b,
            0x06: self.ld_8bit_b_d8,
            0x07: self.rlca,
            0x08: self.ld_16bit_a16_sp,
            0x09: self.add_16bit_hl_bc,
            0x0A: self.ld_8bit_a_bc,
            0x0B: self.dec_16bit_bc,
            0x0C: self.inc_8bit_c,
            0x0D: self.dec_8bit_c,
            0x0E: self.ld_8bit_c_d8,
            0x0F: self.rrca,
            0x10: self.stop,
            0x11: self.ld_16bit_de,
            0x12: self.ld_8bit_de_a,
            0x13: self.inc_16bit_de,
            0x14: self.inc_8bit_d,
            0x15: self.dec_8bit_d,
            0x16: self.ld_8bit_d_d8,
            0x17: self.rla,
            0x18: self.jr_8bit_r8,
            0x19: self.add_16bit_hl_de,
            0x1A: self.ld_8bit_a_de,
            0x1B: self.dec_16bit_de,
            0x1C: self.inc_8bit_e,
            0x1D: self.dec_8bit_e,
            0x1E: self.ld_8bit_e_d8,
            0x1F: self.rra,
            0x20: self.jr_8bit_nz_r8,
            0x21: self.ld_16bit_hl,
            0x22: self.ld_8bit_hli_a,
            0x23: self.inc_16bit_hl,
            0x24: self.inc_8bit_h,
            0x25: self.dec_8bit_h,
            0x26: self.ld_8bit_h_d8
        }

    @property
    def AF(self):
        return self.__AF

    @property
    def BC(self):
        return self.__BC

    @property
    def DE(self):
        return self.__DE

    @property
    def HL(self):
        return self.__HL

    @property
    def SP(self):
        return self.__SP

    @property
    def PC(self):
        return self.__PC

    def nop(self):
        self.__PC += 1
        self.tick(ticks=4)

    def halt(self):
        while True:
            pass

    def stop(self):
        pass

    def rlca(self):
        carry = (self.__AF[RegisterConstants.HIGH] & 0x80) >> 7
        flags = carry << 4
        self.__AF[RegisterConstants.HIGH] = (self.__AF[RegisterConstants.HIGH] << 1) & 0xFF | carry
        self.__AF[RegisterConstants.LOW] = flags
        self.__PC += 1
        self.tick(ticks=4)

    def rla(self):
        carry = (self.__AF[RegisterConstants.LOW] & 0x10) >> 4
        new_carry = (self.__AF[RegisterConstants.HIGH] & 0x80) >> 7
        flags = new_carry << 4
        self.__AF[RegisterConstants.HIGH] = (self.__AF[RegisterConstants.HIGH] << 1) & 0xFF | carry
        self.__AF[RegisterConstants.LOW] = flags
        self.__PC += 1
        self.tick(ticks=4)

    def rrca(self):
        carry = (self.__AF[RegisterConstants.HIGH] & 0x01)
        flags = carry << 4
        self.__AF[RegisterConstants.HIGH] = (self.__AF[RegisterConstants.HIGH] >> 1) | (carry << 7)
        self.__AF[RegisterConstants.LOW] = flags
        self.__PC += 1
        self.tick(ticks=4)

    def rra(self):
        carry = (self.__AF[RegisterConstants.LOW] & 0x10) >> 4
        new_carry = (self.__AF[RegisterConstants.HIGH] & 0x01)
        flags = new_carry << 4
        self.__AF[RegisterConstants.HIGH] = (self.__AF[RegisterConstants.HIGH] >> 1) | (carry << 7)
        self.__AF[RegisterConstants.LOW] = flags
        self.__PC += 1
        self.tick(ticks=4)

    def jr_8bit_r8(self):
        # Add immediate value to current program counter and jump to address by setting program counter to result
        self.__PC += self.__game_data[self.__PC + 1]
        self.tick(ticks=12)

    def jr_8bit_nz_r8(self):
        # Check conditional NZ: If Z is reset, add immediate value to current PC and jump to address
        # Add immediate value to current program counter and jump to address by setting program counter to result
        if not (self.__AF[RegisterConstants.LOW] & 0x80):
            self.__PC += self.__game_data[self.__PC + 1]
            self.tick(ticks=12)
        else:
            self.tick(ticks=8)

    def add_16bit_hl_bc(self):
        val_hl = (self.__HL[RegisterConstants.HIGH] << 8) + self.__HL[RegisterConstants.LOW]
        val_bc = (self.__BC[RegisterConstants.HIGH] << 8) + self.__BC[RegisterConstants.LOW]
        bit_11_carry = ((val_hl & 0x0FFF) + (val_bc & 0x0FFF)) >> 12
        val_hl += val_bc
        bit_15_carry = val_hl >> 16
        val_hl &= 0xFFFF
        self.__HL[RegisterConstants.HIGH] = val_hl >> 8
        self.__HL[RegisterConstants.LOW] = val_hl & 0xFF
        flags = 0b00000000 | bit_11_carry << 5 | bit_15_carry << 4
        self.__AF[RegisterConstants.LOW] = flags
        self.__PC += 1
        self.tick(ticks=8)

    def add_16bit_hl_de(self):
        val_hl = (self.__HL[RegisterConstants.HIGH] << 8) + self.__HL[RegisterConstants.LOW]
        val_de = (self.__DE[RegisterConstants.HIGH] << 8) + self.__DE[RegisterConstants.LOW]
        bit_11_carry = ((val_hl & 0x0FFF) + (val_de & 0x0FFF)) >> 12
        val_hl += val_de
        bit_15_carry = val_hl >> 16
        val_hl &= 0xFFFF
        self.__HL[RegisterConstants.HIGH] = val_hl >> 8
        self.__HL[RegisterConstants.LOW] = val_hl & 0xFF
        flags = 0b00000000 | bit_11_carry << 5 | bit_15_carry << 4
        self.__AF[RegisterConstants.LOW] = flags
        self.__PC += 1
        self.tick(ticks=8)

    def ld_8bit_a_bc(self):
        # Load data stored in memory address stored in BC to A
        memory_location = (self.__BC[RegisterConstants.HIGH] << 8) + self.__BC[RegisterConstants.LOW]
        # TODO: Set memory location specified by BC to value in A when memory module is supported
        self.__PC += 1
        self.tick(ticks=8)

    def ld_8bit_a_de(self):
        # Load data stored in memory address stored in DE to A
        memory_location = (self.__DE[RegisterConstants.HIGH] << 8) + self.__DE[RegisterConstants.LOW]
        # TODO: Set memory location specified by DE to value in A when memory module is supported
        self.__PC += 1
        self.tick(ticks=8)

    def ld_8bit_bc_a(self):
        # Load A into memory address stored in BC
        memory_location = (self.__BC[RegisterConstants.HIGH] << 8) + self.__BC[RegisterConstants.LOW]
        # TODO: Set memory location specified by BC to value in A when memory module is supported
        self.__PC += 1
        self.tick(ticks=8)

    def ld_8bit_de_a(self):
        # Load A into memory address stored in DE
        memory_location = (self.__DE[RegisterConstants.HIGH] << 8) + self.__DE[RegisterConstants.LOW]
        # TODO: Set memory location specified by DE to value in A when memory module is supported
        self.__PC += 1
        self.tick(ticks=8)

    def ld_8bit_hli_a(self):
        # Load A into memory address stored in HL and increment HL
        memory_location = (self.__HL[RegisterConstants.HIGH] << 8) + self.__HL[RegisterConstants.LOW]
        # TODO: Set memory location specified by HL to value in A when memory module is supported
        val = memory_location + 1
        val &= 0xFFFF
        self.__HL[RegisterConstants.HIGH] = val >> 8
        self.__HL[RegisterConstants.LOW] = val & 0xFF
        self.__PC += 1
        self.tick(ticks=8)

    def ld_8bit_b_d8(self):
        self.__BC[RegisterConstants.HIGH] = self.__game_data[self.__PC + 1]
        self.__PC += 2
        self.tick(ticks=8)

    def ld_8bit_c_d8(self):
        self.__BC[RegisterConstants.LOW] = self.__game_data[self.__PC + 1]
        self.__PC += 2
        self.tick(ticks=8)

    def ld_8bit_d_d8(self):
        self.__DE[RegisterConstants.HIGH] = self.__game_data[self.__PC + 1]
        self.__PC += 2
        self.tick(ticks=8)

    def ld_8bit_e_d8(self):
        self.__DE[RegisterConstants.LOW] = self.__game_data[self.__PC + 1]
        self.__PC += 2
        self.tick(ticks=8)

    def ld_8bit_h_d8(self):
        self.__HL[RegisterConstants.HIGH] = self.__game_data[self.__PC + 1]
        self.__PC += 2
        self.tick(ticks=8)

    def ld_16bit_bc(self):
        self.__BC[RegisterConstants.HIGH] = self.__game_data[self.__PC + 1]
        self.__BC[RegisterConstants.LOW] = self.__game_data[self.__PC + 2]
        self.__PC += 3
        self.tick(ticks=12)

    def ld_16bit_de(self):
        self.__DE[RegisterConstants.HIGH] = self.__game_data[self.__PC + 1]
        self.__DE[RegisterConstants.LOW] = self.__game_data[self.__PC + 2]
        self.__PC += 3
        self.tick(ticks=12)

    def ld_16bit_hl(self):
        self.__HL[RegisterConstants.HIGH] = self.__game_data[self.__PC + 1]
        self.__HL[RegisterConstants.LOW] = self.__game_data[self.__PC + 2]
        self.__PC += 3
        self.tick(ticks=12)

    def ld_16bit_a16_sp(self):
        memory_location = (self.__game_data[self.__PC + 1] << 8) + self.__game_data[self.__PC + 2]
        # TODO: Set memory location specified by immediate value to value in SP when memory module is supported
        self.__PC += 3
        self.tick(ticks=20)

    def inc_8bit_b(self):
        self.__BC[RegisterConstants.HIGH] += 1
        self.__BC[RegisterConstants.HIGH] &= 0xFF
        self.__PC += 1
        flags = 0b00000000
        flags = flags | 0x80 if self.__BC == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def inc_8bit_c(self):
        self.__BC[RegisterConstants.LOW] += 1
        self.__BC[RegisterConstants.LOW] &= 0xFF
        self.__PC += 1
        flags = 0b00000000
        flags = flags | 0x80 if self.__BC == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def inc_8bit_d(self):
        self.__DE[RegisterConstants.HIGH] += 1
        self.__DE[RegisterConstants.HIGH] &= 0xFF
        self.__PC += 1
        flags = 0b00000000
        flags = flags | 0x80 if self.__DE == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def inc_8bit_e(self):
        self.__DE[RegisterConstants.LOW] += 1
        self.__DE[RegisterConstants.LOW] &= 0xFF
        self.__PC += 1
        flags = 0b00000000
        flags = flags | 0x80 if self.__DE == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def inc_8bit_h(self):
        self.__HL[RegisterConstants.HIGH] += 1
        self.__HL[RegisterConstants.HIGH] &= 0xFF
        self.__PC += 1
        flags = 0b00000000
        flags = flags | 0x80 if self.__HL == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def inc_16bit_bc(self):
        val = (self.__BC[RegisterConstants.HIGH] << 8) + self.__BC[RegisterConstants.LOW] + 1
        val &= 0xFFFF
        self.__BC[RegisterConstants.HIGH] = val >> 8
        self.__BC[RegisterConstants.LOW] = val & 0xFF
        self.__PC += 1
        self.tick(ticks=8)

    def inc_16bit_de(self):
        val = (self.__DE[RegisterConstants.HIGH] << 8) + self.__DE[RegisterConstants.LOW] + 1
        val &= 0xFFFF
        self.__DE[RegisterConstants.HIGH] = val >> 8
        self.__DE[RegisterConstants.LOW] = val & 0xFF
        self.__PC += 1
        self.tick(ticks=8)

    def inc_16bit_hl(self):
        val = (self.__HL[RegisterConstants.HIGH] << 8) + self.__HL[RegisterConstants.LOW] + 1
        val &= 0xFFFF
        self.__HL[RegisterConstants.HIGH] = val >> 8
        self.__HL[RegisterConstants.LOW] = val & 0xFF
        self.__PC += 1
        self.tick(ticks=8)

    def dec_8bit_b(self):
        self.__BC[RegisterConstants.HIGH] -= 1
        self.__BC[RegisterConstants.HIGH] &= 0xFF
        self.__PC += 1
        flags = 0b01000000
        flags = flags | 0x80 if self.__BC == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def dec_8bit_c(self):
        self.__BC[RegisterConstants.LOW] -= 1
        self.__BC[RegisterConstants.LOW] &= 0xFF
        self.__PC += 1
        flags = 0b01000000
        flags = flags | 0x80 if self.__BC == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def dec_8bit_d(self):
        self.__DE[RegisterConstants.HIGH] -= 1
        self.__DE[RegisterConstants.HIGH] &= 0xFF
        self.__PC += 1
        flags = 0b01000000
        flags = flags | 0x80 if self.__DE == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def dec_8bit_e(self):
        self.__DE[RegisterConstants.LOW] -= 1
        self.__DE[RegisterConstants.LOW] &= 0xFF
        self.__PC += 1
        flags = 0b01000000
        flags = flags | 0x80 if self.__DE == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def dec_8bit_h(self):
        self.__HL[RegisterConstants.HIGH] -= 1
        self.__HL[RegisterConstants.HIGH] &= 0xFF
        self.__PC += 1
        flags = 0b01000000
        flags = flags | 0x80 if self.__HL == 0 else flags & 0x7F
        self.__AF[RegisterConstants.LOW] = flags
        self.tick(ticks=4)

    def dec_16bit_bc(self):
        val = (self.__BC[RegisterConstants.HIGH] << 8) + self.__BC[RegisterConstants.LOW] - 1
        val &= 0xFFFF
        self.__BC[RegisterConstants.HIGH] = val >> 8
        self.__BC[RegisterConstants.LOW] = val & 0xFF
        self.__PC += 1
        self.tick(ticks=8)

    def dec_16bit_de(self):
        val = (self.__DE[RegisterConstants.HIGH] << 8) + self.__DE[RegisterConstants.LOW] - 1
        val &= 0xFFFF
        self.__DE[RegisterConstants.HIGH] = val >> 8
        self.__DE[RegisterConstants.LOW] = val & 0xFF
        self.__PC += 1
        self.tick(ticks=8)

    def tick(self, ticks=1):
        while ticks:
            self.__ticks += 1
            time.sleep(self.__cpu_time)
            ticks -= 1

    def main_loop(self):
        while True:
            op_code = self.__game_data[self.__PC]
            # Stop Operation
            if op_code == 0x10:
                self.__PC += 2
                self.tick(ticks=4)
                break

            self.__opcode_table[op_code]()


if __name__ == '__main__':
    parser = ROMParser(rom_file_path="C:\\Users\\jabedrabbo\\Downloads\\bluepoke\\Pokemon Blue.gb")
    # parser = ROMParser(rom_file_path="C:\\Users\\jabedrabbo\\Downloads\\bluepoke\\Pokemon Green (U) [p1][!].gb")
    # parser = ROMParser(rom_file_path="C:\\Users\\jabedrabbo\\Downloads\\bluepoke\\Super Mario Land (JUE) (V1.1) [!].gb")
    # parser = ROMParser(rom_file_path="C:\\Users\\jabedrabbo\\Downloads\\bluepoke\\Kid Icarus - Of Myths and Monsters (UE) [!].gb")
    # parser = ROMParser(rom_file_path="C:\\Users\\jabedrabbo\\Downloads\\bluepoke\\Game & Watch Gallery (U) (V1.0) [S].gb")
    # parser = ROMParser(rom_file_path="C:\\Users\\jabedrabbo\\Downloads\\bluepoke\\Doraemon (J).gb")
    parser.parse_file()
    cpu = GameBoyColorCPU(parser.game_data)
    cpu.main_loop()
