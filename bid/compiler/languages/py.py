import re
from ..transpiler import BfOptimizingCompiler

py_transpile_table = {
    ">": "ptr += 1",
    "<": "ptr -= 1",
    "+": "tape[ptr] += 1",
    "-": "tape[ptr] -= 1",
    ".": "print(chr(tape[ptr]), end='')",
    ",": "tape[ptr] = ord(sys.stdin.read(1))",
    "[": "while tape[ptr] != 0:",
    "]": "# end while",
}

py_runs_macros = {
    ">": lambda v: f"ptr += {v}",
    "<": lambda v: f"ptr -= {v}",
    "+": lambda v: f"tape[ptr] += {v}",
    "-": lambda v: f"tape[ptr] -= {v}",
}

py_shorts_macros = {
    "CLRC": "tape[ptr] = 0",
    "MFLE": ["while tape[ptr] != 0:", "ptr -= 1", "# end while"],
    "MFRE": ["while tape[ptr] != 0:", "ptr += 1", "# end while"],
    "PSNC": [
        "while tape[ptr] != 0:",
        "print(chr(tape[ptr]), end='');",
        "ptr += 1",
        "# end while",
    ],
    "GSNI": [
        "tape[ptr] = ord(sys.stdin.read(1))",
        "while tape[ptr] != 0:",
        "ptr += 1",
        "# end while",
    ],
}

py_template = lambda code: (
    "#!/usr/bin/env python3\n" "import sys\n" "ptr, tape = 0, [0] * 30000\n\n" f"{code}"
)


class BfToPy(BfOptimizingCompiler):
    def __init__(self):
        super().__init__(
            run_macros=py_runs_macros,
            short_macros=py_shorts_macros,
            transpile_table=py_transpile_table,
            compile_template=py_template,
        )

    def clean_output(self, codelines):
        indent = 0
        idx = 0

        while idx < len(codelines):
            if "while tape[ptr] != 0:" in codelines[idx]:
                tab = "\t" * indent
                codelines[idx] = f"{tab}{codelines[idx]}"
                indent += 1
            else:
                tab = "\t" * indent
                codelines[idx] = f"{tab}{codelines[idx]}"

            if "# end while" in codelines[idx]:
                del codelines[idx]
                idx -= 1
                indent -= 1

            idx += 1

        return "\n".join(codelines)
