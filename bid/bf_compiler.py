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

class BrainfuckCompiler():
    def __init__(self, source_string="", input_string="", debug=False):
        self.tape_size = 128
        self.max_cell_value = 127
        self.min_cell_value = -127
        self.source_string = source_string
        self.input_string = input_string

        self.tape = [0] * self.tape_size
        self.tape_pos = int(self.tape_size / 2)

        self.frames = []
        self.braces = 0

        self.i = 0

        self.output_string = ""

    def parser(self):
        while self.i < len(self.source_string):
            if self.source_string[self.i] == '+':
                pass
            elif self.source_string[self.i] == '-':
                pass
            elif self.source_string[self.i] == '>':
                pass
            elif self.source_string[self.i] == '<':
                pass
            elif self.source_string[self.i] == ']':
                pass
            elif self.source_string[self.i] == '[':
                pass
            elif self.source_string[self.i] == ',':
                pass
            elif self.source_string[self.i] == '.':
                pass

if __name__ == '__main__':
    pass