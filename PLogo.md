# PLogo

PLogo is a Python implementation of the original LOGO programming language that was developed in the late 1960s at Bolt Beranek and Newman, Inc., in Cambridge, MA by W. Feurzeig, D. Bobrow and S. Papert. Its purpose was to teach children to program. Its central feature is that it provides simple commands for moving a turtle on a surface.

There are many versions of LOGO that are distinct in many ways. This implementation more specifically follows closely Brown University's implementation with many differences:
https://cs.brown.edu/courses/bridge/1997/Resources/LogoTutorial.html

## Canvas
The (0, 0) of the canvas of the turtle is its center. The positive x-axis is to the right and the positive y-axis is to the top. The size of the canvas is fixed 800, 600 of width and height respectively.

## Drawing

PLogo has drawing commands to move the turtle and draw in the canvas. The syntax for executing a command is `<keyword>` followed by a comma with relevant arguments.

~~~
<keyword> <argument>, <argument> ...
~~~

For example, to move the turtle forward by 40 pixels and then turn left by 90° and then move forward by 30 pixels, the following will accomplish this:

~~~
fd 40 
lt 30 
fd 30
~~~

The following lists all drawing keywords.

| **Keyword**         | **Description**                                                                                                                                                   | **Argument type** | **Arguments** |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|---------------|
| `fd`, `forward`     | moves the turtle forward by specified amount of logical pixels.                                                                                                   | `float`           | `pixels`      |
| `bd`, `backward`    | moves the turtle backward by specified amount of logical pixels.                                                                                                  | `float`           | `pixels`      |
| `rt`, `right`       | turns the turtle to the right (clockwise) by specified amount of angles in degrees.                                                                               | `float`           | `angles`      |
| `lt`, `left`        | turns the turtle to the left (anti-clockwise) by specified amount of angles in degrees.                                                                           | `float`           | `angles`      |
| `setxy`             | teleports the turtle to specified x- and y- coordinates from the center of the canvas without drawing anything on the canvas. The center of the canvas is (0, 0). | `float`, `float`  | `x`, `y`      |
| `col`, `color`      | changes the color of the pen of the turtle. By default, it is `red`. See List of Colors below this table.                                                         | `str`             | `color`       |
| `fl`, `fill`        | changes the color of the canvas. See List of Colors below this table.                                                                                             | `str`             | `color`       |
| `wd`, `width`       | changes the width of the pen of the turtle.                                                                                                                       | `float`           | `width`       |
| `pu`, `penup`       | disables the pen of the turtle, thus when moved, nothing is drawn on the canvas.                                                                                  | `N/A`             | `N/A`         |
| `pd`, `pendown`     | enables the pen of the turtle, thus when moved, the turtle draws on the canvas. The pen is enabled by default.                                                    | `N/A`             | `N/A`         |
| `ht`, `hideturtle`  | hides turtle without changing the behavior of the pen.                                                                                                            | `N/A`             | `N/A`         |
| `st`, `showturtle`  | shows turtle without changing the behavior of the pen. The turtle is shown by default.                                                                            | `N/A`             | `N/A`         |
| `home`              | teleports the turtle to center (0, 0) without drawing on the canvas.                                                                                              | `N/A`             | `N/A`         |
| `cc`, `clearcanvas` | clears the canvas without moving the turtle to the center.                                                                                                        | `N/A`             | `N/A`         |
| `rst`, `reset`      | clears the canvas, moves the turtle to the center, and resets all other internal attributes returning the canvas to its initialized state.                        | `N/A`             | `N/A`         |

**List of colors supported:**`["red", "green", "blue", "orange", "yellow", "cyan", "violet", "magenta", "white", "gray", "black"]`

## Data Types
PLogo supports two data types, string and number. String can have alphabetical letters in only lowercase anywhere separated by "_" and must be enclosed with double quotes, and number can be integer or float. The interpreter does not differentiate between lower and upper case string.

## Comments
PLogo supports comments. Comments can be made by appending `;`. Any text after `;` are ignored.
~~~
; This is a comment
~~~

## Variables

PLogo provides a way to define variables that can store numbers or string and change their values. These variables can be used in conditional statements, loops, as parameter for procedures or as arguments for drawing commands. Math operations can also be done on them. 

### `make`
The syntax for declaring a variable is by using the `make` keyword:

~~~
make :<variable_name> <argument>
~~~

`<argument>` can be a string or a float or another variable that has a value. To refer to the variable, `:` is added before variable name.

For instance, to define a variable `size` with a value of `1.0`:
~~~
make :size 1.0
~~~

To refer to this variable to a procedure or a drawing commands such as `fd`:

~~~
fd :size
~~~

This will move the turtle by `:size` pixels, i.e. `1.0`.


### `change`
The value of a variable `:x` can be changed by `change` keyword:

`change :x <argument>`

`<argument>` can be a string or a float or another variable that has a value.

## Arithmetic Operations

PLogo provides the usual arithmetic operations of addition, subtraction, multiplication and division, denoted by the symbols +, -, \*, /. These operations can be done on variables, and numbers. 

For instance, going off from our previous example, to move the turtle by an additional pixel of `:size` and half of that:

~~~
fd (:size + 1) / 2
~~~

## Procedures

PLogo allows defining of custom procedures. They provide a way to encapsulate a collection of commands. Once a procedure has been created, it can be used just the way a built-in command is used.

Procedures can have parameters but cannot return anything. Procedures can be stopped by `stop` command which stops the execution of a procedure when it is reached. A procedure can be defined by using the `to` and `end` together:

~~~
to <procedure_name> <parameter>, <parameter>.. <instruction> ... end
~~~

`<parameter>` is always a variable. `stop` command can be used to stop execution of the procedure. To call the procedure, just pass in `procedure_name` with `arguments` separated by spaces. Nested procedures are possible.

Procedures have their own variable scope but also have access to the scope outside of it. This means that the procedure can overwrite values of variables outside its scope. All parameters exists inside the procedure's scope, so it can overwrite the value of its parameters inside the procedure.

However, when a variable is made inside the procedure, that variable only exists inside the procedure's scope. Therefore, changing that variable outside the scope will raise an error.

For instance to define a procedure `f` with parameter `:x` and `:y`, that moves the turtle forward by sum of `:x` and `:y`:

~~~
to f :x :y
fd :x + :y
end
~~~

To call this procedure:

~~~
f 2 2
~~~

## Loops

PLogo allows loops using the keywork `repeat`. Loops can be stopped by `stop` command which stops the execution of a loop when it is reached.

~~~
repeat <argument> [ <instruction> ... ]
~~~

`<argument>` can be an integer or a variable that has a stored integer. All `<instruction>` must be between two square brackets.

## Conditionals

PLogo supports conditional statements, executing instructions based on whether conditions are true or false. Conditional statements can be made by using `if` keyword and optionally `else` keyword can be made:

~~~
if (<expression>)
[ <instruction> ... ]
else
[ <instruction> ... ]
~~~

Like `repeat`, all instruction must be between two square brackets

`<expression>` must be enclosed in brackets and always be binary form:

~~~
<term> <conditional_operator> <term>
~~~

`<term>` must be a variable, a number, a string or a math expression. `<conditional_operator>` must be the following: `==, !=, <, <=, >, >=`





