#!/usr/bin/env python3
"""
Tests for the optimized BF compiler

Verifies that:
1. Optimizations preserve correctness
2. Specific patterns are recognized and optimized
3. Generated code compiles and runs correctly
"""

import unittest
import sys
import subprocess
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bid.compiler.optimizer import BFOptimizer, OpType
from bid.compiler.languages.optimized_c import BfToOptimizedC
from bid.compiler.languages.c import BfToC
from bid.interpreter import BrainfuckInterpreter


class TestOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = BFOptimizer()
    
    def test_run_length_encoding(self):
        """Test that repeated operations are collapsed"""
        ops = self.optimizer.optimize("+++++")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].op_type, OpType.ADD)
        self.assertEqual(ops[0].arg1, 5)
    
    def test_clear_loop(self):
        """Test that [-] is recognized as a clear operation"""
        ops = self.optimizer.optimize("[-]")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].op_type, OpType.SET)
        self.assertEqual(ops[0].arg1, 0)
    
    def test_scan_loop_right(self):
        """Test that [>] is recognized as a scan operation"""
        ops = self.optimizer.optimize("[>]")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].op_type, OpType.SCAN)
        self.assertEqual(ops[0].arg1, 1)
    
    def test_scan_loop_left(self):
        """Test that [<] is recognized as a scan operation"""
        ops = self.optimizer.optimize("[<]")
        self.assertEqual(len(ops), 1)
        self.assertEqual(ops[0].op_type, OpType.SCAN)
        self.assertEqual(ops[0].arg1, -1)
    
    def test_multiply_loop(self):
        """Test that [->+++<] is recognized as multiply-add"""
        ops = self.optimizer.optimize("[->+++<]")
        # Should have: MulAdd(offset=1, factor=3), Set(0)
        mul_ops = [op for op in ops if op.op_type == OpType.MUL_ADD]
        self.assertEqual(len(mul_ops), 1)
        self.assertEqual(mul_ops[0].arg1, 1)  # offset
        self.assertEqual(mul_ops[0].arg2, 3)  # factor
    
    def test_copy_loop(self):
        """Test that [->+<] is recognized as copy"""
        ops = self.optimizer.optimize("[->+<]")
        mul_ops = [op for op in ops if op.op_type == OpType.MUL_ADD]
        self.assertEqual(len(mul_ops), 1)
        self.assertEqual(mul_ops[0].arg2, 1)  # factor is 1 for copy
    
    def test_offset_propagation(self):
        """Test offset propagation (currently disabled for gcc compatibility)"""
        ops = self.optimizer.optimize(">+++<")
        # Offset propagation is disabled because it hurts gcc -O3 performance
        # The ops will be: PTR(+1), ADD(3), PTR(-1)
        self.assertGreater(len(ops), 0)
        # Just verify it's valid code
        ptr_ops = [op for op in ops if op.op_type == OpType.PTR]
        add_ops = [op for op in ops if op.op_type == OpType.ADD]
        # Should have pointer movements and add
        self.assertGreaterEqual(len(ptr_ops), 1)
        self.assertGreaterEqual(len(add_ops), 1)
    
    def test_dead_code_elimination(self):
        """Test dead code elimination (currently disabled for performance)"""
        ops = self.optimizer.optimize("+++++[-]")
        # DCE is disabled, so we'll have: ADD(5), SET(0)
        # The loop pattern recognition turns [-] into SET(0)
        set_ops = [op for op in ops if op.op_type == OpType.SET]
        self.assertGreaterEqual(len(set_ops), 1)
        # Should have at least the SET from the clear loop
        self.assertEqual(set_ops[0].arg1, 0)


class TestCodeGeneration(unittest.TestCase):
    def compile_and_run(self, c_code):
        """Compile and run C code, return output"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "test.c")
            binary_path = os.path.join(tmpdir, "test")
            
            with open(source_path, 'w') as f:
                f.write(c_code)
            
            # Compile
            result = subprocess.run(
                ['gcc', '-O3', source_path, '-o', binary_path],
                capture_output=True
            )
            if result.returncode != 0:
                self.fail(f"Compilation failed: {result.stderr.decode()}")
            
            # Run
            result = subprocess.run(
                [binary_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
    
    def test_hello_world(self):
        """Test that Hello World produces correct output"""
        bf = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
        
        # Get interpreter output
        interp = BrainfuckInterpreter(bf, "")
        interp.run()
        expected = interp.output_string
        
        # Get optimized compiler output
        compiler = BfToOptimizedC()
        c_code = compiler.compile(bf)
        actual = self.compile_and_run(c_code)
        
        self.assertEqual(actual, expected)
    
    def test_multiply_correctness(self):
        """Test that multiply loop produces correct output"""
        bf = "+++[->+++++<]>."  # 3 * 5 = 15
        
        interp = BrainfuckInterpreter(bf, "")
        interp.run()
        expected = interp.output_string
        
        compiler = BfToOptimizedC()
        c_code = compiler.compile(bf)
        actual = self.compile_and_run(c_code)
        
        self.assertEqual(actual, expected)
    
    def test_offset_correctness(self):
        """Test that offset propagation is correct"""
        bf = ">++++++[->++<]>."  # 6 * 2 = 12 at offset 2
        
        interp = BrainfuckInterpreter(bf, "")
        interp.run()
        expected = interp.output_string
        
        compiler = BfToOptimizedC()
        c_code = compiler.compile(bf)
        actual = self.compile_and_run(c_code)
        
        self.assertEqual(actual, expected)


class TestComparisonToUnoptimized(unittest.TestCase):
    """Verify that optimized output matches unoptimized output"""
    
    def test_programs_match(self):
        """Test several programs to ensure optimized = unoptimized output"""
        test_programs = [
            "+++++[->+++++<]>.",  # Multiply
            ">+++<",  # Offset
            "+++++[-]>++.",  # Clear
            "[-]>++++[->++<]>.",  # Combined patterns
        ]
        
        for bf in test_programs:
            with self.subTest(bf=bf):
                # Unoptimized
                unopt_compiler = BfToC()
                unopt_c = unopt_compiler.compile(bf)
                
                # Optimized
                opt_compiler = BfToOptimizedC()
                opt_c = opt_compiler.compile(bf)
                
                # Compile and run both
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Unoptimized
                    unopt_src = os.path.join(tmpdir, "unopt.c")
                    unopt_bin = os.path.join(tmpdir, "unopt")
                    with open(unopt_src, 'w') as f:
                        f.write(unopt_c)
                    subprocess.run(['gcc', '-O3', unopt_src, '-o', unopt_bin], check=True)
                    unopt_output = subprocess.run([unopt_bin], capture_output=True, text=True).stdout
                    
                    # Optimized
                    opt_src = os.path.join(tmpdir, "opt.c")
                    opt_bin = os.path.join(tmpdir, "opt")
                    with open(opt_src, 'w') as f:
                        f.write(opt_c)
                    subprocess.run(['gcc', '-O3', opt_src, '-o', opt_bin], check=True)
                    opt_output = subprocess.run([opt_bin], capture_output=True, text=True).stdout
                    
                    self.assertEqual(unopt_output, opt_output,
                                   f"Output mismatch for program: {bf}")


if __name__ == "__main__":
    unittest.main()
