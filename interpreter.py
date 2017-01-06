#   BID: Brainfuck Visual Debugger and IDE
#   Copyright (C) 2016  Grayson Miller
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU A General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>

class BrainfuckInterpreter:
    def __init__(self, source_string="", input_string="", debug=False, machine_size=1):
        self.machine_size = machine_size
        self.update(source_string, input_string, debug)

    def update(self, source_string, input_string=None, debug=False):
        self.source_string = source_string
        self.input_string = input_string
        self.debug = debug

        self.reset()

    def reset(self):
        self.running = False
        self.max_loops = 65536 * self.machine_size
        self.tape_size = 1024 * self.machine_size
        self.tape = [0] * self.tape_size
        self.tape_pos = int(self.tape_size / 2)

        self.frames = []

        self.loop_n = 0
        self.i = 0

        self.output_string = ""

    def run(self):
        self.running = True

        if self.source_string is None:
            print("No source supplied.")
        else:
            try:
                while self.i < len(self.source_string):
                    self.step()
                print(self.output_string)
            except RecursionError as e:
                print(e)

        self.running = False

    def step(self):
        if self.i < len(self.source_string):
            if self.source_string[self.i] == '+':
                if self.tape[self.tape_pos] < 127:
                    self.tape[self.tape_pos] += 1
                else:
                    self.tape[self.tape_pos] = -127
            elif self.source_string[self.i] == '-':
                if self.tape[self.tape_pos] != -127:
                    self.tape[self.tape_pos] -= 1
                else:
                    self.tape[self.tape_pos] = 127
            elif self.source_string[self.i] == '>':
                if self.tape_pos >= self.tape_size-1:
                    self.tape_pos = 0
                else:
                    self.tape_pos += 1
            elif self.source_string[self.i] == '<':
                if self.tape_pos == 0:
                    self.tape_pos = self.tape_size-1
                else:
                    self.tape_pos -= 1
            elif self.source_string[self.i] == ']':
                if self.tape[self.tape_pos] != 0 and self.loop_n <= self.max_loops:
                    self.i = self.frames.pop()
                    self.loop_n += 1
                elif self.loop_n > self.max_loops:
                    raise RecursionError("Recursion limit exceeded.\nTape: {}".format(self.tape))
                else:
                    # TODO: Max loops per braces (store loop_n with frame)
                    self.frames.pop()
            elif self.source_string[self.i] == '[':
                if self.tape[self.tape_pos] != 0:
                    self.frames.append(self.i-1)
                else:
                    # TODO: Jump to proper braces (inside braces bug)
                    while self.source_string[self.i] != ']':
                        self.i += 1
            elif self.source_string[self.i] == ',':
                if self.input_string != "":
                    self.tape[self.tape_pos] = ord(self.input_string[0])
                    self.input_string = self.input_string[1:]
                else:
                    self.tape[self.tape_pos] = 0
                    self.running = False
            elif self.source_string[self.i] == '.':
                self.output_string += chr(self.tape[self.tape_pos])
            self.i += 1
        else:
            self.running = False

    def save_state(self):
        return {"tape": self.tape.copy(),
                 "tape_pos": self.tape_pos,
                 "frames": self.frames,
                 "i": self.i,
                 "output_string": self.output_string,
                 "input_string": self.input_string,
                 "loop_n": self.loop_n}

    def load_state(self, state):
        self.tape = state["tape"]
        self.tape_pos = state["tape_pos"]
        self.frames = state["frames"]
        self.loop_n = state["loop_n"]
        self.i = state["i"]
        self.output_string = state["output_string"]
        self.input_string = state["input_string"]
