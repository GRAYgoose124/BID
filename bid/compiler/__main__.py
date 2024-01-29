import os
import subprocess
import argparse

from .languages.c import BfToC
from .languages.asm import BfToNASM
from ..utils import load_bf


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input file or string", required=True)
    parser.add_argument(
        "-p", "--programs-dir", help="programs directory", default="programs"
    )
    parser.add_argument("-o", "--output", help="output directory", default="output")
    parser.add_argument("-l", "--language", help="output language", default="c")
    parser.add_argument(
        "-c",
        "--compile",
        help="compile to executable",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-r", "--run", help="run executable", default=False, action="store_true"
    )
    return parser.parse_args()


def main():
    args = argparser()
    possible_name, bf_src = load_bf(args.input, args.programs_dir)
    output_dir = args.output
    language = args.language
    print(f"Input: {bf_src}")

    if args.language in ["c", "py", "asm"]:
        extension = args.language
        build_dir = os.path.join(output_dir, "build")
        os.makedirs(build_dir, exist_ok=True)
        output_name = possible_name or f"output_{language}_{len(bf_src)}"
        output_file = os.path.join(output_dir, f"{output_name}.{extension}")
        compiled_file = os.path.join(build_dir, f"{output_name}_{language}")

        if args.compile or args.run:
            if language == "c":
                BfO = BfToC()
            elif language == "asm":
                BfO = BfToNASM()
            else:
                raise NotImplementedError("language not implemented")

            with open(output_file, "w") as f:
                f.write(BfO.compile(bf_src))

        if args.run:
            if language == "c":
                subprocess.run(["gcc", output_file, "-o", compiled_file])
            elif language == "asm":
                subprocess.run(
                    ["nasm", "-f", "elf64", output_file, "-o", f"{compiled_file}.o"]
                )
                subprocess.run(["ld", f"{compiled_file}.o", "-o", compiled_file])

        subprocess.run([compiled_file])
        print(f"Output: {output_file}", f"Compiled: {compiled_file}", sep="\n")
    else:
        print("Invalid language")


if __name__ == "__main__":
    main()
