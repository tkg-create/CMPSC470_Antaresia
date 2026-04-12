import re

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
