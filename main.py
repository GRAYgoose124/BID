#   Irk: irc bot
#   Copyright (C) 2016  Grayson Miller
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import tkinter as tk
from tkinter import filedialog, messagebox


# TODO: Display filename loaded
# TODO: Visual+interactive debugger
# TODO: Separate app into separate frames and organize
# TODO: Display output
class BrainfuckApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.interpreter = BrainfuckInterpreter()
        self.tape_cell = None

        self.master.wm_title("Brainfuck Interactive Debugger")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.create_widgets()


    def create_widgets(self):
        self.grid(sticky=tk.E+tk.W+tk.N+tk.S)
        self.rowconfigure(1, weight=4)
        self.columnconfigure(0, weight=1)

        # Parent frames
        self.button_frame = tk.LabelFrame(self, text="")
        self.button_frame.grid(row=0, column=0, sticky=tk.W)
        self.text_frame = tk.LabelFrame(self, text="Input / Source")
        self.text_frame.grid(row=1, column=0, columnspan=4, sticky=tk.E+tk.W+tk.S+tk.N)
        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.columnconfigure(1, weight=1)
        self.output_frame = tk.LabelFrame(self, text="Output")
        self.output_frame.grid(row=2, column=0, sticky=tk.W)
        self.debug_frame = tk.LabelFrame(self, text="")
        self.debug_frame.grid(row=2, column=1)
        self.debug_button_frame = tk.LabelFrame(self, text="")
        self.debug_button_frame.grid(row=3, column=2)

        # Button frame for basic operations.
        self.run = tk.Button(self.button_frame, text="run", command=self.bf_default_run)
        self.run.grid(row=0, column=0)
        self.load = tk.Button(self.button_frame, text="load", command=self.load_bf_file)
        self.load.grid(row=0, column=1)
        self.save = tk.Button(self.button_frame, text="save", command=self.save_bf_file)
        self.save.grid(row=0, column=2)
        self.clear = tk.Button(self.button_frame, text="clear", command=self.clear_inputs)
        self.clear.grid(row=0, column=3)
        # Debug frame for displaying the interpreter state.
        self.tape_text = tk.Text(self.debug_frame, background="#CCCCCC", height=1, state=tk.DISABLED)
        self.tape_text.grid(row=0, column=0)
        # Debug Button frame for the interpreter operations.
        self.debug = tk.Button(self.debug_button_frame, text="debug", command=self.bf_debug_run)
        self.debug.grid(row=0, column=0)
        self.step_backward = tk.Button(self.debug_button_frame, text="←")
        self.step_backward.grid(row=0, column=1)
        self.step_forward = tk.Button(self.debug_button_frame, text="→", command=self.bf_step_forward)
        self.step_forward.grid(row=0, column=2)
        # Text frame for modifying the source and input.
        self.input = tk.Text(self.text_frame)
        self.input.bind("<Control-r>", lambda _: self.bf_default_run)
        self.input.config(background="#CCCCCC")
        self.input.grid(row=0, column=0, sticky=tk.E+tk.W+tk.S+tk.N)

        self.source = tk.Text(self.text_frame)
        self.source.bind("<Control-r>", lambda _: self.bf_default_run)
        self.source.config(background="#CCCCCC")
        self.source.grid(row=0, column=1, sticky=tk.E + tk.W + tk.S + tk.N)
        # Output Frame for displaying the results of running the BF program.
        self.output = tk.Text(self.output_frame)
        self.output.config(background="#CCCCCC", height=10, state=tk.DISABLED)
        self.output.grid(row=0, column=0, sticky=tk.E+tk.W)

    def update_gui_bf_state(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(1.0, self.interpreter.output_string)
        self.output.config(state=tk.DISABLED)

        self.source.tag_remove("current_instr", index1="{}.{}".format(1, self.interpreter.last_i))
        self.source.tag_add("current_instr", index1="{}.{}".format(1, self.interpreter.i))
        self.source.tag_config("current_instr", foreground='red')

        self.tape_text.config(state=tk.NORMAL)
        self.tape_text.delete(1.0, tk.END)
        tape_str = self.interpreter.tape.copy()
        tape_str[self.interpreter.tape_pos] = "<{}>".format(tape_str[self.interpreter.tape_pos])
        self.tape_text.insert(1.0, tape_str)
        self.tape_text.config(state=tk.DISABLED)

    def bf_default_run(self):
        self.interpreter.update(source_string=self.source.get(1.0, tk.END), input_string=self.input.get(1.0, tk.END), debug=False)
        self.interpreter.run()
        self.update_gui_bf_state()

    def bf_debug_run(self):
        if not self.interpreter.running:
            self.interpreter.update(source_string=self.source.get(1.0, tk.END), input_string=self.input.get(1.0, tk.END), debug=True)
            if self.interpreter.source_string.strip(' \n    ') != '':
                self.interpreter.running = True
            self.bf_step_forward()
        else:
            self.source.tag_delete("current_instr")
            self.interpreter.reset()
            self.bf_debug_run()

    def bf_step_forward(self):
        if self.interpreter.running:
            self.update_gui_bf_state()
            self.interpreter.step()
        else:
            messagebox.askquestion(message="There is no program being run, please start a debugging instance.")

    # File I/O
    def load_bf_file(self):
        filename = filedialog.askopenfilename()
        if filename == '':
            return

        self.source.delete(1.0, tk.END)
        with open(filename, mode='r') as source_file:
            for line in source_file:
                self.source.insert(tk.END, line)

    def save_bf_file(self):
        filename = filedialog.asksaveasfilename(defaultextension="bf")
        if filename == '':
            return

        with open(filename, mode='w') as source_file:
            source_file.writelines((self.source.get(1.0, tk.END)))

    def clear_inputs(self):
        self.source.tag_delete("current_instr")
        self.source.delete(1.0, tk.END)
        self.input.delete(1.0, tk.END)
        self.tape_text.delete(1.0, tk.END)
        self.stop()

    def stop(self):
        self.interpreter.reset()
        self.update_gui_bf_state()


class BrainfuckInterpreter:
    def __init__(self, source_string=None, input_string=None, debug=False, machine_size=1):
        self.update(source_string, input_string, debug, machine_size)

    def update(self, source_string, input_string=None, debug=False, machine_size=1):
        self.source_string = source_string
        self.input_string = input_string
        self.debug = debug

        self.reset(machine_size)

    def reset(self, machine_size=1):
        self.running = False
        self.max_loops = 128 * machine_size
        self.tape_size = 32 * machine_size
        self.tape = [0] * self.tape_size
        self.tape_pos = int(self.tape_size / 2)

        self.frames = []

        self.loop_n = 0
        self.i = 0
        self.last_i = 0

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
                self.tape[self.tape_pos] += 1
            elif self.source_string[self.i] == '-':
                self.tape[self.tape_pos] -= 1
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
                    self.last_i = self.i
                    self.i = self.frames.pop()
                    self.loop_n += 1
                elif self.loop_n >self.max_loops:
                    raise RecursionError("Recursion limit exceeded.\nTape: {}".format(self.tape))
            elif self.source_string[self.i] == '[':
                if self.tape[self.tape_pos] != 0:
                    self.frames.append(self.i-1)
                else:
                    self.last_i = self.i
                    while self.source_string[self.i] != ']':
                        self.i += 1
            elif self.source_string[self.i] == ',':
                if self.input_string != "":
                    self.tape[self.tape_pos] = ord(self.input_string[0])
                    self.input_string = self.input_string[1:]
                else:
                    self.tape[self.tape_pos] = 0
                    return
            elif self.source_string[self.i] == '.':
                self.output_string += chr(self.tape[self.tape_pos])
            self.last_i = self.i
            self.i += 1
        else:
            self.running = False


if __name__ == '__main__':

    root = tk.Tk()
    app = BrainfuckApp(master=root)
    app.mainloop()