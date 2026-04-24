# Compiler for Antaresia to produce Python Bytecode
import sys
import os
from parser import Parser


class AntaresiaCompiler:
    def __init__(self):
        self.symbols = {}  # type map for semantic analysis
        self.parallel_counter = 0

    # Semantic analysis over list of statements
    def semantic_analyze(self, statements):
        for stmt in statements:
            self._analyze_statement(stmt)

    def _check_expr(self, tokens):
        for token in tokens:
            if token.isidentifier() and token not in self.symbols:
                # allow built-ins
                continue

    # Analyze a single statement for semantic errors
    def _analyze_statement(self, stmt):
        t = stmt["type"]
        if t == "declaration":
            name = stmt["name"]
            if name in self.symbols:
                raise Exception(f"Semantic Error: '{name}' already declared")

            self.symbols[name] = stmt["datatype"]
            self._check_expr(stmt["value"])
        elif t == "assignment":
            name = stmt["name"]
            if name not in self.symbols:
                raise Exception(f"Semantic Error: '{name}' used but not declared")

            self._check_expr(stmt["value"])
        elif t == "if":
            for sub in stmt["body"]:
                self._analyze_statement(sub)
            for sub in stmt.get("else", []):
                self._analyze_statement(sub)
        elif t == "for":
            for sub in stmt["body"]:
                self._analyze_statement(sub)
        elif t == "while":
            for sub in stmt["body"]:
                self._analyze_statement(sub)
        elif t == "parallel":
            for sub in stmt["body"]:
                self._analyze_statement(sub)

    # Generate Python code from a list of statements
    def generate_code(self, statements, indent=0):
        code = ""
        for stmt in statements:
            code += self._gen_statement(stmt, indent)
        return code

    def indent(self, level):
        return "    " * level

    def _safe_block(self, code, indent):
        if not code.strip():
            return self.indent(indent) + "pass\n"
        return "\n".join(self.indent(indent) + line for line in code.splitlines()) + "\n"

    # Generate code for a single statement
    def _gen_statement(self, stmt, indent=0):

        t = stmt["type"]
        ind = self.indent(indent)

        # Declaration
        if t == "declaration":
            name = stmt["name"]
            value = "".join(stmt["value"])
            return f"{ind}{name} = {value}\n"

        # Assignment
        elif t == "assignment":
            name = stmt["name"]
            value = "".join(stmt["value"])
            return f"{ind}{name} = {value}\n"

        # Print
        elif t == "print":
            value = "".join(stmt["value"])
            return f"{ind}print({value})\n"

        # If / Else
        elif t == "if":
            cond = "".join(stmt["condition"])

            body_code = self.generate_code(stmt["body"], indent + 1)
            result = f"{ind}if {cond}:\n"
            result += self._safe_block(body_code, indent + 1)

            if stmt.get("else"):
                else_code = self.generate_code(stmt["else"], indent + 1)
                result += f"{ind}else:\n"
                result += self._safe_block(else_code, indent + 1)

            return result

        # While
        elif t == "while":
            cond = "".join(stmt["condition"])
            body_code = self.generate_code(stmt["body"], indent + 1)

            result = f"{ind}while {cond}:\n"
            result += self._safe_block(body_code, indent + 1)
            return result

        # For
        elif t == "for":
            var = stmt["variable"]
            iterable = stmt["iterable"]

            body_code = self.generate_code(stmt["body"], indent + 1)

            result = f"{ind}for {var} in {iterable}:\n"
            result += self._safe_block(body_code, indent + 1)
            return result

        # Parallel
        elif t == "parallel":

            self.parallel_counter += 1
            block_id = self.parallel_counter

            func_defs = ""
            func_names = []
            assign_targets = []

            for i, sub in enumerate(stmt["body"]):

                if sub["type"] != "assignment":
                    continue

                fname = f"_anta_task_{block_id}_{i}"
                func_names.append(fname)
                assign_targets.append(sub["name"])

                expr = "".join(sub["value"])

                func_defs += f"{ind}def {fname}():\n"
                func_defs += f"{ind}    return {expr}\n\n"

            # generate pool execution
            call_list = ", ".join(func_names)
            targets = ", ".join(assign_targets)

            parallel_code = f"{ind}with ProcessPoolExecutor() as pool:\n"
            parallel_code += f"{ind}    results = list(pool.map(lambda f: f(), [{call_list}]))\n"
            parallel_code += f"{ind}{targets} = results\n"

            return func_defs + parallel_code
        # Unknown
        else:
            return f"{ind}# Unhandled statement type: {t}\n"

    # Full compilation pipeline: parse -> analyze -> generate
    def compile(self, source_file):
        parser = Parser(source_file)
        statements = parser.parse()
        self.semantic_analyze(statements)
        header = (
            "from concurrent.futures import ProcessPoolExecutor\n"
            "import math\n\n"
            "# ---- Antaresia Runtime Library ----\n"
            "def circ_area(r):\n"
            "    return math.pi * r * r\n\n"
            "def tri_area(b, h):\n"
            "    return (b * h) / 2\n\n"
            "def rect_area(w, h):\n"
            "    return w * h\n\n"
            "def sph_vol(r):\n"
            "    return (4/3) * math.pi * r**3\n\n"
        )
        code = self.generate_code(statements)
        return header + code


# Helper to locate file (current dir or testing source files folder)
def find_file(filename):
    if os.path.exists(filename):
        return filename
    test_path = os.path.join("testing source files", filename)
    if os.path.exists(test_path):
        return test_path
    return None


def main():

    source = None

    while source is None:

        if len(sys.argv) == 2:
            candidate = sys.argv[1]
            source = find_file(candidate)

            if source is None:
                print(f"File not found: {candidate}")
                sys.argv = [sys.argv[0]]

        else:
            candidate = input("Enter source file: ").strip()

            if not candidate:
                continue

            source = find_file(candidate)

            if source is None:
                print(f"File not found: {candidate}")

    compiler = AntaresiaCompiler()

    output_code = compiler.compile(source)

    base = os.path.splitext(source)[0]
    out_file = base + ".py"

    with open(out_file, "w") as f:
        f.write(output_code)

    print(f"Success: Generated {out_file}\n")
    print(output_code)


if __name__ == "__main__":
    main()
