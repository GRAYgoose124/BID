c_template = (
    lambda code: f"""
#include <stdio.h>

unsigned char tape[30000] = {{0}};
unsigned int ptr = 0;

int main() {{
{code}
\treturn 0;
}}
"""
)


transpile_table_c = {
    ">": "ptr += 1;",  # ptr++;
    "<": "ptr -= 1;",  # ptr--;
    "+": "tape[ptr] += 1;",  # tape[ptr]++;
    "-": "tape[ptr] -= 1;",  # tape[ptr]--;
    ".": "putchar(tape[ptr]);",
    ",": "tape[ptr] = getchar();",
    "[": "while (tape[ptr] != 0) {",
    "]": "}",
}
