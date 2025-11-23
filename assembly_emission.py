from assembly_generator import (
    AssemblyProgram,
    AssemblyInstruction,
    Mov,
    Ret,
    Reg,
    ImmediateValue,
    Operand,
    Register,
)


class AssemblyEmitter:
    def __init__(self, assembly_ast: AssemblyProgram) -> None:
        self.assembly_ast: AssemblyProgram = assembly_ast

    def emit(self) -> str:
        lines = []

        func = self.assembly_ast.function_definition

        lines.append(f"    .globl {func.name}")
        lines.append(f"{func.name}:")

        for instr in func.instructions:
            lines.append("    " + self.emit_instruction(instr))

        lines.append('    .section .note.GNU-stack,"",@progbits')

        return "\n".join(lines)

    def emit_instruction(self, instr: AssemblyInstruction) -> str:

        if isinstance(instr, Mov):
            src = self.emit_operand(instr.src)
            dst = self.emit_operand(instr.dst)
            return f"movl {src}, {dst}"

        elif isinstance(instr, Ret):
            return "ret"
        else:
            raise ValueError(f"Unknown instruction type: {type(instr).__name__}")

    def emit_operand(self, operand: Operand):

        if isinstance(operand, ImmediateValue):
            return f"${operand.value}"
        elif isinstance(operand, Reg):
            return self.get_register_name(operand.register)
        else:
            raise ValueError(f"Unknown operand type: {type(operand).__name__}")

    def get_register_name(self, register: Register) -> str:
        mapping = {
            Register.EAX: "%eax",
        }
        if register not in mapping:
            raise ValueError(f"Unknown register: {register.name}")
        return mapping[register]
