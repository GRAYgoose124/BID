# Brainfuck Interactive Developer
BID is an IDE for [brainfuck](https://esolangs.org/wiki/Brainfuck) designed to aid in learning about debugging and 
interpreter operation. It is meant to be an all-in-one learning environment, including tutorials and practice.

Brainfuck is a great language to learn about these topics. It is easy to understand because of its minimal form, but it
lays a solid foundation for understanding how an interpreter works. It's possible to use it to do the same with 
debugging and compilation.


## Running
BID requires `Python 3.5+` to run correctly and BID currently depends on `tkinter`.

For Debian-based distributions you can install python3 and tkinter in this fashion:

`sudo apt-get install python3 python3-tk`


## About the IDE
### The Debugger
The debugger has the basic functionality of stepping forwards and backwards as well as auto-stepping. 

To use the debugger. You first click debug. This will start the debugging process and execute the first instruction. 
From that point on, you may step forward or backward or auto-step. These are performed by the arrow buttons next to the
debug button. In order from left to right they are: 

`auto-step backward, step backward, pause auto-step, step forward, auto-step forward`

To understand the debugger, first know that it will display the just finished instruction as well as the next 
instruction to run in green and blued respectively. Next, at the bottom the window, the bottom-most textbox that starts
filled in with `...0 0 <0> 0 0...` is displaying the brainfuck tape for the currently debugged program at that moment.
The angle brackets (<>) denote the active cell. This is the cell which brainfuck is currently using with `+-,.[]`.

Above the tape textbox is the state textbox. It displays the previous two states, before the last executed instruction
ran. This includes the tape, where the interpreter was on the tape, the current loop frames, the 
input/output strings and so on.

The breakpoint button allows you to select a location in the source where you would like the program to stop if you are
auto-stepping. This allows you to quickly run through unimportant code while not missing what you intended. To use it, 
click where you would like the program to stop after you click the button, multiple points can be set. The breakpoints
appear in red.

In order to implement simple backsteps we save every state of the debugged program. This allows us to also build state
trees that we can use to more precisely examine what happened in that time frame.

## About Brainfuck



## Current Features
* Input/Source editing, loading, and saving
* Debugger has forward/backward stepping, variable speed auto-stepping, and breakpoints
* Rudimentary tape and state visualization


## Planned Features
* Visualization of the interpreter running
* Compilation to Python and C (Including optimizations)
* Tutorial Interface and step-by-step guide (BF Examples included)
* More Debugging features
* Add custom BF commands
* Variable BF Interpreter support (default to reference: far-left init tape, 30k cells, etc)


## Information about the Source



## FAQ and Concerns
* The name is offensive!

Learning is learning, don't be petty!