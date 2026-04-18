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

            if line.strip() == "":
                i += 1
                continue

            indent = len(line) - len(line.lstrip())

            if indent <= parent_indent:
                break

            tokens = tokenize(line.strip())

            # Handle Nested If
            if tokens[0] == "if":
                condition = tokens[1:]
                body, i = self.parse_block(lines, i + 1, indent)

                block.append({
                    "type": "if",
                    "condition": condition,
                    "body": body,
                    "else": []
                })

                continue

            # Handle Nested Parallel
            if tokens[0] == "parallel":
                body, i = self.parse_block(lines, i + 1, indent)

                block.append({
                    "type": "parallel",
                    "body": body
                })

                continue

            stmt = self.parse_statement(tokens)

            if stmt:
                block.append(stmt)

            i += 1

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
            stmt = self.parse_statement(tokens)

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
