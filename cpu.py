# Matrix44 [M44] CPU

import typing
import colorama
import time
import argparse
import random
parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
parser.add_argument("-c", "--clock-speed", required=False, type=int, help="run at specified clock speed in hertz (type -1 for stepping)")
parser.add_argument("-d", "--debug", required=False, action="store_true", help="run in debug mode")
args = parser.parse_args()
colorama.init(autoreset=True)

class Logs:
    def info(string: str, end: str = "\n", flush: bool = False) -> None:
        print(f"{colorama.Fore.LIGHTCYAN_EX}▣ {string}", end=end, flush=flush)
    def log(string: str, end: str = "\n", flush: bool = False) -> None:
        print(f"{colorama.Fore.LIGHTGREEN_EX}☑ {string}", end=end, flush=flush)
    def warn(string: str, end: str = "\n", flush: bool = False) -> None:
        print(f"{colorama.Fore.LIGHTYELLOW_EX}⚠ {string}", end=end, flush=flush)

ports_present = False

try:
    import ports
    ports_present = True
except ModuleNotFoundError:
    Logs.warn(f"no \"ports.py\" file has been found.")

if ports_present:
    for port in ports.ports:
        ports.ports[port].__pinit__()

class Bits:
    def get_word(value: int) -> int:
        return value & 0xFFFF
    def get_byte(value: int, part: int = 0) -> int:
        return (value & (0xFF * (16**(part*2)))) >> (part * 8)
    def get_nybble(value: int, part: typing.Literal["low", "high"]) -> int:
        if part == "low":
            return value & 0x0F
        elif part == "high":
            return (value & 0xF0) >> 4
        return 0
    def get_bit(value: int, part: int) -> int:
        return ((value & 0xFF) & (2**part)) >> part
    def word_to_bytes(value: int) -> tuple[int, int]:
        return (Bits.get_byte(value, 1), Bits.get_byte(value, 0))
    def bytes_to_word(value: tuple[int, int]) -> int:
        return value[0] * (16**2) + value[1]

class Memory:
    ram = bytearray(0xFFFF+1) # bytearray spanning from 0x0000 to 0xFFFF filled with zeroes
    def get_ram_at(address: int) -> int:
        return Memory.ram[Bits.get_word(address)]
    def set_ram_at(address: int, value: int) -> None:
        Memory.ram[Bits.get_word(address)] = Bits.get_byte(value)

class Registers:
    a = 0x00
    b = 0x00
    c = 0x00
    d = 0x00
    ipl = 0x00
    iph = 0x00
    f = 0b00000000
    # ZF
    # EF
    # CF
    # LF
    # Reserved
    # Reserved
    # Reserved
    # Reserved

    def get_ip_word() -> int:
        return Bits.bytes_to_word((Registers.iph, Registers.ipl))
    def set_ip_word(value: int) -> None:
        Registers.iph, Registers.ipl = Bits.word_to_bytes(value)
    def get_ip_bytes() -> tuple[int, int]:
        return (Registers.iph, Registers.ipl)
    def set_ip_bytes(value: tuple[int, int]) -> None:
        Registers.iph, Registers.ipl = value
    def set_flag(flag: typing.Literal["ZF", "EF", "CF", "LF"], value: bool) -> None:
        flagn = -1
        match flag:
            case "ZF": flagn = 7
            case "EF": flagn = 6
            case "CF": flagn = 5
            case "LF": flagn = 4
            case _: flagn = -1
        if value:
            Registers.f |= (1 << flagn)
        else:
            Registers.f &= ~(1 << flagn)
    def get_flag(flag: typing.Literal["ZF", "EF", "CF", "LF"]) -> None:
        flagn = 8
        match flag:
            case "ZF": flagn = 7
            case "EF": flagn = 6
            case "CF": flagn = 5
            case "LF": flagn = 4
            case _: flagn = 8
        return (Registers.f & (1 << flagn)) >> flagn
    
