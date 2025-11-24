from dataclasses import dataclass
from abc import ABC
from enum import Enum
from tacky import (
    TackyProgram,
    TackyFunction,
    TackyInstruction,
    TackyReturn,
    TackyUnary,
    TackyVal,
    TackyConstant,
    TackyVar,
    TackyUnaryOperator,
    TackyComplement,
    TackyNegate,
)


class AssemblyInstruction(ABC):
    pass


class AssemblyOperand(ABC):
    pass


class AssemblyUnaryOperator(ABC):
    pass


class Register(Enum):
    EAX = "EAX"
    R10 = "R10"


@dataclass
class AssemblyProgram:
    function_definition: "AssemblyFunction"


@dataclass
class AssemblyFunction:
    name: str
    instructions: list[AssemblyInstruction]


@dataclass
class Mov(AssemblyInstruction):
    src: AssemblyOperand
    dst: AssemblyOperand


@dataclass
class Unary(AssemblyInstruction):
    unary_operator: AssemblyUnaryOperator
    operand: AssemblyOperand


@dataclass
class AllocateStack(AssemblyInstruction):
    val: int


@dataclass
class Ret(AssemblyInstruction):
    pass


@dataclass
class Neg(AssemblyUnaryOperator):
    pass


@dataclass
class Not(AssemblyUnaryOperator):
    pass


@dataclass
class ImmediateValue(AssemblyOperand):
    value: int


@dataclass
class Reg(AssemblyOperand):
    register: Register


@dataclass
class Pseudo(AssemblyOperand):
    identifier: str


@dataclass
class Stack(AssemblyOperand):
    val: int


class AssemblyGenerator:
    def __init__(self, tacky_program: TackyProgram) -> None:
        self.tacky_program = tacky_program
        self.pseudo_map: dict[str, Stack] = {}
        self.current_offset = 0

    def generate_assembly_ast(self) -> AssemblyProgram:

        func = self.tacky_program.function_definition
        assembly_function: AssemblyFunction = self.generate_function(func)
        return AssemblyProgram(assembly_function)

    def generate_function(self, func: TackyFunction):

        instructions: list[AssemblyInstruction] = self.generate_instructions(func.body)
        replaced_instructions = self.replace_pseudos(instructions)
        fixed_instructions: list[AssemblyInstruction] = self.fix_mov_double_address(
            replaced_instructions
        )
        final_instructions = fixed_instructions
        if self.current_offset < 0:
            final_instructions = [
                AllocateStack(abs(self.current_offset))
            ] + fixed_instructions
        return AssemblyFunction(
            name=func.name,
            instructions=final_instructions,
        )

    def generate_instructions(
        self, func_body: list[TackyInstruction]
    ) -> list[AssemblyInstruction]:
        assembly_instructions: list[AssemblyInstruction] = []
        for instruction in func_body:

            match instruction:

                case TackyReturn(val):
                    assembly_instructions.extend(self.tacky_return_to_assembly_ast(val))

                case TackyUnary(unary_operator, src, dst):
                    assembly_instructions.extend(
                        self.tacky_unary_operator_to_assembly_ast(
                            unary_operator, src, dst
                        )
                    )

                case _:
                    raise ValueError(f"Unknown expression type: {type(instruction)}")
        return assembly_instructions

    def tacky_unary_operator_to_assembly_ast(
        self, unary_operator: TackyUnaryOperator, src: TackyVal, dst: TackyVal
    ):

        instructions = []
        new_src = self.convert_tacky_operand_assembly(src)
        new_dst = self.convert_tacky_operand_assembly(dst)
        new_unary_operator = self.convert_unary_operator_assembly(unary_operator)
        instructions.append(Mov(new_src, new_dst))
        instructions.append(Unary(new_unary_operator, new_dst))
        return instructions

    def tacky_return_to_assembly_ast(self, val: TackyVal):

        instructions = []
        assembly_operand: AssemblyOperand = self.convert_tacky_operand_assembly(val)
        instructions.append(Mov(assembly_operand, Reg(Register.EAX)))
        instructions.append(Ret())
        return instructions

    def convert_unary_operator_assembly(self, unary_operator: TackyUnaryOperator):
        match unary_operator:
            case TackyComplement():
                return Not()
            case TackyNegate():
                return Neg()
            case _:
                raise ValueError(f"Unknown TACKY operator type: {type(unary_operator)}")

    def convert_tacky_operand_assembly(self, val: TackyVal) -> AssemblyOperand:
        match val:
            case TackyConstant(value):
                return ImmediateValue(value)
            case TackyVar(identifier):
                return Pseudo(identifier)
            case _:
                raise ValueError(f"Unknown TACKY value type: {type(val)}")

    def replace_pseudos(self, instructions: list[AssemblyInstruction]):

        new_instructions = []
        for instruction in instructions:

            match instruction:
                case Mov(src, dst):
                    new_src = self.replace_operand(src)
                    new_dst = self.replace_operand(dst)
                    new_instructions.append(Mov(new_src, new_dst))

                case Unary(unary_operator, operand):
                    new_operand = self.replace_operand(operand)
                    new_instructions.append(Unary(unary_operator, new_operand))

                case _:
                    new_instructions.append(instruction)
        return new_instructions

    def replace_operand(self, operand: AssemblyOperand) -> AssemblyOperand:
        if isinstance(operand, Pseudo):
            if operand.identifier not in self.pseudo_map:
                self.current_offset -= 4
                self.pseudo_map[operand.identifier] = Stack(self.current_offset)
            return self.pseudo_map[operand.identifier]
        return operand

    def fix_mov_double_address(self, instructions: list[AssemblyInstruction]):
        new_instructions = []
        for instruction in instructions:
            match instruction:
                case Mov(src=Stack(), dst=Stack()):
                    new_instructions.append(Mov(instruction.src, Reg(Register.R10)))
                    new_instructions.append(Mov(Reg(Register.R10), instruction.dst))
                case _:
                    new_instructions.append(instruction)
        return new_instructions
