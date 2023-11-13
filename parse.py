from nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0

    def get_token(self) -> Optional[Token]:
        return self.tokens[self.index] if self.is_index_valid() else None
    
    def is_index_valid(self) -> bool:
        return self.index < len(self.tokens)
    
    def iterate(self):
        self.index += 1

    def parse(self) -> Node:
        return self.parse_factor()
    
    def parse_factor(self) -> ExpressionNode:
        token = self.get_token()
        self.iterate()

        if type(token) == IntegerToken:
            return LiteralNode(IntValue(int(token.text)), token.context)
        
        if type(token) == FloatToken:
            return LiteralNode(FloatValue(float(token.text)), token.context)
        
        if type(token) == StringToken:
            return LiteralNode(StringValue(float(token.text)), token.context)
        
        if type(token) == CharToken:
            return LiteralNode(CharValue(float(token.text)), token.context)
        
        if type(token) == IdentifierToken:
            return IdentifierNode(token.text, token.context)
        
def parse(tokens: List[Token]) -> Node:
    return Parser(tokens).parse()