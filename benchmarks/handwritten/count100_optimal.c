/*
 * Optimal handwritten C for count100
 * Just the essential computation without BF overhead
 */
#include <stdio.h>

int main() {
    for (int i = 0; i < 100; i++) {
        putchar(i);
    }
    return 0;
}
