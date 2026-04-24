from parser import Parser
from tokenizer import BUILTIN_FUNCTIONS, BOOLEAN_LITERALS
from concurrent.futures import ProcessPoolExecutor
import math
import os


# Symbol Table Entry
class Symbol:

    def __init__(self, name, datatype, value):
        self.name = name
        self.datatype = datatype
        self.value = value

    def __str__(self):
        return f"{self.name:<15}{self.datatype:<10}{self.value}"


class SymbolTable:

    def __init__(self):
        self.symbols = {}

    def insert(self, name, datatype, value):

        if name in self.symbols:
            raise Exception(f"Variable '{name}' already declared")

        self.symbols[name] = Symbol(name, datatype, value)

    def lookup(self, name):

        return self.symbols.get(name)

    def update(self, name, value):

        if name not in self.symbols:
            raise Exception(f"Variable '{name}' not declared")

        self.symbols[name].value = value

    def values(self):

        return {k: v.value for k, v in self.symbols.items()}

    def display(self):

        print("\nSymbol Table")
        print("-----------------------------")

        for s in self.symbols.values():
            print(s)


# Built-in math functions
ENV = {
    "true": True,
    "false": False,
    "sqrt": math.sqrt,
    "pow": pow,
    "log": math.log,
    "abs": abs,
    "factorial": math.factorial,
    "circ_area": lambda r: math.pi * r * r,
    "tri_area": lambda b, h: (b * h) / 2,
    "rect_area": lambda w, h: w * h,
    "sph_vol": lambda r: (4/3) * math.pi * r**3
}


def eval_expr(tokens, table):

    expr = "".join(tokens)

    env = dict(ENV)
    env.update(table.values())

    return eval(expr, {"__builtins__": {}}, env)


def run_parallel(task, variables):

    expr = "".join(task["value"]).replace(" ", "")

    env = dict(ENV)
    env.update(variables)

    return task["name"], eval(expr, {"__builtins__": {}}, env)


def execute(statements, table=None):

    root_call = False

    if table is None:
        table = SymbolTable()
        root_call = True

    for stmt in statements:

        t = stmt["type"]

        # Declaration
        if t == "declaration":

            value = eval_expr(stmt["value"], table)
            table.insert(stmt["name"], stmt["datatype"], value)

        # Assignment
        elif t == "assignment":

            value = eval_expr(stmt["value"], table)
            table.update(stmt["name"], value)

        # Print
        elif t == "print":

            value = eval_expr(stmt["value"], table)
            print(value)

        # Parallel
        elif t == "parallel":

            tasks = stmt["body"]

            with ProcessPoolExecutor() as pool:
                results = list(
                    pool.map(
                        run_parallel,
                        tasks,
                        [table.values()] * len(tasks)
                    )
                )

            for name, value in results:
                table.update(name, value)

        # For Loop
        elif t == "for":

            iterable_symbol = table.lookup(stmt["iterable"])

            if iterable_symbol is None:
                raise Exception(f"Iterable '{stmt['iterable']}' not declared")

            iterable = iterable_symbol.value

            # declare loop variable if needed
            if not table.lookup(stmt["variable"]):
                table.insert(stmt["variable"], "int", 0)

            for v in iterable:
                table.update(stmt["variable"], v)
                execute(stmt["body"], table)

        # If / Else
        elif t == "if":

            condition = eval_expr(stmt["condition"], table)

            if condition:
                execute(stmt["body"], table)
            elif stmt.get("else"):
                execute(stmt["else"], table)

        # While Loop
        elif t == "while":

            while eval_expr(stmt["condition"], table):
                execute(stmt["body"], table)

        # Unknown
        else:
            print("Warning: Unknown statement", stmt)

    if root_call:
        table.display()


def main():

    filename = input("Enter Source File: ")
    filepath = os.path.join("testing source files", filename)

    parser = Parser(filepath)

    program = parser.parse()

    execute(program)


if __name__ == "__main__":
    main()