class ALU:
    def operation(op: int) -> None:
        global opcode
        match op:
            case 0x0:
                opcode = "AND"
                Registers.c = Registers.a & Registers.b
            case 0x1:
                opcode = "OR"
                Registers.c = Registers.a | Registers.b
            case 0x2:
                opcode = "XOR"
                Registers.c = Registers.a ^ Registers.b
            case 0x3:
                opcode = "NOT"
                Registers.c = Bits.get_byte(~ Registers.a)
            case 0x4:
                opcode = "LSR"
                Registers.c = Registers.a >> 1
            case 0x5:
                opcode = "LSL"
                Registers.c = Registers.a << 1
            case 0x6:
                opcode = "ADD"
                Registers.c = Registers.a + Registers.b
                Registers.set_flag("CF", Registers.c > 0xFF)
                Registers.c = Bits.get_byte(Registers.c)
            case 0x7:
                opcode = "SUB"
                Registers.c = Registers.a + Bits.get_byte(~Registers.b) + 1
                Registers.set_flag("CF", Registers.c > 0xFF)
                Registers.c = Bits.get_byte(Registers.c)
            case 0x8:
                opcode = "MUL"
                Registers.c = Registers.a * Registers.b
                Registers.set_flag("CF", Registers.c > 0xFF)
                Registers.c = Bits.get_byte(Registers.c)
            case 0x9:
                opcode = "DIV"
                try:
                    Registers.c = int((Registers.a - (Registers.a % Registers.b)) / Registers.b)
                    Registers.d = Registers.a % Registers.b
                except ZeroDivisionError:
                    Registers.c = 0xFF
                    Registers.d = 0xFF
            case 0xA:
                opcode = "INCA"
                Registers.a = Registers.a + 1
                Registers.set_flag("CF", Registers.a > 0xFF)
                Registers.a = Bits.get_byte(Registers.a)
            case 0xB:
                opcode = "INCB"
                Registers.b = Registers.b + 1
                Registers.set_flag("CF", Registers.b > 0xFF)
                Registers.b = Bits.get_byte(Registers.b)
            case 0xC:
                opcode = "INCC"
                Registers.c = Registers.c + 1
                Registers.set_flag("CF", Registers.c > 0xFF)
                Registers.c = Bits.get_byte(Registers.c)
            case 0xD:
                opcode = "INCD"
                Registers.d = Registers.d + 1
                Registers.set_flag("CF", Registers.d > 0xFF)
                Registers.d = Bits.get_byte(Registers.d)
            case 0xE:
                opcode = "CMP A, B"
                Registers.a = Bits.get_byte(Registers.a)
                Registers.b = Bits.get_byte(Registers.b)
                Registers.set_flag("ZF", Registers.a == 0)
                Registers.set_flag("EF", Registers.a == Registers.b)
                Registers.set_flag("LF", Registers.b < Registers.a)
            case 0xF:
                opcode = "ALU-???"

class PrintUtils:
    def pad_hex(value: int, chars: int, uppercase: bool = True) -> str:
        string = str(hex(value)).replace("0x", "").rjust(chars, "0")
        return "0x" + (string.upper() if uppercase else string.lower())
    def pad_bin(value: int, chars: int) -> str:
        return "0b" + str(bin(value)).replace("0b", "").rjust(chars, "0")
    def pad_byte(value: int, uppercase: bool = True, display_bits: bool = False) -> str:
        return PrintUtils.pad_bin(value, 8) if display_bits else PrintUtils.pad_hex(value, 2, uppercase)
    def pad_word(value: int, uppercase: bool = True, display_bits: bool = False) -> str:
        return PrintUtils.pad_bin(value, 16) if display_bits else PrintUtils.pad_hex(value, 4, uppercase)

filename = args.file

# Copy the contents of the file to the RAM
with open(filename, "rb") as file:
    readableBuffer = file.read()
    for i, byte in enumerate(readableBuffer):
        if i < 0x10000:
            Memory.set_ram_at(i, byte)
        else:
            Logs.warn(f"input file \"{filename}\" exceeds the maximum RAM size of 65536 bytes (addresses spanning from 0x0000 to 0xFFFF) by {len(readableBuffer)-0x10000} byte{"s" if len(readableBuffer-0x10000) > 1 else ""}")
            break
    if len(readableBuffer) == 0:
        Logs.warn(f"input file \"{filename}\" is empty: the entire RAM is filled with zeroes (0x0000 - 0xFFFF).")
    else:
        Logs.log(f"input file \"{filename}\" copied over to RAM from address {PrintUtils.pad_word(0x0000)} to address {PrintUtils.pad_word(i)}: filled addresses from {PrintUtils.pad_word(i+1)} to {PrintUtils.pad_word(0xFFFF)} with zeroes.")
    
