from parse import *

class DefinitionError(Exception):
    def __init__(self, message: str, identifier: IdentifierNode):
        super().__init__(message)
        self.identifier = identifier

class Definition:
    def __init__(self, identifier: IdentifierNode, defined_value: Value, datatype: ExpressionNode):
        self.identifier = identifier
        self.value = defined_value
        self.datatype = datatype

class DefinitionSet:
    def __init__(self):
        self.definitions: List[Definition] = []

    def add_definition(self, definition: Definition):
        self.definitions.append(definition)

    def get_identifier_value(self, identifier: IdentifierNode):
        for definition in self.definitions:
            if definition.identifier == identifier:
                return definition.value
        raise DefinitionError(f'no definition for {identifier.identifier} exists', identifier)

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
        function_value = FunctionValue(node.parameter_identifier, node.block_node, node.input_datatype, node.output_datatype)
        function_type = FunctionType(node.input_datatype, node.output_datatype)
        definition = Definition(node.function_name, function_value, function_type)
        self.definitions.add_definition(definition)
