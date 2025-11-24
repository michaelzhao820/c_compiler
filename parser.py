from dataclasses import dataclass
from abc import ABC
from lexer import Token, TokenType


class Statement(ABC):
    pass


class Expression(ABC):
    pass


class UnaryOperator(ABC):
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


@dataclass
class Unary(Expression):
    unary_operator: UnaryOperator
    exp: "Expression"


@dataclass
class Complement(UnaryOperator):
    pass


@dataclass
class Negate(UnaryOperator):
    pass


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
        token: Token = self.peek()
        if token.tt == TokenType.CONSTANT:
            token = self.consume(TokenType.CONSTANT)
            if token.value is None:
                raise SyntaxError(
                    f"Internal error: CONSTANT token at position {self.index} has no value"
                )
            return Constant(token.value)

        elif token.tt in (TokenType.HYPHEN, TokenType.TILDE):
            operator: UnaryOperator = self.parse_unary_operator()
            inner_expr = self.parse_expression()
            return Unary(operator, inner_expr)

        elif token.tt == TokenType.OPEN_PARENTHESIS:
            self.consume(TokenType.OPEN_PARENTHESIS)
            inner_expr = self.parse_expression()
            self.consume(TokenType.CLOSE_PARENTHESIS)
            return inner_expr
        else:
            raise SyntaxError(
                f"Expected expression, found {token.tt.value} "
                f"('{token.lexeme}') at position {self.index}"
            )

    def parse_unary_operator(self) -> UnaryOperator:
        token = self.peek()
        if token.tt == TokenType.TILDE:
            self.consume(TokenType.TILDE)
            return Complement()
        elif token.tt == TokenType.HYPHEN:
            self.consume(TokenType.HYPHEN)
            return Negate()
        else:
            raise SyntaxError(f"Expected unary operator, found {token.tt.value}")
