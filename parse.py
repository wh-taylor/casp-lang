from nodes import *
from context import ContextualError

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0

    def get_token(self) -> Token:
        return self.tokens[self.index]
    
    def is_index_valid(self) -> bool:
        return self.index < len(self.tokens)
    
    def iterate(self):
        self.index += 1

    def parse(self) -> Node:
        return self.parse_expression()
    
    def parse_expression(self) -> ExpressionNode:
        return self.parse_addition_and_subtraction()
    
    def parse_addition_and_subtraction(self) -> ExpressionNode:
        parse_subprecedence = self.parse_multiplication_and_division
        left_node = parse_subprecedence()
        while self.is_index_valid():
            if self.get_token().matches(SymbolToken, "+"):
                self.iterate()
                right_node = parse_subprecedence()
                left_node = AdditionNode(left_node, right_node, left_node.context + right_node.context)
            elif self.get_token().matches(SymbolToken, "-"):
                self.iterate()
                right_node = parse_subprecedence()
                left_node = SubtractionNode(left_node, right_node, left_node.context + right_node.context)
            else:
                break
        return left_node
    
    def parse_multiplication_and_division(self) -> ExpressionNode:
        parse_subprecedence = self.parse_function_application
        left_node = parse_subprecedence()
        while self.is_index_valid():
            if self.get_token().matches(SymbolToken, "*"):
                self.iterate()
                right_node = parse_subprecedence()
                left_node = MultiplicationNode(left_node, right_node, left_node.context + right_node.context)
            elif self.get_token().matches(SymbolToken, "/"):
                self.iterate()
                right_node = parse_subprecedence()
                left_node = DivisionNode(left_node, right_node, left_node.context + right_node.context)
            else:
                break
        return left_node
    
    def parse_function_application(self) -> ExpressionNode:
        parse_subprecedence = self.parse_atom
        token = self.get_token()
        if type(token) != IdentifierToken: return parse_subprecedence()
        self.iterate()
        if not self.is_index_valid() or not self.get_token().matches(SymbolToken, '('):
            return IdentifierNode(token.text, token.context)
        expr = self.parse_expression()
        return FunctionApplicationNode(IdentifierNode(token.text, token.context), expr, token.context + expr.context)
    
    def parse_atom(self) -> ExpressionNode:
        token = self.get_token()
        self.iterate()

        if type(token) == IntegerToken:
            return LiteralNode(IntValue(int(token.text)), token.context)
        
        if type(token) == FloatToken:
            return LiteralNode(FloatValue(float(token.text)), token.context)
        
        if type(token) == StringToken:
            return LiteralNode(StringValue(token.text), token.context)
        
        if type(token) == CharToken:
            return LiteralNode(CharValue(token.text), token.context)
        
        if token.matches(SymbolToken, '('):
            expr = self.parse_expression()
            if not self.get_token().matches(SymbolToken, ')'):
                raise ContextualError('expected parenthesis', self.get_token().context)
            self.iterate()
            return expr
        
def parse(tokens: List[Token]) -> Node:
    return Parser(tokens).parse()