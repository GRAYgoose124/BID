import re
import logging

from ..transpiler import BfOptimizingCompiler


log = logging.getLogger(__name__)


class BfToNASM(BfOptimizingCompiler):
    def __init__(self):
        super().__init__(
            run_macros={},
            short_macros={},
            transpile_table={
                ">": "inc ebx ; Move right",
                "<": "dec ebx ; Move left",
                "+": "inc byte [ebx] ; Increment",
                "-": "dec byte [ebx] ; Decrement",
                ".": self._io_command(input=False),
                ",": self._io_command(input=True),
                "[": self._loop_start_command,
                "]": self._loop_end_command,
            },
            compile_template=lambda code: (
                "section .bss\n"
                "tape resb 30000 ; Reserve 30000 bytes for the tape\n\n"
                "section .text\n"
                "global _start\n\n"
                "_start:\n"
                "mov ebx, tape ; Set EBX to point to the start of the tape\n"
                f"{code}\n\n"
                "mov eax, 1 ; syscall number for exit\n"
                "xor ebx, ebx ; status 0\n"
                "int 0x80 ; call kernel\n"
            ),
            data_table={
                "current_loop": 0,  # Current loop ID
                "loop_stack": [],   # Stack of loop IDs
            },
        )

    @staticmethod
    def _io_command(input=True):
        return (
            f"mov eax, {3 if input else 4} ; syscall number for {input}\n"
            "mov ecx, ebx ; pointer to data\n"
            "mov edx, 1 ; number of bytes to read\n"
            "int 0x80 ; call kernel\n"
        )

    def _loop_start_command(self):
        loop_id = self.data_table["current_loop"]
        self.data_table["loop_stack"].append(loop_id)
        
        command = (
            f"loop_start_{loop_id}:\n"
            f"cmp byte [ebx], 0\n"
            f"je loop_end_{loop_id}\n"
        )
        self.data_table["current_loop"] += 1
        return command

    def _loop_end_command(self):
        if not self.data_table["loop_stack"]:
            raise SyntaxError("Unmatched ']'")
            
        loop_id = self.data_table["current_loop"]
        
        command = (
            f"jmp loop_start_{loop_id}\n"
            f"loop_end_{loop_id}:\n"
        )
        self.data_table["current_loop"] -= 1
        return command

    def clean_output(self, codelines):
        code = "\n".join(codelines)
        code = re.sub(r";.*\n", "\n", code)  # Remove comments
        code = re.sub(r"\n+", "\n", code)    # Remove empty lines
        return code
