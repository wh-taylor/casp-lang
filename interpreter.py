from parse import *
from lex import lex

class DefinitionError(Exception):
    def __init__(self, message: str, identifier: IdentifierNode):
        super().__init__(message)
        self.message = message
        self.identifier = identifier

class Definition:
    def __init__(self, identifier: IdentifierNode, defined_value: Value, datatype: ExpressionNode):
        self.identifier = identifier
        self.value = defined_value
        self.datatype = datatype

class Namespace(Value):
    def __init__(self):
        super().__init__([], NamespaceType())
        self.value: List[Definition] = [] # type: ignore

    def add_definition(self, definition: Definition):
        self.value.append(definition)

    def get_value_by_identifier(self, identifier: IdentifierNode) -> Value:
        for definition in self.value:
            if definition.identifier == identifier:
                return definition.value
        raise DefinitionError(f'no definition for {identifier.identifier} exists', identifier)
    
    def edit_value_by_identifier(self, identifier: IdentifierNode, value: Value) -> Value:
        for definition in self.value:
            if definition.identifier == identifier:
                definition.value = value
                return definition.value
        raise DefinitionError(f'no definition for {identifier.identifier} exists', identifier)
    
    def get_value_by_name(self, name: str) -> Value:
        for definition in self.value:
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
    
    def edit_value_by_identifier(self, identifier: IdentifierNode, value: Value) -> Value:
        for scope in reversed(self.scopes):
            try:
                return scope.edit_value_by_identifier(identifier, value)
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
        if isinstance(node, ImportNode):
            return self.interpret_import(node)
        if isinstance(node, FunctionDefinitionNode):
            return self.interpret_function_definition_node(node)
        if isinstance(node, StructDefinitionNode):
            return self.interpret_struct_definition_node(node)
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
        if isinstance(node, AnonymousFunctionDefinitionNode):
            return self.interpret_anonymous_function_definition_node(node)
        if isinstance(node, AnonymousStructDefinitionNode):
            return self.interpret_anonymous_struct_definition_node(node)
        if isinstance(node, VariableDeclarationNode):
            return self.interpret_variable_declaration(node)
        if isinstance(node, VariableReassignmentNode):
            return self.interpret_variable_reassignment(node)
        if isinstance(node, ConstructorNode):
            return self.interpret_constructor(node)
        if isinstance(node, MemberAccessNode):
            return self.interpret_member_access(node)
        if isinstance(node, FunctionApplicationNode):
            return self.interpret_function_application(node)
        if isinstance(node, ScopeNode):
            return self.interpret_scope(node)
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
        if isinstance(node, SubtractionNode):
            return self.interpret_subtraction(node)
        if isinstance(node, MultiplicationNode):
            return self.interpret_multiplication(node)
        if isinstance(node, DivisionNode):
            return self.interpret_division(node)
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)

    def interpret_anonymous_function_definition_node(self, node: AnonymousFunctionDefinitionNode) -> Value:
        function_value = FunctionValue(node.parameter_identifiers, node.expression_node, node.input_datatypes, node.output_datatype)
        return function_value
    
    def interpret_anonymous_struct_definition_node(self, node: AnonymousStructDefinitionNode) -> Value:
        struct_type = AnonymousType(node.member_identifiers, [self.interpret_datatype(t) for t in node.member_datatypes])
        return DatatypeValue(struct_type)

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
        definition = Definition(node.identifier, value, node.datatype)
        self.namespace_set.add_definition(definition)
        return NullValue()

    def interpret_variable_reassignment(self, node: VariableReassignmentNode) -> Value:
        value = self.interpret(node.expression)
        if isinstance(node.locator, IdentifierNode):
            self.namespace_set.edit_value_by_identifier(node.locator, value)
        if isinstance(node.locator, ScopeNode):
            scope_value = self.interpret(node.locator.scope_node)
            if isinstance(scope_value, Namespace):
                try:
                    scope_value.edit_value_by_identifier(node.locator.reference_node, value)
                except DefinitionError as e:
                    raise ContextualError(e.message, e.identifier.context)
        if isinstance(node.locator, MemberAccessNode):
            struct = self.interpret(node.locator.struct_node)
            if not isinstance(struct, StructValue) or not isinstance(struct.value, StructObject):
                raise ContextualError(f'member access must source from a struct, not {struct.datatype}', node.context)
            for member in struct.value.members:
                if member.identifier == node.locator.member_node:
                    member.value = value
        return NullValue()
    
    def interpret_addition(self, node: AdditionNode) -> Value:
        left_value = self.interpret(node.left_node)
        right_value = self.interpret(node.right_node)
        if hasattr(left_value, '__add__'):
            return left_value + right_value
        else:
            raise ContextualError(f'addition is not implemented for {left_value.datatype} and {right_value.datatype}', node.context)
    
    def interpret_subtraction(self, node: SubtractionNode) -> Value:
        left_value = self.interpret(node.left_node)
        right_value = self.interpret(node.right_node)
        if hasattr(left_value, '__sub__'):
            return left_value - right_value
        else:
            raise ContextualError(f'subtraction is not implemented for {left_value.datatype} and {right_value.datatype}', node.context)
    
    def interpret_multiplication(self, node: MultiplicationNode) -> Value:
        left_value = self.interpret(node.left_node)
        right_value = self.interpret(node.right_node)
        if hasattr(left_value, '__mul__'):
            return left_value * right_value
        else:
            raise ContextualError(f'multiplication is not implemented for {left_value.datatype} and {right_value.datatype}', node.context)
        
    def interpret_division(self, node: DivisionNode) -> Value:
        left_value = self.interpret(node.left_node)
        right_value = self.interpret(node.right_node)
        if hasattr(left_value, '__truediv__'):
            return left_value / right_value
        else:
            raise ContextualError(f'division is not implemented for {left_value.datatype} and {right_value.datatype}', node.context)
        
    def interpret_member_access(self, node: MemberAccessNode) -> Value:
        struct = self.interpret(node.struct_node)
        if not isinstance(struct, StructValue) or not isinstance(struct.value, StructObject):
            raise ContextualError(f'member access must source from a struct, not {struct.datatype}', node.context)
        for member in struct.value.members:
            if member.identifier == node.member_node:
                return member.value
        raise ContextualError(f'struct {struct.datatype} does not have member called {node.member_node}', node.context)
        
    def interpret_constructor(self, node: ConstructorNode) -> Value:
        constructed_datatype = self.interpret(node.datatype_node)
        
        if not isinstance(constructed_datatype, DatatypeValue):
            raise ContextualError(f'expected datatype, received {constructed_datatype}', node.datatype_node.context)

        if not isinstance(constructed_datatype.value, NewType) and not isinstance(constructed_datatype.value, AnonymousType):
            raise ContextualError(f'non-literal datatype {constructed_datatype.datatype} does not have a constructor', node.datatype_node.context)
        
        datatype = constructed_datatype.value
        member_ids = node.member_ids
        member_value_nodes = node.member_value_nodes
        member_names = constructed_datatype.value.member_names
        member_ts = constructed_datatype.value.member_ts
        members: List[StructMemberObject] = []

        for expected_member_id, received_member_id in zip(member_ids, constructed_datatype.value.member_names):
            if expected_member_id != received_member_id:
                raise ContextualError(f'expected {expected_member_id} member, receieved {received_member_id}', received_member_id.context)
        
        for expected_member_t, received_member_t in zip(member_ts, constructed_datatype.value.member_ts):
            if expected_member_t != received_member_t:
                raise ContextualError(f'expected {expected_member_t} member, receieved {received_member_t}', node.datatype_node.context)

        if len(member_value_nodes) != len(member_names):
            raise ContextualError(f'expected {len(member_names)} members, received {len(member_value_nodes)}', node.context)

        for input_node, member_name, member_t in zip(member_value_nodes, member_names, member_ts):
            value = self.interpret(input_node)
            if member_t != value.datatype:
                raise ContextualError(f'expected {member_t} member, receieved {value.datatype}', input_node.context)
            members.append(StructMemberObject(member_name, member_t, value))
        
        return StructValue(members, datatype)

    def interpret_function_application(self, node: FunctionApplicationNode) -> Value:
        called_value = self.interpret(node.function_node)

        if not isinstance(called_value, FunctionValue):
            raise ContextualError(f'expected function, received {called_value}', node.function_node.context)
        
        function_object = called_value.value
        if not isinstance(function_object, FunctionObject):
            raise ContextualError(f'function value {called_value} does not contain function object', node.function_node.context)

        expression = function_object.output_node

        if len(node.input_nodes) != len(function_object.input_nodes):
            raise ContextualError(f'expected {len(function_object.input_nodes)} inputs, received {len(node.input_nodes)}', node.context)

        self.namespace_set.add_scope()

        for i, input_node in enumerate(function_object.input_nodes):
            received_input_value = self.interpret(node.input_nodes[i])
            self.namespace_set.add_definition(Definition(input_node, received_input_value, function_object.input_datatypes[i]))

            expected_input_value = self.interpret_datatype(function_object.input_datatypes[i])

            if received_input_value.datatype != expected_input_value:
                raise ContextualError(f'expected output type {expected_input_value} received output type {received_input_value.datatype}', node.input_nodes[i].context)
        
        if isinstance(expression, BlockExpressionNode):
            for statement in expression.statements:
                try:
                    self.interpret(statement)
                except ReturnExit as exit:
                    output_value = self.interpret(exit.node)
                    break
            else:
                output_value = self.interpret(expression.expression) if expression.expression is not None else NullValue()
        else:
            output_value = self.interpret(expression)
            
        if output_value.datatype != self.interpret_datatype(function_object.output_datatype):
            raise ContextualError(f'expected output type {function_object.output_datatype} received output type {output_value.datatype}', node.context)
        
        self.namespace_set.drop_scope()

        return output_value

    def interpret_scope(self, node: ScopeNode) -> Value:
        scope_value = self.interpret(node.scope_node)
        if isinstance(scope_value, Namespace):
            try:
                return scope_value.get_value_by_identifier(node.reference_node)
            except DefinitionError as e:
                raise ContextualError(e.message, e.identifier.context)
        raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)
    
    def interpret_statement(self, node: StatementNode) -> Value:
        if isinstance(node, FunctionApplicationNode) \
            and isinstance(node.function_node, IdentifierNode) \
            and node.function_node.identifier == 'println':

            if len(node.input_nodes) != 1:
                raise ContextualError(f'expected 1 arg in println, received {len(node.input_nodes)}', node.context)

            input_node = node.input_nodes[0]
            input_value = self.interpret(input_node)

            if hasattr(input_value, "println"):
                input_value.println()
            else:
                raise ContextualError(f'println is not implemented for {input_value.datatype}', node.context)
            
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

    def interpret_import(self, node: ImportNode) -> Value:
        file_name_value = self.interpret(node.file_name_node)

        if not isinstance(file_name_value, StringValue):
            raise ContextualError(f'expected String, received {file_name_value.datatype}', node.file_name_node.context)

        try:
            with open(file_name_value.value) as f:
                code = f.read()
        except FileNotFoundError:
            raise ContextualError(f'file {file_name_value.value} was not found', node.file_name_node.context)
        
        tokens = lex(file_name_value.value, code)
        head_node = parse(tokens)
        interpreter = interpret(head_node)

        namespace = interpreter.namespace_set.scopes[0]
        self.namespace_set.add_definition(Definition(node.identifier_node, namespace, DatatypeNode(DatatypeValue(NamespaceType()), node.context)))

        return NullValue()

    def interpret_function_definition_node(self, node: FunctionDefinitionNode) -> Value:
        function_value = FunctionValue(node.parameter_identifiers, node.expression_node, node.input_datatypes, node.output_datatype)
        function_type = FunctionType(node.input_datatypes, node.output_datatype)
        definition = Definition(node.function_name, function_value, DatatypeNode(DatatypeValue(function_type), node.context))
        self.namespace_set.add_definition(definition)
        return NullValue()
    
    def interpret_struct_definition_node(self, node: StructDefinitionNode) -> Value:
        member_ts: List[DataType] = []
        struct_type = NewType(node.struct_name.identifier, node.member_identifiers, member_ts)
        definition = Definition(node.struct_name, DatatypeValue(struct_type), DatatypeNode(DatatypeValue(DatatypeType()), node.context))
        self.namespace_set.add_definition(definition)
        for t in node.member_datatypes:
            member_ts.append(self.interpret_datatype(t))
        return NullValue()

    def interpret_datatype(self, node: ExpressionNode) -> DataType:
        if isinstance(node, DatatypeNode):
            return node.value.value
        if isinstance(node, FunctionDatatypeNode):
            return FunctionType(node.input_datatype_nodes, node.output_datatype_node)
        if isinstance(node, IdentifierNode):
            datatype_value = self.namespace_set.get_value_by_identifier(node)
            if isinstance(datatype_value, DatatypeValue):
                return datatype_value.value
        if isinstance(node, ScopeNode):
            scope_value = self.interpret(node.scope_node)
            if isinstance(scope_value, Namespace):
                try:
                    datatype_value = scope_value.get_value_by_identifier(node.reference_node)
                except DefinitionError as e:
                    raise ContextualError(e.message, e.identifier.context)
                if isinstance(datatype_value, DatatypeValue):
                    return datatype_value.value
            raise ContextualError(f'interpretation of node {node}: {type(node)} is unimplemented', node.context)
        datatype_value = self.interpret(node)
        if isinstance(datatype_value, DatatypeValue):
            return datatype_value.value
        raise ContextualError(f'expected datatype node, received {node}', node.context)
        
def interpret(head_node: HeadNode) -> Interpreter:
    namespace_set = NamespaceSet()
    interpreter = Interpreter(namespace_set)

    interpreter.interpret_head(head_node)

    try:
        # Run main function if it exists
        function_value = namespace_set.get_value_by_name('main')
    except ValueError:
        return interpreter
    
    if not isinstance(function_value, FunctionValue):
        raise ValueError('main definition is not a function')
    
    function_object = function_value.value
    if not isinstance(function_object, FunctionObject):
        raise ValueError('function value does not contain function object')
    
    expression_node = function_object.output_node
    interpreter.interpret(expression_node)

    return interpreter
