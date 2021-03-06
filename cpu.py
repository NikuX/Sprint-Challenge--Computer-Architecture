"""CPU functionality."""

import sys

# Operations
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
HLT = 0b00000001
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
CMP = 0b10100111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.sp = 255
        self.running = False


    def ram_read(self, add_reg):
        return self.ram[add_reg]


    def ram_write(self, add_reg, value):
        self.ram[add_reg] = value


    def load(self):
        """Load a program into memory."""
        program = []

        address = 0

        with open(sys.argv[1]) as f:
            for line in f:
                comment_split = line.split('#')
                num = comment_split[0].strip()
                try:
                    program.append(int(num, 2))
                except ValueError:
                    pass



        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CMP:
            self.E = 0b00000000
            self.G = 0b00000000
            self.L = 0b00000000
            if self.reg[reg_a] == self.reg[reg_b]:
                self.E = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.G = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.L = 0b00000001

        elif op == 'AND':
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == 'OR':
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == 'XOR':
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == 'NOT':
            self.reg[reg_a] = 0b11111111 - self.reg[reg_b]
        elif op == 'NOP':
            self.reg[reg_a] = 0b00000000

        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def jmp(self, operand):
        self.pc = self.reg[operand]


    def jeq(self, operand):
        if self.E == 0b00000001:
            self.pc = self.reg[operand]
        else:
            self.pc += 2


    def jne(self, operand):
        if self.E == 0b00000000:
            self.pc = self.reg[operand]
        else:
            self.pc += 2


    def push(self, operand):
        self.sp = (self.sp - 1) % 255
        self.ram[self.sp] = self.reg[operand]


    def pop(self, operand):
        self.reg[operand] = self.ram[self.sp]
        self.sp = (self.sp + 1) % 255
        return self.sp


    def run(self):
        """Run the CPU."""
        running = True

        while running:
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if self.ram[self.pc] == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif self.ram[self.pc] in [CMP, ADD, MUL]:
                self.alu(self.ram[self.pc], operand_a, operand_b)
                self.pc += 3

            elif self.ram[self.pc] == JMP:
                self.jmp(operand_a)

            elif self.ram[self.pc] == JEQ:
                self.jeq(operand_a)

            elif self.ram[self.pc] == JNE:
                self.jne(operand_a)

            elif self.ram[self.pc] == PUSH:
                self.push(operand_a)

            elif self.ram[self.pc] == POP:
                self.pop(operand_a)

            elif self.ram[self.pc] == PRN:
                print(self.reg[operand_a])
                self.pc += 2

            elif self.ram[self.pc] == HLT:
                running = False
                sys.exit(1)