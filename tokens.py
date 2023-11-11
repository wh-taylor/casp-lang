class Token:
    def __init__(self, tokentype: str, text: str):
        self.tokentype = tokentype
        self.text = text

    def __repr__(self) -> str:
        return f'{self.text}: {self.tokentype}'

class IdentifierToken(Token):
    def __init__(self, text: str):
        super().__init__('id', text)

class SymbolToken(Token):
    def __init__(self, text: str):
        super().__init__('sym', text)

class IntegerToken(Token):
    def __init__(self, text: str):
        super().__init__('int', text)

class FloatToken(Token):
    def __init__(self, text: str):
        super().__init__('float', text)

class StringToken(Token):
    def __init__(self, text: str):
        super().__init__('str', text)

class CharToken(Token):
    def __init__(self, text: str):
        super().__init__('char', text)
