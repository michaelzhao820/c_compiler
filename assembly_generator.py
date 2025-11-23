from dataclasses import dataclass
from abc import ABC
from enum import Enum
from parser import Program, Statement, Function, Return, Expression, Constant


class AssemblyInstruction(ABC):
    pass


class Operand(ABC):
    pass


class Register(Enum):
    EAX = "EAX"


@dataclass
class AssemblyProgram:
    function_definition: "AssemblyFunction"


@dataclass
class AssemblyFunction:
    name: str
    instructions: list[AssemblyInstruction]


@dataclass
class Mov(AssemblyInstruction):
    src: Operand
    dst: Operand


@dataclass
class ImmediateValue(Operand):
    value: int


@dataclass
class Reg(Operand):
    register: Register


@dataclass
class Ret(AssemblyInstruction):
    pass


class AssemblyGenerator:
    def __init__(self, ast: Program) -> None:
        self.ast = ast

    def generate_assembly_ast(self) -> AssemblyProgram:

        func = self.ast.function_definition
        assembly_function: AssemblyFunction = self.generate_function(func)
        return AssemblyProgram(assembly_function)

    def generate_function(self, func: Function):

        instructions: list[AssemblyInstruction] = self.generate_instructions(func.body)

        return AssemblyFunction(name=func.name, instructions=instructions)

    def generate_instructions(self, func_body: Statement) -> list[AssemblyInstruction]:

        if isinstance(func_body, Return):
            return self.generate_return_and_mov(func_body.exp)
        return []

    def generate_return_and_mov(self, func_body_expression: Expression):
        instructions: list[AssemblyInstruction] = []
        if isinstance(func_body_expression, Constant):
            instructions.append(
                Mov(
                    src=ImmediateValue(func_body_expression.value),
                    dst=Reg(Register.EAX),
                )
            )
        else:
            raise ValueError(
                f"Unknown expression type: {type(func_body_expression).__name__}"
            )
        instructions.append(Ret())
        return instructions
