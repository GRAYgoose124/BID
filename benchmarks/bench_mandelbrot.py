#!/usr/bin/env python3
"""
Mandelbrot benchmark - the real test of BF compiler performance
"""

import subprocess
import time
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bid.compiler.languages.c import BfToC
from bid.compiler.languages.optimized_c import BfToOptimizedC


def load_bf(path):
    with open(path) as f:
        content = f.read()
    # Remove comments (lines starting with anything but BF commands)
    lines = content.split('\n')
    bf_chars = set('+-<>[].,')
    result = []
    for line in lines:
        # Keep only BF commands
        result.append(''.join(c for c in line if c in bf_chars))
    return ''.join(result)


def compile_and_time(name, c_code):
    """Compile C code and time its execution"""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, f"{name}.c")
        binary_path = os.path.join(tmpdir, name)
        output_path = os.path.join(tmpdir, f"{name}.output")
        
        # Write source
        with open(source_path, 'w') as f:
            f.write(c_code)
        
        print(f"Compiling {name}...")
        compile_result = subprocess.run(
            ['gcc', '-O3', '-march=native', source_path, '-o', binary_path],
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode != 0:
            print(f"Compilation failed: {compile_result.stderr}")
            return None, None
        
        print(f"Running {name}...")
        start = time.time()
        with open(output_path, 'w') as output_file:
            run_result = subprocess.run(
                [binary_path],
                stdout=output_file,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120
            )
        elapsed = time.time() - start
        
        if run_result.returncode != 0:
            print(f"Runtime error: {run_result.stderr}")
            return None, None
        
        # Read output
        with open(output_path) as f:
            output = f.read()
        
        return elapsed, output


def main():
    bf_path = Path(__file__).parent.parent / "programs" / "mandelbrot.bf"
    print(f"Loading {bf_path}...")
    bf_source = load_bf(bf_path)
    print(f"BF source: {len(bf_source)} commands")
    
    print("\n" + "="*60)
    print("MANDELBROT BENCHMARK")
    print("="*60)
    
    # Generate unoptimized C
    print("\nGenerating unoptimized C...")
    compiler_unopt = BfToC()
    c_unopt = compiler_unopt.compile(bf_source, clean=True)
    print(f"Unoptimized C: {len(c_unopt)} chars")
    
    # Generate optimized C
    print("\nGenerating optimized C...")
    compiler_opt = BfToOptimizedC()
    c_opt = compiler_opt.compile(bf_source)
    print(f"Optimized C: {len(c_opt)} chars")
    print(f"Size reduction: {(1 - len(c_opt)/len(c_unopt))*100:.1f}%")
    
    # Benchmark unoptimized
    time_unopt, output_unopt = compile_and_time("mandelbrot_unopt", c_unopt)
    
    # Benchmark optimized
    time_opt, output_opt = compile_and_time("mandelbrot_opt", c_opt)
    
    # Print results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    if time_unopt:
        print(f"Unoptimized C:  {time_unopt:.3f} seconds")
    if time_opt:
        print(f"Optimized C:    {time_opt:.3f} seconds")
    
    if time_unopt and time_opt:
        speedup = time_unopt / time_opt
        print(f"\nSpeedup: {speedup:.2f}x faster")
        print(f"Time saved: {time_unopt - time_opt:.3f} seconds ({(1-1/speedup)*100:.1f}% faster)")
    
    # Verify outputs match
    if output_unopt and output_opt:
        if output_unopt == output_opt:
            print("\n✓ Output verification: PASSED (outputs match)")
        else:
            print("\n✗ Output verification: FAILED (outputs differ)")
            print(f"Unoptimized output length: {len(output_unopt)}")
            print(f"Optimized output length: {len(output_opt)}")
    
    # Show sample output
    if output_opt:
        print("\nFirst 5 lines of output:")
        lines = output_opt.split('\n')[:5]
        for line in lines:
            print(f"  {line}")


if __name__ == "__main__":
    main()
