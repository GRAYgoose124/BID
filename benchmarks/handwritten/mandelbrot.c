/*
 * Handwritten Mandelbrot fractal renderer in C
 * Produces ASCII art similar to the BF version
 * 
 * This is a reference implementation to compare against
 * the BF-compiled version for performance.
 */
#include <stdio.h>

#define WIDTH 76
#define HEIGHT 24
#define MAX_ITER 64

int main() {
    int x, y, i;
    double real, imag, r, im, temp;
    
    for (y = 0; y < HEIGHT; y++) {
        for (x = 0; x < WIDTH; x++) {
            // Map pixel to complex plane
            real = (x - WIDTH/2.0) * 4.0 / WIDTH - 0.5;
            imag = (y - HEIGHT/2.0) * 4.0 / WIDTH;
            
            // Mandelbrot iteration
            r = 0;
            im = 0;
            i = 0;
            
            while (i < MAX_ITER && r*r + im*im < 4.0) {
                temp = r*r - im*im + real;
                im = 2*r*im + imag;
                r = temp;
                i++;
            }
            
            // Map iteration count to ASCII character
            if (i >= MAX_ITER) {
                putchar(' ');
            } else if (i >= 32) {
                putchar('A' + (i - 32));
            } else if (i >= 16) {
                putchar('B' + (i - 16));
            } else {
                putchar('C' + i);
            }
        }
        putchar('\n');
    }
    
    return 0;
}
