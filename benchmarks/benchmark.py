#!/usr/bin/env python3
"""
Benchmark suite for BF compiler

Compares:
1. Unoptimized C transpiler
2. Optimized C transpiler  
3. Handwritten C equivalent
4. Python interpreter (for baseline)
"""

import subprocess
import time
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bid.compiler.languages.c import BfToC
from bid.compiler.languages.optimized_c import BfToOptimizedC
from bid.interpreter import BrainfuckInterpreter


class Benchmark:
    def __init__(self, name, bf_source, handwritten_c=None, expected_output=None):
        self.name = name
        self.bf_source = bf_source
        self.handwritten_c = handwritten_c
        self.expected_output = expected_output
    
    def run(self):
        """Run all benchmark variants"""
        print(f"\n{'='*60}")
        print(f"Benchmark: {self.name}")
        print(f"BF source length: {len(self.bf_source)} chars")
        print(f"{'='*60}")
        
        results = {}
        
        # 1. Python interpreter (baseline)
        print("Running Python interpreter...")
        results['interpreter'] = self.bench_interpreter()
        
        # 2. Unoptimized C
        print("Running unoptimized C transpiler...")
        results['c_unopt'] = self.bench_c_unoptimized()
        
        # 3. Optimized C
        print("Running optimized C compiler...")
        results['c_opt'] = self.bench_c_optimized()
        
        # 4. Handwritten C (if available)
        if self.handwritten_c:
            print("Running handwritten C...")
            results['c_handwritten'] = self.bench_handwritten_c()
        
        self.print_results(results)
        return results
    
    def bench_interpreter(self):
        """Benchmark the Python interpreter"""
        interp = BrainfuckInterpreter(self.bf_source, "", debug=False)
        
        start = time.time()
        try:
            interp.run()
            elapsed = time.time() - start
            output = interp.output_string
            return {'time': elapsed, 'output': output, 'error': None}
        except Exception as e:
            return {'time': None, 'output': None, 'error': str(e)}
    
    def bench_c_unoptimized(self):
        """Benchmark the unoptimized C transpiler"""
        compiler = BfToC()
        c_code = compiler.compile(self.bf_source)
        return self.compile_and_run_c(c_code, "unopt")
    
    def bench_c_optimized(self):
        """Benchmark the optimized C compiler"""
        compiler = BfToOptimizedC()
        c_code = compiler.compile(self.bf_source)
        return self.compile_and_run_c(c_code, "opt")
    
    def bench_handwritten_c(self):
        """Benchmark handwritten C code"""
        return self.compile_and_run_c(self.handwritten_c, "handwritten")
    
    def compile_and_run_c(self, c_code, variant):
        """Compile and run C code, returning timing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, f"prog_{variant}.c")
            binary_path = os.path.join(tmpdir, f"prog_{variant}")
            
            # Write source
            with open(source_path, 'w') as f:
                f.write(c_code)
            
            # Compile with optimizations
            compile_result = subprocess.run(
                ['gcc', '-O3', '-march=native', source_path, '-o', binary_path],
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return {
                    'time': None,
                    'output': None,
                    'error': f"Compilation failed: {compile_result.stderr}"
                }
            
            # Run and time
            start = time.time()
            run_result = subprocess.run(
                [binary_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            elapsed = time.time() - start
            
            if run_result.returncode != 0:
                return {
                    'time': elapsed,
                    'output': run_result.stdout,
                    'error': f"Runtime error: {run_result.stderr}"
                }
            
            return {
                'time': elapsed,
                'output': run_result.stdout,
                'error': None
            }
    
    def print_results(self, results):
        """Print benchmark results in a nice table"""
        print(f"\n{'Variant':<20} {'Time (s)':<12} {'Speedup':<10} {'Status'}")
        print("-" * 60)
        
        baseline_time = results.get('interpreter', {}).get('time')
        
        for variant, result in results.items():
            time_val = result.get('time')
            if time_val is None:
                time_str = "FAILED"
                speedup_str = "-"
                status = result.get('error', 'Unknown error')[:30]
            else:
                time_str = f"{time_val:.6f}"
                if baseline_time and baseline_time > 0:
                    speedup = baseline_time / time_val
                    speedup_str = f"{speedup:.2f}x"
                else:
                    speedup_str = "-"
                
                # Check output correctness
                if self.expected_output and result.get('output') != self.expected_output:
                    status = "WRONG OUTPUT"
                else:
                    status = "✓"
            
            print(f"{variant:<20} {time_str:<12} {speedup_str:<10} {status}")


# Define benchmarks

HELLO_WORLD = Benchmark(
    name="Hello World",
    bf_source="++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.",
    handwritten_c="""
#include <stdio.h>
int main() {
    printf("Hello World!\\n");
    return 0;
}
""",
    expected_output="Hello World!\n"
)

SIMPLE_LOOP = Benchmark(
    name="Simple Loop (count to 10)",
    bf_source="++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.",
    handwritten_c="""
#include <stdio.h>
int main() {
    printf("Hello World!\\n");
    return 0;
}
""",
    expected_output="Hello World!\n"
)

MULTIPLY_TEST = Benchmark(
    name="Multiply Loop Test",
    bf_source="++++++[>++++++++<-]>.",  # 6 * 8 = 48 = '0'
    handwritten_c="""
#include <stdio.h>
int main() {
    putchar(6 * 8);
    return 0;
}
"""
)

# Heavy computation benchmark (small mandelbrot)
COMPUTE_HEAVY = Benchmark(
    name="Compute Heavy (nested loops)",
    bf_source="""
++++[>+++++<-]>[<+++++>-]+<+[
    >[>+>+<<-]++>>[<<+>>-]>>>[-]++>[-]+
    >>>+[[-]++++++>>>]<<<[[<++++++++<++>>-]+<.<[>----<-]<]
    <<[>>>>>[>>>[-]+++++++++<[>-<-]+++++++++>[-[<->-]+[<<<]]<[>+<-]>]<<-]<<-
]
""".replace('\n', ''),
    handwritten_c=None  # Too complex for simple handwritten version
)


def main():
    benchmarks = [
        HELLO_WORLD,
        MULTIPLY_TEST,
        SIMPLE_LOOP,
    ]
    
    all_results = {}
    for bench in benchmarks:
        all_results[bench.name] = bench.run()
    
    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print("\nSpeedup of optimized compiler vs unoptimized:")
    for name, results in all_results.items():
        unopt_time = results.get('c_unopt', {}).get('time')
        opt_time = results.get('c_opt', {}).get('time')
        if unopt_time and opt_time and unopt_time > 0:
            speedup = unopt_time / opt_time
            print(f"  {name:<30} {speedup:.2f}x faster")


if __name__ == "__main__":
    main()
