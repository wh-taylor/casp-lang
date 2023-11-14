from parse import *

class DefinitionError(Exception):
    def __init__(self, message: str, identifier: IdentifierNode):
        super().__init__(message)
        self.identifier = identifier

class Definition:
    def __init__(self, identifier: IdentifierNode, defined_value: Value, datatype: DataType):
        self.identifier = identifier
        self.value = defined_value
        self.datatype = datatype

class DefinitionSet:
    def __init__(self):
        self.definitions: List[Definition] = []

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

class Interpreter:
    def __init__(self, definitions: DefinitionSet):
        self.definitions = definitions
    
    def interpret(self, node: Node):
        if isinstance(node, HeadNode):
            return self.interpret_head_node(node)
        if isinstance(node, ItemNode):
            return self.interpret_item_node(node)
        raise ContextualError(f'interpretation of node {node} is unimplemented', node.context)
    
    def interpret_head_node(self, node: HeadNode):
        for item_node in node.item_nodes:
            self.interpret(item_node)
    
    def interpret_item_node(self, node: ItemNode):
        if isinstance(node, FunctionDefinitionNode):
            self.interpret_function_definition_node(node)

    def interpret_function_definition_node(self, node: FunctionDefinitionNode):
        input_datatype = self.interpret_datatype(node.input_datatype)
        output_datatype = self.interpret_datatype(node.output_datatype)
        function_value = FunctionValue(node.parameter_identifier, node.block_node, input_datatype, output_datatype)
        function_type = FunctionType(input_datatype, output_datatype)
        definition = Definition(node.function_name, function_value, function_type)
        self.definitions.add_definition(definition)

    def interpret_datatype(self, node: ExpressionNode) -> DataType:
        if not isinstance(node, DatatypeNode):
            raise ContextualError(f'expected literal node, received {node}', node.context)
        return node.value.value
        
def interpret(head_node: HeadNode):
    definitions = DefinitionSet()
    interpreter = Interpreter(definitions)
    interpreter.interpret_head_node(head_node)

    # Run main function if it exists
    try:
        function_value = definitions.get_value_by_name('main')
        if not isinstance(function_value, FunctionValue):
            raise ValueError('main definition is not a function')
        
        function_object = function_value.value
        if not isinstance(function_object, FunctionObject):
            raise ValueError('function value does not contain function object')
        
        block_node = function_object.output_node
        interpreter.interpret(block_node)
    except DefinitionError:
        pass

    print([definition.value for definition in definitions.definitions])
