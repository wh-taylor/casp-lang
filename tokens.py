from context import Context

class Token:
    def __init__(self, tokentype: str, text: str, context: Context):
        self.tokentype = tokentype
        self.text = text
        self.context = context

    def __repr__(self) -> str:
        return f'{self.text}: {self.tokentype}'
    
    def _matches(self, tokentype: type, text: str) -> bool:
        return type(self) == tokentype and self.text == text
    
    def is_semicolon(self):
        return self._matches(SymbolToken, ';')
    
    def is_left_paren(self):
        return self._matches(SymbolToken, '(')
    
    def is_right_paren(self):
        return self._matches(SymbolToken, ')')
    
    def is_eq(self):
        return self._matches(SymbolToken, '=')
    
    def is_add(self):
        return self._matches(SymbolToken, '+')
    
    def is_sub(self):
        return self._matches(SymbolToken, '-')
    
    def is_mul(self):
        return self._matches(SymbolToken, '*')
    
    def is_div(self):
        return self._matches(SymbolToken, '/')
    
    def is_return(self):
        return self._matches(SymbolToken, 'return')
    
    def is_break(self):
        return self._matches(SymbolToken, 'break')
    
    def is_continue(self):
        return self._matches(SymbolToken, 'continue')
    
    def is_let(self):
        return self._matches(SymbolToken, 'let')
    
class EOFToken(Token):
    def __init__(self, context: Context):
        super().__init__('EOF', 'EOF', context)

    def __repr__(self) -> str:
        return f'{self.text}: {self.tokentype}'

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
