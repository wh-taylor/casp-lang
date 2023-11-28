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

    def retract(self):
        if self.index == 0: return
        self.index -= 1

    def parse(self) -> HeadNode:
        items: List[ItemNode] = []
        while not self.get_token().is_eof():
            items.append(self.parse_item())
        return HeadNode(items, sum([item.context for item in items[1:]], start=items[0].context))
    
    def parse_item(self) -> ItemNode:
        parse_subprecedence = self.parse_import
        return parse_subprecedence()
    
    def parse_import(self) -> ItemNode:
        parse_subprecedence = self.parse_function_definition
        token = self.get_token()
        if not token.is_import():
            return parse_subprecedence()
        self.iterate()
        file_expression = self.parse_expression()
        self.expect_symbol('as')
        self.iterate()
        identifier_node = self.parse_identifier()
        self.expect_symbol(';')
        self.iterate()
        return ImportNode(file_expression, identifier_node, token.context + file_expression.context + identifier_node.context)

    def parse_function_definition(self) -> ItemNode:
        parse_subprecedence = self.parse_struct
        token = self.get_token()
        if not token.is_fn():
            return parse_subprecedence()
        self.iterate()
        function_name = self.parse_identifier()
        
        parameter_names = []
        parameter_datatypes = []

        # Parse parameter `(parameter: datatype)`
        while self.get_token().is_left_paren():
            self.iterate()
            parameter_names.append(self.parse_identifier())
            self.expect_symbol(':')
            self.iterate()
            parameter_datatypes.append(self.parse_expression())
            self.expect_symbol(')')
            self.iterate()
        self.expect_symbol('->')
        self.iterate()
        return_datatype_name = self.parse_expression()

        self.expect_symbol('{', '=')
        if self.get_token().is_left_brace():
            expr = self.parse_block_as_expression()
        elif self.get_token().is_eq():
            self.iterate()
            expr = self.parse_expression()
            self.expect_symbol(';')
            self.iterate()

        return FunctionDefinitionNode(function_name, parameter_names, expr, parameter_datatypes, return_datatype_name, function_name.context + expr.context)
    
    def parse_struct(self) -> ItemNode:
        parse_subprecedence = None
        token = self.get_token()
        if not token.is_struct():
            raise ContextualError(f'expected import, fn, or struct, received {token}', token.context)
        self.iterate()
        struct_name = self.parse_identifier()

        member_names: List[IdentifierNode] = []
        member_datatypes: List[ExpressionNode] = []

        if self.get_token().is_semicolon():
            last_context = self.get_token().context
            self.iterate()
            return StructDefinitionNode(struct_name, member_names, member_datatypes, struct_name.context + last_context)

        self.expect_symbol('{')
        self.iterate()
        
        while not self.get_token().is_right_brace():
            member_names.append(self.parse_identifier())
            self.expect_symbol(':')
            self.iterate()
            member_datatypes.append(self.parse_expression())
            self.expect_symbol(',')
            self.iterate()

        self.expect_symbol('}')
        last_context = self.get_token().context
        self.iterate()

        return StructDefinitionNode(struct_name, member_names, member_datatypes, struct_name.context + last_context)

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
        return self.parse_function_datatype()
    
    def parse_function_datatype(self) -> ExpressionNode:
        parse_subprecedence = self.parse_block_as_expression
        if self.get_token().is_right_arrow():
            arrow_token = self.get_token()
            self.iterate()
            right_node = self.parse_function_datatype()
            return FunctionDatatypeNode([], right_node, arrow_token.context + right_node.context)
        sub_node = parse_subprecedence()
        left_node = [sub_node]
        while self.is_index_valid():
            if self.get_token().is_ampersand():
                self.iterate()
                right_node = parse_subprecedence()
                left_node.append(right_node)
            elif self.get_token().is_right_arrow():
                self.iterate()
                right_node = self.parse_function_datatype()
                return FunctionDatatypeNode(left_node, right_node, left_node[0].context + right_node.context)
            else:
                break
        return sub_node

    def parse_block_as_expression(self) -> ExpressionNode:
        parse_subprecedence = self.parse_addition_and_subtraction
        if not self.get_token().is_left_brace(): return parse_subprecedence()
        return self.parse_block()
    
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
        parse_subprecedence = self.parse_member_access
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
    
    def parse_member_access(self) -> ExpressionNode:
        parse_subprecedence = self.parse_constructor
        left_node = parse_subprecedence()
        while self.is_index_valid():
            if self.get_token().is_dot():
                self.iterate()
                right_node = self.parse_identifier()
                left_node = MemberAccessNode(left_node, right_node, left_node.context + right_node.context)
            else:
                break
        return left_node
    
    def parse_constructor(self) -> ExpressionNode:
        parse_subprecedence = self.parse_function_application
        if not self.get_token().is_new():
            return parse_subprecedence()
        kw_new_token = self.get_token()
        self.iterate()
        datatype_node = parse_subprecedence()
        if not self.is_index_valid() or not self.get_token().is_left_brace():
            raise ContextualError('expected {', self.get_token().context)
        member_ids: List[IdentifierNode] = []
        member_value_nodes: List[ExpressionNode] = []
        self.expect_symbol('{')
        self.iterate()
        while not self.get_token().is_right_brace():
            member_ids.append(self.parse_identifier())
            self.expect_symbol(':')
            self.iterate()
            member_value_nodes.append(self.parse_expression())
            self.expect_symbol('}', ',')
            if self.get_token().is_right_brace():
                break
            if self.get_token().is_comma():
                self.iterate()
        self.iterate()
        return ConstructorNode(datatype_node, member_ids, member_value_nodes, kw_new_token.context + member_value_nodes[-1].context if len(member_value_nodes) > 0 else kw_new_token.context)
    
    def parse_function_application(self) -> ExpressionNode:
        parse_subprecedence = self.parse_scoper
        function_token = self.get_token()
        function_node = parse_subprecedence()
        if not self.is_index_valid() or not self.get_token().is_left_paren():
            return function_node
        input_nodes: List[ExpressionNode] = []
        self.expect_symbol('(')
        self.iterate()
        if not self.get_token().is_right_paren():
            input_nodes.append(self.parse_expression())
            while self.get_token().is_comma():
                self.iterate()
                input_nodes.append(self.parse_expression())
            self.expect_symbol(')')
            self.iterate()
        else:
            self.iterate()
        return FunctionApplicationNode(function_node, input_nodes, function_token.context + input_nodes[-1].context if len(input_nodes) > 0 else function_token.context)
    
    def parse_scoper(self) -> ExpressionNode:
        parse_subprecedence = self.parse_anonymous_function_definition
        left_node = parse_subprecedence()
        while self.is_index_valid():
            if self.get_token().is_scoper():
                self.iterate()
                right_node = self.parse_identifier()
                left_node = ScopeNode(left_node, right_node, left_node.context + right_node.context)
            else:
                break
        return left_node
    
    def parse_anonymous_function_definition(self) -> ExpressionNode:
        parse_subprecedence = self.parse_anonymous_struct
        token = self.get_token()
        if not token.is_fn():
            return parse_subprecedence()
        self.iterate()
        
        parameter_names = []
        parameter_datatypes = []

        # Parse parameter `(parameter: datatype)`
        while self.get_token().is_left_paren():
            self.iterate()
            parameter_names.append(self.parse_identifier())
            self.expect_symbol(':')
            self.iterate()
            parameter_datatypes.append(self.parse_expression())
            self.expect_symbol(')')
            self.iterate()
        self.expect_symbol('->')
        self.iterate()
        return_datatype_name = self.parse_expression()

        self.expect_symbol('{', '=')
        if self.get_token().is_left_brace():
            expr = self.parse_block_as_expression()
        elif self.get_token().is_eq():
            self.iterate()
            expr = self.parse_expression()
            self.expect_symbol(';')
            self.iterate()

        return AnonymousFunctionDefinitionNode(parameter_names, expr, parameter_datatypes, return_datatype_name, token.context + expr.context)
    
    def parse_anonymous_struct(self) -> ItemNode:
        parse_subprecedence = self.parse_identifier_as_expression
        token = self.get_token()
        if not token.is_struct():
            return parse_subprecedence()
        self.iterate()

        member_names: List[IdentifierNode] = []
        member_datatypes: List[ExpressionNode] = []

        if self.get_token().is_semicolon():
            raise ContextualError('anonymous struct must have members', self.get_token().context)

        self.expect_symbol('{')
        self.iterate()
        
        while not self.get_token().is_right_brace():
            member_names.append(self.parse_identifier())
            self.expect_symbol(':')
            self.iterate()
            member_datatypes.append(self.parse_expression())
            self.expect_symbol(',')
            self.iterate()

        self.expect_symbol('}')
        last_context = self.get_token().context
        self.iterate()

        return AnonymousStructDefinitionNode(member_names, member_datatypes, token.context + last_context)
    
    def parse_identifier_as_expression(self) -> ExpressionNode:
        parse_subprecedence = self.parse_atom
        if type(self.get_token()) != IdentifierToken:
            return parse_subprecedence()
        return self.parse_identifier()
    
    def parse_atom(self) -> ExpressionNode:
        token = self.get_token()
        self.iterate()

        if token.is_left_paren():
            expr = self.parse_expression()
            self.expect_symbol(')')
            self.iterate()
            return expr

        if type(token) == IntegerToken:
            return IntNode(IntValue(int(token.text)), token.context)
        
        if type(token) == FloatToken:
            return FloatNode(FloatValue(float(token.text)), token.context)
        
        if type(token) == StringToken:
            return StringNode(StringValue(token.text), token.context)
        
        if type(token) == CharToken:
            return CharNode(CharValue(token.text), token.context)
        
        if token.is_Null():
            return DatatypeNode(DatatypeValue(NullType()), token.context)
        
        if token.is_Int():
            return DatatypeNode(DatatypeValue(IntType()), token.context)
        
        if token.is_Float():
            return DatatypeNode(DatatypeValue(FloatType()), token.context)
        
        if token.is_Bool():
            return DatatypeNode(DatatypeValue(BoolType()), token.context)
        
        if token.is_String():
            return DatatypeNode(DatatypeValue(StringType()), token.context)
        
        if token.is_Char():
            return DatatypeNode(DatatypeValue(CharType()), token.context)
        
        if token.is_Type():
            return DatatypeNode(DatatypeValue(DatatypeType()), token.context)
        
        raise ContextualError(f'unhandled token {token}', token.context)

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
        
def parse(tokens: List[Token]) -> HeadNode:
    return Parser(tokens).parse()