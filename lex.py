from typing_extensions import List
from tokens import *
from context import ContextualError

LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
DIGITS = '0123456789'
WHITESPACE = ' \n\v\t\f\r\b'

KEYWORDS = [
    'fn', 'struct',
]

SYMBOLS = '()[]{}'

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, file: str, code: str):
        self._file = file
        self._code = code
        self._index = 0
        self.tokens: List[Token] = []

    def is_index_valid(self) -> bool:
        return self._index < len(self._code)

    def get_current_character(self) -> str:
        return self._code[self._index]
    
    def peek_character(self) -> str:
        return self._code[self._index+1]
    
    def chars_match(self, text: str) -> bool:
        return self._code[self._index:self._index+len(text)] == text
    
    def append_token(self, token: Token):
        self.tokens.append(token)

    def get_context(self, init_index: int, final_index: int) -> Context:
        return Context(self._file, self._code, init_index, final_index)
    
    def iterate(self, i: int = 1):
        self._index += i

    def get_index(self) -> int:
        return self._index

    def lex(self) -> List[Token]:
        self.tokens = []

        while self.is_index_valid():
            # Iterate through code characters
            for symbol in KEYWORDS + list(SYMBOLS):
                if self.chars_match(symbol):
                    init_index = self.get_index()
                    self.iterate(len(symbol)-1)
                    final_index = self.get_index()
                    self.append_token(SymbolToken(symbol, self.get_context(init_index, final_index)))
                    self.iterate()
                    break
            else:
                if self.chars_match('//'):
                    while self.is_index_valid() and not self.chars_match('\n'):
                        self.iterate()
                    self.iterate()
                elif self.chars_match('/*'):
                    while self.is_index_valid() and not self.chars_match('*/'):
                        self.iterate()
                    self.iterate(2)
                elif self.get_current_character() in LETTERS:
                    self.lex_word()
                elif self.get_current_character() in DIGITS:
                    self.lex_number()
                elif self.chars_match('\"'):
                    self.lex_string()
                elif self.chars_match('\''):
                    self.lex_char()
                elif self.get_current_character() in WHITESPACE:
                    self.iterate()
                else:
                    self.lex_operator()

        self.append_token(EOFToken(self.get_context(self.get_index(), self.get_index())))
        return self.tokens
    
    def lex_word(self):
        init_index = self.get_index()
        final_index = self.get_index()
        text = ''

        while True:
            if not self.is_index_valid(): break
            if not self.get_current_character() in LETTERS + DIGITS: break
            text += self.get_current_character()
            final_index = self.get_index()
            self.iterate()

        self.append_token(IdentifierToken(text, self.get_context(init_index, final_index)))

    def lex_number(self):
        init_index = self.get_index()
        final_index = self.get_index()
        text = ''

        while True:
            if not self.is_index_valid(): break
            if not self.get_current_character() in DIGITS + '.': break
            if self.chars_match('.') and '.' in text: break
            if self.chars_match('.') and self.peek_character() not in DIGITS: break
            text += self.get_current_character()
            final_index = self.get_index()
            self.iterate()

        if '.' in text:
            self.append_token(FloatToken(text, self.get_context(init_index, final_index)))
        else:
            self.append_token(IntegerToken(text, self.get_context(init_index, final_index)))

    def lex_string(self):
        self.iterate()
        init_index = self.get_index()-1
        final_index = self.get_index()
        text = ''

        while True:
            if not self.is_index_valid() or self.chars_match('\n'):
                final_index = self.get_index()
                context = self.get_context(init_index, final_index)
                raise ContextualError('char literal is unclosed', context)
            if self.chars_match('\"'):
                self.iterate()
                break
            if self.chars_match('\\'):
                text += self.get_escape_sequence()
                continue
            text += self.get_current_character()
            final_index = self.get_index()
            self.iterate()
        
        self.append_token(StringToken(text, self.get_context(init_index, final_index+1)))

    def lex_char(self):
        self.iterate()
        init_index = self.get_index()-1
        final_index = self.get_index()
        text = ''

        while True:
            if not self.is_index_valid() or self.chars_match('\n'):
                final_index = self.get_index()
                context = self.get_context(init_index, final_index)
                raise ContextualError('char literal is unclosed', context)
            if self.chars_match('\''):
                self.iterate()
                break
            if self.chars_match('\\'):
                text += self.get_escape_sequence()
                continue
            text += self.get_current_character()
            final_index = self.get_index()
            self.iterate()

        context = self.get_context(init_index, final_index+1)

        if len(text) != 1: raise ContextualError('length of char literal must be 1', context)
        
        self.append_token(CharToken(text, context))

    def lex_operator(self):
        init_index = self.get_index()
        final_index = self.get_index()
        text = ''

        while True:
            if not self.is_index_valid(): break
            if self.get_current_character() in LETTERS + DIGITS + WHITESPACE + SYMBOLS: break
            text += self.get_current_character()
            final_index = self.get_index()
            self.iterate()

        self.append_token(SymbolToken(text, self.get_context(init_index, final_index)))
    
    def get_escape_sequence(self) -> str:
        if self.chars_match('\\n'):
            self.iterate(2)
            return '\n'
        elif self.chars_match('\\\\'):
            self.iterate(2)
            return '\\'
        elif self.chars_match('\\\"'):
            self.iterate(2)
            return '\"'
        elif self.chars_match('\\\''):
            self.iterate(2)
            return '\''
        self.iterate()
        return '\\'

def lex(file: str, code: str) -> List[Token]:
    return Lexer(file, code).lex()
