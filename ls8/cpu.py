"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU. / ADD THE CONSTRUCTOR TO CPU"""
        # Create memory (256 bits)
        # The LS-8 has 8-bit addressing, so can address 256 bytes of RAM total.
        self.ram = [0] * 256

        # Add properties for other internal registers needed, e.g. reg pc ir

        # 8 general-purpose 8-bit numeric registers R0-R7
        # R5 is reserved as the interrupt mask (IM)
        # R6 is reserved as the interrupt status (IS)
        # R7 is reserved as the stack pointer (SP)
        self.reg = [0] * 8

        self.SP = 7

        self.reg[self.SP] = 0xf4

        # Program Counter (PC)
        # PC: Program Counter, address of the currently executing instruction
        # Keep track of where you are on the memory stack
        self.pc = 0

        # IR: Instruction Register, contains a copy of the currently executing instruction

        # Flag register (FL)
        # Holds the current flags status
        # These flags can change based on the operands given to the CMP opcode
        # The register is made up of 8 bits. If a particular bit is set, that flag is "true".
        '''
        FL bits: 00000LGE
        L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
        G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
        E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwise.
        '''
        self.fl = 0b00000000

        # Used for generic functions for the CPU
        def LDI(operand_a, operand_b):
            self.reg[operand_a] = operand_b
            self.pc += 3

        def PRN(operand_a, operand_b):
            print(f'{self.reg[operand_a]}')
            self.pc += 2

        def PUSH(operand_a, operand_b):
            self.reg[self.SP] -= 1
            reg_num = self.ram[self.pc + 1]
            reg_val = self.reg[reg_num]
            self.ram[self.reg[self.SP]] = reg_val
            self.pc += 2

        def POP(operand_a, operand_b):
            val = self.ram[self.reg[self.SP]]
            reg_num = self.ram[self.pc + 1]
            self.reg[reg_num] = val
            self.reg[self.SP] += 1
            self.pc += 2

        # Calls on ALU

        def MUL(operand_a, operand_b):
            self.alu('MUL', operand_a, operand_b)
            self.pc += 3

        def ADD(operand_a, operand_b):
            self.alu('ADD', operand_a, operand_b)
            self.pc += 3

        def SUB(operand_a, operand_b):
            self.alu('SUB', operand_a, operand_b)
            self.pc += 3

        # Used to stop running CPU

        def HLT(operand_a, operand_b):
            self.running = False

        self.running = True

        self.opcodes = {
            # List of opcodes
            0b10000010: LDI,
            0b01000111: PRN,
            0b00000001: HLT,
            0b10100010: MUL,
            0b10100000: ADD,
            0b10100001: SUB,
            0b01000101: PUSH,
            0b01000110: POP
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        program = []

        f = open(f'examples/{sys.argv[1]}', 'r')

        for i in f.read().split('\n'):
            if i != '' and i[0] != '#':
                x = int(i[:8], 2)
                program.append(x)

        f.close()

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        def ADD(reg_a, reg_b):
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc

        def MUL(reg_a, reg_b):
            self.reg[reg_a] *= self.reg[reg_b]

        def SUB(reg_a, reg_b):
            self.reg[reg_a] -= self.reg[reg_b]

        alu_opcodes = {
            'ADD': ADD,
            'SUB': SUB,
            'MUL': MUL
        }

        alu_op = alu_opcodes[op]

        if alu_op:
            alu_op(reg_a, reg_b)
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    '''
    Inside the CPU, there are two internal registers used for memory operations: 
    the Memory Address Register (MAR) and the Memory Data Register (MDR). 
    The MAR contains the address that is being read or written to. 
    The MDR contains the data that was read or the data to write.
    '''

    # ADD RAM FUNCTIONS

    # Accepts the address to read and return the value stored there.
    def ram_read(self, mar):
        return self.ram[mar]

    # Accepts a value to write, and the address to write it to.
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
        return True

    def run(self):
        """Run the CPU."""

        # Start running the CPU
        while self.running:
            self.trace()
            # Get the first set of instructions
            # Instruction Register (IR)
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # # LDI: register immediate--Set the value of a register to an integer.
            # if ir == ldi:
            #     self.reg[operand_a] = operand_b
            #     self.pc += 3
            # # PRN (register) pseudo-instruction -- Print numeric value stored in the given register. Print to the console the decimal integer value that is stored in the given register.
            # # Some instructions requires up to the next two bytes of data after the PC in memory to perform operations on. Sometimes the byte value is a register number, other times it’s a constant value (in the case of LDI). Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case the instruction needs them.
            # elif ir == prn:
            #     print(f'{self.reg[operand_a]}')
            #     self.pc += 2
            # elif ir == mul:
            #     self.alu('MUL', operand_a, operand_b)
            #     self.pc += 3
            # elif ir == add:
            #     self.alu('ADD', operand_a, operand_b)
            #     self.pc += 3
            # elif ir == sub:
            #     self.alu('SUB', operand_a, operand_b)
            #     self.pc += 3

            # # HLT
            # # Halt the CPU (and exit the emulator).
            # elif ir == hlt:
            #     running = False

            opcode = self.opcodes[ir]

            if opcode:
                opcode(operand_a, operand_b)

            else:
                print(f'Unknown command: {ir}')
                sys.exit(1)
