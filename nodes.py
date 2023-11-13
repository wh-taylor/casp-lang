from __future__ import annotations
from typing_extensions import List, Optional
from tokens import *
from datatypes import *

# Values

# Base value class
class Value:
    def __init__(self, value, datatype: DataType):
        self.value = value
        self.datatype = datatype

    def get_datatype(self) -> DataType:
        return self.datatype
    
    def __repr__(self) -> str:
        return repr(self.value)

# Value objects    

class StructMemberObject:
    def __init__(self, identifier: IdentifierNode, datatype: DataType, value: Value):
        self.identifier = identifier
        self.datatype = datatype
        self.value = value

class StructObject:
    def __init__(self, members: List[StructMemberObject]):
        self.members = members

class FunctionObject:
    def __init__(self, input_identifier_node: IdentifierNode, expression_node: ExpressionNode, input_datatype: DataType, output_datatype: DataType):
        self.input_node = input_identifier_node
        self.output_node = expression_node
        self.input_datatype = input_datatype
        self.output_datatype = output_datatype

# Value subclasses

class NullValue(Value):
    def __init__(self):
        super().__init__(None, NullType())

class IntValue(Value):
    def __init__(self, raw_int: int):
        super().__init__(raw_int, IntType())

class FloatValue(Value):
    def __init__(self, raw_float: float):
        super().__init__(raw_float, FloatType())

class BoolValue(Value):
    def __init__(self, raw_bool: bool):
        super().__init__(raw_bool, BoolType())

class StringValue(Value):
    def __init__(self, raw_str: str):
        super().__init__(raw_str, StringType())

    def __repr__(self) -> str:
        return f'"{self.value}"'

class CharValue(Value):
    def __init__(self, raw_char: str):
        # Ensure that the string is only one character long
        if len(raw_char) != 1:
            raise ValueError('char value must contain only one character')
        super().__init__(raw_char, CharType())

class FunctionValue(Value):
    def __init__(self, input_identifier_node: IdentifierNode, expression_node: ExpressionNode, input_datatype: DataType, output_datatype: DataType):
        super().__init__(FunctionObject(input_identifier_node, expression_node, input_datatype, output_datatype), FunctionType(input_datatype, output_datatype))

class ArrayValue(Value):
    def __init__(self, raw_values: List[Value], datatype: DataType):
        super().__init__(raw_values, ArrayType(datatype))

class VectorValue(Value):
    def __init__(self, raw_values: List[Value], datatypes: List[DataType]):
        # Raise an error if there are too few values.
        if len(raw_values) < len(datatypes):
            raise ValueError('too few values in vector')
        
        # Raise an error if there are too many values.
        if len(raw_values) > len(datatypes):
            raise ValueError('too many values in vector')
        
        # Match the values' datatypes and expected datatypes;
        # if there is an incorrect value datatype
        for i in range(len(raw_values)):
            actual_datatype = raw_values[i].get_datatype()
            expected_datatype = datatypes[i]

            if actual_datatype != expected_datatype:
                raise ValueError(f'value had type {actual_datatype} when {expected_datatype} was expected')
        
        super().__init__(raw_values, VectorType(datatypes))

class StructValue(Value):
    def __init__(self, members: List[StructMemberObject], struct_type: DataType):
        super().__init__(StructObject(members), struct_type)



# Nodes

# Base node

class Node:
    def __init__(self, context: Context):
        self.context = context

# Base statement node

class StatementNode(Node):
    def __init__(self, context: Context):
        super().__init__(context)

# Base expression node

class ExpressionNode(StatementNode):
    def __init__(self, context: Context):
        super().__init__(context)

# Value nodes

class LiteralNode(ExpressionNode):
    def __init__(self, value: Value, context: Context):
        super().__init__(context)

        self.value = value

    def __repr__(self) -> str:
        return repr(self.value)


class IntNode(LiteralNode):
    def __init__(self, value: IntValue, context: Context):
        super().__init__(value, context)

