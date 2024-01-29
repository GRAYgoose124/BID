# bf to py compiler


from enum import Enum
import re


from .c import c_template


class BfOptimizingCompiler:
    utilities = {
        "runs_re": re.compile(r"(\d+)(.)"),
        "shorts_re": re.compile(r"([A-Z]{4});"),
    }

    shorts = {
        "CLRC": re.compile(r"(\[-\])"),  # [-]
        "MFLE": re.compile(r"(\[<\])"),  # [<]
        "MFRE": re.compile(r"(\[>\])"),  # [>]
        "PSNC": re.compile(r"(\[\.>\])"),  # [.>]
        "GSNI": re.compile(r"(,\[\>,\])"),  # ,[>,]
    }
    shorts_macros = {
        "CLRC": "tape[ptr] = 0;",
        "MFLE": "while (tape[ptr] != 0) {ptr--;}",
        "MFRE": "while (tape[ptr] != 0) {ptr++;}",
        "PSNC": "while (tape[ptr] != 0) {putchar(tape[ptr]); ptr += 1;}",
        "GSNI": "tape[ptr] = getchar(); while (tape[ptr] != 0) {ptr += 1;}",
    }

    runs = {
        ">": re.compile(r"(>{2,})"),  # >n
        "<": re.compile(r"(<{2,})"),  # <n
        "+": re.compile(r"(\+{2,})"),  # +n
        "-": re.compile(r"(-{2,})"),  # -n
    }

    runs_macros = {
        ">": lambda v: f"ptr += {v};",
        "<": lambda v: f"ptr -= {v};",
        "+": lambda v: f"tape[ptr] += {v};",
        "-": lambda v: f"tape[ptr] -= {v};",
    }

    def replace_runs(self, src):
        for ty in self.runs:
            src = self.runs[ty].sub(lambda x: f"{len(x.group(1))}{ty}", src)

        return src

    def replace_shorts(self, src):
        for ty in self.shorts:
            src = self.shorts[ty].sub(lambda x: f"{ty};", src)

        return src

    def get_unspanned(self, to_replaces):
        spans = sorted(to_replaces.keys())
        unspanned = []
        for i in range(len(spans) - 1):
            unspanned.append((spans[i][1], spans[i + 1][0]))

        return unspanned

    def parse_spanning(self, ir, i, spanning, span):
        if ir[i] == ">":
            spanning[span] += "ptr += 1;"
        elif ir[i] == "<":
            spanning[span] += "ptr -= 1;"
        elif ir[i] == "+":
            spanning[span] += "tape[ptr] += 1;"
        elif ir[i] == "-":
            spanning[span] += "tape[ptr] -= 1;"
        elif ir[i] == ".":
            spanning[span] += "putchar(tape[ptr]);"
        elif ir[i] == ",":
            spanning[span] += "tape[ptr] = getchar();"
        elif ir[i] == "[":
            spanning[span] += "while (tape[ptr] != 0) {"
        elif ir[i] == "]":
            spanning[span] += "}"

    def to_ir(self, src):
        ir = self.replace_shorts(src)
        ir = self.replace_runs(ir)
        return ir

    def compile_ir(self, ir):
        # first, replace all the runs and shorts
        runs_to_replace = {}
        for m in self.utilities["runs_re"].finditer(ir):
            count, ty = m.groups()
            count = int(count)
            span = m.span()
            runs_to_replace[span] = self.runs_macros[ty](count)

        shorts_to_replace = {}
        for m in self.utilities["shorts_re"].finditer(ir):
            span = m.span()
            ty = m.groups()[0]
            shorts_to_replace[span] = self.shorts_macros[ty]

        # now standard parse the unspanned
        spanned = {**runs_to_replace, **shorts_to_replace}
        unspanned = {span: "" for span in self.get_unspanned(spanned)}
        for span in unspanned:
            for i in range(span[0], span[1]):
                self.parse_spanning(ir, i, unspanned, span)

        # finally, build the code from the spanning
        spanning = {**unspanned, **spanned}
        sorted_spanning = sorted(spanning.keys())
        code = ""
        for span in sorted_spanning:
            code += f"{spanning[span]}"

        return code

    def clean_output(self, code):
        code = re.sub(r"\s", "", code)
        # add \n after every ;{}
        new_code = re.sub(r";", ";\n", code)
        new_code = re.sub(r"{", "{\n", new_code)
        new_code = re.sub(r"}", "}\n", new_code)

        indent = 0
        idx = 0
        while idx < len(new_code):
            if new_code[idx] == "{":
                indent += 1
            elif new_code[idx] == "}":
                indent -= 1

            if new_code[idx] == "\n":
                insert_position = idx + 1
                new_code = (
                    new_code[:insert_position]
                    + ("\t" * indent)
                    + new_code[insert_position:]
                )
                idx += indent

            idx += 1

        return new_code

    def compile(self, src):
        ir = self.to_ir(src)
        code = self.compile_ir(ir)
        return c_template(self.clean_output(code))
