import re
from ..transpiler import BfOptimizingCompiler


class BfToNASM(BfOptimizingCompiler):
    def __init__(self):
        self.loop_id = 0

        nasm_transpile_table = {
            ">": "inc ebx ; Move right",
            "<": "dec ebx ; Move left",
            "+": "inc byte [ebx] ; Increment",
            "-": "dec byte [ebx] ; Decrement",
            ".": self._output_command(),
            ",": self._input_command(),
            "[": self._loop_start_command(),
            "]": self._loop_end_command(),
        }
        super().__init__(
            run_macros={},  # Define any run-length encoded macros if needed
            short_macros={},  # Define any short macros if needed
            transpile_table=nasm_transpile_table,
        )
        del self.utilities["runs_re"]

    def compile(self, src):
        compiled_code = super().compile(src, runs_re=False, shorts_re=False)
        return self.nasm_template(compiled_code)

    @staticmethod
    def _output_command():
        return (
            "mov eax, 4 ; syscall number for write\n"
            "mov ecx, ebx ; pointer to data\n"
            "mov edx, 1 ; number of bytes to write\n"
            "int 0x80 ; call kernel"
        )

    @staticmethod
    def _input_command():
        return (
            "mov eax, 3 ; syscall number for read\n"
            "mov ecx, ebx ; pointer to data\n"
            "mov edx, 1 ; number of bytes to read\n"
            "int 0x80 ; call kernel"
        )

    def _loop_start_command(self):
        self.loop_id += 1

        out = f"loop_start_{self.loop_id}:\ncmp byte [ebx], 0\nje loop_end_{self.loop_id}\n; Loop start"
        return out

    def _loop_end_command(self):
        out = f"jmp loop_start_{self.loop_id}\nloop_end_{self.loop_id}:\n; Loop end"
        self.loop_id -= 1
        return out

    @staticmethod
    def nasm_template(code):
        return (
            "section .bss\n"
            "tape resb 30000 ; Reserve 30000 bytes for the tape\n"
            "data_ptr resd 1 ; Reserve a dword for the pointer, initialized to 0\n\n"
            "section .text\n"
            "global _start\n\n"
            "_start:\n"
            "mov ebx, tape ; Set EBX to point to the start of the tape\n"
            f"{code}\n\n"
            "mov eax, 1 ; syscall number for exit\n"
            "xor ebx, ebx ; status 0\n"
            "int 0x80 ; call kernel\n"
        )

    def clean_output(self, code):
        # remove all comments
        code = re.sub(r";.*", "", code)
        return code
