transpile_globals = {
    "ptr": "0",
    "tape": "[0] * 30000",
}

transpile_table_py = {
    ">": "ptr += 1",
    "<": "ptr -= 1",
    "+": "tape[ptr] += 1",
    "-": "tape[ptr] -= 1",
    ".": "print(chr(tape[ptr]), end='')",
    ",": "tape[ptr] = ord(sys.stdin.read(1))",
    "[": "while tape[ptr] != 0:",
    "]": "",
}
