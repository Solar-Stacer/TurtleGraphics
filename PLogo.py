import rich
from lark import Lark, lark
from lark.visitors import Interpreter, v_args


class StopSignal(Exception):
    pass


class PLogoInterpreter(Interpreter):
    """
    The Lark Trees have “data” and “children” in attributes of the same name. Trees can be hashed and compared.
    Attributes:
        data – The name of the rule or alias
        children – List of matched sub-rules and terminals

    The Lark Tokens are a string with meta-information, that is produced by the lexer.
        type: str - Name of the token (as specified in grammar)
        value: Any - Value of the token (redundant, as token.value == token will always be true)

    Interpreter walks the tree starting at the root. It visits the tree, starting
    with the root and finally the leaves (top-down). For each tree node, it calls its methods (provided by user via
    inheritance) according to tree.data.

    Unlike Transformer and Visitor, the Interpreter doesn’t automatically visit its sub-branches. The user has to
    explicitly call visit, visit_children, or use the @visit_children_decor. This allows the user to implement
    branching and loops.

    visit(tree: Tree[_Leaf_T]) -> _Return_T
        Visit the tree, starting with the root and finally the leaves (top-down).

    visit_children(tree: Tree[_Leaf_T]) -> List
        Visit all the children of this tree and return the results as a list.

    v_args is a convenience decorator factory for modifying the behavior of user-supplied callback methods of Transformer
    or Interpreter classes. By default, the callback methods for these classes accept one argument - a list of the
    node’s children. v_args can modify this behavior. When used on the class definition, it applies to all the
    callback methods inside it.
    Parameters:
        inline: bool, optional – Children are provided as *args instead of a list argument (not recommended for very
        long lists).

    """

    variable_scope_stack = [{}]
    procedure_environment = {}
    function_queue = []

    @staticmethod
    def lookup_variable_in_scope(name: str):
        for scope in reversed(PLogoInterpreter.variable_scope_stack):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable {name} is not defined.")

    @staticmethod
    def clearEnvironment():
        PLogoInterpreter.variable_scope_stack = [{}]
        PLogoInterpreter.procedure_environment.clear()
        PLogoInterpreter.function_queue.clear()

    # /// NON-TERMINAL BACKEND FUNCTIONS /// #

    def arguments(self, tree):
        return self.visit_children(tree)

    @v_args(inline=True)
    def arg(self, tree):
        return self.visit(tree)

    @v_args(inline=True)
    def parameter(self, items: lark.Tree):
        return self.visit(items)

    @v_args(inline=True)
    def instruction(self, tree: lark.Tree):
        return self.visit(tree)

    @v_args(inline=True)
    def variable(self, items: lark.Tree):
        name = self.visit(items)
        return self.lookup_variable_in_scope(name)

    @v_args(inline=True)
    def string(self, items):
        return str(items)[1:-1]

    @v_args(inline=True)
    def variable_name(self, items: lark.Tree):
        return str(items)

    @v_args(inline=True)
    def procedure_name(self, items):
        return str(items)

    @v_args(inline=True)
    def stop(self):
        raise StopSignal

    # /// PROGRAMMING COMMANDS /// #

    @v_args(inline=True)
    def call_procedure(self, proc: lark.Tree, args: lark.Tree):
        name = str(self.visit(proc))
        if name not in PLogoInterpreter.procedure_environment:
            raise Exception(f"Procedure {name} is not defined.")
        function_args = PLogoInterpreter.procedure_environment[name]["params"]
        call_function_args = []
        args = self.visit(args)
        for arg in args:
            call_function_args.append(arg)
        if len(call_function_args) != len(function_args):
            raise Exception(f"Procedure {name} only expects {len(function_args)} "
                            f"parameter but {len(call_function_args)} were given.")
        local_scope = {}
        for i in range(len(function_args)):
            local_scope.update({function_args[i]: call_function_args[i]})
        PLogoInterpreter.variable_scope_stack.append(local_scope)
        try:
            for ins in PLogoInterpreter.procedure_environment[name]["body"]:
                self.visit(ins)
        except StopSignal:
            pass
        PLogoInterpreter.variable_scope_stack.pop()

    @v_args(inline=True)
    def make(self, variable_name: lark.Tree, variable_value: lark.Tree):
        name = str(self.visit(variable_name))
        value = self.visit(variable_value)
        if name in PLogoInterpreter.variable_scope_stack[-1].keys():
            raise Exception(f"Variable {name} is already defined.")
        PLogoInterpreter.variable_scope_stack[-1].update({name: value})

    @v_args(inline=True)
    def change(self, variable_name: lark.Tree, variable_value: lark.Tree):
        name = self.visit(variable_name)
        value = self.visit(variable_value)
        for scope in reversed(PLogoInterpreter.variable_scope_stack):
            if name in scope:
                scope[name] = value
                return
        raise Exception(f"Variable {name} is not defined.")

    @v_args(inline=True)
    def to(self, *items):
        to_tree = iter(items)
        proc_name = self.visit(next(to_tree))
        instructions = []
        parameter = []
        while True:
            try:
                ins = next(to_tree)
            except StopIteration:
                break
            if isinstance(ins, lark.Tree):
                if ins.data == "parameter":
                    arg_name = self.visit(ins)
                    parameter.append(arg_name)
                elif ins.data != "end":
                    instructions.append(ins)
        PLogoInterpreter.procedure_environment.update({proc_name: {"params": parameter, "body": instructions}})

    @v_args(inline=True)
    def repeat(self, *items):
        iteration_count = self.visit(items[0])
        if not isinstance(iteration_count, (int, float)):
            raise Exception(f"Repeat count {iteration_count} must be an integer type.")
        if iteration_count.is_integer():
            iteration_count = int(iteration_count)
        else:
            raise Exception(f"Repeat count {iteration_count} must be an integer.")
        try:
            for i in range(iteration_count):
                for ins in items[1:]:
                    self.visit(ins)
        except StopSignal:
            pass

    @v_args(inline=True)
    def if_else_relation(self, *items):
        if_else_tree = iter(items)
        expression_eval = self.visit(next(if_else_tree))
        run_if = expression_eval
        if_chunk = next(if_else_tree)
        try:
            _else_chunk = next(if_else_tree)
        except StopIteration:
            if run_if:
                self.visit(if_chunk)
            return
        if run_if:
            self.visit(if_chunk)
        else:
            self.visit(_else_chunk)

    @v_args(inline=True)
    def conditional_expression(self, *items) -> bool | None:
        value_left = self.visit(items[0]) if isinstance(items[0], lark.Tree) else items[0]
        operator = str(items[1])
        value_right = self.visit(items[2]) if isinstance(items[2], lark.Tree) else items[2]
        match operator:
            case "==":
                return value_left == value_right
            case "!=":
                return value_left != value_right
            case "<":
                return value_left < value_right
            case "<=":
                return value_left <= value_right
            case ">":
                return value_left > value_right
            case ">=":
                return value_left >= value_right
        raise AssertionError("Unknown relational operator")

    # /// MATH EXPRESSION /// #

    @v_args(inline=True)
    def add(self, *items):
        return self.visit(items[0]) + self.visit(items[1])

    @v_args(inline=True)
    def sub(self, *items):
        return self.visit(items[0]) - self.visit(items[1])

    @v_args(inline=True)
    def mul(self, *items):
        return self.visit(items[0]) * self.visit(items[1])

    @v_args(inline=True)
    def div(self, *items):
        return self.visit(items[0]) / self.visit(items[1])

    @v_args(inline=True)
    def pos(self, items):
        return self.visit(items)

    @v_args(inline=True)
    def neg(self, items):
        return self.visit(items) * -1

    @v_args(inline=True)
    def expr(self, items):
        return self.visit(items)

    @v_args(inline=True)
    def term(self, items):
        return self.visit(items)

    @v_args(inline=True)
    def factor(self, items):
        return self.visit(items)

    @v_args(inline=True)
    def number(self, items: lark.Token) -> float:
        return float(items)

    # /// TURTLE CONTROLS /// #

    @v_args(inline=True)
    def fd(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'fd' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, str):
            raise TypeError("Argument for 'fd' must be a float.")
        PLogoInterpreter.function_queue.append(["fd", value])

    @v_args(inline=True)
    def bd(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'bd' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, str):
            raise TypeError("Argument for 'bd' must be a float.")
        PLogoInterpreter.function_queue.append(["bd", value])

    @v_args(inline=True)
    def rt(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'rt' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, str):
            raise TypeError("Argument for 'rt' must be a float.")
        PLogoInterpreter.function_queue.append(["rt", value])

    @v_args(inline=True)
    def lt(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'lt' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, str):
            raise TypeError("Argument for 'lt' must be a float.")
        PLogoInterpreter.function_queue.append(["lt", value])

    @v_args(inline=True)
    def setxy(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 2:
            raise Exception(f"Procedure 'setxy' expects exactly two arguments. Got {len(args)} instead.")
        x = args[0]
        y = args[1]
        if isinstance(x, str) or isinstance(y, str):
            raise TypeError("Arguments for 'setxy' must be a float.")
        PLogoInterpreter.function_queue.append(["setxy", x, y])

    @v_args(inline=True)
    def col(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'col' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, float):
            raise TypeError("Argument for 'col' must be a string.")
        PLogoInterpreter.function_queue.append(["col", value])

    @v_args(inline=True)
    def wd(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'wd' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, str):
            raise TypeError("Argument for 'wd' must be a float.")
        PLogoInterpreter.function_queue.append(["wd", value])

    @v_args(inline=True)
    def fl(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 1:
            raise Exception(f"Procedure 'fl' expects exactly one argument. Got {len(args)} instead.")
        value = args[0]
        if isinstance(value, float):
            raise TypeError("Argument for 'fl' must be a string.")
        PLogoInterpreter.function_queue.append(["fl", value])

    @v_args(inline=True)
    def pu(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'pu' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["pu"])

    @v_args(inline=True)
    def pd(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'pd' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["pd"])

    @v_args(inline=True)
    def ht(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'ht' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["ht"])

    @v_args(inline=True)
    def st(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'st' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["st"])

    @v_args(inline=True)
    def home(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'home' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["home"])

    @v_args(inline=True)
    def cc(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'cc' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["cc"])

    @v_args(inline=True)
    def rst(self, args: lark.Tree):
        args = self.visit(args)
        if len(args) != 0:
            raise Exception(f"Procedure 'rst' expects exactly no argument. Got {len(args)} instead.")
        PLogoInterpreter.function_queue.append(["rst"])


class PLogoObject:
    def __init__(self):
        self.grammar = \
            r"""
            %import common.WS
            %import common.ESCAPED_STRING
            %import common.CNAME
            %import common.FLOAT
            %import common.INT
            %ignore COMMENT
            %ignore WS
            
            start: (instruction)+ 
            
            instruction: fd | bd | rt | lt | setxy | col | fl | wd | pu | pd | ht | st | cc | home | rst
                        | repeat
                        | make
                        | to
                        | change
                        | call_procedure
                        | if_else_relation
            
            // DRAWING COMMANDS
            fd: ("fd" | "forward") arguments
            bd: ("bd" | "backward" ) arguments
            rt: ("rt" | "right" ) arguments
            lt: ("lt" | "left" ) arguments
            setxy: "setxy" arguments
            col: ("col" | "color") arguments
            fl: ( "fl" | "fill" ) arguments
            wd: ( "wd" | "width" ) arguments
            pu: ( "pu" | "penup" ) arguments
            pd: ( "pd" | "pendown" ) arguments
            ht: ( "ht" | "hideturtle" ) arguments
            st: ( "st" | "showturtle" ) arguments
            cc: ( "cc" | "clearcanvas" ) arguments
            home: "home" arguments
            rst: ("rst" | "reset" ) arguments
            
            //PROGRAMMING KEYWORDS
            repeat: "repeat" (arg) "[" (instruction | stop)* "]" 
            make: "make" ":" variable_name (arg)
            to: "to" procedure_name [parameter+] instruction* [stop] "end"
            change: "change" ":" variable_name (arg)
            stop: "stop"
            
            call_procedure: procedure_name arguments
            if_else_relation: "if" "(" conditional_expression ")" if_chunk [else_chunk] 
            if_chunk: "[" (instruction | stop)* "]"
            else_chunk: "else" "[" (instruction | stop)* "]"
            
            conditional_expression: (arg) RELATIONAL (arg)
            procedure_name: CNAME
            variable_name:  CNAME
            
            variable: ":" variable_name
            arguments: [arg ("," arg)*]
            arg: string | expr
            parameter: ":" variable_name
            
            // MATH EXPRESSIONS AND NUMBERS
            expr: (expr "+" term) -> add
                | (expr "-" term) -> sub
                | term
    
            term: (term "*" factor) -> mul
                | (term "/" factor) -> div
                | factor

            factor: number
                   | variable
                   | "(" expr ")"
                   | "-" factor -> neg
                   | "+" factor -> pos
            
            // DATA TYPES
            number: NUMBER
            string: ESCAPED_STRING
            
            // TERMINALS
            RELATIONAL:  ("==" | "!=" | "<" | "<=" | ">" | ">=")
            STRING: ESCAPED_STRING | NUMBER
            NUMBER: FLOAT | INT
            COMMENT: /;.*/
            
            """

        """
        LALR(1) stands for Left-to-right parsing order, Rightmost derivation (bottom-up), Lookahead of 1 token.
        
        LALR(1) parser in Lark only supports 'basic' or 'contextual' lexers. To make it explicit that the lexer must be
        "contextual", lexer="contextual" is set.
        
        Lark extends the traditional YACC-based architecture with a contextual lexer, which processes feedback from the 
        parser. The contextual lexer communicates with the parser, and uses the parser’s lookahead prediction to narrow 
        its choice of terminals. So at each point, the lexer only matches the subgroup of terminals that are legal at 
        that parser state, instead of all of the terminals. It is effective at resolving common terminal collisions, 
        and allows one to parse languages that LALR(1) was previously incapable of parsing.
        
        maybe_placeholders=True makes sure that None is not generated when there is no match.
        
        """
        self.parser = Lark(self.grammar, parser="lalr", lexer="contextual", debug=True, maybe_placeholders=False)
        # self.parser = Lark(self.grammar, parser="earley", debug=True, maybe_placeholders=False)
        self.parsed_tree = None
        self.executeTransform = PLogoInterpreter()

    def executePLogo(self, plogo_code):
        self.parsed_tree = self.parser.parse(plogo_code)
        if __name__ == "__main__":
            rich.print(self.parsed_tree)
        PLogoInterpreter.clearEnvironment()
        self.executeTransform.transform(self.parsed_tree)
        if __name__ == "__main__":
            for proc, *args in self.executeTransform.function_queue:
                print(proc, *args)
        return self.executeTransform.function_queue


if __name__ == "__main__":
    code = """
    make :c 54
    fd :c * 3
    """
    PLogoInt = PLogoObject()
    PLogoInt.executePLogo(code)
