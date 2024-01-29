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
import os.path

from .interpreter import BrainfuckInterpreter


class BID(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()

        super().__init__(master)

        # Set up interpreter and GUI states
        self.interpreter = BrainfuckInterpreter()
        self.interpreter_states = []
        self.tape_cell = None
        self.pause = False
        self.current_after = None

        self.breakpoint_mouse_bind = None
        self.breakpoints = []
        self.breakpoint_text_locations = []

        # Set up GUI window
        self.master.wm_title("Brainfuck Interactive Developer")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.create_widgets()
        self.update_gui()

    # GUI
    def create_widgets(self):
        self.grid(sticky=tk.E + tk.W + tk.N + tk.S)
        self.rowconfigure(1, weight=4)
        self.columnconfigure(0, weight=1)

        # Parent frames
        self.button_frame = tk.LabelFrame(self, text="")
        self.button_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.info_frame = tk.LabelFrame(self, text="")
        self.info_frame.grid(
            row=0,
            column=1,
            columnspan=2,
            padx=10,
            pady=10,
        )
        self.text_frame = tk.LabelFrame(self, text="Source")
        self.text_frame.grid(
            row=1, column=0, columnspan=3, padx=10, sticky=tk.E + tk.W + tk.S + tk.N
        )
        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=0)
        self.io_frame = tk.LabelFrame(self, text="Input/Output")
        self.io_frame.grid(row=2, column=0, padx=10, sticky=tk.W, columnspan=3)
        self.debug_frame = tk.LabelFrame(self, text="Debug Info")
        self.debug_frame.grid(row=3, column=0, padx=10, pady=10)
        self.debug_button_frame = tk.LabelFrame(self, text="")
        self.debug_button_frame.grid(row=3, column=2, padx=10, pady=10)

        # Button frame for basic operations.
        self.run_btn = tk.Button(
            self.button_frame, text="run", command=self.bf_default_run
        )
        self.run_btn.grid(row=0, column=0, pady=(5, 5), padx=(5, 0))
        self.reset_btn = tk.Button(self.button_frame, text="reset", command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=(0, 20))
        self.load_btn = tk.Button(
            self.button_frame, text="load", command=self.load_bf_file
        )
        self.load_btn.grid(row=0, column=2)
        self.save_btn = tk.Button(
            self.button_frame, text="save", command=self.save_bf_file
        )
        self.save_btn.grid(row=0, column=3)
        self.clear_btn = tk.Button(
            self.button_frame, text="clear all", command=self.clear_all
        )
        self.clear_btn.grid(row=0, column=4, padx=(20, 5))

        # Info frame for miscellaneous info.
        self.active_file_text = tk.Text(
            self.info_frame,
            background=self.master.cget("background"),
            borderwidth=0,
            height=1,
            width=40,
        )
        self.active_file_text.grid(row=0, column=0, padx=5, pady=5)
        self.active_file_text.config(state=tk.DISABLED)
        self.is_running_text = tk.Text(
            self.info_frame,
            background=self.master.cget("background"),
            borderwidth=0,
            height=1,
            width=40,
        )
        self.is_running_text.grid(row=1, column=0, padx=5, pady=5)
        self.is_running_text.config(state=tk.DISABLED)

        # Debug frame for displaying the interpreter state.
        self.states_text = tk.Text(
            self.debug_frame, height=2, width=97, background="#CCCCCC", wrap=tk.NONE
        )
        self.states_text.grid(row=0, column=0, padx=5, pady=5)
        self.state_memory_text = tk.Text(
            self.debug_frame,
            background=self.master.cget("background"),
            borderwidth=0,
            height=1,
            width=30,
        )
        self.state_memory_text.grid(row=0, column=1)
        self.tape_text = tk.Text(
            self.debug_frame,
            background="#CCCCCC",
            height=1,
            width=127,
            state=tk.DISABLED,
        )
        self.tape_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Debug Button frame for the interpreter operations.
        self.debug_btn = tk.Button(
            self.debug_button_frame, text="debug", command=self.bf_debug_start
        )
        self.debug_btn.grid(row=0, column=0, padx=(5, 20), pady=5)
        self.auto_step_backward_btn = tk.Button(
            self.debug_button_frame,
            text="<-",
            command=lambda: self.bf_auto_step("backward"),
        )
        self.auto_step_backward_btn.grid(
            row=0,
            column=1,
        )
        self.step_backward_btn = tk.Button(
            self.debug_button_frame, text="<", command=self.bf_step_backward
        )
        self.step_backward_btn.grid(row=0, column=2)
        self.pause_btn = tk.Button(
            self.debug_button_frame, text="o", command=self.toggle_pause
        )
        self.pause_btn.grid(row=0, column=3)
        self.step_forward_btn = tk.Button(
            self.debug_button_frame, text=">", command=self.bf_step_forward
        )
        self.step_forward_btn.grid(row=0, column=4)
        self.auto_step_forward_btn = tk.Button(
            self.debug_button_frame,
            text="->",
            command=lambda: self.bf_auto_step("forward"),
        )
        self.auto_step_forward_btn.grid(row=0, column=5, padx=(0, 5))
        self.hertz_scale = tk.Scale(
            self.debug_button_frame,
            from_=1,
            to_=300,
            orient=tk.HORIZONTAL,
            sliderlength=20,
        )
        self.hertz_scale.grid(row=1, column=0, pady=(0, 5), columnspan=1)
        self.break_btn = tk.Button(
            self.debug_button_frame, text="breakpoint", command=self.set_breakpoint
        )
        self.break_btn.grid(row=1, column=2, columnspan=5, padx=(0, 5))

        # Text frame for modifying the source.
        self.source_text = tk.Text(self.text_frame)
        self.source_text.bind("<Control-r>", lambda _: self.bf_default_run)
        self.source_text.config(background="#CCCCCC")
        self.source_text.grid(row=0, column=0, sticky=tk.E + tk.W + tk.S + tk.N)

        # Output Frame for displaying the results of running the BF program  and input.
        self.input_text = tk.Text(self.io_frame)
        self.input_text.bind("<Control-r>", lambda _: self.bf_default_run)
        self.input_text.config(background="#CCCCCC", height=10)
        self.input_text.grid(row=0, column=0, sticky=tk.E + tk.W + tk.S + tk.N)
        self.output_text = tk.Text(self.io_frame)
        self.output_text.config(background="#CCCCCC", height=10, state=tk.DISABLED)
        self.output_text.grid(row=0, column=1, sticky=tk.E + tk.W)

    def update_gui(self, debug=False):
        """Update GUI Elements. (usually called after an interpreter state change)"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, self.interpreter.output_string)
        self.output_text.config(state=tk.DISABLED)

        # Update to display whether running or not.
        self.is_running_text.config(state=tk.NORMAL)
        if self.interpreter.running:
            self.is_running_text.delete(1.0, tk.END)
            self.is_running_text.insert(1.0, "Now Running.")
        else:
            self.is_running_text.delete(1.0, tk.END)
        self.is_running_text.config(state=tk.DISABLED)

        # Place the breakpoint markers
        for i, bp in enumerate(self.breakpoint_text_locations):
            self.source_text.tag_delete("bp{}".format(i))
            self.source_text.tag_add("bp{}".format(i), index1=bp)
            self.source_text.tag_config("bp{}".format(i), background="red")

        # Place the markers for current debugger instructions
        if debug and self.interpreter.running:
            self.source_text.configure(state=tk.NORMAL)

            self.source_text.tag_delete("done_instr")
            self.source_text.tag_delete("next_instr")
            if self.interpreter.i <= len(self.interpreter.source_string) - 1:
                if (
                    self.interpreter.source_string[self.interpreter.i] == "["
                    and self.interpreter.source_string[self.interpreter_states[-1]["i"]]
                    == "]"
                ):
                    self.source_text.tag_add(
                        "done_instr",
                        index1="{}.{}".format(
                            *self.get_line_offset(self.interpreter_states[-1]["i"])
                        ),
                    )
                    self.source_text.tag_config("done_instr", background="green")
                else:
                    self.source_text.tag_add(
                        "done_instr",
                        index1="{}.{}".format(
                            *self.get_line_offset(self.interpreter.i - 1)
                        ),
                    )
                    self.source_text.tag_config("done_instr", background="green")

                self.source_text.tag_add(
                    "next_instr",
                    index1="{}.{}".format(*self.get_line_offset(self.interpreter.i)),
                )
                self.source_text.tag_config("next_instr", background="blue")

            self.source_text.configure(state=tk.DISABLED)

        # Update the tape GUI
        self.tape_text.config(state=tk.NORMAL)
        self.tape_text.delete(1.0, tk.END)

        tape_str = self.interpreter.tape.copy()
        tape_str[self.interpreter.tape_pos] = "<{}>".format(
            tape_str[self.interpreter.tape_pos]
        )
        if self.interpreter.tape_size - self.interpreter.tape_pos < 32:
            start = self.interpreter.tape_pos - (
                self.interpreter.tape_size - self.interpreter.tape_pos
            )
            end = self.interpreter.tape_pos + (
                self.interpreter.tape_size - self.interpreter.tape_pos
            )
        else:
            start = self.interpreter.tape_pos - 32
            end = self.interpreter.tape_pos + 32

        tape_str = tape_str[start:end]

        self.tape_text.insert(1.0, tape_str)
        self.tape_text.config(state=tk.DISABLED)

        # Update the current state memory usage.
        self.state_memory_text.config(state=tk.NORMAL)
        self.state_memory_text.delete(1.0, tk.END)
        self.state_memory_text.insert(
            1.0,
            "State Memory: {}KiB".format(sys.getsizeof(self.interpreter_states) / 1024),
        )
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

    def get_line_offset(self, source_offset):
        """Find where the current instruction is in the Text element by (line, column) from source offset."""
        total_len = 0
        line_count = 0
        current_line = 1
        lines = self.source_text.get(1.0, tk.END).split("\n")

        for line in lines:
            current_line = len(line)
            total_len += current_line
            line_count += 1

            if source_offset <= total_len:
                break
            source_offset -= 1

        return line_count, (source_offset - (total_len - current_line))

    def get_source_offset(self, line_offset):
        y, x = line_offset.split(".")
        y, x = int(y), int(x)

        total_len = 0
        line_count = 0
        lines = self.source_text.get(1.0, tk.END).split("\n")

        for line in lines:
            line_count += 1
            if line_count == y:
                total_len += x
                return total_len

            total_len += len(line)

    def toggle_pause(self):
        self.pause = not self.pause

    def clear_all(self):
        """Clear the GUI Text elements and resets the interpreter."""
        answer = messagebox.askyesno(
            "Full Reset",
            "This will completely reset the IDE, including your source.\nAre you sure?",
        )

        if answer:
            self.source_text.delete(1.0, tk.END)
            self.input_text.delete(1.0, tk.END)
            self.tape_text.delete(1.0, tk.END)
            self.active_file_text.delete(1.0, tk.END)

            self.breakpoints = []
            self.breakpoint_text_locations = []

            self.reset()

    def reset(self):
        """Stops and resets the interpreter and debug elements."""
        if self.current_after is not None:
            self.master.after_cancel(self.current_after)
        self.current_after = None

        # Reset locked GUI elements.
        self.run_btn.config(state=tk.NORMAL)
        self.source_text.configure(state=tk.NORMAL)
        self.auto_step_forward_btn.configure(state=tk.NORMAL)
        self.auto_step_backward_btn.configure(state=tk.NORMAL)
        self.source_text.tag_delete("done_instr")
        self.source_text.tag_delete("next_instr")

        # Reset the interpreter and GUI related states
        self.interpreter_states = []
        self.interpreter.reset()
        self.update_gui()

    # Run
    def bf_default_run(self):
        """Run the interpreter normally with the source Text."""
        if not self.interpreter.running:
            self.reset()
            self.interpreter.update(
                source_string=self.source_text.get(1.0, tk.END)[:-1],
                input_string=self.input_text.get(1.0, tk.END)[:-1],
                debug=False,
            )
            self.interpreter.running = True
        else:
            self.source_text.tag_delete("done_instr")
            self.source_text.tag_delete("next_instr")
            self.interpreter_states = []
            self.update_gui()

        self.run_btn.config(state=tk.DISABLED)
        self._bf_default_run()

    def _bf_default_run(self):
        """Recursively run and give up scheduling to the GUI."""
        if self.interpreter.i < len(self.interpreter.source_string):
            self.interpreter.step()
        else:
            self.interpreter.running = False

        if self.interpreter.running:
            self.current_after = self.master.after_idle(self._bf_default_run)
        else:
            self.run_btn.config(state=tk.NORMAL)
            self.update_gui()

    # Debug
    def bf_debug_start(self):
        """Start a debugging instance."""
        self.source_text.configure(state=tk.DISABLED)
        self.source_text.tag_delete("done_instr")
        self.source_text.tag_delete("next_instr")

        if not self.interpreter.running:
            self.interpreter.update(
                source_string=self.source_text.get(1.0, tk.END)[:-1],
                input_string=self.input_text.get(1.0, tk.END)[:-1],
                debug=True,
            )
            self.interpreter.running = True
            if self.interpreter.source_string.strip("\n     ") != "":
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

        # If active, continue stepping. If we're at a breakpoint, stop.
        if (
            self.interpreter.running
            and not self.pause
            and self.interpreter.i not in self.breakpoints
        ):
            self.auto_step_backward_btn.configure(state=tk.DISABLED)
            self.auto_step_forward_btn.configure(state=tk.DISABLED)
            self.current_after = self.master.after(
                int(1000 / step_hertz), lambda: self.bf_auto_step(direction)
            )
        # Unlock GUI as the debugger is inactive.
        else:
            self.auto_step_backward_btn.configure(state=tk.NORMAL)
            self.auto_step_forward_btn.configure(state=tk.NORMAL)

            if not self.pause:
                self.source_text.configure(state=tk.NORMAL)
            self.pause = False

    def set_breakpoint(self):
        """Set a breakpoint to stop auto-stepping."""
        self.source_text.configure(background="#CCFFCC")
        self.breakpoint_mouse_bind = self.source_text.bind(
            "<Button-1>", self._set_breakpoint
        )

    def _set_breakpoint(self, event):
        self.source_text.configure(background="#CCCCCC")
        self.source_text.unbind("<Button-1>", self.breakpoint_mouse_bind)
        click_location = self.source_text.index("@{},{}".format(event.x, event.y))
        source_location = self.get_source_offset(click_location) + 1
        if click_location not in self.breakpoint_text_locations:
            self.breakpoint_text_locations.append(click_location)
            self.breakpoints.append(source_location)
        else:
            for i, bp in enumerate(self.breakpoints):
                if bp == source_location:
                    self.source_text.tag_delete("bp{}".format(i))
                    del self.breakpoint_text_locations[i]
                    del self.breakpoints[i]
        self.update_gui()

    # File I/O
    def load_bf_file(self):
        """Load a brainfuck file from disk."""
        filename = filedialog.askopenfilename(
            defaultextension=".bf",
            filetypes=(("Brainfuck Script", "*.bf"), ("All Files", "*.*")),
        )

        try:
            with open(filename, mode="r") as source_file:
                self.reset()
                self.source_text.delete(1.0, tk.END)

                for line in source_file:
                    self.source_text.insert(tk.END, line)

            self.active_file_text.config(state=tk.NORMAL)
            self.active_file_text.delete(1.0, tk.END)
            self.active_file_text.insert(1.0, os.path.split(filename)[-1])
            self.active_file_text.config(state=tk.DISABLED)
        except FileNotFoundError:
            pass

    def save_bf_file(self):
        """Save a brainfuck file from disk."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".bf",
            filetypes=(("Brainfuck Script", "*.bf"), ("All Files", "*.*")),
        )

        try:
            with open(filename, mode="w") as source_file:
                source_file.writelines((self.source_text.get(1.0, tk.END)))

            self.active_file_text.config(state=tk.NORMAL)
            self.active_file_text.delete(1.0, tk.END)
            self.active_file_text.insert(1.0, os.path.split(filename)[-1])
            self.active_file_text.config(state=tk.DISABLED)
        except FileNotFoundError:
            pass
