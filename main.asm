#include "asm/core.m44"
#include "asm/extra.m44"

print_char: ; A: char
    .start:
        outa 0x01
    .check:
        qina 0x01
        cmp a, b
        mova .end
        jz ab
        jmp .check
    .end:
        ;ret

print_string: ; AB: address
