import os
import sys
import subprocess

from parser import Parser
from symbol_table import execute
from antaresia_compiler import AntaresiaCompiler


# UI Helpers
def banner():
    print("\n" + "=" * 50)
    print("        ANTARESiA LANGUAGE SYSTEM")
    print("=" * 50 + "\n")


def menu():
    print("Select Mode:")
    print("1. Interpret (.txt file)")
    print("2. Compile to Python (.py)")
    print("3. Compile + Run")
    print("4. Exit\n")


def find_file(filename):

    if os.path.exists(filename):
        return filename

    alt = os.path.join("testing source files", filename)

    if os.path.exists(alt):
        return alt

    return None


def get_file():

    filename = input("Enter Antaresia source file: ").strip()

    path = find_file(filename)

    if not path:
        print(f"[Error] File not found: {filename}")
        return None

    return path


# Mode 1: Interpreter
def run_interpreter(file_path):

    print("\n[Interpreter Mode]\n")

    parser = Parser(file_path)
    program = parser.parse()

    execute(program)


# Mode 2: Compiler
def run_compiler(file_path, run_after=False):

    print("\n[Compiler Mode]\n")

    compiler = AntaresiaCompiler()
    output_code = compiler.compile(file_path)

    out_file = os.path.splitext(file_path)[0] + ".py"

    with open(out_file, "w") as f:
        f.write(output_code)

    print(f"[Success] Generated: {out_file}\n")
    print("----- Generated Python Code -----\n")
    print(output_code)
    print("---------------------------------\n")

    if run_after:
        print("[Executing Generated Python Program]\n")
        subprocess.run([sys.executable, out_file])


# Main Loop
def main():

    while True:

        banner()
        menu()

        choice = input("Enter choice (1-4): ").strip()

        if choice == "4":
            print("\nExiting Antaresia System...\n")
            break

        file_path = get_file()

        if not file_path:
            continue

        if choice == "1":
            run_interpreter(file_path)

        elif choice == "2":
            run_compiler(file_path, run_after=False)

        elif choice == "3":
            run_compiler(file_path, run_after=True)

        else:
            print("[Error] Invalid selection")


if __name__ == "__main__":
    main()
