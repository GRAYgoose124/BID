/*
 * Handwritten C equivalent of count100.bf
 * Outputs 100 characters starting from 0
 */
#include <stdio.h>

int main() {
    unsigned char tape[30000] = {0};
    unsigned int ptr = 0;
    
    // Set cell 1 to 100
    tape[1] = 100;
    
    // Loop 100 times
    ptr = 1;
    while (tape[ptr]) {
        putchar(tape[ptr]);
        tape[ptr]++;
        tape[ptr-1]--;
        ptr = 0;
        ptr = 1;
    }
    
    return 0;
}
