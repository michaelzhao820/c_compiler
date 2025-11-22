from dataclasses import dataclass
from abc import ABC
from enum import Enum
from parser import Program, Statement, Function, Return, Expression, Constant


class IRInstruction(ABC):
    pass


class Operand(ABC):
    pass


class Register(Enum):
    EAX = "EAX"


@dataclass
class IRProgram:
    function_definition: "IRFunction"


@dataclass
class IRFunction:
    name: str
    instructions: list[IRInstruction]


@dataclass
class Mov(IRInstruction):
    src: Operand
    dst: Operand


@dataclass
class ImmediateValue(Operand):
    value: int


@dataclass
class Reg(Operand):
    register: Register


@dataclass
class Ret(IRInstruction):
    pass


class AssemblyGenerator:
    def __init__(self, ast: Program) -> None:
        self.ast = ast

    def generate_assembly_ast(self) -> IRProgram:

        func = self.ast.function_definition
        ir_function: IRFunction = self.generate_function(func)
        return IRProgram(ir_function)

    def generate_function(self, func: Function):

        instructions: list[IRInstruction] = self.generate_instructions(func.body)

        return IRFunction(name=func.name, instructions=instructions)

    def generate_instructions(self, func_body: Statement) -> list[IRInstruction]:

        if isinstance(func_body, Return):
            return self.generate_return_and_mov(func_body.exp)
        return []

    def generate_return_and_mov(self, func_body_expression: Expression):
        instructions: list[IRInstruction] = []
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
