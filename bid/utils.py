from pathlib import Path
import os


def load_bf(filepath: Path) -> str | None:
    if filepath.is_file():
        with open(filepath) as f:
            return f.read()
    else:
        print("file does not exist")
        return None
