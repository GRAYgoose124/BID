import os
import subprocess

from .c import BfToC
from ..utils import load_bf


def main():
    os.makedirs("output/build", exist_ok=True)

    bf_src = load_bf("hello_world")

    # test ir optimizer
    BfO = BfToC()
    with open("output/test_ir.c", "w") as f:
        f.write(BfO.compile(bf_src))

    subprocess.run(["gcc", "output/test_ir.c", "-o", "output/build/test_ir"])
    subprocess.run(["output/build/test_ir"])
    print()


if __name__ == "__main__":
    main()
