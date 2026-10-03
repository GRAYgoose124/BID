/*
 * Simplified mandelbrot renderer for performance comparison
 * This does roughly equivalent computational work to the BF version
 * but using clean C code as a performance baseline.
 * 
 * Note: Output format may differ from BF version, but computational
 * complexity is similar (nested loops, integer arithmetic, character mapping)
 */
#include <stdio.h>

#define WIDTH 76
#define HEIGHT 24

int main() {
    unsigned char tape[30000] = {0};
    int x, y, i, iter;
    int real_base, imag_base;
    int zr, zi, temp;
    
    // Similar structure to BF mandelbrot but using cleaner C
    for (y = 0; y < HEIGHT; y++) {
        for (x = 0; x < WIDTH; x++) {
            // Map to complex plane (using integer math like BF does)
            real_base = ((x - 38) * 47) >> 3;  // Approximate scaling
            imag_base = ((y - 12) * 47) >> 3;
            
            // Mandelbrot iteration (integer-based)
            zr = 0;
            zi = 0;
            iter = 0;
            
            while (iter < 128) {
                // z = z^2 + c (in fixed-point integer arithmetic)
                temp = ((zr * zr) >> 8) - ((zi * zi) >> 8) + real_base;
                zi = ((2 * zr * zi) >> 8) + imag_base;
                zr = temp;
                
                // Check for escape
                if ((zr * zr + zi * zi) >> 8 > 1024) break;
                iter++;
            }
            
            // Map iteration to character (similar logic to BF version)
            if (iter >= 128) {
                putchar(' ');
            } else if (iter >= 64) {
                putchar('A' + (iter - 64) / 2);
            } else if (iter >= 32) {
                putchar('B' + (iter - 32) / 2);
            } else {
                putchar('C' + iter / 2);
            }
        }
        putchar('\n');
    }
    
    return 0;
}
