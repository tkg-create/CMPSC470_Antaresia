from tokenizer import tokenize, DATA_TYPES


class Parser:

    def __init__(self, filename):
        self.filename = filename
        self.statements = []

    def parse_block(self, lines, start_index, parent_indent):

        block = []
        i = start_index

        while i < len(lines):

            line = lines[i]

            if line.strip() == "" or line.strip().startswith("#"):
                i += 1
                continue

            indent = len(line) - len(line.lstrip())

            if indent <= parent_indent:
                break

            stmt, i = self.parse_statement(lines, i, parent_indent)

            if stmt:
                block.append(stmt)

        return block, i

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

            # If Block
            if tokens[0] == "if":

                condition = tokens[1:]

                body, new_i = self.parse_block(lines, i + 1, indent)

                else_block = []

                if new_i < len(lines):

                    next_tokens = tokenize(lines[new_i].strip())

                    if next_tokens and next_tokens[0] == "else":
                        else_block, new_i = self.parse_block(lines, new_i + 1, indent)

                self.statements.append({
                    "type": "if",
                    "condition": condition,
                    "body": body,
                    "else": else_block
                })

                i = new_i
                continue

            # Parallel Block
            if tokens[0] == "parallel":
                body, new_i = self.parse_block(lines, i + 1, indent)

                self.statements.append({
                    "type": "parallel",
                    "body": body
                })

                i = new_i
                continue

            # Normal Statements
            stmt, i = self.parse_statement(lines, i, indent)
            self.statements.append(stmt)

        return self.statements

    def parse_statement(self, lines, i, indent):

        tokens = tokenize(lines[i].strip())
        first = tokens[0]

        # Declaration
        if first in DATA_TYPES and len(tokens) >= 4 and tokens[2] == "=":
            return ({
                        "type": "declaration",
                        "datatype": tokens[0],
                        "name": tokens[1],
                        "value": tokens[3:]
                    }, i + 1)

        # Assignment
        if len(tokens) >= 3 and tokens[1] == "=":
            return ({
                        "type": "assignment",
                        "name": tokens[0],
                        "value": tokens[2:]
                    }, i + 1)

        # Print
        if first == "print":
            return ({
                        "type": "print",
                        "value": tokens[1:]
                    }, i + 1)

        # If Block
        if first == "if":
            body, new_i = self.parse_block(lines, i + 1, indent)
            return ({
                        "type": "if",
                        "condition": tokens[1:],
                        "body": body,
                        "else": []
                    }, new_i)

        # While Block
        if first == "while":
            body, new_i = self.parse_block(lines, i + 1, indent)
            return ({
                        "type": "while",
                        "condition": tokens[1:],
                        "body": body
                    }, new_i)

        # For Block
        if first == "for" and "in" in tokens:
            body, new_i = self.parse_block(lines, i + 1, indent)
            return ({
                        "type": "for",
                        "variable": tokens[1],
                        "iterable": tokens[tokens.index("in") + 1],
                        "body": body
                    }, new_i)

        # Parallel Block
        if first == "parallel":
            body, new_i = self.parse_block(lines, i + 1, indent)
            return ({
                        "type": "parallel",
                        "body": body
                    }, new_i)

        # Unknown
        return ({
                    "type": "unknown",
                    "tokens": tokens
                }, i + 1)
