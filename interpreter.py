from parse import *

class DefinitionError(Exception):
    def __init__(self, message: str, identifier: IdentifierNode):
        super().__init__(message)
        self.message = message
        self.identifier = identifier

class Definition:
    def __init__(self, identifier: IdentifierNode, defined_value: Value, datatype: DataType):
        self.identifier = identifier
        self.value = defined_value
        self.datatype = datatype

class Namespace:
    def __init__(self):
        self.definitions: List[Definition] = [] # type: ignore

    def add_definition(self, definition: Definition):
        self.definitions.append(definition)

    def get_value_by_identifier(self, identifier: IdentifierNode) -> Value:
        for definition in self.definitions:
            if definition.identifier == identifier:
                return definition.value
        raise DefinitionError(f'no definition for {identifier.identifier} exists', identifier)
    
    def get_value_by_name(self, name: str) -> Value:
        for definition in self.definitions:
            if definition.identifier.identifier == name:
                return definition.value
        raise ValueError(f'no definition that goes by {name} exists')
    
class NamespaceSet:
    def __init__(self):
        self.scopes: List[Namespace] = [Namespace()] # type: ignore

    def _get_current_scope(self):
        return self.scopes[-1]

    def add_scope(self):
        self.scopes.append(Namespace())
    
    def drop_scope(self):
        self.scopes.pop()

    def add_definition(self, definition: Definition):
        self._get_current_scope().add_definition(definition)

    def get_value_by_identifier(self, identifier: IdentifierNode) -> Value:
        for scope in reversed(self.scopes):
            try:
                return scope.get_value_by_identifier(identifier)
            except DefinitionError:
                continue
        raise DefinitionError(f'no definition for {identifier.identifier} exists', identifier)
    
    def get_value_by_name(self, name: str) -> Value:
        for scope in reversed(self.scopes):
            try:
                return scope.get_value_by_name(name)
            except ValueError:
                continue
        raise ValueError(f'no definition that goes by {name} exists')

