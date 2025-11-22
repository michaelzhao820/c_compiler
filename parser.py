from dataclasses import dataclass
from abc import ABC
from lexer import Token, TokenType


class Statement(ABC):
    pass


class Expression(ABC):
    pass


@dataclass
class Program:
    function_definition: "Function"


@dataclass
class Function:
    name: str
    body: "Statement"


@dataclass
class Return(Statement):
    exp: "Expression"


@dataclass
class Constant(Expression):
    value: int


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def peek(self) -> Token:
        if self.index >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")
        return self.tokens[self.index]

    def consume(self, expected_type):
        if self.index >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")

        token: Token = self.peek()
        if token.tt != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, found {token.tt.value} "
                f"('{token.lexeme}') at position {self.index}"
            )
        self.index += 1
        return token

    def parse_program(self):

        func: Function = self.parse_function()
        if self.index < len(self.tokens):
            unexpected = self.tokens[self.index]
            raise SyntaxError(
                f"Unexpected token {unexpected.tt.value} ('{unexpected.lexeme}') "
                f"after end of program"
            )
        return Program(func)

    def parse_function(self) -> Function:

        self.consume(TokenType.INT)
        name: str = self.consume(TokenType.IDENTIFIER).lexeme
        self.consume(TokenType.OPEN_PARENTHESIS)
        self.consume(TokenType.VOID)
        self.consume(TokenType.CLOSE_PARENTHESIS)
        self.consume(TokenType.OPEN_BRACE)
        statement: Statement = self.parse_statement()
        self.consume(TokenType.CLOSE_BRACE)
        return Function(name, statement)

    def parse_statement(self) -> Statement:
        self.consume(TokenType.RETURN)
        expr: Expression = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        return Return(expr)

    def parse_expression(self):
        token: Token = self.consume(TokenType.CONSTANT)
        if token.value is None:
            raise SyntaxError(
                f"Internal error: CONSTANT token at position {self.index} has no value"
            )
        return Constant(token.value)
