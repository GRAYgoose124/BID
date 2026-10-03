"""
Truly naive BF to C transpiler with no optimizations
One C statement per BF command
"""

class BfToNaiveC:
    def __init__(self, cell_bits=8, tape_size=30000):
        self.cell_bits = cell_bits
        self.tape_size = tape_size
        
        if cell_bits == 8:
            self.cell_type = "unsigned char"
        else:
            self.cell_type = "unsigned char"
    
    def compile(self, source: str) -> str:
        """Generate truly naive C code - one statement per BF command"""
        lines = []
        indent = 1
        
        for char in source:
            if char == '+':
                lines.append("\t" * indent + "tape[ptr]++;")
            elif char == '-':
                lines.append("\t" * indent + "tape[ptr]--;")
            elif char == '>':
                lines.append("\t" * indent + "ptr++;")
            elif char == '<':
                lines.append("\t" * indent + "ptr--;")
            elif char == '[':
                lines.append("\t" * indent + "while (tape[ptr] != 0) {")
                indent += 1
            elif char == ']':
                indent -= 1
                lines.append("\t" * indent + "}")
            elif char == '.':
                lines.append("\t" * indent + "putchar(tape[ptr]);")
            elif char == ',':
                lines.append("\t" * indent + "tape[ptr] = getchar();")
        
        code = "\n".join(lines)
        
        result = f"""#include <stdio.h>

{self.cell_type} tape[{self.tape_size}] = {{0}};
unsigned int ptr = 0;

int main() {{
{code}
\treturn 0;
}}
"""
        return result