class FloatNode(LiteralNode):
    def __init__(self, value: FloatValue, context: Context):
        super().__init__(value, context)

class BoolNode(LiteralNode):
    def __init__(self, value: BoolValue, context: Context):
        super().__init__(value, context)

class StringNode(LiteralNode):
    def __init__(self, value: StringValue, context: Context):
        super().__init__(value, context)

class CharNode(LiteralNode):
    def __init__(self, value: CharValue, context: Context):
        super().__init__(value, context)

class ArrayNode(LiteralNode):
    def __init__(self, value: ArrayValue, context: Context):
        super().__init__(value, context)

class VectorNode(LiteralNode):
    def __init__(self, value: VectorValue, context: Context):
        super().__init__(value, context)


class IdentifierNode(ExpressionNode):
    def __init__(self, identifier: str, context: Context):
        super().__init__(context)

        self.identifier = identifier

    def __repr__(self) -> str:
        return self.identifier

# Operation nodes

# Binary operators

class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(context)

        self.left_node = left_node
        self.right_node = right_node

    def __repr__(self, operator: str) -> str:
        return f'{self.left_node} {operator} {self.right_node}'

# x + y
class AdditionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('+')

# x - y
class SubtractionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('-')

# x * y
class MultiplicationNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('*')

# x / y
class DivisionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('/')

# x % y
class ModulusNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('%')

# Logical Binary Operators

# x and y
class AndNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('and')

# x or y
class OrNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('or')

# Relational Binary Operators

# x == y
class EqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('==')

# x != y
class NotEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('!=')

# x < y
class LessThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('<')

# x > y
class GreaterThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('>')

# x <= y
class LessThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('<=')

# x >= y
class GreaterThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

    def __repr__(self) -> str:
        return super().__repr__('>=')

# Function application

# f x
class FunctionApplicationNode(BinaryOperatorNode):
    def __init__(self, function_node: ExpressionNode, input_node: ExpressionNode, context: Context):
        super().__init__(function_node, input_node, context)

    def __repr__(self) -> str:
        return f'{self.left_node}({self.right_node})'
        
# Unary Operators

class UnaryOperatorNode(ExpressionNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(context)

        self.node = node

# -x
class NegativeNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(node, context)

# not x
class NotNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(node, context)

# Type cast node

# x as t
class TypeCastNode(ExpressionNode):
    def __init__(self, node: ExpressionNode, datatype: DataType, context: Context):
        super().__init__(context)

        self.node = node
        self.datatype = datatype

# Variables

class VariableDeclarationNode(ExpressionNode):
    def __init__(self, identifier: IdentifierNode, datatype: DataType, expression: ExpressionNode, context: Context):
        super().__init__(context)
        
        self.identifier = identifier
        self.datatype = datatype
        self.expression = expression

class VariableReassignmentNode(ExpressionNode):
    def __init__(self, identifier: IdentifierNode, expression: ExpressionNode, context: Context):
        super().__init__(context)

        self.identifier = identifier
        self.expression = expression

# Statements

class ReturnNode(StatementNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(context)

        self.node = node

class BreakNode(StatementNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(context)

        self.node = node

class ContinueNode(StatementNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(context)

        self.node = node

# Block expressions

class BlockExpressionNode(ExpressionNode):
    def __init__(self, statements: List[StatementNode], expression: Optional[ExpressionNode], context: Context):
        super().__init__(context)

        self.statements = statements
        self.expression = expression

class IfExpressionNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, block: BlockExpressionNode, elseblock: BlockExpressionNode, context: Context):
        super().__init__(context)

        self.condition = condition
        self.block = block
        self.elseblock = elseblock

class WhileExpressionNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, block: BlockExpressionNode, context: Context):
        super().__init__(context)

        self.condition = condition
        self.block = block

class LoopExpressionNode(ExpressionNode):
    def __init__(self, block: BlockExpressionNode, context: Context):
        super().__init__(context)

        self.block = block