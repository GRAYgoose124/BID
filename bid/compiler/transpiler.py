# bf to py compiler


import re
import logging

log = logging.getLogger(__name__)

class BfOptimizingCompiler:
    def __init__(
        self,
        run_macros=None,
        short_macros=None,
        transpile_table=None,
        compile_template=None,
        data_table=None,
    ):
        self.run_macros = run_macros or {}
        self.short_macros = short_macros or {}
        self.transpile_table = transpile_table or {}
        self.compile_template = compile_template or (lambda x: f"{x}")
        self.data_table = data_table or {}

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
        log.debug(f"Replacing runs: {src}")
        for ty in self.runs:
            src = self.runs[ty].sub(lambda x: f"{len(x.group(1))}{ty}", src)
        log.debug(f"Replaced runs: {src}")
        return src

    def replace_shorts(self, src):
        log.debug(f"Replacing shorts: {src}")
        for ty in self.shorts:
            src = self.shorts[ty].sub(lambda x: f"{ty};", src)
        log.debug(f"Replaced shorts: {src}")
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
            spanning[span].append(self.transpile_table[ir[i]])

    def to_ir(self, src):
        ir = self.replace_shorts(src)
        ir = self.replace_runs(ir)
        return ir

    def compile_ir(self, ir, runs_re=True, shorts_re=True):
        # first, replace all the runs and shorts
        runs_to_replace = {}
        if runs_re and len(self.run_macros):
            for m in self.utilities["runs_re"].finditer(ir):
                count, ty = m.groups()
                count = int(count)
                span = m.span()
                runs_to_replace[span] = self.run_macros[ty](count)

        shorts_to_replace = {}
        if shorts_re and len(self.short_macros):
            for m in self.utilities["shorts_re"].finditer(ir):
                span = m.span()
                ty = m.groups()[0]
                shorts_to_replace[span] = self.short_macros[ty]

        log.debug(f"Runs to replace: {runs_to_replace}")
        log.debug(f"Shorts to replace: {shorts_to_replace}")
        
        # now standard parse the unspanned
        spanned = {**runs_to_replace, **shorts_to_replace}
        unspanned = {
            span: [] for span in self.get_unspanned(spanned, total_length=len(ir))
        }
        for span in unspanned:
            for i in range(span[0], span[1]):
                self.parse_spanning(ir, i, unspanned, span)

        # finally, build the code from the spanning
        spanning = {**unspanned, **spanned}
        sorted_spanning = sorted(spanning.keys())
        codelines = []
        for span in sorted_spanning:
            if isinstance(spanning[span], list):
                codelines.extend(spanning[span])
            else:
                codelines.append(spanning[span])

        return codelines
    
    def _internal_post_process(self, code):
        for i, line in enumerate(code):
            # some lines are actually methods, so we need to call them now to generate the code
            if callable(line):
                log.debug(f"Calling {line}")
                code[i] = line()
                log.debug(f"Now: {code[i]=}")
                
    def clean_output(self, code):
        raise NotImplementedError
    
    def post_process(self, code):
        return code

    def compile(self, src, runs_re=True, shorts_re=True, clean=True):
        log.debug(f"Transpiling: {src}")
        ir = self.to_ir(src)
        log.debug(f"IR: {ir}")
        code = self.compile_ir(ir, runs_re, shorts_re)
        log.debug(f"Code: {code}")
        self._internal_post_process(code)
        log.debug(f"Post processed code: {code}")
        code = self.post_process(code)
        log.debug(f"Post processed code 2: {code}")
        if clean:
            code = self.clean_output(code)
        else:
            code = "\n".join(code)
        log.debug(f"Final code: {code}")
            
        code = self.compile_template(code)
        #log.debug(f"With template: {code}")
        return code
