# bf to py compiler


import re


class BfOptimizingCompiler:
    def __init__(self, run_macros=None, short_macros=None, transpile_table=None):
        self.run_macros = run_macros or {}
        self.short_macros = short_macros or {}
        self.transpile_table = transpile_table or {}

        self.utilities = {
            "runs_re": re.compile(r"(\d+)(.)"),
            "shorts_re": re.compile(r"([A-Z]{4});"),
        }

        self.shorts = {
            "CLRC": re.compile(r"(\[-\])"),  # [-]
            "MFLE": re.compile(r"(\[<\])"),  # [<]
            "MFRE": re.compile(r"(\[>\])"),  # [>]
            "PSNC": re.compile(r"(\[\.>\])"),  # [.>]
            "GSNI": re.compile(r"(,\[\>,\])"),  # ,[>,]
        }

        self.runs = {
            ">": re.compile(r"(>{2,})"),  # >n
            "<": re.compile(r"(<{2,})"),  # <n
            "+": re.compile(r"(\+{2,})"),  # +n
            "-": re.compile(r"(-{2,})"),  # -n
        }

    def replace_runs(self, src):
        for ty in self.runs:
            src = self.runs[ty].sub(lambda x: f"{len(x.group(1))}{ty}", src)

        return src

    def replace_shorts(self, src):
        for ty in self.shorts:
            src = self.shorts[ty].sub(lambda x: f"{ty};", src)

        return src

    def get_unspanned(self, to_replaces, total_length):
        if not to_replaces:
            # If there are no spans, return a span covering the whole string
            return [(0, total_length)]

        spans = sorted(to_replaces.keys())
        unspanned = []
        # If there is a gap at the beginning
        if spans[0][0] > 0:
            unspanned.append((0, spans[0][0]))

        for i in range(len(spans) - 1):
            # Append the gap between two spans
            unspanned.append((spans[i][1], spans[i + 1][0]))

        # If there is a gap at the end
        if spans[-1][1] < total_length:
            unspanned.append((spans[-1][1], total_length))

        return unspanned

    def parse_spanning(self, ir, i, spanning, span):
        if ir[i] in self.transpile_table:
            spanning[span] += self.transpile_table[ir[i]]

    def to_ir(self, src):
        ir = self.replace_shorts(src)
        ir = self.replace_runs(ir)
        return ir

    def compile_ir(self, ir, runs_re=True, shorts_re=True):
        # first, replace all the runs and shorts
        runs_to_replace = {}

        if runs_re:
            for m in self.utilities["runs_re"].finditer(ir):
                count, ty = m.groups()
                count = int(count)
                span = m.span()
                runs_to_replace[span] = self.run_macros[ty](count)

        shorts_to_replace = {}

        if shorts_re:
            for m in self.utilities["shorts_re"].finditer(ir):
                span = m.span()
                ty = m.groups()[0]
                shorts_to_replace[span] = self.short_macros[ty]

        # now standard parse the unspanned
        spanned = {**runs_to_replace, **shorts_to_replace}
        unspanned = {
            span: "" for span in self.get_unspanned(spanned, total_length=len(ir))
        }
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
        raise NotImplementedError

    def compile(self, src, runs_re=True, shorts_re=True):
        ir = self.to_ir(src)
        code = self.compile_ir(ir, runs_re, shorts_re)
        return self.clean_output(code)
