import re
from ..transpiler import BfOptimizingCompiler



class BfToC(BfOptimizingCompiler):
    def __init__(self):
        super().__init__(
            run_macros={
                ">": lambda v: f"ptr += {v};",
                "<": lambda v: f"ptr -= {v};",
                "+": lambda v: f"tape[ptr] += {v};",
                "-": lambda v: f"tape[ptr] -= {v};",
            },
            short_macros={
                "CLRC": "tape[ptr] = 0;",
                "MFLE": "while (tape[ptr] != 0) {ptr--;}",
                "MFRE": "while (tape[ptr] != 0) {ptr++;}",
                "PSNC": "while (tape[ptr] != 0) {putchar(tape[ptr]); ptr += 1;}",
                "GSNI": "tape[ptr] = getchar(); while (tape[ptr] != 0) {ptr += 1;}",
            },
            transpile_table={
                ">": "ptr += 1;",  # ptr++;
                "<": "ptr -= 1;",  # ptr--;
                "+": "tape[ptr] += 1;",  # tape[ptr]++;
                "-": "tape[ptr] -= 1;",  # tape[ptr]--;
                ".": "putchar(tape[ptr]);",
                ",": "tape[ptr] = getchar();",
                "[": "while (tape[ptr] != 0) {",
                "]": "}",
            },
            compile_template=lambda code: (
                "#include <stdio.h>\n\n"
                "unsigned char tape[30000] = {0};\n"
                "unsigned int ptr = 0;\n\n"
                "int main() {\n"
                f"{code}\n"
                "\treturn 0;\n"
                "}\n"
            ),
        )

    def clean_output(self, codelines):
        code = "\n".join(codelines)
        code = re.sub(r"\s", "", code)
        # add \n after every ;{} and include statemnts if they don't have a newline
        code = re.sub(r";", ";\n", code)
        code = re.sub(r"{", "{\n", code)
        code = re.sub(r"}", "}\n", code)

        indent = 1
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
