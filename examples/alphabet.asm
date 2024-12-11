#include "asm/core.m44"
#include "asm/extra.m44"

mov d, "A"
mov c, "Z"
output:
    tda
    outa 0x01
loop:
    qina 0x01
    cmp a, b
    mov a, (continue & 0xFF00) >> 8
    mov b, (continue & 0xFF)
    jz ab
    jmp loop
continue:
    incd
    tda
    tcb
    cmp a, b
    mov a, (end & 0xFF00) >> 8
    mov b, (end & 0xFF)
    jg ab
    jmp output

end:
    mov a, 0x0A
    outa 0x01
    mov d, 0x40
    jmp loop