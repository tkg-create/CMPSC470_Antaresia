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

    env = ENV.copy()
    env.update(table.values())

    return eval(expr, {}, env)

def run_parallel(task, variables):

    expr = "".join(task["value"])

    env = ENV.copy()
    env.update(variables)

    value = eval(expr, {}, env)

    return task["name"], value

def execute(statements):

    table = SymbolTable()

    for stmt in statements:

        t = stmt["type"]

        if t == "declaration":

            value = eval_expr(stmt["value"], table)

            table.insert(stmt["name"], stmt["datatype"], value)

        elif t == "assignment":

            value = eval_expr(stmt["value"], table)

            table.update(stmt["name"], value)

        elif t == "print":

            value = eval_expr(stmt["value"], table)

            print(value)

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

        elif t == "for":

            iterable = table.lookup(stmt["iterable"])

            if iterable:

                for v in iterable.value:
                    table.update(stmt["variable"], v)

    table.display()


def main():

    filename = input("Enter Source File: ")
    filepath = os.path.join("testing source files", filename)

    parser = Parser(filepath)

    program = parser.parse()

    execute(program)


if __name__ == "__main__":
    main()