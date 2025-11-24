from assembly_generator import (
    AllocateStack,
    AssemblyProgram,
    AssemblyInstruction,
    Mov,
    Neg,
    Not,
    Ret,
    Reg,
    ImmediateValue,
    AssemblyOperand,
    AssemblyUnaryOperator,
    Register,
    Stack,
    Unary,
)


class AssemblyEmitter:
    def __init__(self, assembly_ast: AssemblyProgram) -> None:
        self.assembly_ast: AssemblyProgram = assembly_ast

    def emit(self) -> str:
        lines = []

        func = self.assembly_ast.function_definition

        lines.append(f"    .globl {func.name}")
        lines.append(f"{func.name}:")
        lines.append("    pushq %rbp")
        lines.append("    movq %rsp, %rbp")

        for instr in func.instructions:
            lines.append("    " + self.emit_instruction(instr))

        lines.append('    .section .note.GNU-stack,"",@progbits')

        return "\n".join(lines)

    def emit_instruction(self, instr: AssemblyInstruction) -> str:

        match instr:
            case Mov(src, dst):
                src_str = self.emit_operand(src)
                dst_str = self.emit_operand(dst)
                return f"movl {src_str}, {dst_str}"

            case Unary(unary_operator, operand):
                op_str = self.emit_unary_operator(unary_operator)
                operand_str = self.emit_operand(operand)
                return f"{op_str} {operand_str}"

            case AllocateStack(val):
                return f"subq ${val}, %rsp"

            case Ret():
                # Function epilogue: restore stack and return
                return "movq %rbp, %rsp\n    popq %rbp\n    ret"

            case _:
                raise ValueError(f"Unknown instruction type: {type(instr).__name__}")

    def emit_unary_operator(self, operator: AssemblyUnaryOperator):
        match operator:
            case Neg():
                return "negl"
            case Not():
                return "notl"
            case _:
                raise ValueError(f"Unknown operand type: {type(operator).__name__}")

    def emit_operand(self, operand: AssemblyOperand):

        match operand:
            case ImmediateValue():
                return f"${operand.value}"
            case Reg():
                return self.get_register_name(operand.register)
            case Stack(val):
                return f"{val}(%rbp)"
            case _:
                raise ValueError(f"Unknown operand type: {type(operand).__name__}")

    def get_register_name(self, register: Register) -> str:
        mapping = {Register.EAX: "%eax", Register.R10: "%r10d"}
        if register not in mapping:
            raise ValueError(f"Unknown register: {register.name}")
        return mapping[register]
