import os
import subprocess

from .transpiler import BfPyTranspiler
from ..utils import load_bf


def main():
    test = BfPyTranspiler(load_bf("hello_world"))
    test.parse()
    # print(test.dump())

    os.makedirs("output/build", exist_ok=True)
    test.write("output/test.c")
    subprocess.run(["gcc", "output/test.c", "-o", "output/build/test"])
    subprocess.run(["output/build/test"])


if __name__ == "__main__":
    main()
