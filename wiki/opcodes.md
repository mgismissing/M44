# Opcodes

## Register management 1

| Opcode | Action | Equivalent in Assembly |
|-|-|-|
| `0x00` | none | `NOP` |
| `0x01aa` | `A` = `aa` | `MOV A, aa` |
| `0x02aa` | `B` = `aa` | `MOV B, aa` |
| `0x03aa` | `C` = `aa` | `MOV C, aa` |
| `0x04aa` | `D` = `aa` | `MOV D, aa` |
| `0x05aaaa` | `A` = `[aaaa]` | `MOV A, [aaaa]` |
| `0x06aaaa` | `B` = `[aaaa]` | `MOV B, [aaaa]` |
| `0x07aaaa` | `C` = `[aaaa]` | `MOV C, [aaaa]` |
| `0x08aaaa` | `D` = `[aaaa]` | `MOV D, [aaaa]` |

## Port management

| Opcode | Action | Equivalent in Assembly |
|-|-|-|
| `0x09aa` | `port(A)` = `aa` | `OUTA aa` |
| `0x0Aaa` | `A` = `port(aa)` | `INA aa` |

## Jumps 1

| Opcode | Action | Equivalent in Assembly |
|-|-|-|
| `0x0Baaaa` | `IP` = `aaaa` | `JMP aaaa` |
| `0x0C` | `IP` = `A:B` | `JMP A:B` |
| `0x0D` | `IP` = `A:B` if `ZF == 1` else `IP` | `JZ A:B` |
| `0x0E` | `IP` = `A:B` if `ZF == 0` else `IP` | `JNZ A:B` |
| `0x0F` | `IP` = `A:B` if `EF == 1` else `IP` | `JE A:B` |

## ALU operations

| Opcode | Action | Equivalent in Assembly |
|-|-|-|
| `0x10` | `C` = `A` AND `B` | `AND` |
| `0x11` | `C` = `A` OR `B` | `OR` |
| `0x12` | `C` = `A` XOR `B` | `XOR` |
| `0x13` | `C` = NOT `A` | `NOT` |
| `0x14` | `C` = `A` >> 1 | `LSR` |
| `0x15` | `C` = `A` << 1 | `LSL` |
| `0x16` | `C` = `A` + `B` | `ADD` |
| `0x17` | `C` = `A` - `B` | `SUB` |
| `0x18` | `C` = `A` * `B` | `MUL` |
| `0x19` | `C` = (`A` - (`A` % `B`)) / `B`, `D` = `A` % `B` | `DIV` |
| `0x1A` | `A` = `A` + 1 | `INCA` |
| `0x1B` | `B` = `B` + 1 | `INCB` |
| `0x1C` | `C` = `C` + 1 | `INCC` |
| `0x1D` | `D` = `D` + 1 | `INCD` |
| `0x1E` | `A` = `A`, `B` = `B` | `CMP A, B` |
| `0x1Faa` | `A` = `A`, `B` = `aa` | `CMP A, aa` |

## Jumps 2

| Opcode | Action | Equivalent in Assembly |
|-|-|-|
| `0x20` | `IP` = `A:B` if `EF == 0` else `IP` | `JNE A:B` |
| `0x21` | `IP` = `A:B` if `LF == 1` else `IP` | `JG A:B` |
| `0x22` | `IP` = `A:B` if `LF == 0` else `IP` | `JLE A:B` |
| `0x23` | `IP` = `A:B` if `LF == 1` or `EF == 1` else `IP` | `JGE A:B` |
| `0x24` | `IP` = `A:B` if `LF == 0` and `EF == 0` else `IP` | `JL A:B` |
| `0x25` | `IP` = `A:B` if `CF == 1` else `IP` | `JC A:B` |
| `0x26` | `IP` = `A:B` if `CF == 0` else `IP` | `JNC A:B` |

## Register management 2

| Opcode | Action | Equivalent in Assembly |
|-|-|-|
| `0xAA` | `A` = `A` | `TAA` |
| `0xAB` | `A` = `B` | `TAB` |
| `0xAC` | `A` = `C` | `TAC` |
| `0xAD` | `A` = `D` | `TAD` |
| `0xBB` | `B` = `B` | `TBB` |
| `0xBC` | `B` = `C` | `TBC` |
| `0xBD` | `B` = `D` | `TBD` |
| `0xCC` | `C` = `C` | `TCC` |
| `0xCD` | `C` = `D` | `TCD` |
| `0xDD` | `D` = `D` | `TDD` |
