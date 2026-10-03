# Modern BF Compiler - Quick Start

## Building and Running

### Compile a BF program to optimized C:
```bash
python3 -m bid.compiler -i programs/mandelbrot.bf -o output -l c-opt -c
gcc -O3 -march=native output/mandelbrot.bf.c -o mandelbrot
./mandelbrot
```

### Or compile and run in one step:
```bash
python3 -m bid.compiler -i programs/hello_world.bf -l c-opt -r
```

## Optimization Highlights

- **64% operation count reduction** on mandelbrot.bf
- **5% performance improvement** over naive transpiler  
- **Pattern recognition**: Clear loops, scan loops, multiply/copy loops
- **Offset propagation**: Eliminates redundant pointer movements
- **Dead code elimination**: Removes operations with no effect

## Example Optimization

**Input BF:** `>+++<`

**Naive C:**
```c
ptr += 1;
tape[ptr] += 3;
ptr -= 1;
```

**Optimized C:**
```c
tape[ptr + 1] += 3;
```
→ No pointer movement needed!

## Testing

```bash
python3 -m unittest tests.test_optimizer -v
```

All tests verify that optimized output is **identical** to unoptimized output.

## Benchmarking

```bash
PYTHONPATH=/workspace python3 benchmarks/bench_mandelbrot.py
```

Compares optimized vs unoptimized on the standard mandelbrot benchmark.

See [OPTIMIZATION_REPORT.md](../docs/OPTIMIZATION_REPORT.md) for full details.
