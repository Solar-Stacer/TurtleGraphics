How to Use
==========

* This program provides a drawing environment for Turtle Graphics, an implementation of the popular geometric
  drawing tools introduced in Logo, developed by Wally Feurzeig, Seymour Papert and Cynthia Solomon in 1967.
* The interface of the Turtle rests on a custom implementation of the original Logo language in Python, named PLogo.
  Therefore, to interact with the Turtle, code written in PLogo and must accede with the syntax of PLogo. Check **PLogo
  Documentation** in **About** menu for more details pertaining to PLogo or read the **PLogo.md** (if you have the 
  source code).
* The canvas is by default black background and the pen is red.
* There are two fields to the right. The top is an editable input field that include code written in PLogo. The bottom
  is the output field that provides an indication of "Success!" in green if Turtle ran successfully, otherwise an error
  in red.
* There is a slider above the fields that controls the time interval between two instructions from 0 ms (in theory but
  not in practice) to 1 second (1000 ms). This slider thus controls Turtle speed. By default, it is set at half a
  second (500 ms).
* When **Run** button is pressed, the turtle and the canvas resets, and runs the instructions placed in the input field.
* The execution can be paused by pressing the **Pause** button, and can be played when the button is pressed again.
* The execution can be paused by pressing the **Pause** button, and can be played when the button is pressed again.
* The PLogo code can be saved as a .plogo or .txt file by navigating to **File** menu and clicking **Save PLogo**.
* Custom PLogo code can be opened and executed by navigating to **File** menu and clicking **Open PLogo**.
* The image of the canvas can be exported to a PNG by navigating to **File** menu and clicking **Export Canvas**. The
  turtle will not be rendered in the image.