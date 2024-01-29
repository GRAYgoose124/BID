import re
from ..transpiler import BfOptimizingCompiler

c_template = (
    lambda code: f"""#include <stdio.h>

unsigned char tape[30000] = {{0}};
unsigned int ptr = 0;

int main() {{
{code}
\treturn 0;
}}
"""
)

c_shorts_macros = {
    "CLRC": "tape[ptr] = 0;",
    "MFLE": "while (tape[ptr] != 0) {ptr--;}",
    "MFRE": "while (tape[ptr] != 0) {ptr++;}",
    "PSNC": "while (tape[ptr] != 0) {putchar(tape[ptr]); ptr += 1;}",
    "GSNI": "tape[ptr] = getchar(); while (tape[ptr] != 0) {ptr += 1;}",
}

c_runs_macros = {
    ">": lambda v: f"ptr += {v};",
    "<": lambda v: f"ptr -= {v};",
    "+": lambda v: f"tape[ptr] += {v};",
    "-": lambda v: f"tape[ptr] -= {v};",
}

c_transpile_table = {
    ">": "ptr += 1;",  # ptr++;
    "<": "ptr -= 1;",  # ptr--;
    "+": "tape[ptr] += 1;",  # tape[ptr]++;
    "-": "tape[ptr] -= 1;",  # tape[ptr]--;
    ".": "putchar(tape[ptr]);",
    ",": "tape[ptr] = getchar();",
    "[": "while (tape[ptr] != 0) {",
    "]": "}",
}


class BfToC(BfOptimizingCompiler):
    def __init__(self):
        super().__init__(
            run_macros=c_runs_macros,
            short_macros=c_shorts_macros,
            transpile_table=c_transpile_table,
            compile_template=c_template,
        )

    def clean_output(self, codelines):
        code = "\n".join(codelines)
        code = re.sub(r"\s", "", code)
        # add \n after every ;{}
        code = re.sub(r";", ";\n", code)
        code = re.sub(r"{", "{\n", code)
        code = re.sub(r"}", "}\n", code)

        indent = 0
        idx = 0
        while idx < len(code):
            if code[idx] == "{":
                indent += 1
            elif code[idx] == "}":
                indent -= 1

            if code[idx] == "\n":
                insert_position = idx + 1
                code = code[:insert_position] + ("\t" * indent) + code[insert_position:]
                idx += indent

            idx += 1

        return code
