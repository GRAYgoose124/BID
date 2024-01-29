import os
import subprocess

from .languages.c import BfToC
from .languages.asm import BfToNASM
from ..utils import load_bf


def c_compile_write_and_run(bf_src, BfO, output_dir="output"):
    print("C")
    os.makedirs(f"{output_dir}/build", exist_ok=True)
    with open(f"{output_dir}/test.c", "w") as f:
        f.write(BfO.compile(bf_src))

    subprocess.run(["gcc", f"{output_dir}/test.c", "-o", f"{output_dir}/build/test_c"])
    subprocess.run([f"{output_dir}/build/test_c"])
    print()


def nasm_compile_write_and_run(bf_src, BfO, output_dir="output"):
    print("ASM")
    os.makedirs(f"{output_dir}/build", exist_ok=True)
    with open(f"{output_dir}/test.asm", "w") as f:
        f.write(BfO.compile(bf_src))

    subprocess.run(
        [
            "nasm",
            "-f",
            "elf64",
            f"{output_dir}/test.asm",
            "-o",
            f"{output_dir}/build/test_nasm.o",
        ]
    )
    subprocess.run(
        ["ld", f"{output_dir}/build/test_nasm.o", "-o", f"{output_dir}/build/test_nasm"]
    )
    subprocess.run([f"{output_dir}/build/test_nasm"])
    print()


def main():
    os.makedirs("output/build", exist_ok=True)

    bf_src = load_bf("hello_world")

    c_compile_write_and_run(bf_src, BfToC())
    nasm_compile_write_and_run(bf_src, BfToNASM())


if __name__ == "__main__":
    main()
