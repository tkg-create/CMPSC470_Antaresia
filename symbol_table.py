from tokenizer_testing import BOOLEAN_LITERALS, BUILTIN_FUNCTIONS
from parser import Parser
import re
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


# Symbol Table
class SymbolTable:

    def __init__(self, size=50):
        self.size = size
        self.table = [[] for _ in range(size)]

    def hash(self, key):
        return sum(ord(c) for c in key) % self.size

    def insert(self, name, datatype, value):

        index = self.hash(name)

        for symbol in self.table[index]:
            if symbol.name == name:
                raise Exception(f"Variable '{name}' already declared")

        self.table[index].append(Symbol(name, datatype, value))

    def lookup(self, name):

        index = self.hash(name)

        for symbol in self.table[index]:
            if symbol.name == name:
                return symbol

        return None

    def update(self, name, value):

        symbol = self.lookup(name)

        if symbol is None:
            raise Exception(f"Variable '{name}' not declared")

        symbol.value = value

    def display(self):

        print("\nSymbol Table")
        print("-----------------------------------")
        print(f"{'Name':<15}{'Type':<10}Value")
        print("-----------------------------------")

        for bucket in self.table:
            for symbol in bucket:
                print(symbol)


# Function Evaluation
def evaluate_function(tokens, table):

    name = tokens[0]

    args = []
    current = ""

    for t in tokens[2:-1]:

        if t == ",":
            args.append(current)
            current = ""
        else:
            current += t

    if current:
        args.append(current)

    parsed_args = []

    for arg in args:

        if re.fullmatch(r"-?\d+", arg):
            parsed_args.append(int(arg))

        elif re.fullmatch(r"-?\d+\.\d+", arg):
            parsed_args.append(float(arg))

        else:
            symbol = table.lookup(arg)

            if symbol is None:
                raise Exception(f"Undefined variable '{arg}'")

            parsed_args.append(symbol.value)

    if name == "pow":
        return math.pow(parsed_args[0], parsed_args[1])

    if name == "factorial":
        return math.factorial(parsed_args[0])

    if name == "sqrt":
        return math.sqrt(parsed_args[0])

    if name == "log":
        return math.log10(parsed_args[0])

    if name == "abs":
        return abs(parsed_args[0])

    if name == "circ_area":
        r = parsed_args[0]
        return math.pi * r * r

    if name == "tri_area":
        return (parsed_args[0] * parsed_args[1]) / 2

    if name == "rect_area":
        return parsed_args[0] * parsed_args[1]

    if name == "sph_vol":
        r = parsed_args[0]
        return (4 / 3) * math.pi * r ** 3

    raise Exception("Unknown function")


# Boolean Evaluation
def evaluate_boolean(tokens, table):

    left, operator, right = tokens

    if table.lookup(left):
        left = table.lookup(left).value
    else:
        left = float(left)

    if table.lookup(right):
        right = table.lookup(right).value
    else:
        right = float(right)

    if operator == ">":
        return left > right

    if operator == "<":
        return left < right

    if operator == "==":
        return left == right

    if operator == "!=":
        return left != right

    if operator == ">=":
        return left >= right

    if operator == "<=":
        return left <= right


# Value Evaluation
def evaluate_value(datatype, tokens, table):

    value_str = "".join(tokens)

    # Boolean expression
    if datatype == "bool" and len(tokens) == 3:
        return evaluate_boolean(tokens, table)

    # Function call
    if tokens[0] in BUILTIN_FUNCTIONS:
        return evaluate_function(tokens, table)

    if datatype == "int":
        if re.fullmatch(r"-?\d+", value_str):
            return int(value_str)

    if datatype == "float":
        if re.fullmatch(r"-?\d+\.\d+", value_str):
            return float(value_str)

    if datatype == "string":
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str.strip('"')

    if datatype == "bool":
        if value_str in BOOLEAN_LITERALS:
            return value_str == "true"

    if datatype == "vector":
        if value_str.startswith("["):
            return eval(value_str)

    if datatype == "matrix":
        if value_str.startswith("[["):
            return eval(value_str)

    raise Exception(f"Type error: invalid value '{value_str}' for type {datatype}")


# Process Parsed Statements
def process_program(statements):

    table = SymbolTable()
    assignments = []

    for stmt in statements:

        if stmt["type"] == "declaration":

            datatype = stmt["datatype"]
            name = stmt["name"]

            try:

                value = evaluate_value(datatype, stmt["value"], table)

                table.insert(name, datatype, value)

            except Exception as e:
                print(e)

        elif stmt["type"] == "assignment":

            assignments.append(stmt)

    print("\nState Before Updates")
    table.display()

    for stmt in assignments:

        name = stmt["name"]
        symbol = table.lookup(name)

        if symbol is None:
            print(f"Error: variable '{name}' not declared")
            continue

        try:

            value = evaluate_value(symbol.datatype, stmt["value"], table)

            table.update(name, value)

        except Exception as e:
            print(e)

    print("\nState After Updates")
    table.display()


# Main
def main():

    filename = input("Enter Source File: ")
    filepath = os.path.join("testing source files", filename)

    parser = Parser(filepath)

    statements = parser.parse()

    process_program(statements)


if __name__ == "__main__":
    main()