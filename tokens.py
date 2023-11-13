from context import Context

class Token:
    def __init__(self, tokentype: str, text: str, context: Context):
        self.tokentype = tokentype
        self.text = text
        self.context = context

    def __repr__(self) -> str:
        return f'{self.text}: {self.tokentype}'
    
    def matches(self, tokentype: type, text: str) -> bool:
        return type(self) == tokentype and self.text == text

class IdentifierToken(Token):
    def __init__(self, text: str, context: Context):
        super().__init__('id', text, context)

class SymbolToken(Token):
    def __init__(self, text: str, context: Context):
        super().__init__('sym', text, context)

class IntegerToken(Token):
    def __init__(self, text: str, context: Context):
        super().__init__('int', text, context)

class FloatToken(Token):
    def __init__(self, text: str, context: Context):
        super().__init__('float', text, context)

class StringToken(Token):
    def __init__(self, text: str, context: Context):
        super().__init__('str', text, context)

class CharToken(Token):
    def __init__(self, text: str, context: Context):
        super().__init__('char', text, context)
