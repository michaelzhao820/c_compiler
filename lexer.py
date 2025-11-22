from enum import Enum
from pathlib import Path
import re
from dataclasses import dataclass


class TokenType(Enum):
    IDENTIFIER = "IDENTIFIER"
    CONSTANT = "CONSTANT"
    INT = "INT"
    VOID = "VOID"
    RETURN = "RETURN"
    OPEN_PARENTHESIS = "OPEN_PARENTHESIS"
    CLOSE_PARENTHESIS = "CLOSE_PARENTHESIS"
    OPEN_BRACE = "OPEN_BRACE"
    CLOSE_BRACE = "CLOSE_BRACE"
    SEMICOLON = "SEMICOLON"


@dataclass
class Token:
    tt: TokenType
    lexeme: str
    value: int | None


class Lexer:
    def __init__(self, preprocess_file: Path) -> None:
        self.preprocess_file = preprocess_file
        self.identifier = re.compile(r"[a-zA-Z_]\w*\b")
        self.constant = re.compile(r"[0-9]+\b")
        self.int = re.compile("int\b")
        self.void = re.compile("void\b")
        self.return_ = re.compile("return\b")
        self.open_paren = re.compile(r"\(")
        self.close_paren = re.compile(r"\)")
        self.open_brace = re.compile(r"{")
        self.close_brace = re.compile(r"}")
        self.semicolon = re.compile(r";")

    def tokenize(self) -> list[Token]:

        with open(self.preprocess_file, "r") as f:
            file_str = f.read()

        tokens: list[Token] = []

        patterns = [
            (self.identifier, TokenType.IDENTIFIER),
            (self.constant, TokenType.CONSTANT),
            (self.open_paren, TokenType.OPEN_PARENTHESIS),
            (self.close_paren, TokenType.CLOSE_PARENTHESIS),
            (self.open_brace, TokenType.OPEN_BRACE),
            (self.close_brace, TokenType.CLOSE_BRACE),
            (self.semicolon, TokenType.SEMICOLON),
        ]
        pos = 0
        while pos < len(file_str):

            while pos < len(file_str) and file_str[pos].isspace():
                pos += 1

            if pos >= len(file_str):
                break

            matched = False
            for pattern, tt in patterns:
                m = pattern.match(file_str, pos)
                if m:
                    lexeme = m.group()
                    if tt == TokenType.IDENTIFIER:
                        if lexeme == "int":
                            tt = TokenType.INT
                        elif lexeme == "void":
                            tt = TokenType.VOID
                        elif lexeme == "return":
                            tt = TokenType.RETURN
                    value = int(lexeme) if tt == TokenType.CONSTANT else None
                    tokens.append(Token(tt, lexeme, value))
                    pos = m.end()
                    matched = True
                    break
            if not matched:
                raise ValueError(
                    f"Unexpected character '{file_str[pos]}' at position {pos}"
                )
        return tokens
