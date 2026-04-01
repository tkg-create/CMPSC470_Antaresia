import re
from collections import Counter

# Antaresia Language Definitions
DATA_TYPES = {
    "int", "float", "bool", "vector", "matrix", "string"
}

RESERVED_WORDS = {
    "if", "else", "while", "for", "return",
    "function", "print", "parallel", "in"
}

BUILTIN_FUNCTIONS = {
    "pow", "factorial", "sqrt", "log", "abs",
    "circ_area", "tri_area", "rect_area", "sph_vol"
}

OPERATORS = {
    "+", "-", "*", "/", "%", "^",
    "=", "==", "!=", "<", ">", "<=", ">="
}

PUNCTUATION = {
    "(", ")", "[", "]", "{", "}", ","
}

BOOLEAN_LITERALS = {"true", "false"}

# Token Storage
literals = Counter()
operators_used = Counter()
variables = Counter()
reserved_used = Counter()
datatypes_used = Counter()
punctuation_used = Counter()

variable_declarations = {}
duplicate_variables = Counter()

lines_processed = 0


# Token Classification
def is_integer(token):
    return re.fullmatch(r"-?\d+", token) is not None


def is_float(token):
    return re.fullmatch(r"-?\d+\.\d+", token) is not None


def is_string(token):
    return re.fullmatch(r'"[^"]*"', token) is not None


def is_identifier(token):
    return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token) is not None


# Tokenizer
def tokenize(line):
    tokens = re.findall(
        r'==|!=|<=|>=|'
        r'[A-Za-z_][A-Za-z0-9_]*|'
        r'\d+\.\d+|\d+|'
        r'".*?"|'
        r'[+\-*/%^=<>]|'
        r'[()\[\]{},]',
        line
    )

    return tokens


# Source File Processing
def process_file(filename):

    global lines_processed

    with open(filename, "r") as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            lines_processed += 1

            tokens = tokenize(line)

            for i, token in enumerate(tokens):

                # Data Types
                if token in DATA_TYPES:
                    datatypes_used[token] += 1

                    # Detecting Variable Declaration
                    if i + 1 < len(tokens):
                        var = tokens[i + 1]
                        if is_identifier(var):
                            if var in variable_declarations:
                                duplicate_variables[var] += 1
                            variable_declarations[var] = True
                            variables[var] += 1

                # Reserved Words
                elif token in RESERVED_WORDS:
                    reserved_used[token] += 1

                # Built-In functions
                elif token in BUILTIN_FUNCTIONS:
                    reserved_used[token] += 1

                # Operators
                elif token in OPERATORS:
                    operators_used[token] += 1

                # Punctuation
                elif token in PUNCTUATION:
                    punctuation_used[token] += 1

                # Literals
                elif is_integer(token) or is_float(token) or is_string(token):
                    literals[token] += 1

                # Literals Part 2 - Boolean Edition
                elif token in BOOLEAN_LITERALS:
                    literals[token] += 1

                # Identifiers
                elif is_identifier(token):
                    variables[token] += 1


# Print Report
def print_report():

    print("\nSource File Report")
    print("-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-\n")

    print("Lines Processed:", lines_processed)
    print()

    print("Literals (" + str(len(literals)) + ")")
    for token, count in sorted(literals.items()):
        print(f"{token} : {count}")
    print()

    print("Operators (" + str(len(operators_used)) + ")")
    for token, count in sorted(operators_used.items()):
        print(f"{token} : {count}")
    print()

    print("Punctuation (" + str(len(punctuation_used)) + ")")
    for token, count in sorted(punctuation_used.items()):
        print(f"{token} : {count}")
    print()

    print("Variables (" + str(len(variables)) + ")")
    for token, count in sorted(variables.items()):
        print(f"{token} : {count}")
    print()

    print("Duplicate Variable Declarations:")
    if duplicate_variables:
        for d in duplicate_variables:
            print(d)
    else:
        print("None")
    print()

    print("Reserved Words (" + str(len(reserved_used)) + ")")
    for token, count in sorted(reserved_used.items()):
        print(f"{token} : {count}")
    print()

    print("Data Types (" + str(len(datatypes_used)) + ")")
    for token, count in sorted(datatypes_used.items()):
        print(f"{token} : {count}")
    print()


# Main Program
def main():

    filename = input("Enter Source File: ")

    process_file(filename)

    print_report()


if __name__ == "__main__":
    main()
