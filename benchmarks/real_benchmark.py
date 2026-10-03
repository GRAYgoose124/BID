#!/usr/bin/env python3
"""
Real benchmark comparing generated code to handwritten C equivalents
"""

import subprocess
import time
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bid.compiler.languages.optimized_c import BfToOptimizedC
from bid.compiler.languages.c import BfToC


def load_bf(path):
    with open(path) as f:
        content = f.read()
    bf_chars = set('+-<>[].,')
    return ''.join(c for c in content if c in bf_chars)


def compile_c(c_code, name, optimization="-O3"):
    """Compile C code and return the binary path"""
    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, f"{name}.c")
        binary_path = f"/tmp/bench_{name}"
        
        with open(source_path, 'w') as f:
            f.write(c_code)
        
        result = subprocess.run(
            ['gcc', optimization, '-march=native', source_path, '-o', binary_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Compilation failed: {result.stderr}")
            return None
        
        return binary_path


def time_program(binary_path, runs=3):
    """Run a program multiple times and return best time"""
    times = []
    output = None
    
    for _ in range(runs):
        start = time.time()
        result = subprocess.run(
            [binary_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        elapsed = time.time() - start
        times.append(elapsed)
        output = result.stdout
    
    return min(times), output


def benchmark_program(name, bf_source, handwritten_c_path=None):
    """Benchmark a program: unopt, opt, handwritten"""
    print(f"\n{'='*60}")
    print(f"Benchmark: {name}")
    print(f"BF source: {len(bf_source)} commands")
    print(f"{'='*60}")
    
    results = {}
    
    # Unoptimized C
    print("Generating unoptimized C...")
    compiler_unopt = BfToC()
    c_unopt = compiler_unopt.compile(bf_source, clean=True)
    
    binary_unopt = compile_c(c_unopt, f"{name}_unopt")
    if binary_unopt:
        print("Running unoptimized...")
        time_unopt, output_unopt = time_program(binary_unopt)
        results['unoptimized'] = {'time': time_unopt, 'output': output_unopt}
        print(f"  Time: {time_unopt:.6f}s")
    
    # Optimized C
    print("Generating optimized C...")
    compiler_opt = BfToOptimizedC()
    c_opt = compiler_opt.compile(bf_source)
    
    binary_opt = compile_c(c_opt, f"{name}_opt")
    if binary_opt:
        print("Running optimized...")
        time_opt, output_opt = time_program(binary_opt)
        results['optimized'] = {'time': time_opt, 'output': output_opt}
        print(f"  Time: {time_opt:.6f}s")
    
    # Handwritten C
    if handwritten_c_path and os.path.exists(handwritten_c_path):
        print("Compiling handwritten C...")
        with open(handwritten_c_path) as f:
            c_handwritten = f.read()
        
        binary_hand = compile_c(c_handwritten, f"{name}_hand")
        if binary_hand:
            print("Running handwritten...")
            time_hand, output_hand = time_program(binary_hand)
            results['handwritten'] = {'time': time_hand, 'output': output_hand}
            print(f"  Time: {time_hand:.6f}s")
    
    return results


def main():
    print("="*60)
    print("REAL PERFORMANCE BENCHMARK")
    print("Comparing generated C to handwritten C equivalents")
    print("="*60)
    
    all_results = {}
    
    # Benchmark 1: Simple multiply
    bf_multiply = "+++[->+++++<]>."
    results = benchmark_program(
        "multiply",
        bf_multiply,
        "benchmarks/handwritten/multiply.c"
    )
    all_results['multiply'] = results
    
    # Benchmark 2: Hello World
    bf_hello = load_bf("programs/hello_world.bf")
    results = benchmark_program(
        "hello_world",
        bf_hello,
        "benchmarks/handwritten/hello_world.c"
    )
    all_results['hello_world'] = results
    
    # Benchmark 3: Mandelbrot (no handwritten yet)
    bf_mandel = load_bf("programs/mandelbrot.bf")
    results = benchmark_program(
        "mandelbrot",
        bf_mandel,
        None
    )
    all_results['mandelbrot'] = results
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'Program':<15} {'Unopt (s)':<12} {'Opt (s)':<12} {'Hand (s)':<12} {'Gap':<10}")
    print("-"*70)
    
    for name, results in all_results.items():
        unopt_time = results.get('unoptimized', {}).get('time', 0)
        opt_time = results.get('optimized', {}).get('time', 0)
        hand_time = results.get('handwritten', {}).get('time')
        
        if hand_time:
            gap = opt_time / hand_time
            gap_str = f"{gap:.2f}x slower"
        else:
            gap_str = "N/A"
        
        print(f"{name:<15} {unopt_time:>11.6f} {opt_time:>11.6f} "
              f"{hand_time if hand_time else 'N/A':<11} {gap_str:<10}")
    
    # Verify correctness
    print("\n" + "="*70)
    print("CORRECTNESS")
    print("="*70)
    for name, results in all_results.items():
        unopt_out = results.get('unoptimized', {}).get('output', '')
        opt_out = results.get('optimized', {}).get('output', '')
        hand_out = results.get('handwritten', {}).get('output')
        
        match = opt_out == unopt_out
        if hand_out:
            match = match and opt_out == hand_out
        
        status = "✓ PASS" if match else "✗ FAIL"
        print(f"{name:<15} {status}")


if __name__ == "__main__":
    main()