# CPU cycles
opcode = ""
cycles = 0
clock_speed = 0
if args.clock_speed:
    clock_speed = 1 / args.clock_speed
try:
    if ports_present:
        for port in ports.ports:
            ports.ports[port].__pboot__()
    while True:
        # Debug
        print(end=f"┣╸Reading address {PrintUtils.pad_word(Registers.get_ip_word())}: {PrintUtils.pad_byte(Memory.get_ram_at(Registers.get_ip_word()))}", flush=True)

        ai = 1
        match Memory.get_ram_at(Registers.get_ip_word()):
            case 0x00:
                opcode = f"NOP"
            case 0x01:
                opcode = f"MOV A, {PrintUtils.pad_byte(Memory.get_ram_at(Registers.get_ip_word()+1))}"
                Registers.a = Memory.get_ram_at(Registers.get_ip_word()+1)
                ai = 2
            case 0x02:
                opcode = f"MOV B, {PrintUtils.pad_byte(Memory.get_ram_at(Registers.get_ip_word()+1))}"
                Registers.b = Memory.get_ram_at(Registers.get_ip_word()+1)
                ai = 2
            case 0x03:
                opcode = f"MOV C, {PrintUtils.pad_byte(Memory.get_ram_at(Registers.get_ip_word()+1))}"
                Registers.c = Memory.get_ram_at(Registers.get_ip_word()+1)
                ai = 2
            case 0x04:
                opcode = f"MOV D, {PrintUtils.pad_byte(Memory.get_ram_at(Registers.get_ip_word()+1))}"
                Registers.d = Memory.get_ram_at(Registers.get_ip_word()+1)
                ai = 2
            case 0x05:
                opcode = f"MOV A, [{PrintUtils.pad_word(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))}]"
                Registers.a = Memory.get_ram_at(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))
                ai = 3
            case 0x06:
                opcode = f"MOV B, [{PrintUtils.pad_word(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))}]"
                Registers.b = Memory.get_ram_at(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))
                ai = 3
            case 0x07:
                opcode = f"MOV C, [{PrintUtils.pad_word(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))}]"
                Registers.c = Memory.get_ram_at(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))
                ai = 3
            case 0x08:
                opcode = f"MOV D, [{PrintUtils.pad_word(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))}]"
                Registers.d = Memory.get_ram_at(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))
                ai = 3
            case 0x09:
                opcode = f"OUTA {PrintUtils.pad_byte(Registers.get_ip_word()+1)}"
                if ports_present:
                    try:
                        ports.ports[Memory.get_ram_at(Registers.get_ip_word()+1)].port = Bits.get_byte(Registers.a)
                    except KeyError:
                        pass
                ai = 2
            case 0x0A:
                opcode = f"INA {PrintUtils.pad_byte(Memory.get_ram_at(Registers.get_ip_word()+1))}"
                if ports_present:
                    try:
                        Registers.a = Bits.get_byte(ports.ports[Memory.get_ram_at(Registers.get_ip_word()+1)].port)
                        ports.ports[Memory.get_ram_at(Registers.get_ip_word()+1)].port = 0x00
                    except KeyError:
                        Registers.a = random.randint(0x00, 0xFF)
                ai = 2
            case 0x0B:
                opcode = f"JMP {PrintUtils.pad_word(Bits.bytes_to_word((Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2))))}"
                Registers.iph, Registers.ipl = Memory.get_ram_at(Registers.get_ip_word()+1), Memory.get_ram_at(Registers.get_ip_word()+2)
                ai = 0
            case 0x0C:
                opcode = f"JMP A:B"
                Registers.iph, Registers.ipl = Registers.a, Registers.b
                ai = 0
            case 0x0D:
                opcode = f"JZ A:B"
                if Registers.get_flag("ZF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x0E:
                opcode = f"JNZ A:B"
                if not Registers.get_flag("ZF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x0F:
                opcode = f"JE A:B"
                if Registers.get_flag("EF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x10:
                ALU.operation(0x0)
            case 0x11:
                ALU.operation(0x1)
            case 0x12:
                ALU.operation(0x2)
            case 0x13:
                ALU.operation(0x3)
            case 0x14:
                ALU.operation(0x4)
            case 0x15:
                ALU.operation(0x5)
            case 0x16:
                ALU.operation(0x6)
            case 0x17:
                ALU.operation(0x7)
            case 0x18:
                ALU.operation(0x8)
            case 0x19:
                ALU.operation(0x9)
            case 0x1A:
                ALU.operation(0xA)
            case 0x1B:
                ALU.operation(0xB)
            case 0x1C:
                ALU.operation(0xC)
            case 0x1D:
                ALU.operation(0xD)
            case 0x1E:
                ALU.operation(0xE)
            case 0x1F:
                ALU.operation(0xF)
            case 0x20:
                opcode = f"JNE A:B"
                if not Registers.get_flag("EF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x21:
                opcode = f"JG A:B"
                if Registers.get_flag("LF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x22:
                opcode = f"JLE A:B"
                if not Registers.get_flag("LF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x23:
                opcode = f"JGE A:B"
                if Registers.get_flag("LF") or Registers.get_flag("EF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x24:
                opcode = f"JL A:B"
                if (not Registers.get_flag("LF")) and (not Registers.get_flag("EF")):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x25:
                opcode = f"JC A:B"
                if Registers.get_flag("CF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            case 0x26:
                opcode = f"JNC A:B"
                if not Registers.get_flag("CF"):
                    Registers.iph, Registers.ipl = Registers.a, Registers.b
                    ai = 0
            
            case 0xAA:
                opcode = f"TAA"
                Registers.a = Registers.a
            case 0xAB:
                opcode = f"TAB"
                Registers.b = Registers.a
            case 0xAC:
                opcode = f"TAC"
                Registers.c = Registers.a
            case 0xAD:
                opcode = f"TAD"
                Registers.d = Registers.a
            case 0xBA:
                opcode = f"TBA"
                Registers.a = Registers.b
            case 0xBB:
                opcode = f"TBB"
                Registers.b = Registers.b
            case 0xBC:
                opcode = f"TBC"
                Registers.c = Registers.b
            case 0xBD:
                opcode = f"TBD"
                Registers.d = Registers.b
            case 0xCA:
                opcode = f"TCA"
                Registers.a = Registers.c
            case 0xCB:
                opcode = f"TCB"
                Registers.b = Registers.c
            case 0xCC:
                opcode = f"TCC"
                Registers.c = Registers.c
            case 0xCD:
                opcode = f"TCD"
                Registers.d = Registers.c
            case 0xDA:
                opcode = f"TDA"
                Registers.a = Registers.d
            case 0xDB:
                opcode = f"TDB"
                Registers.b = Registers.d
            case 0xDC:
                opcode = f"TDC"
                Registers.c = Registers.d
            case 0xDD:
                opcode = f"TDD"
                Registers.d = Registers.d
                
            case _:
                opcode = f"???"

        print(end=f" \"{opcode}\"\n", flush=True)

        # Debug mode
        if args.debug:
            print(f"┇ [Cycle {str(cycles).rjust(8, "0")}] A: {PrintUtils.pad_byte(Registers.a)} B: {PrintUtils.pad_byte(Registers.b)} C: {PrintUtils.pad_byte(Registers.c)} D: {PrintUtils.pad_byte(Registers.d)} FLAGS: {PrintUtils.pad_byte(Registers.f, display_bits=True)}")
            if ports_present:
                for port in ports.ports:
                    if ports.ports[port].port != 0x00:
                        print(f"┇ Port {PrintUtils.pad_byte(port)} has value {PrintUtils.pad_byte(ports.ports[port].port)}")

        if clock_speed > 0:
            time.sleep(clock_speed)
        elif clock_speed == -1:
            input()
        
        # Tick ports
        
        if ports_present:
            for port in ports.ports:
                ports.ports[port].__ptick__()

        # Prepare to fetch the next instruction
        Registers.set_ip_word(Registers.get_ip_word()+ai)
        cycles += 1
except KeyboardInterrupt:
    Logs.info("program interrupted by user.")
    pass