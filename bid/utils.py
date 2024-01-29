import os


def load_bf(filename_or_bf_str, programs_dir="programs") -> tuple[str, str]:
    filename = f"{programs_dir}/{filename_or_bf_str}.bf"

    print(filename)
    if os.path.isfile(filename):
        name = filename_or_bf_str
        with open(filename) as f:
            return name, f.read()
    else:
        print("file does not exist")
        return None, filename_or_bf_str
