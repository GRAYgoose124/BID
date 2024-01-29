# bf to py compiler


import re
import subprocess


from .c import c_template


class BfFuncLib:
    CLEAR_CELL = "[-]"
    MOVE_TO_FIRST_L_EMPTY = "[<]"
    MOVE_TO_FIRST_R_EMPTY = "[>]"
    PRINT_SEQ_NONZERO_CELLS = "[.>]"
    GET_SEQ_NONZERO_INPUT = ",[>,]"
    PTR_INC_RUN = ">n"
    PTR_DEC_RUN = "<n"
    CELL_INC_RUN = "+n"
    CELL_DEC_RUN = "-n"

    def to_ir(self, src):
        pass


class BfPyTranspiler:
    def __init__(self, src):
        self.src = src
        self.indent = 1
        self.last_c = ""
        self.output = []

    def add_line(self, line, indent=False):
        self.output.append("\t" * self.indent + line)

        if indent != False:
            self.indent += indent

    def mod_last_line(self, value):
        last_value = int(self.output[-1].split("=")[1][:-1].strip())
        value += last_value

        last_s = self.output[-1].split("=")[0]
        self.output[-1] = f"{last_s}= {value};"

    def parse(self):
        last_c = ""
        for c in self.src:
            if c == ">":
                if last_c == ">":
                    self.mod_last_line(1)
                else:
                    self.add_line("ptr += 1;")
            elif c == "<":
                if last_c == "<":
                    self.mod_last_line(-1)
                else:
                    self.add_line("ptr += -1;")
            elif c == "+":
                if last_c == "+":
                    self.mod_last_line(1)
                else:
                    self.add_line("tape[ptr] += 1;")
            elif c == "-":
                if last_c == "-":
                    self.mod_last_line(-1)
                else:
                    self.add_line("tape[ptr] += -1;")
            elif c == ".":
                self.add_line("putchar(tape[ptr]);")
            elif c == ",":
                self.add_line("tape[ptr] = getchar();")
            elif c == "[":
                self.add_line("while (tape[ptr] != 0) {", indent=1)
            elif c == "]":
                self.indent -= 1
                self.add_line("}")
            else:
                continue
            last_c = c

    def dump(self):
        return c_template("\n".join(self.output))

    def write(self, fname, compile=False):
        with open(fname, "w") as f:
            f.write(self.dump())


HELLO_WORLD_LONG = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
if __name__ == "__main__":
    test = BfPyTranspiler(HELLO_WORLD_LONG)
    test.parse()
    # print(test.dump())

    test.write("test.c")
    subprocess.run(["gcc", "test.c", "-o", "test", "-O3"])
    subprocess.run(["./test"])
