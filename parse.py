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
        if type(self.get_token()) == EOFToken: return
        self.index += 1

    def parse(self) -> Node:
        return self.parse_item()
    
    def parse_item(self) -> ItemNode:
        parse_subprecedence = self.parse_function_definition
        return parse_subprecedence()

    def parse_function_definition(self) -> ItemNode:
        parse_subprecedence = None
        token = self.get_token()
        if not token.is_fn():
            raise ContextualError('expected fn', token.context)
        self.iterate()
        function_name = self.parse_identifier()

        # Parse parameter `(parameter: datatype)`
        self.expect_symbol('(')
        self.iterate()
        parameter_name = self.parse_identifier()
        self.expect_symbol(':')
        self.iterate()
        parameter_datatype_name = self.parse_expression()
        self.expect_symbol(')')
        self.iterate()
        self.expect_symbol('->')
        self.iterate()
        return_datatype_name = self.parse_expression()

        block = self.parse_block()

        return FunctionDefinitionNode(function_name, parameter_name, block, parameter_datatype_name, return_datatype_name, function_name.context + block.context)
    
    def parse_statement(self) -> StatementNode:
        parse_subprecedence = self.parse_return
        statement = parse_subprecedence()
        return statement
    
    def parse_return(self) -> StatementNode:
        parse_subprecedence = self.parse_break
        token = self.get_token()
        if not token.is_return(): return parse_subprecedence()
        self.iterate()
        if self.get_token().is_semicolon():
            return ReturnNode(NullNode(token.context), token.context)
        expression = self.parse_expression()
        return ReturnNode(expression, token.context + expression.context)

    def parse_break(self) -> StatementNode:
        parse_subprecedence = self.parse_continue
        token = self.get_token()
        if not token.is_break(): return parse_subprecedence()
        self.iterate()
        if self.get_token().is_semicolon():
            return BreakNode(NullNode(token.context), token.context)
        expression = self.parse_expression()
        return BreakNode(expression, token.context + expression.context)

    def parse_continue(self) -> StatementNode:
        parse_subprecedence = self.parse_variable_declaration
        token = self.get_token()
        if not token.is_continue(): return parse_subprecedence()
        self.iterate()
        return ContinueNode(token.context)
    
    def parse_variable_declaration(self) -> StatementNode:
        parse_subprecedence = self.parse_variable_reassignment
        if not self.get_token().is_let(): return parse_subprecedence()
        self.iterate()
        identifier = self.parse_identifier()
        self.expect_symbol(':')
        self.iterate()
        datatype = self.parse_expression()
        self.expect_symbol('=')
        self.iterate()
        expression = self.parse_expression()
        return VariableDeclarationNode(identifier, datatype, expression, identifier.context + datatype.context + expression.context)

    def parse_variable_reassignment(self) -> StatementNode:
        parse_subprecedence = self.parse_expression
        left_node = parse_subprecedence()
        if not self.get_token().is_eq():
            return left_node
        self.iterate()
        right_node = self.parse_expression()
        if type(left_node) != IdentifierNode:
            raise ContextualError('expected identifier', left_node.context)
        return VariableReassignmentNode(left_node, right_node, left_node.context + right_node.context)
    
    def parse_block(self) -> BlockExpressionNode:
        init_context = self.get_token().context
        self.expect_symbol('{')
        self.iterate()
        statements: List[StatementNode] = []
        expression: Optional[ExpressionNode] = None
        while not self.get_token().is_right_brace():
            statement = self.parse_statement()
            self.expect_symbol('}', ';')
            if self.get_token().is_semicolon():
                self.iterate()
                statements.append(statement)
            elif self.get_token().is_right_brace():
                if not isinstance(statement, ExpressionNode):
                    raise ContextualError('expected an expression, found a statement', statement.context)
                expression = statement
                break

        self.expect_symbol('}')
        final_context = self.get_token().context
        self.iterate()
        return BlockExpressionNode(statements, expression, init_context + final_context)

    def parse_expression(self) -> ExpressionNode:
        return self.parse_addition_and_subtraction()
    
    def parse_addition_and_subtraction(self) -> ExpressionNode:
        parse_subprecedence = self.parse_multiplication_and_division
        left_node = parse_subprecedence()
        while self.is_index_valid():
            if self.get_token().is_add():
                self.iterate()
                right_node = parse_subprecedence()
                left_node = AdditionNode(left_node, right_node, left_node.context + right_node.context)
            elif self.get_token().is_sub():
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
            if self.get_token().is_mul():
                self.iterate()
                right_node = parse_subprecedence()
                left_node = MultiplicationNode(left_node, right_node, left_node.context + right_node.context)
            elif self.get_token().is_div():
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
        if not self.is_index_valid() or not self.get_token().is_left_paren():
            return IdentifierNode(token.text, token.context)
        self.iterate()
        expr = self.parse_expression()
        self.expect_symbol(')')
        self.iterate()
        return FunctionApplicationNode(IdentifierNode(token.text, token.context), expr, token.context + expr.context)
    
    def parse_atom(self) -> ExpressionNode:
        token = self.get_token()
        self.iterate()

        if token.is_left_paren():
            expr = self.parse_expression()
            self.expect_symbol(')')
            self.iterate()
            return expr

        if type(token) == IntegerToken:
            return LiteralNode(IntValue(int(token.text)), token.context)
        
        if type(token) == FloatToken:
            return LiteralNode(FloatValue(float(token.text)), token.context)
        
        if type(token) == StringToken:
            return LiteralNode(StringValue(token.text), token.context)
        
        if type(token) == CharToken:
            return LiteralNode(CharValue(token.text), token.context)
        
        if token.is_Int():
            return LiteralNode(DatatypeValue(IntType()), token.context)
        
        if token.is_Float():
            return LiteralNode(DatatypeValue(FloatType()), token.context)
        
        if token.is_Bool():
            return LiteralNode(DatatypeValue(BoolType()), token.context)
        
        if token.is_String():
            return LiteralNode(DatatypeValue(StringType()), token.context)
        
        if token.is_Char():
            return LiteralNode(DatatypeValue(CharType()), token.context)
        
        if token.is_Type():
            return LiteralNode(DatatypeValue(DatatypeType()), token.context)
        
        raise ContextualError('unhandled token', token.context)

    def parse_identifier(self):
        token = self.get_token()
        self.iterate()
        if type(token) != IdentifierToken:
            raise ContextualError('expected identifier', token.context)
        return IdentifierNode(token.text, token.context)
    
    def expect_symbol(self, *symbols: str):
        for symbol in symbols:
            if self.get_token()._matches(SymbolToken, symbol):
                return
        raise ContextualError(f'expected {symbol}', self.get_token().context)
        
def parse(tokens: List[Token]) -> Node:
    return Parser(tokens).parse()