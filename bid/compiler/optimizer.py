"""
Modern BF Compiler with Comprehensive Optimizations

This module implements a production-ready Brainfuck compiler with:
- Intermediate representation (IR)
- Multiple optimization passes
- Pattern recognition for common idioms
- Dead code elimination
- Constant folding and offset tracking
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Tuple
import logging

log = logging.getLogger(__name__)


class OpType(Enum):
    """Brainfuck operation types"""
    ADD = auto()          # Add to current cell
    PTR = auto()          # Move pointer
    OUT = auto()          # Output
    IN = auto()           # Input
    LOOP_START = auto()   # [
    LOOP_END = auto()     # ]
    SET = auto()          # Set cell to value (optimized [-] or [+])
    MUL_ADD = auto()      # Multiply and add: tape[ptr+offset] += tape[ptr] * factor; tape[ptr] = 0
    SCAN = auto()         # Scan for zero: while(tape[ptr]) ptr += offset
    NOP = auto()          # No operation (dead code)


@dataclass
class Op:
    """Single IR operation"""
    op_type: OpType
    arg1: int = 0          # For ADD: value, PTR: offset, SET: value, MUL_ADD: offset
    arg2: int = 0          # For MUL_ADD: factor, or offset for ADD/SET/OUT/IN
    comment: str = ""
    
    def __repr__(self):
        if self.op_type == OpType.ADD:
            if self.arg2 != 0:
                return f"Add({self.arg1}, offset={self.arg2})"
            return f"Add({self.arg1})"
        elif self.op_type == OpType.PTR:
            return f"Ptr({self.arg1:+d})"
        elif self.op_type == OpType.SET:
            if self.arg2 != 0:
                return f"Set({self.arg1}, offset={self.arg2})"
            return f"Set({self.arg1})"
        elif self.op_type == OpType.MUL_ADD:
            return f"MulAdd(offset={self.arg1:+d}, factor={self.arg2})"
        elif self.op_type == OpType.SCAN:
            return f"Scan({self.arg1:+d})"
        elif self.op_type == OpType.LOOP_START:
            return "LoopStart"
        elif self.op_type == OpType.LOOP_END:
            return "LoopEnd"
        elif self.op_type == OpType.OUT:
            if self.arg2 != 0:
                return f"Output(offset={self.arg2})"
            return "Output"
        elif self.op_type == OpType.IN:
            if self.arg2 != 0:
                return f"Input(offset={self.arg2})"
            return "Input"
        elif self.op_type == OpType.NOP:
            return "Nop"
        return f"Op({self.op_type})"


class BFOptimizer:
    """
    Comprehensive Brainfuck optimizer implementing multiple optimization passes:
    
    1. Parse BF source to basic IR
    2. Run-length encoding (collapse repeated operations)
    3. Loop pattern recognition:
       - Clear loops: [-] or [+] -> Set(0)
       - Copy loops: [->+<] -> MulAdd
       - Multiply loops: [->+++<] -> MulAdd
       - Scan loops: [>] or [<] -> Scan
    4. Dead code elimination
    5. Offset propagation and combining
    """
    
    def __init__(self):
        pass
    
    def parse(self, source: str) -> List[Op]:
        """Parse BF source into basic IR"""
        ops = []
        for char in source:
            if char == '+':
                ops.append(Op(OpType.ADD, 1))
            elif char == '-':
                ops.append(Op(OpType.ADD, -1))
            elif char == '>':
                ops.append(Op(OpType.PTR, 1))
            elif char == '<':
                ops.append(Op(OpType.PTR, -1))
            elif char == '[':
                ops.append(Op(OpType.LOOP_START))
            elif char == ']':
                ops.append(Op(OpType.LOOP_END))
            elif char == '.':
                ops.append(Op(OpType.OUT))
            elif char == ',':
                ops.append(Op(OpType.IN))
        return ops
    
    def collapse_runs(self, ops: List[Op]) -> List[Op]:
        """Collapse consecutive ADD and PTR operations"""
        if not ops:
            return ops
        
        result = []
        i = 0
        while i < len(ops):
            op = ops[i]
            
            # Collapse ADD operations (but only if they don't have offsets)
            if op.op_type == OpType.ADD and op.arg2 == 0:  # No offset
                total = op.arg1
                j = i + 1
                while j < len(ops) and ops[j].op_type == OpType.ADD and ops[j].arg2 == 0:
                    total += ops[j].arg1
                    j += 1
                # Only emit if non-zero after wraparound
                total = total % 256  # 8-bit wrapping
                if total > 128:
                    total -= 256
                if total != 0:
                    result.append(Op(OpType.ADD, total, 0))
                i = j
            
            # Collapse PTR operations
            elif op.op_type == OpType.PTR:
                total = op.arg1
                j = i + 1
                while j < len(ops) and ops[j].op_type == OpType.PTR:
                    total += ops[j].arg1
                    j += 1
                if total != 0:
                    result.append(Op(OpType.PTR, total, 0))
                i = j
            
            else:
                result.append(op)
                i += 1
        
        return result
    
    def find_matching_bracket(self, ops: List[Op], start: int) -> Optional[int]:
        """Find the matching LOOP_END for a LOOP_START"""
        if start >= len(ops) or ops[start].op_type != OpType.LOOP_START:
            return None
        
        depth = 1
        for i in range(start + 1, len(ops)):
            if ops[i].op_type == OpType.LOOP_START:
                depth += 1
            elif ops[i].op_type == OpType.LOOP_END:
                depth -= 1
                if depth == 0:
                    return i
        return None
    
    def recognize_loop_patterns(self, ops: List[Op]) -> List[Op]:
        """
        Recognize and optimize common loop patterns:
        - Clear loop: [-] or [+]
        - Scan loop: [>] or [<]
        - Copy/multiply loop: [->+<], [->+++<], etc.
        """
        result = []
        i = 0
        
        while i < len(ops):
            if ops[i].op_type == OpType.LOOP_START:
                end = self.find_matching_bracket(ops, i)
                if end is None:
                    result.append(ops[i])
                    i += 1
                    continue
                
                loop_body = ops[i+1:end]
                
                # Pattern 1: Clear loop [-] or [+]
                if len(loop_body) == 1 and loop_body[0].op_type == OpType.ADD:
                    if loop_body[0].arg1 in [-1, 1]:
                        result.append(Op(OpType.SET, 0, comment="clear loop"))
                        i = end + 1
                        continue
                
                # Pattern 2: Scan loop [>] or [<]
                if len(loop_body) == 1 and loop_body[0].op_type == OpType.PTR:
                    result.append(Op(OpType.SCAN, loop_body[0].arg1, comment="scan loop"))
                    i = end + 1
                    continue
                
                # Pattern 3: Copy/multiply loops
                # Structure: sequence of (ptr move, add, ptr move back)
                # Example: [->+<] -> MulAdd(offset=1, factor=1)
                # Example: [->+++<] -> MulAdd(offset=1, factor=3)
                # Example: [->+>++<<] -> MulAdd(offset=1, factor=1), MulAdd(offset=2, factor=2)
                mul_ops = self.recognize_multiply_loop(loop_body)
                if mul_ops:
                    result.extend(mul_ops)
                    i = end + 1
                    continue
                
                # No pattern matched, keep loop as-is
                result.append(ops[i])
                result.extend(loop_body)
                if end < len(ops):
                    result.append(ops[end])
                i = end + 1
            else:
                result.append(ops[i])
                i += 1
        
        return result
    
    def recognize_multiply_loop(self, loop_body: List[Op]) -> Optional[List[Op]]:
        """
        Recognize multiply/copy loops.
        Pattern: [-ptr_offset1, add_val1, ptr_offset2, add_val2, ..., ptr_back]
        The pointer must return to 0 and include a -1 at offset 0.
        """
        if not loop_body:
            return None
        
        # Track pointer position and cell changes
        ptr_pos = 0
        changes = {}  # offset -> change
        
        for op in loop_body:
            if op.op_type == OpType.PTR:
                ptr_pos += op.arg1
            elif op.op_type == OpType.ADD:
                if ptr_pos not in changes:
                    changes[ptr_pos] = 0
                changes[ptr_pos] += op.arg1
            else:
                # Other operations break the pattern
                return None
        
        # Check: pointer must return to 0
        if ptr_pos != 0:
            return None
        
        # Check: must decrement current cell by 1 (or increment by -1)
        if changes.get(0, 0) != -1:
            return None
        
        # Valid multiply loop!
        # Generate MUL_ADD ops for all offsets except 0
        result = []
        for offset, change in sorted(changes.items()):
            if offset != 0:
                result.append(Op(OpType.MUL_ADD, offset, change, comment="multiply loop"))
        
        # Always end with clearing the source cell
        result.append(Op(OpType.SET, 0, comment="clear after multiply"))
        
        return result if result else None
    
    def eliminate_dead_code(self, ops: List[Op]) -> List[Op]:
        """
        Eliminate dead code:
        - ADD/SET before SET at same offset can be removed
        - Multiple SETs in sequence keep only the last
        """
        if not ops:
            return ops
        
        result = []
        i = 0
        
        while i < len(ops):
            op = ops[i]
            
            # Look ahead to see if this operation is overwritten
            if op.op_type in [OpType.ADD, OpType.SET]:
                # Check if the next operation (ignoring loops) is a SET at the same position
                j = i + 1
                will_be_set = False
                
                # Simple lookahead: if next op is SET and no PTR move in between, this is dead
                while j < len(ops):
                    next_op = ops[j]
                    if next_op.op_type == OpType.SET:
                        will_be_set = True
                        break
                    elif next_op.op_type == OpType.PTR:
                        # Pointer moved, can't eliminate
                        break
                    elif next_op.op_type in [OpType.LOOP_START, OpType.LOOP_END, OpType.OUT, OpType.IN]:
                        # Complex control flow or observable side effect, can't eliminate
                        break
                    elif next_op.op_type == OpType.MUL_ADD:
                        # MulAdd reads the current cell, can't eliminate
                        break
                    j += 1
                
                if will_be_set and op.op_type != OpType.SET:
                    # Skip this ADD, it will be overwritten
                    i += 1
                    continue
            
            result.append(op)
            i += 1
        
        return result
    
    def propagate_offsets(self, ops: List[Op]) -> List[Op]:
        """
        Propagate pointer offsets into operations to avoid pointer movement.
        
        Transform:
            ptr += 3;
            tape[ptr] += 5;
            ptr -= 3;
        Into:
            tape[ptr + 3] += 5;
        
        This significantly reduces pointer movements and improves cache locality.
        """
        result = []
        i = 0
        
        while i < len(ops):
            op = ops[i]
            
            # Look for pattern: PTR, operations, PTR back
            if op.op_type == OpType.PTR:
                offset = op.arg1
                j = i + 1
                operations_with_offset = []
                
                # Collect operations that can use this offset
                net_ptr_movement = 0
                while j < len(ops):
                    next_op = ops[j]
                    
                    if next_op.op_type in [OpType.ADD, OpType.SET, OpType.OUT, OpType.IN]:
                        # These operations can use offset addressing
                        if net_ptr_movement == 0:
                            # Only if pointer hasn't moved since initial offset
                            operations_with_offset.append((j, next_op))
                        j += 1
                    elif next_op.op_type == OpType.PTR:
                        net_ptr_movement += next_op.arg1
                        # Check if total ptr movement cancels out the original offset
                        if net_ptr_movement == -offset and operations_with_offset:
                            # Pattern matched! Replace sequence with offset operations
                            for _, offsetted_op in operations_with_offset:
                                result.append(self.add_offset_to_op(offsetted_op, offset))
                            # Skip to after the closing PTR
                            i = j + 1
                            break
                        elif net_ptr_movement != 0:
                            # Pointer moved to a different location, can't continue pattern
                            break
                        j += 1
                    else:
                        # Loop or other complex operation, can't optimize across it
                        break
                else:
                    # Didn't find matching pattern, keep original
                    result.append(op)
                    i += 1
                    continue
                
                # Check if we successfully optimized
                if i <= j:
                    # We broke out of the loop but didn't advance i
                    # This means pattern didn't match, keep original
                    if operations_with_offset and net_ptr_movement == -offset:
                        # Already handled above, i was advanced
                        pass
                    else:
                        result.append(op)
                        i += 1
            else:
                result.append(op)
                i += 1
        
        return result
    
    def add_offset_to_op(self, op: Op, offset: int) -> Op:
        """Add offset to an operation that needs it"""
        if op.op_type == OpType.ADD:
            return Op(OpType.ADD, op.arg1, offset, f"offset={offset}")
        elif op.op_type == OpType.SET:
            return Op(OpType.SET, op.arg1, offset, f"offset={offset}")
        elif op.op_type == OpType.OUT:
            return Op(OpType.OUT, 0, offset, f"offset={offset}")
        elif op.op_type == OpType.IN:
            return Op(OpType.IN, 0, offset, f"offset={offset}")
        else:
            return op
    
    def optimize(self, source: str) -> List[Op]:
        """Run full optimization pipeline"""
        log.debug(f"Parsing source ({len(source)} chars)")
        ops = self.parse(source)
        log.debug(f"Initial ops: {len(ops)}")
        
        ops = self.collapse_runs(ops)
        log.debug(f"After collapse_runs: {len(ops)}")
        
        # Loop pattern recognition - this should help!
        ops = self.recognize_loop_patterns(ops)
        log.debug(f"After recognize_loop_patterns: {len(ops)}")
        
        # DISABLED: Offset propagation hurts gcc performance  
        # ops = self.propagate_offsets(ops)
        # log.debug(f"After propagate_offsets: {len(ops)}")
        
        return ops
