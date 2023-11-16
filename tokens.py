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
    
    def _is_symbol(self, symbol: str) -> bool:
        return self._matches(SymbolToken, symbol)
    
    def is_semicolon(self) -> bool:
        return self._is_symbol(';')
    
    def is_left_paren(self) -> bool:
        return self._is_symbol('(')
    
    def is_right_paren(self) -> bool:
        return self._is_symbol(')')
    
    def is_left_brace(self) -> bool:
        return self._is_symbol('{')
    
    def is_right_brace(self) -> bool:
        return self._is_symbol('}')
    
    def is_left_bracket(self) -> bool:
        return self._is_symbol('[')
    
    def is_right_bracket(self) -> bool:
        return self._is_symbol(']')
    
    def is_colon(self) -> bool:
        return self._is_symbol(':')
    
    def is_scoper(self) -> bool:
        return self._is_symbol('::')

    def is_comma(self) -> bool:
        return self._is_symbol(',')
    
    def is_right_arrow(self) -> bool:
        return self._is_symbol('->')
    
    def is_ampersand(self) -> bool:
        return self._is_symbol('&')
    
    def is_eq(self) -> bool:
        return self._is_symbol('=')
    
    def is_add(self) -> bool:
        return self._is_symbol('+')
    
    def is_sub(self) -> bool:
        return self._is_symbol('-')
    
    def is_mul(self) -> bool:
        return self._is_symbol('*')
    
    def is_div(self) -> bool:
        return self._is_symbol('/')
    
    def is_return(self) -> bool:
        return self._is_symbol('return')
    
    def is_break(self) -> bool:
        return self._is_symbol('break')
    
    def is_continue(self) -> bool:
        return self._is_symbol('continue')
    
    def is_let(self) -> bool:
        return self._is_symbol('let')
    
    def is_import(self) -> bool:
        return self._is_symbol('import')
    
    def is_fn(self) -> bool:
        return self._is_symbol('fn')
    
    def is_Null(self) -> bool:
        return self._is_symbol('Null')
    
    def is_Int(self) -> bool:
        return self._is_symbol('Int')
    
    def is_Float(self) -> bool:
        return self._is_symbol('Float')
    
    def is_Bool(self) -> bool:
        return self._is_symbol('Bool')
    
    def is_String(self) -> bool:
        return self._is_symbol('String')
    
    def is_Char(self) -> bool:
        return self._is_symbol('Char')
    
    def is_Type(self) -> bool:
        return self._is_symbol('Type')
    
    def is_eof(self) -> bool:
        return self._matches(EOFToken, 'EOF')

    
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
