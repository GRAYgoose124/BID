"""
Optimized C code generator for BF
Uses the optimized IR to generate efficient C code
"""

import re
from typing import List
from ..optimizer import BFOptimizer, Op, OpType


class BfToOptimizedC:
    """
    Generate optimized C code from BF source.
    Uses the BFOptimizer to produce an IR, then generates tight C code.
    """
    
    def __init__(self, cell_bits=8, tape_size=30000):
        self.optimizer = BFOptimizer()
        self.cell_bits = cell_bits
        self.tape_size = tape_size
        
        # Determine C type based on cell size
        if cell_bits == 8:
            self.cell_type = "unsigned char"
        elif cell_bits == 16:
            self.cell_type = "unsigned short"
        elif cell_bits == 32:
            self.cell_type = "unsigned int"
        else:
            self.cell_type = "unsigned char"
    
    def generate_op(self, op: Op) -> str:
        """Generate C code for a single IR operation"""
        if op.op_type == OpType.ADD:
            if op.arg2 != 0:  # Has offset
                return f"tape[ptr + ({op.arg2})] += {op.arg1};"
            return f"tape[ptr] += {op.arg1};"
        
        elif op.op_type == OpType.PTR:
            return f"ptr += {op.arg1};"
        
        elif op.op_type == OpType.SET:
            if op.arg2 != 0:  # Has offset
                return f"tape[ptr + ({op.arg2})] = {op.arg1};"
            return f"tape[ptr] = {op.arg1};"
        
        elif op.op_type == OpType.OUT:
            if op.arg2 != 0:  # Has offset
                return f"putchar(tape[ptr + ({op.arg2})]);"
            return "putchar(tape[ptr]);"
        
        elif op.op_type == OpType.IN:
            if op.arg2 != 0:  # Has offset
                return f"tape[ptr + ({op.arg2})] = getchar();"
            return "tape[ptr] = getchar();"
        
        elif op.op_type == OpType.LOOP_START:
            return "while (tape[ptr] != 0) {"
        
        elif op.op_type == OpType.LOOP_END:
            return "}"
        
        elif op.op_type == OpType.SCAN:
            # Optimized scan loop
            if op.arg1 > 0:
                return f"while (tape[ptr]) ptr += {op.arg1};"
            else:
                return f"while (tape[ptr]) ptr -= {-op.arg1};"
        
        elif op.op_type == OpType.MUL_ADD:
            # Multiply and add operation
            if op.arg2 == 1:
                return f"tape[ptr + ({op.arg1})] += tape[ptr];"
            else:
                return f"tape[ptr + ({op.arg1})] += tape[ptr] * {op.arg2};"
        
        elif op.op_type == OpType.NOP:
            return "/* nop */"
        
        return f"/* unknown op: {op} */"
    
    def generate(self, ops: List[Op]) -> str:
        """Generate C code from IR operations"""
        lines = []
        indent = 1
        
        for op in ops:
            code = self.generate_op(op)
            
            # Adjust indent
            if op.op_type == OpType.LOOP_END:
                indent -= 1
            
            lines.append("\t" * indent + code)
            
            if op.op_type == OpType.LOOP_START:
                indent += 1
        
        return "\n".join(lines)
    
    def compile(self, source: str) -> str:
        """Compile BF source to optimized C code"""
        # Run optimization passes
        ops = self.optimizer.optimize(source)
        
        # Generate C code
        code = self.generate(ops)
        
        # Wrap in main function
        result = f"""#include <stdio.h>

{self.cell_type} tape[{self.tape_size}] = {{0}};
unsigned int ptr = 0;

int main() {{
{code}
\treturn 0;
}}
"""
        return result
