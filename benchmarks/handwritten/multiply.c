/*
 * Handwritten C equivalent of BF program: +++[->+++++<]>.
 * This multiplies 3 * 5 to produce character 15.
 */
#include <stdio.h>

int main() {
    unsigned char tape[30000] = {0};
    unsigned int ptr = 0;
    
    // +++
    tape[ptr] = 3;
    
    // [->+++++<]
    while (tape[ptr]) {
        tape[ptr + 1] += 5;
        tape[ptr]--;
    }
    
    // >.
    ptr++;
    putchar(tape[ptr]);
    
    return 0;
}
