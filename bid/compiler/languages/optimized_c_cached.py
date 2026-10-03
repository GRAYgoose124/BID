"""
Advanced C code generator with pointer caching optimization

Generates C code that caches tape[ptr] in a local variable to reduce
array access overhead.
"""

from typing import List
from ..optimizer import BFOptimizer, Op, OpType


class BfToOptimizedCCached:
    """
    Generate highly optimized C code with pointer caching.
    
    Key optimization: Cache tape[ptr] in a local variable to avoid
    redundant array accesses. This is safe when we can prove the pointer
    doesn't change.
    """
    
    def __init__(self, cell_bits=8, tape_size=30000):
        self.optimizer = BFOptimizer()
        self.cell_bits = cell_bits
        self.tape_size = tape_size
        
        if cell_bits == 8:
            self.cell_type = "unsigned char"
        elif cell_bits == 16:
            self.cell_type = "unsigned short"
        elif cell_bits == 32:
            self.cell_type = "unsigned int"
        else:
            self.cell_type = "unsigned char"
    
    def generate(self, ops: List[Op]) -> str:
        """Generate C code from IR operations with pointer caching"""
        lines = []
        indent = 1
        
        # Track if we need a cached cell variable
        uses_cell_cache = self.should_use_cell_cache(ops)
        if uses_cell_cache:
            lines.append("\t" * indent + f"{self.cell_type} *cell = &tape[ptr];")
        
        i = 0
        while i < len(ops):
            op = ops[i]
            
            # Look ahead for sequences that can use cached pointer
            if uses_cell_cache and op.op_type in [OpType.ADD, OpType.SET]:
                # Check if we can cache multiple operations
                seq_ops = []
                j = i
                while j < len(ops) and ops[j].op_type in [OpType.ADD, OpType.SET] and ops[j].arg2 == 0:
                    seq_ops.append(ops[j])
                    j += 1
                
                if len(seq_ops) > 1:
                    # Generate cached sequence
                    for seq_op in seq_ops:
                        code = self.generate_op_cached(seq_op)
                        if op.op_type == OpType.LOOP_END:
                            indent -= 1
                        lines.append("\t" * indent + code)
                        if op.op_type == OpType.LOOP_START:
                            indent += 1
                    i = j
                    continue
            
            # Generate normal operation
            code = self.generate_op(op)
            
            # Adjust indent
            if op.op_type == OpType.LOOP_END:
                indent -= 1
            
            lines.append("\t" * indent + code)
            
            if op.op_type == OpType.LOOP_START:
                indent += 1
            
            # Update cell pointer after PTR operations
            if uses_cell_cache and op.op_type == OpType.PTR:
                lines.append("\t" * indent + "cell = &tape[ptr];")
            
            i += 1
        
        return "\n".join(lines)
    
    def should_use_cell_cache(self, ops: List[Op]) -> bool:
        """Determine if pointer caching would be beneficial"""
        # Count operations that would benefit from caching
        add_count = sum(1 for op in ops if op.op_type == OpType.ADD and op.arg2 == 0)
        set_count = sum(1 for op in ops if op.op_type == OpType.SET and op.arg2 == 0)
        return (add_count + set_count) > 10  # Only if significant benefit
    
    def generate_op_cached(self, op: Op) -> str:
        """Generate operation using cached pointer"""
        if op.op_type == OpType.ADD:
            return f"*cell += {op.arg1};"
        elif op.op_type == OpType.SET:
            return f"*cell = {op.arg1};"
        else:
            return self.generate_op(op)
    
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
            if op.arg1 > 0:
                return f"while (tape[ptr]) ptr += {op.arg1};"
            else:
                return f"while (tape[ptr]) ptr -= {-op.arg1};"
        
        elif op.op_type == OpType.MUL_ADD:
            if op.arg2 == 1:
                return f"tape[ptr + ({op.arg1})] += tape[ptr];"
            else:
                return f"tape[ptr + ({op.arg1})] += tape[ptr] * {op.arg2};"
        
        elif op.op_type == OpType.NOP:
            return "/* nop */"
        
        return f"/* unknown op: {op} */"
    
    def compile(self, source: str) -> str:
        """Compile BF source to optimized C code"""
        # Run optimization passes
        ops = self.optimizer.optimize(source)
        
        # Generate C code with caching
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
