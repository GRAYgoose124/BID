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

import tkinter as tk
from tkinter import filedialog, messagebox
import sys

from interpreter import BrainfuckInterpreter


class BID(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # Set up interpreter and GUI states
        self.interpreter = BrainfuckInterpreter()
        self.interpreter_states = []
        self.tape_cell = None
        self.pause = False
        self.current_after = None

        # Set up GUI window
        self.master.wm_title("Brainfuck Interactive Developer")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        self.grid(sticky=tk.E+tk.W+tk.N+tk.S)
        self.rowconfigure(1, weight=4)
        self.columnconfigure(0, weight=1)

        # Parent frames
        self.button_frame = tk.LabelFrame(self, text="")
        self.button_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.text_frame = tk.LabelFrame(self, text="Source")
        self.text_frame.grid(row=1, column=0, columnspan=3, padx=10, sticky=tk.E+tk.W+tk.S+tk.N)
        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=0)
        self.io_frame = tk.LabelFrame(self, text="Input/Output")
        self.io_frame.grid(row=2, column=0, padx=10, sticky=tk.W, columnspan=3)
        self.debug_frame = tk.LabelFrame(self, text="Debug Info")
        self.debug_frame.grid(row=3, column=0, padx=10, pady=10)
        self.debug_button_frame = tk.LabelFrame(self, text="")
        self.debug_button_frame.grid(row=3, column=2, padx=10, pady=10)

        # Button frame for basic operations.
        self.run_btn = tk.Button(self.button_frame, text="run", command=self.bf_default_run)
        self.run_btn.grid(row=0, column=0, pady=(5, 5), padx=(5, 0))
        self.reset_btn = tk.Button(self.button_frame, text="reset", command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=(0, 20))
        self.load_btn = tk.Button(self.button_frame, text="load", command=self.load_bf_file)
        self.load_btn.grid(row=0, column=2)
        self.save_btn = tk.Button(self.button_frame, text="save", command=self.save_bf_file)
        self.save_btn.grid(row=0, column=3)
        self.clear_btn = tk.Button(self.button_frame, text="clear all", command=self.clear_all)
        self.clear_btn.grid(row=0, column=4, padx=(20, 5))

        # Debug frame for displaying the interpreter state.
        self.states_text = tk.Text(self.debug_frame, height=2, width=97, background="#CCCCCC", wrap=tk.NONE)
        self.states_text.grid(row=0, column=0, padx=5, pady=5)
        self.state_memory_text = tk.Text(self.debug_frame, background=self.master.cget("background"),
                                         borderwidth=0, height=1, width=30)
        self.state_memory_text.grid(row=0, column=1)
        self.tape_text = tk.Text(self.debug_frame, background="#CCCCCC", height=1, width=127, state=tk.DISABLED)
        self.tape_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Debug Button frame for the interpreter operations.
        self.debug_btn = tk.Button(self.debug_button_frame, text="debug", command=self.bf_debug_start)
        self.debug_btn.grid(row=0, column=0, padx=(5, 20), pady=5)
        self.auto_step_backward_btn = tk.Button(self.debug_button_frame, text="←", command=lambda: self.bf_auto_step("backward"))
        self.auto_step_backward_btn.grid(row=0, column=1, )
        self.step_backward_btn = tk.Button(self.debug_button_frame, text="◄", command=self.bf_step_backward)
        self.step_backward_btn.grid(row=0, column=2)
        self.pause_btn = tk.Button(self.debug_button_frame, text="●", command=lambda: not self.pause)
        self.pause_btn.grid(row=0, column=3)
        self.step_forward_btn = tk.Button(self.debug_button_frame, text="►", command=self.bf_step_forward)
        self.step_forward_btn.grid(row=0, column=4)
        self.auto_step_forward_btn = tk.Button(self.debug_button_frame, text="→", command=lambda: self.bf_auto_step("forward"))
        self.auto_step_forward_btn.grid(row=0, column=5, padx=(0, 5))
        self.hertz_scale = tk.Scale(self.debug_button_frame, from_=1, to_=256, orient=tk.HORIZONTAL, sliderlength=20)
        self.hertz_scale.grid(row=1, column=0, columnspan=5, pady=(0, 5))

        # Text frame for modifying the source and input.
        self.source_text = tk.Text(self.text_frame)
        self.source_text.bind("<Control-r>", lambda _: self.bf_default_run)
        self.source_text.config(background="#CCCCCC")
        self.source_text.grid(row=0, column=0, sticky=tk.E + tk.W + tk.S + tk.N)

        # Output Frame for displaying the results of running the BF program.
        self.input_text = tk.Text(self.io_frame)
        self.input_text.bind("<Control-r>", lambda _: self.bf_default_run)
        self.input_text.config(background="#CCCCCC", height=10)
        self.input_text.grid(row=0, column=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.output_text = tk.Text(self.io_frame)
        self.output_text.config(background="#CCCCCC", height=10, state=tk.DISABLED)
        self.output_text.grid(row=0, column=1, sticky=tk.E + tk.W)

    def clear_all(self):
        """Clear the GUI Text elements and resets the interpreter."""
        answer = messagebox.askyesno("Full Reset",
                                "This will completely reset the IDE, including your source.\nAre you sure?")

        if answer == "yes":
            self.source_text.delete(1.0, tk.END)
            self.input_text.delete(1.0, tk.END)
            self.tape_text.delete(1.0, tk.END)

            self.reset()

    def reset(self):
        """Stops and resets the interpreter and debug elements."""
        if self.current_after is not None:
            self.master.after_cancel(self.current_after)
        self.current_after = None

        # Reset locked GUI elements.
        self.source_text.configure(state=tk.NORMAL)
        self.auto_step_forward_btn.configure(state=tk.NORMAL)
        self.auto_step_backward_btn.configure(state=tk.NORMAL)
        self.source_text.tag_delete("current_instr")

        # Reset the interpreter
        self.interpreter_states = []
        self.interpreter.reset()
        self.update_gui()

    def update_gui(self, debug=False):
        """Update GUI Elements. (usually called after an interpreter state change)"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, self.interpreter.output_string)
        self.output_text.config(state=tk.DISABLED)

        # Place the marker for current debugger instruction
        if debug:
            if self.interpreter.running:
                self.source_text.configure(state=tk.NORMAL)

            self.source_text.tag_delete("current_instr")
            self.source_text.tag_add("current_instr", index1="{}.{}".format(*self.get_line_offset(self.interpreter.i)))
            self.source_text.tag_config("current_instr", background='green')

            if self.interpreter.running:
                self.source_text.configure(state=tk.DISABLED)

        # Update the tape GUI
        self.tape_text.config(state=tk.NORMAL)
        self.tape_text.delete(1.0, tk.END)

        tape_str = self.interpreter.tape.copy()
        tape_str[self.interpreter.tape_pos] = "<{}>".format(tape_str[self.interpreter.tape_pos])
        tape_str = tape_str[self.interpreter.tape_pos - 32:self.interpreter.tape_pos + 32]

        self.tape_text.insert(1.0, tape_str)
        self.tape_text.config(state=tk.DISABLED)

        # Update the current state memory usage.
        self.state_memory_text.config(state=tk.NORMAL)
        self.state_memory_text.delete(1.0, tk.END)
        self.state_memory_text.insert(1.0, "State Memory: {}KiB".format(sys.getsizeof(self.interpreter_states) / 1024))
        self.state_memory_text.config(state=tk.DISABLED)

        # Update the previous displayed states.
        self.states_text.config(state=tk.NORMAL)
        self.states_text.delete(1.0, tk.END)
        try:
            state1 = self.interpreter_states[-1].copy()
            state2 = self.interpreter_states[-2].copy()
            state1["tape"] = list(filter((0).__ne__, state1["tape"]))
            state2["tape"] = list(filter((0).__ne__, state2["tape"]))
            self.states_text.insert(1.0, "{}\n{}".format(state1, state2))
        except IndexError:
            pass
        self.states_text.config(state=tk.DISABLED)

    def get_line_offset(self, ins_pos):
        """Find where the current instruction is in the Text element by (line, column) from source offset."""
        ins_pos-=1
        total_len = 0
        line_count = 0
        current_line = 1
        lines = self.source_text.get(1.0, tk.END).split("\n")

        for line in lines:
            current_line = len(line)
            total_len += current_line
            line_count += 1

            if ins_pos <= total_len:
                break
            ins_pos -= 1

        return line_count, (ins_pos-(total_len-current_line))

    def bf_default_run(self):
        """Run the interpreter normally with the source Text."""
        if not self.interpreter.running:
            self.reset()
            self.interpreter.update(source_string=self.source_text.get(1.0, tk.END),
                                    input_string=self.input_text.get(1.0, tk.END), debug=False)
            self.interpreter.running = True

        self._bf_default_run()

    def _bf_default_run(self):
        """Recursively run and give up scheduling to the GUI."""
        if self.interpreter.i < len(self.interpreter.source_string):
            self.interpreter.step()
        else:
            self.update_gui()
            self.source_text.configure(state=tk.NORMAL)
            self.interpreter.running = False

        if self.interpreter.running:
            self.current_after = self.master.after_idle(self._bf_default_run)

    def bf_debug_start(self):
        """Start a debugging instance."""
        self.source_text.configure(state=tk.DISABLED)
        self.source_text.tag_delete("current_instr")

        if not self.interpreter.running:
            self.interpreter.update(source_string=self.source_text.get(1.0, tk.END),
                                    input_string=self.input_text.get(1.0, tk.END), debug=True)
            self.interpreter.running = True
            if self.interpreter.source_string.strip('\n     ') != '':
                self.interpreter.running = True

            self.bf_step_forward()
        else:
            self.reset()
            self.bf_debug_start()

    def bf_step_forward(self):
        """Move the current debugging instance forward one instruction."""
        if self.interpreter.running:
            state = self.interpreter.save_state()
            self.interpreter_states.append(state)

            self.interpreter.step()

            self.update_gui(debug=True)

    def bf_step_backward(self):
        """Move the current debugging instance forward one instruction."""
        if not self.interpreter.running and self.interpreter_states != []:
            self.interpreter.running = True

        if self.interpreter.running:
            if self.interpreter_states == []:
                self.pause = True
                print("Stepped to beginning.")
                return

            self.interpreter.load_state(self.interpreter_states.pop())
            self.update_gui(debug=True)

    def bf_auto_step(self, direction):
        """Move the current debugging instance forward until paused or stopped."""
        step_hertz = self.hertz_scale.get()

        if direction == "forward":
            self.bf_step_forward()
        elif direction == "backward":
            self.bf_step_backward()
        else:
            return

        if self.pause or not self.interpreter.running:
            self.auto_step_backward_btn.configure(state=tk.NORMAL)
            self.auto_step_forward_btn.configure(state=tk.NORMAL)
            self.source_text.configure(state=tk.NORMAL)
            self.pause = False

        if self.interpreter.running and not self.pause:
            self.auto_step_backward_btn.configure(state=tk.DISABLED)
            self.auto_step_forward_btn.configure(state=tk.DISABLED)
            self.current_after = self.master.after(int(1000 / step_hertz), lambda: self.bf_auto_step(direction))

    def load_bf_file(self):
        filename = filedialog.askopenfilename(defaultextension=".bf",
                                              filetypes=(("Brainfuck Script", "*.bf"), ("All Files", "*.*")))

        try:
            with open(filename, mode='r') as source_file:
                self.clear_all()
                self.source_text.delete(1.0, tk.END)

                for line in source_file:
                    self.source_text.insert(tk.END, line)
        except FileNotFoundError:
            pass

    def save_bf_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".bf",
                                                filetypes=(("Brainfuck Script", "*.bf"), ("All Files", "*.*")))

        try:
            with open(filename, mode='w') as source_file:
                source_file.writelines((self.source_text.get(1.0, tk.END)))
        except FileNotFoundError:
            pass