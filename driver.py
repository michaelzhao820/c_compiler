#!/usr/bin/env python3


import os
import sys
import argparse
import subprocess
from pathlib import Path
from lexer import Lexer, Token
from parser import Parser, Program
from assembly_generator import AssemblyProgram, AssemblyGenerator
from assembly_emission import AssemblyEmitter
from tacky import TackyGenerator, TackyProgram


class CompilerDriver:
    def __init__(self, file_path: str):
        self.file_path: Path = Path(file_path)
        self.path: Path = (
            self.file_path.parent if self.file_path.parent != Path() else Path(".")
        )
        self.file_name: str = self.file_path.name

    def generate_preprocess_file(self) -> Path:

        preprocess_file_name: str = self.file_name.rsplit(".", 1)[0] + ".i"
        preprocess_file = self.path / preprocess_file_name

        result = subprocess.run(
            ["gcc", "-E", "-P", self.file_path, "-o", preprocess_file],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("Preprocessing failed:")
            print(result.stderr)
            sys.exit(1)
        return preprocess_file

    def compile_preprocess_file(self, preprocess_file: Path):

        # Lexer produces a list of tokens
        lex = Lexer(preprocess_file)
        tokens: list[Token] = lex.tokenize()

        # Parser which turns these list of tokens into a AST
        p = Parser(tokens)
        ast: Program = p.parse_program()

        # IR three-address code (TAC) pass
        tg = TackyGenerator(ast)
        tacky_program: TackyProgram = tg.generate_tacky_ir()

        # Assembly generation pass : Convert the Tacky into assembly AST
        ag: AssemblyGenerator = AssemblyGenerator(tacky_program)
        assembly_ast: AssemblyProgram = ag.generate_assembly_ast()

        # Code emission pass : Write that assembly to a file
        ae: AssemblyEmitter = AssemblyEmitter(assembly_ast)
        assembly_text: str = ae.emit()
        assembly_file: Path = self.write_assembly(assembly_text)
        return assembly_file

    def write_assembly(self, assembly_text: str) -> Path:

        assembly_file_name: str = self.file_name.rsplit(".", 1)[0] + ".s"
        assembly_file = self.path / assembly_file_name

        with open(assembly_file, "w") as f:
            f.write(assembly_text)

        return assembly_file

    def delete_preprocess_file(self, preprocess_file: Path):
        os.remove(preprocess_file)

    def assemble_and_link(self, assembly_file: Path):

        executable_file_name: str = self.file_name.rsplit(".", 1)[0]
        executable_file_path = self.path / executable_file_name

        result = subprocess.run(
            ["gcc", assembly_file, "-o", executable_file_path],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Assembly/linking failed:")
            print(result.stderr)
            sys.exit(1)

    def delete_assembly_file(self, assembly_file: Path):
        os.remove(assembly_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("c_file")
    args = parser.parse_args()
    file_path: str = args.c_file

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    if not file_path.endswith(".c"):
        print("Error: File must be a .c C source file.")
        sys.exit(1)

    cd = CompilerDriver(file_path)
    preprocess_file: Path = cd.generate_preprocess_file()
    assembly_file: Path = cd.compile_preprocess_file(preprocess_file)
    cd.delete_preprocess_file(preprocess_file)
    cd.assemble_and_link(assembly_file)
    cd.delete_assembly_file(assembly_file)


if __name__ == "__main__":
    main()
