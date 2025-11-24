from dataclasses import dataclass
from abc import ABC
from parser import (
    Program,
    Statement,
    Function,
    Return,
    Expression,
    Constant,
    Unary,
    UnaryOperator,
    Complement,
    Negate,
)


class TackyVal(ABC):
    pass


class TackyUnaryOperator(ABC):
    pass


class TackyInstruction(ABC):
    pass


@dataclass
class TackyProgram:
    function_definition: "TackyFunction"


@dataclass
class TackyFunction:
    name: str
    body: list[TackyInstruction]


@dataclass
class TackyReturn(TackyInstruction):
    val: "TackyVal"


@dataclass
class TackyUnary(TackyInstruction):
    unary_operator: TackyUnaryOperator
    src: TackyVal
    dst: TackyVal


@dataclass
class TackyConstant(TackyVal):
    value: int


@dataclass
class TackyVar(TackyVal):
    identifier: str


@dataclass
class TackyComplement(TackyUnaryOperator):
    pass


@dataclass
class TackyNegate(TackyUnaryOperator):
    pass


class TackyGenerator:
    def __init__(self, ast: Program) -> None:
        self.ast = ast
        self.temp_counter = 0

    def generate_tacky_ir(self) -> TackyProgram:

        function: Function = self.ast.function_definition
        tacky_function = TackyFunction(
            name=function.name, body=self.generate_tacky_instructions(function.body)
        )
        return TackyProgram(tacky_function)

    def generate_tacky_instructions(
        self, function_body: Statement
    ) -> list[TackyInstruction]:

        if isinstance(function_body, Return):

            result_val, tacky_instructions = self.emit_tacky(function_body.exp)
            tacky_instructions.append(TackyReturn(result_val))
            return tacky_instructions
        return []

    def emit_tacky(
        self, func_body_expression: Expression
    ) -> tuple[TackyVal, list[TackyInstruction]]:

        match func_body_expression:

            case Constant(c):
                return (TackyConstant(c), [])

            case Unary(operator, inner):

                src, instructions = self.emit_tacky(inner)
                dst_name = self.make_temporary()
                dst = TackyVar(dst_name)
                tacky_op: TackyUnaryOperator = self.convert_unop(operator)
                unary_instr = TackyUnary(tacky_op, src, dst)
                return (dst, instructions + [unary_instr])

            case _:
                raise ValueError(
                    f"Unknown expression type: {type(func_body_expression)}"
                )

    def make_temporary(self):
        name = f"tmp.{self.temp_counter}"
        self.temp_counter += 1
        return name

    def convert_unop(self, operator: UnaryOperator) -> TackyUnaryOperator:

        match operator:

            case Complement():
                return TackyComplement()

            case Negate():
                return TackyNegate()
            case _:
                raise ValueError(f"Unknown operator: {type(operator)}")
