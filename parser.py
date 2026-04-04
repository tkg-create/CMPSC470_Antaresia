from tokenizer_testing import tokenize, DATA_TYPES


class Parser:

    def __init__(self, filename):
        self.filename = filename
        self.statements = []

    def parse(self):

        with open(self.filename, "r") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                tokens = tokenize(line)

                if not tokens:
                    continue

                statement = self.parse_statement(tokens)

                if statement:
                    self.statements.append(statement)

        return self.statements

    def parse_statement(self, tokens):

        first = tokens[0]

        # Variable Declaration
        if first in DATA_TYPES:

            if len(tokens) >= 4 and tokens[2] == "=":

                return {
                    "type": "declaration",
                    "datatype": tokens[0],
                    "name": tokens[1],
                    "value": tokens[3:]
                }

        # Assignment
        if len(tokens) >= 3 and tokens[1] == "=":

            return {
                "type": "assignment",
                "name": tokens[0],
                "value": tokens[2:]
            }

        # If Statement
        if first == "if":

            return {
                "type": "if",
                "condition": tokens[1:]
            }

        # For Loop
        if first == "for":

            if "in" in tokens:

                var = tokens[1]
                iterable = tokens[tokens.index("in") + 1]

                return {
                    "type": "for",
                    "variable": var,
                    "iterable": iterable
                }

        # Print
        if first == "print":

            return {
                "type": "print",
                "value": tokens[1:]
            }

        # Parallel Block
        if first == "parallel":

            return {
                "type": "parallel"
            }

        # Unknown Statement
        return {
            "type": "unknown",
            "tokens": tokens
        }
