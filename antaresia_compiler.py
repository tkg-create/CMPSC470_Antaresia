#Compiler for Antaresia to produce Python Bytecode
import sys
import os
from parser import Parser

class AntaresiaCompiler:
    def __init__(self):
        self.symbols = {}  #type map for semantic analysis

    #Semantic analysis over list of statements
    def semantic_analyze(self, statements):
        for stmt in statements:
            self._analyze_statement(stmt)

    #Analyze a single statement for semantic errors
    def _analyze_statement(self, stmt):
        if stmt['type'] == 'declaration':
            name = stmt['name']
            if name in self.symbols:
                raise Exception(f"Semantic Error: '{name}' already declared")
            self.symbols[name] = stmt['datatype']
        elif stmt['type'] == 'assignment':
            name = stmt['name']
            if name not in self.symbols:
                raise Exception(f"Semantic Error: '{name}' used but not declared")
        elif stmt['type'] == 'if':
            for sub in stmt['body']:
                self._analyze_statement(sub)
            for sub in stmt['else']:
                self._analyze_statement(sub)
        elif stmt['type'] == 'parallel':
            for sub in stmt['body']:
                self._analyze_statement(sub)

    #Generate Python code from a list of statements
    def generate_code(self, statements):
        code_lines = []
        for stmt in statements:
            code_lines.append(self._gen_statement(stmt))
        return ''.join(code_lines)

    #Generate code for a single statement
    def _gen_statement(self, stmt):
        t = stmt['type']
        if t == 'declaration':
            name = stmt['name']
            value = ' '.join(stmt['value'])  #combine tokens into expression string
            return f"{name} = {value}\n"
        elif t == 'assignment':
            name = stmt['name']
            value = ' '.join(stmt['value'])
            return f"{name} = {value}\n"
        elif t == 'print':
            value = ' '.join(stmt['value'])
            return f"print({value})\n"
        elif t == 'if':
            condition = ' '.join(stmt['condition'])
            body_code = self.generate_code(stmt['body'])
            else_code = self.generate_code(stmt['else']) if stmt['else'] else ''

            indented_body = '\n    '.join(body_code.splitlines())
            result = f"if {condition}:\n    {indented_body}"
            if else_code:
                indented_else = '\n    '.join(else_code.splitlines())
                result += f"\nelse:\n    {indented_else}"
            return result + '\n'
        elif t == 'parallel':
            #Parallel not supported in generated code; just generate body sequentially
            return self.generate_code(stmt['body'])
        elif t == 'for':
            var = stmt['variable']
            iterable = stmt['iterable']
            #assumes iterable is a variable name (simplified)
            return f"for {var} in {iterable}:\n    pass\n"
        else:
            return f"#Unhandled statement type: {t}\n"

#Full compilation pipeline: parse -> analyze -> generate
def compile_antaresia(source_file):
    parser = Parser(source_file)
    statements = parser.parse()
    compiler = AntaresiaCompiler()
    compiler.semantic_analyze(statements)
    generated_code = compiler.generate_code(statements)
    return generated_code

#Helper to locate file (current dir or testing source files folder)
def find_file(filename):
    if os.path.exists(filename):
        return filename
    test_path = os.path.join("testing source files", filename)
    if os.path.exists(test_path):
        return test_path
    return None

if __name__ == "__main__":
    source = None
    #Keep asking until a valid source file is provided
    while source is None:
        if len(sys.argv) == 2:
            candidate = sys.argv[1]
            source = find_file(candidate)
            if source is None:
                print(f"File not found: {candidate}")
                print("Please try again.")
                sys.argv = [sys.argv[0]]  #reset to prompt mode
        else:
            candidate = input("Enter source file: ").strip()
            if not candidate:
                print("No file entered. Try again.")
                continue
            source = find_file(candidate)
            if source is None:
                print(f"File not found: {candidate}")
                print("Make sure the file is in the current directory or in 'testing source files/'")

    output_code = compile_antaresia(source)
    base = os.path.splitext(source)[0]  #strip extension
    out_file = base + '.py'
    with open(out_file, 'w') as f:
        f.write(output_code)
    print(f"Success, Generated {out_file}")
    print("Generated Python code:\n")
    print(output_code)