from tokenizer import tokenize, DATA_TYPES


class Parser:

    def __init__(self, filename):
        self.filename = filename
        self.statements = []

    def parse(self):

        with open(self.filename) as f:
            lines = f.readlines()

        i = 0

        while i < len(lines):

            raw = lines[i]

            if raw.strip() == "" or raw.strip().startswith("#"):
                i += 1
                continue

            indent = len(raw) - len(raw.lstrip())
            tokens = tokenize(raw.strip())

            if not tokens:
                i += 1
                continue

            # Parallel Block
            if tokens[0] == "parallel":

                block = []
                i += 1

                while i < len(lines):

                    line = lines[i]

                    if line.strip() == "":
                        i += 1
                        continue

                    new_indent = len(line) - len(line.lstrip())

                    if new_indent <= indent:
                        break

                    stmt = self.parse_statement(tokenize(line.strip()))

                    if stmt:
                        block.append(stmt)

                    i += 1

                self.statements.append({
                    "type": "parallel",
                    "body": block
                })

                continue

            stmt = self.parse_statement(tokens)

            if stmt:
                self.statements.append(stmt)

            i += 1

        return self.statements

    def parse_statement(self, tokens):

        first = tokens[0]

        if first in DATA_TYPES and len(tokens) >= 4 and tokens[2] == "=":

            return {
                "type": "declaration",
                "datatype": tokens[0],
                "name": tokens[1],
                "value": tokens[3:]
            }

        if len(tokens) >= 3 and tokens[1] == "=":

            return {
                "type": "assignment",
                "name": tokens[0],
                "value": tokens[2:]
            }

        if first == "print":

            return {
                "type": "print",
                "value": tokens[1:]
            }

        if first == "if":

            return {
                "type": "if",
                "condition": tokens[1:]
            }

        if first == "for" and "in" in tokens:

            return {
                "type": "for",
                "variable": tokens[1],
                "iterable": tokens[tokens.index("in") + 1]
            }

        return {
            "type": "unknown",
            "tokens": tokens
        }
