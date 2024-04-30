import decoder

class if_id_register:
    def __init__(self):
        self.instruction = 0
        self.pc = 0

class id_ex_register:
    def __init__(self):
        self.rs1 = 0
        self.rs2 = 0
        self.rd = 0
        self.imm = 0
        self.control_signals = {
            'RegWrite': 0,
            'Branch': 0,
            'ALUSrc': 0,
            'MemWrite': 0,
            'MemtoReg': 0,
            'MemRead': 0,
            'Jump': 0
        }

class ex_mem_register:
    def __init__(self):
        self.ALU_result = 0
        self.branch_target = 0
        self.zero_flag = 0
        self.rd = 0
        self.control_signals = {
            'RegWrite': 0,
            'Branch': 0,
            'MemWrite': 0,
            'MemtoReg': 0,
            'MemRead': 0,
            'Jump': 0
        }

class mem_wb_register:
    def __init__(self):
        self.read_data = 0
        self.ALU_result = 0
        self.rd = 0
        self.control_signals = {
            'RegWrite': 0,
            'MemtoReg': 0,
            'MemRead': 0,
            'Jump': 0
        }

# Initialize pipeline stage registers
if_id = if_id_register()
id_ex = id_ex_register()
ex_mem = ex_mem_register()
mem_wb = mem_wb_register()

def Fetch():
    global if_id, pc, lines, instruction
    # Read instruction from program text file based on pc value
    next_pc = pc + 4
    pc = next_pc
    if_id.pc = pc
    
    line_number = int(pc/4) - 1
    if_id.instruction = lines[line_number]
    total_clock_cycles += 1

def Decode():
    global if_id, id_ex, opcode, rd, rs1, rs2, imm, funct3, funct7
    # Extract opcode and operands from instruction in if_id
    instruction = if_id.instruction
    opcode, rd, rs1, rs2, imm, funct3, funct7 = decoder.decoder(instruction)

    # Buffer control signals in id_ex
    id_ex.opcode = opcode
    id_ex.rd = rd
    id_ex.rs1 = rs1
    id_ex.rs2 = rs2
    id_ex.imm = imm
    id_ex.funct3 = funct3
    id_ex.funct7 = funct7
    
    total_clock_cycles += 1

def Execute():
    global id_ex, ex_mem, total_clock_cycles
    # Perform ALU operation based on control signals and operands in id_ex
    # Buffer results in ex_mem
    ex_mem.ALU_result = id_ex.rs1 + id_ex.imm
    total_clock_cycles += 1

def Mem():
    global ex_mem, mem_wb, total_clock_cycles, d_mem
    # Perform memory read/write based on control signals in ex_mem
    # Buffer results in mem_wb
    mem_wb.read_data = d_mem[ex_mem.ALU_result]
    total_clock_cycles += 1

def Writeback():
    global mem_wb, total_clock_cycles
    # Write back result to register file based on control signals in mem_wb
    total_clock_cycles += 1

def ControlUnit():
    # Control signals
    global RegWrite, Branch, MemWrite, MemtoReg, MemRead, Jump, ALUSrc
    global alu_ctrl, opcode, funct3, funct7

    RegWrite = 0
    MemRead = 0
    MemWrite = 0
    MemtoReg = 0
    Branch = 0
    ALUSrc = 0
    alu_ctrl = 0
    Jump = 0

    if opcode == 0b0100011:  # sw
        MemWrite = 1
        ALUSrc = 1
        MemtoReg = 1
        alu_ctrl = 0b0010  # add 
    
    elif opcode == 0b1100011:  # beq
        Branch = 1
        alu_ctrl = 0b0110  # ALU: sub
    
    elif opcode == 0b0000011:  # lw
        MemRead = 1
        ALUSrc = 1
        RegWrite = 1
        MemtoReg = 1
        alu_ctrl = 0b0010  # ALU: add

    elif opcode == 0b0010011: # I-type
        RegWrite = 1
        ALUSrc = 1
        MemtoReg = 1
        if funct3 == 0b000: # addi
            alu_ctrl = 0b0010  # ALU: add
        elif funct3 == 0b110: # ori
            alu_ctrl = 0b0001  # ALU: OR
        elif funct3 == 0b111: # andi
            alu_ctrl = 0b0000  # ALU: AND

    elif opcode == 0b1100111: # jalr
        RegWrite = 1
        ALUSrc = 1
        Jump = 1
        MemtoReg = 1
        alu_ctrl = 0b0010  # ALU: add
    
    elif opcode == 0b0110011:  # R-type
        RegWrite = 1
        if funct7 == 0b0000000:
            if funct3 == 0b000:  # add
                alu_ctrl = 0b0010  # ALU: add
            elif funct3 == 0b110:  # or
                alu_ctrl = 0b0001  # ALU: OR
            elif funct3 == 0b111:  # and
                alu_ctrl = 0b0000  # ALU: AND
        elif funct7 == 0b0100000:
            if funct3 == 0b000:  # sub
                alu_ctrl = 0b0110  # ALU: sub
    
    elif opcode == 0b1101111:  # jal
        RegWrite = 1
        Jump = 1
        alu_ctrl = "NA"

# Main function
def main():
    global pc, lines, instruction, total_clock_cycles

    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, 'r') as file:
        lines = file.readlines()

        # Execute until all instructions finish execution
        while pc < len(lines) * 4:
            # Perform pipeline stages
            Fetch()
            Decode()
            ControlUnit()
            Execute()
            Mem()
            Writeback()

            # Check if the first instruction has finished execution
            if pc >= 4 * len(lines):
                # Print output when the first instruction finishes execution
                print(f"Instruction finished at cycle {total_clock_cycles}")
                break

    print("Program terminated.")

if __name__ == "__main__":
    main()
