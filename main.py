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
from tkinter import filedialog, messagebox
import tkinter as tk
import sys


# TODO: BF breakpoints, debug run should full run and only stop at breaks then start button for what debug run does now
# TODO: Auto-step pause, finish, etc.
# TODO: Time Taken
# TODO: Display filename loaded
# TODO: Separate app into separate frames and organize
# TODO: Display output
# TODO: Init all variables in __init__???
# TODO: Show position on input string
class BrainfuckApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.interpreter = BrainfuckInterpreter()
        self.interpreter_states = []
        self.tape_cell = None
        self.pause = False
        self.current_after = None

        self.master.wm_title("Brainfuck Interactive Debugger")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.create_widgets()
        self.update_gui_bf_state()

    # TODO: organize all names, to _btn or whatever...so you don't mix up different shit...
    def create_widgets(self):
        self.grid(sticky=tk.E+tk.W+tk.N+tk.S)
        self.rowconfigure(1, weight=4)
        self.columnconfigure(0, weight=1)
        # Parent frames
        self.button_frame = tk.LabelFrame(self, text="")
        self.button_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.text_frame = tk.LabelFrame(self, text="Input / Source")
        self.text_frame.grid(row=1, column=0, columnspan=3, padx=10, sticky=tk.E+tk.W+tk.S+tk.N)
        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.columnconfigure(1, weight=1)
        self.output_frame = tk.LabelFrame(self, text="Output")
        self.output_frame.grid(row=2, column=0, padx=10, sticky=tk.W, columnspan=3)
        self.debug_frame = tk.LabelFrame(self, text="Debug Info")
        self.debug_frame.grid(row=3, column=0, padx=10, pady=10)
        self.debug_button_frame = tk.LabelFrame(self, text="")
        self.debug_button_frame.grid(row=3, column=2, padx=10, pady=10)
        # Button frame for basic operations.
        self.run = tk.Button(self.button_frame, text="run", command=self.bf_default_run)
        self.run.grid(row=0, column=0, pady=(5,5), padx=(5,0))
        self.reset_btn = tk.Button(self.button_frame, text="reset", command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=(0,20))
        self.load = tk.Button(self.button_frame, text="load", command=self.load_bf_file)
        self.load.grid(row=0, column=2)
        self.save = tk.Button(self.button_frame, text="save", command=self.save_bf_file)
        self.save.grid(row=0, column=3)
        self.clear = tk.Button(self.button_frame, text="clear", command=self.clear_inputs)
        self.clear.grid(row=0, column=4, padx=(20,5))
        # Debug frame for displaying the interpreter state.
        self.states = tk.Text(self.debug_frame, height=2, width=97, background="#CCCCCC", wrap=tk.NONE)
        self.states.grid(row=0, column=0, padx=5, pady=5)
        self.state_memory = tk.Text(self.debug_frame, background=self.master.cget("background"),
                                    borderwidth=0, height=1, width=30)
        self.state_memory.grid(row=0, column=1)
        self.tape_text = tk.Text(self.debug_frame, background="#CCCCCC", height=1, width=127, state=tk.DISABLED)
        self.tape_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        # Debug Button frame for the interpreter operations.
        self.debug = tk.Button(self.debug_button_frame, text="debug", command=self.bf_debug_run)
        self.debug.grid(row=0, column=0, padx=(5,20),pady=5)
        self.auto_step_backward = tk.Button(self.debug_button_frame, text="←", command=self.bf_auto_step_backward)
        self.auto_step_backward.grid(row=0, column=1, )
        self.step_backward = tk.Button(self.debug_button_frame, text="◄", command=self.bf_step_backward)
        self.step_backward.grid(row=0, column=2)
        self.pause_btn = tk.Button(self.debug_button_frame, text="●", command=self.toggle_pause)
        self.pause_btn.grid(row=0, column=3)
        self.step_forward = tk.Button(self.debug_button_frame, text="►", command=self.bf_step_forward)
        self.step_forward.grid(row=0, column=4)
        self.auto_step_forward = tk.Button(self.debug_button_frame, text="→", command=self.bf_auto_step_forward)
        self.auto_step_forward.grid(row=0, column=5, padx=(0,5))
        self.hertz_slider = tk.Scale(self.debug_button_frame, from_=1, to_=100, orient=tk.HORIZONTAL)
        self.hertz_slider.grid(row=1, column=0, columnspan=5, pady=(0,5))
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

    def toggle_pause(self):
        self.pause = not self.pause

    def clear_inputs(self):
        self.source.delete(1.0, tk.END)
        self.input.delete(1.0, tk.END)
        self.tape_text.delete(1.0, tk.END)

        self.reset()

    def reset(self):
        if self.current_after is not None:
            self.master.after_cancel(self.current_after)
        self.current_after = None

        # TODO: This is the reenable that shoudl be in its own function and accompanied by debug dsiable function
        self.source.configure(state=tk.NORMAL)
        self.auto_step_forward.configure(state=tk.NORMAL)
        self.auto_step_backward.configure(state=tk.NORMAL)
        self.source.tag_delete("current_instr")

        self.interpreter_states = []
        self.interpreter.reset()
        self.update_gui_bf_state()

    def update_gui_bf_state(self, debug=False):
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(1.0, self.interpreter.output_string)
        self.output.config(state=tk.DISABLED)

        if debug:
            if self.interpreter.running:
                self.source.configure(state=tk.NORMAL)
            self.source.tag_delete("current_instr")
            self.source.tag_add("current_instr", index1="{}.{}".format(*self.get_line_offset(self.interpreter.i)))
            self.source.tag_config("current_instr", background='green')
            if self.interpreter.running:
                self.source.configure(state=tk.DISABLED)
        # TODO: Fix for when you hit edges to wrap the visible cells
        self.tape_text.config(state=tk.NORMAL)
        self.tape_text.delete(1.0, tk.END)
        tape_str = self.interpreter.tape.copy()
        tape_str[self.interpreter.tape_pos] = "<{}>".format(tape_str[self.interpreter.tape_pos])
        tape_str = tape_str[self.interpreter.tape_pos-32:self.interpreter.tape_pos+32]
        self.tape_text.insert(1.0, tape_str)
        self.tape_text.config(state=tk.DISABLED)

        self.state_memory.config(state=tk.NORMAL)
        self.state_memory.delete(1.0, tk.END)
        self.state_memory.insert(1.0, "State Memory: {}KiB".format(sys.getsizeof(self.interpreter_states)/1000))
        self.state_memory.config(state=tk.DISABLED)

        self.states.config(state=tk.NORMAL)
        self.states.delete(1.0, tk.END)
        try:
            state1 = self.interpreter_states[-1]
            state1["tape"] = list(filter((0).__ne__, state1["tape"]))
            state2 = self.interpreter_states[-2]
            state2["tape"] = list(filter((0).__ne__, state2["tape"]))
            self.states.insert(1.0, "{}\n{}".format(state1, state2))
        except IndexError:
            pass
        self.states.config(state=tk.DISABLED)


    def get_line_offset(self, ins_pos):
        ins_pos-=1
        total_len = 0
        line_count = 0
        current_line = 1
        lines = self.source.get(1.0, tk.END).split("\n")

        for line in lines:
            current_line = len(line)
            total_len += current_line
            line_count += 1

            if ins_pos <= total_len:
                break
            ins_pos -= 1

        return line_count, (ins_pos-(total_len-current_line))

    # TODO: Factor functions that loop separately to not have as much redundant code or unnecessary code running...
    # TODO: Disable all debug buttons in one function and have a reenable function reenable all buttons
    # ...There are a lot of repetitions in different code blocks, functionalize this.
    def bf_default_run(self):
        if not self.interpreter.running:
            self.interpreter.update(source_string=self.source.get(1.0, tk.END),
                                    input_string=self.input.get(1.0, tk.END), debug=False)
            if self.interpreter.source_string.strip('\n     ') != '':
                self.interpreter.running = True

        if self.interpreter.i < len(self.interpreter.source_string):
            self.interpreter.step()
        else:
            self.update_gui_bf_state()
            self.source.configure(state=tk.NORMAL)
            self.interpreter.running = False

        if self.interpreter.running and not self.pause:
            self.current_after = self.master.after_idle(self.bf_default_run)




    def bf_debug_run(self):
        self.source.configure(state=tk.DISABLED)
        self.source.tag_delete("current_instr")

        if not self.interpreter.running:
            self.interpreter.update(source_string=self.source.get(1.0, tk.END),
                                    input_string=self.input.get(1.0, tk.END), debug=True)
            if self.interpreter.source_string.strip('\n     ') != '':
                self.interpreter.running = True

            self.bf_step_forward()
        else:
            self.interpreter.reset()
            self.bf_debug_run()

    # TODO: Thread the mainloop/etc on main thread and interpreter/all inited functions in secondary
    # TODO: Separate looping parts from init parts for all buttons
    def bf_auto_step_forward(self):
        step_hertz = self.hertz_slider.get()

        self.bf_step_forward()

        if self.interpreter.running and not self.pause:
            self.auto_step_forward.configure(state=tk.DISABLED)
            self.auto_step_backward.configure(state=tk.DISABLED)
            self.current_after = self.master.after(int(1000 / step_hertz), self.bf_auto_step_forward)
        else:
            self.auto_step_backward.configure(state=tk.NORMAL)
            self.auto_step_forward.configure(state=tk.NORMAL)
            self.source.configure(state=tk.NORMAL)

    def bf_auto_step_backward(self):
        step_hertz = self.hertz_slider.get()

        self.bf_step_backward()

        if self.interpreter.running and not self.pause:
            self.auto_step_forward.configure(state=tk.DISABLED)
            self.auto_step_backward.configure(state=tk.DISABLED)
            self.current_after = self.master.after(int(1000 / step_hertz), self.bf_auto_step_backward)
        else:
            self.auto_step_backward.configure(state=tk.NORMAL)
            self.auto_step_forward.configure(state=tk.NORMAL)
            self.toggle_pause()

    #TODO: if you modify source while running it'll run the loaded source...lock source input while debugging
    def bf_step_forward(self):
        if self.interpreter.running:
            self.interpreter_states.append(self.interpreter.save_state())
            self.interpreter.step()

            self.update_gui_bf_state(debug=True)
        #Needs to init when pasted and used first
        elif self.interpreter.source_string.strip('\n     ') != '':
            result = messagebox.askquestion(
                message="There is no program being run, would you like to start a debugging instance?")
            if result == "yes":
                self.bf_debug_run()

    def bf_step_backward(self):
        if self.interpreter.running:
            if self.interpreter_states == []:
                self.toggle_pause()
                print("Stepped to beginning.")
                return

            self.interpreter.load_state(self.interpreter_states.pop())
            self.update_gui_bf_state(debug=True)
        elif self.interpreter.source_string.strip('\n     ') != '':
            result = messagebox.askquestion(
                message="There is no program being run, would you like to start a debugging instance?")
            if result == "yes":
                self.bf_debug_run()

    def load_bf_file(self):
        filename = filedialog.askopenfilename(defaultextension=".bf", filetypes=(("Brainfuck Script", "*.bf"),("All Files", "*.*")))

        if filename == '':
            return

        self.clear_inputs()
        self.source.delete(1.0, tk.END)

        with open(filename, mode='r') as source_file:
            for line in source_file:
                self.source.insert(tk.END, line)

    def save_bf_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".bf", filetypes=(("Brainfuck Script", "*.bf"),("All Files", "*.*")))
        if filename == '':
            return

        with open(filename, mode='w') as source_file:
            source_file.writelines((self.source.get(1.0, tk.END)))


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

# TODO: threading
# TODO: Fix glitches to run Esolang examples (Not really glitches, just different interpreter types)
# TODO: Modify to toggle unbounded, bounded, no wrap, wrap, EOF, etc wrap cells etc Have a new command like # to...
# ... denote all this so individual programs can specify their needs.
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

if __name__ == '__main__':
    root = tk.Tk()
    app = BrainfuckApp(master=root)
    app.mainloop()