class Interpreter:
    def __init__(self, namespace_set: NamespaceSet):
        self.namespace_set = namespace_set
    
    def interpret(self, node: Node) -> Value:
        if isinstance(node, HeadNode):
            return self.interpret_head(node)
        if isinstance(node, ItemNode):
            return self.interpret_item(node)
        if isinstance(node, StatementNode):
            return self.interpret_statement(node)
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)
    
    def interpret_head(self, node: HeadNode) -> Value:
        for item_node in node.item_nodes:
            self.interpret(item_node)
        return NullValue()
    
    def interpret_item(self, node: ItemNode) -> Value:
        if isinstance(node, FunctionDefinitionNode):
            return self.interpret_function_definition_node(node)
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)

    def interpret_expression(self, node: ExpressionNode) -> Value:
        if isinstance(node, IdentifierNode):
            return self.interpret_identifier(node)
        if isinstance(node, LiteralNode):
            return self.interpret_literal(node)
        if isinstance(node, BinaryOperatorNode):
            return self.interpret_binary_operator(node)
        if isinstance(node, BlockExpressionNode):
            return self.interpret_block(node)
        if isinstance(node, VariableDeclarationNode):
            return self.interpret_variable_declaration(node)
        if isinstance(node, FunctionApplicationNode):
            return self.interpret_function_application(node)
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)
    
    def interpret_identifier(self, node: IdentifierNode) -> Value:
        try:
            return self.namespace_set.get_value_by_identifier(node)
        except DefinitionError as e:
            raise ContextualError(e.message, e.identifier.context)
    
    def interpret_literal(self, node: LiteralNode) -> Value:
        return node.value

    def interpret_binary_operator(self, node: BinaryOperatorNode) -> Value:
        if isinstance(node, AdditionNode):
            return self.interpret_addition(node)
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)

    def interpret_block(self, node: BlockExpressionNode) -> Value:
        for statement in node.statements:
            try:
                self.interpret(statement)
            except BreakExit as exit:
                return self.interpret(exit.node)
            
        return self.interpret(node.expression) if node.expression is not None else NullValue()
    
    def interpret_variable_declaration(self, node: VariableDeclarationNode) -> Value:
        value = self.interpret(node.expression)
        datatype = self.interpret_datatype(node.datatype)
        if value.datatype != datatype:
            raise ContextualError(f'expected type {datatype} received type {value.datatype}', node.expression.context)
        definition = Definition(node.identifier, value, datatype)
        self.namespace_set.add_definition(definition)
        return NullValue()
    
    def interpret_addition(self, node: AdditionNode) -> Value:
        left_value = self.interpret(node.left_node)
        right_value = self.interpret(node.right_node)
        try:
            return left_value + right_value # type: ignore
        except AttributeError:
            raise ContextualError(f'addition is not implemented for {left_value.datatype} and {right_value.datatype}', node.context)
        
    def interpret_function_application(self, node: FunctionApplicationNode) -> Value:
        function_value = self.interpret(node.function_node)

        if not isinstance(function_value, FunctionValue):
            raise ContextualError(f'expected function, received {function_value}', node.function_node.context)
        
        function_object = function_value.value
        if not isinstance(function_object, FunctionObject):
            raise ContextualError(f'function value {function_value} does not contain function object', node.function_node.context)

        expression = function_object.output_node

        if len(node.input_nodes) != len(function_object.input_nodes):
            raise ContextualError(f'expected {len(function_object.input_nodes)} inputs, received {len(node.input_nodes)}', node.context)

        self.namespace_set.add_scope()

        for i, input_node in enumerate(function_object.input_nodes):
            input_value = self.interpret(node.input_nodes[i])
            self.namespace_set.add_definition(Definition(input_node, input_value, function_object.input_datatypes[i]))

            if input_value.datatype != function_object.input_datatypes[i]:
                raise ContextualError(f'expected output type {function_object.input_datatypes[i]} received output type {input_value.datatype}', input_node.context)
        
        if isinstance(expression, BlockExpressionNode):
            for statement in expression.statements:
                try:
                    self.interpret(statement)
                except ReturnExit as exit:
                    output_value = self.interpret(exit.node)
                    break
            else:
                output_value = self.interpret(expression) if expression is not None else NullValue()
        else:
            output_value = self.interpret(expression)
            
        self.namespace_set.drop_scope()

        if output_value.datatype != function_object.output_datatype:
            raise ContextualError(f'expected output type {function_object.output_datatype} received output type {output_value.datatype}', node.context)

        return output_value

    
    def interpret_statement(self, node: StatementNode) -> Value:
        if isinstance(node, FunctionApplicationNode) \
            and isinstance(node.function_node, IdentifierNode) \
            and node.function_node.identifier == 'print':

            if len(node.input_nodes) != 1:
                raise ContextualError(f'expected 1 arg in print, received {len(node.input_nodes)}', node.context)

            input_node = node.input_nodes[0]
            input_value = self.interpret(input_node)

            try:
                input_value.print() # type: ignore
            except AttributeError:
                raise ContextualError(f'print is not implemented for {input_value.datatype}', node.context)
            
            return NullValue()
        if isinstance(node, ExpressionNode):
            return self.interpret_expression(node)
        if isinstance(node, ReturnNode):
            raise ReturnExit(node.node)
        if isinstance(node, BreakNode):
            raise BreakExit(node.node)
        if isinstance(node, ContinueNode):
            raise ContinueExit()
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)

    def interpret_function_definition_node(self, node: FunctionDefinitionNode) -> Value:
        input_datatypes = [self.interpret_datatype(input_datatype) for input_datatype in node.input_datatypes]
        output_datatype = self.interpret_datatype(node.output_datatype)
        function_value = FunctionValue(node.parameter_identifiers, node.expression_node, input_datatypes, output_datatype)
        function_type = FunctionType(input_datatypes, output_datatype)
        definition = Definition(node.function_name, function_value, function_type)
        self.namespace_set.add_definition(definition)
        return NullValue()

    def interpret_datatype(self, node: ExpressionNode) -> DataType:
        if not isinstance(node, DatatypeNode):
            raise ContextualError(f'expected literal node, received {node}', node.context)
        return node.value.value
        
def interpret(head_node: HeadNode):
    namespace_set = NamespaceSet()
    interpreter = Interpreter(namespace_set)
    try:
        interpreter.interpret_head(head_node)
    except ContextualError as e:
        print(e.get_context().highlight_context_line('^'), e)

    try:
        # Run main function if it exists
        function_value = namespace_set.get_value_by_name('main')
    except DefinitionError:
        return
    
    try:
        if not isinstance(function_value, FunctionValue):
            raise ValueError('main definition is not a function')
        
        function_object = function_value.value
        if not isinstance(function_object, FunctionObject):
            raise ValueError('function value does not contain function object')
        
        expression_node = function_object.output_node
        interpreter.interpret(expression_node)
    except ContextualError as e:
        # print(e.get_context().highlight_context_line('^'), e)
        raise e
