import os
from pathlib import Path
import subprocess
import argparse
import logging
from .languages.c import BfToC
from .languages.asm import BfToNASM
from .languages.py import BfToPy

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
        "-cl",
        "--clean",
        help="clean output",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-r", "--run", help="run executable", default=False, action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", help="verbose output", default=False, action="store_true"
    )
    return parser.parse_args()


def main():
    args = argparser()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    log = logging.getLogger(__name__)
    
    filepath = Path(args.input)
    bf_src = load_bf(filepath)
    name = filepath.name
    output_dir = args.output
    language = args.language
    
    log.debug(f"Input: {bf_src}")
    if args.language in ["c", "py", "asm"]:
        extension = args.language
        build_dir = os.path.join(output_dir, "build")
        os.makedirs(build_dir, exist_ok=True)
        output_name = name or f"output_{language}_{len(bf_src)}"
        output_file = os.path.join(output_dir, f"{output_name}.{extension}")
        compiled_file = os.path.join(build_dir, f"{output_name}_{language}")

        if args.compile or args.run:
            if language == "c":
                BfO = BfToC()
            elif language == "asm":
                BfO = BfToNASM()
            elif language == "py":
                BfO = BfToPy()
            else:
                print("Invalid language")
                return

            with open(output_file, "w") as f:
                compiled = BfO.compile(bf_src, args.clean)
                f.write(compiled)

        if args.run:
            if language == "c":
                subprocess.run(["gcc", output_file, "-o", compiled_file])
            elif language == "asm":
                subprocess.run(
                    ["nasm", "-f", "elf64", output_file, "-o", f"{compiled_file}.o"]
                )
                subprocess.run(["ld", f"{compiled_file}.o", "-o", compiled_file])
            elif language == "py":
                compiled_file = output_file
                subprocess.run(["chmod", "+x", compiled_file])

            subprocess.run([compiled_file])
            print(f"Ran: {compiled_file}")
    else:
        print("Invalid language")


if __name__ == "__main__":
    main()
