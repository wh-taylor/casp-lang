from __future__ import annotations
from typing_extensions import List, Self, Optional
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
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Value):
            return False
        return self.value == other.value and self.datatype == other.datatype

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

    def __eq__(self, _: object):
        return NotImplemented
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return self

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
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LiteralNode):
            return False
        return self.value == other.value


class NullNode(LiteralNode):
    def __init__(self, context: Context):
        super().__init__(NullValue(), context)

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
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IdentifierNode):
            return False
        return self.identifier == other.identifier

# Operation nodes

# Binary operators

class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, operator: str, context: Context):
        super().__init__(context)

        self.left_node = left_node
        self.right_node = right_node
        self.operator = operator

    def __repr__(self) -> str:
        return f'{self.left_node} {self.operator} {self.right_node}'
    
    def __eq__(self, other: object):
        if not isinstance(other, BinaryOperatorNode):
            return False
        return self.left_node == other.left_node and self.right_node == other.right_node and self.operator == other.operator

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return BinaryOperatorNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.operator,
            self.context)

# x + y
class AdditionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '+', context)

# x - y
class SubtractionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '-', context)

# x * y
class MultiplicationNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '*', context)

# x / y
class DivisionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '/', context)

# x % y
class ModulusNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '%', context)

# Logical Binary Operators

# x and y
class AndNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, 'and', context)

# x or y
class OrNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, 'or', context)

# Relational Binary Operators

# x == y
class EqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '==', context)

# x != y
class NotEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '!=', context)

# x < y
class LessThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '<', context)

# x > y
class GreaterThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '>', context)

# x <= y
class LessThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '<=', context)

# x >= y
class GreaterThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '>=', context)

# Function application

# f x
class FunctionApplicationNode(BinaryOperatorNode):
    def __init__(self, function_node: ExpressionNode, input_node: ExpressionNode, context: Context):
        super().__init__(function_node, input_node, '', context)

    def __repr__(self) -> str:
        return f'{self.left_node}({self.right_node})'
    
# Type cast node

# x as t
class TypeCastNode(BinaryOperatorNode):
    def __init__(self, node: ExpressionNode, datatype: ExpressionNode, context: Context):
        super().__init__(node, datatype, 'as', context)
        
# Unary Operators

class UnaryOperatorNode(ExpressionNode):
    def __init__(self, node: ExpressionNode, operator: str, context: Context):
        super().__init__(context)

        self.node = node
        self.operator = operator

    def __eq__(self, other: object):
        if not isinstance(other, UnaryOperatorNode):
            return False
        return self.node == other.node and self.operator == other.operator
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return UnaryOperatorNode(
            self.node.sub(old_node, new_node),
            self.operator,
            self.context)

# -x
class NegativeNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(node, '-', context)

# not x
class NotNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(node, 'not', context)

# Variables

class VariableDeclarationNode(ExpressionNode):
    def __init__(self, identifier: IdentifierNode, datatype: ExpressionNode, expression: ExpressionNode, context: Context):
        super().__init__(context)
        
        self.identifier = identifier
        self.datatype = datatype
        self.expression = expression

    def __repr__(self) -> str:
        return f'let {self.identifier}: {self.datatype} = {self.expression}'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VariableDeclarationNode):
            return False
        return self.identifier == other.identifier and self.datatype == other.datatype and self.expression == other.expression

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return VariableDeclarationNode(
            self.identifier.sub(old_node, new_node),
            self.datatype.sub(old_node, new_node),
            self.expression.sub(old_node, new_node),
            self.context)

class VariableReassignmentNode(ExpressionNode):
    def __init__(self, identifier: IdentifierNode, expression: ExpressionNode, context: Context):
        super().__init__(context)

        self.identifier = identifier
        self.expression = expression

    def __repr__(self) -> str:
        return f'{self.identifier} = {self.expression}'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VariableReassignmentNode):
            return False
        return self.identifier == other.identifier and self.expression == other.expression
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return VariableReassignmentNode(
            self.identifier.sub(old_node, new_node),
            self.expression.sub(old_node, new_node),
            self.context)

# Statements

class ReturnNode(StatementNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(context)

        self.node = node

    def __repr__(self) -> str:
        return f'return {self.node}'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReturnNode):
            return False
        return self.node == other.node
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return ReturnNode(
            self.node.sub(old_node, new_node),
            self.context)

class BreakNode(StatementNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(context)

        self.node = node

    def __repr__(self) -> str:
        return f'break {self.node}'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BreakNode):
            return False
        return self.node == other.node
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return BreakNode(
            self.node.sub(old_node, new_node),
            self.context)

class ContinueNode(StatementNode):
    def __init__(self, context: Context):
        super().__init__(context)

    def __repr__(self) -> str:
        return 'continue'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, ContinueNode)

# Block expressions

class BlockExpressionNode(ExpressionNode):
    def __init__(self, statements: List[StatementNode], expression: Optional[ExpressionNode], context: Context):
        super().__init__(context)

        self.statements = statements
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BlockExpressionNode):
            return False
        for i in range(len(self.statements)):
            if self.statements[i] != other.statements[i]:
                return False
        return self.expression == other.expression
    
    def __repr__(self) -> str:
        return '{ ' + '; '.join([repr(s) for s in self.statements + [self.expression]]) + ' }'
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return BlockExpressionNode(
            [statement.sub(old_node, new_node) for statement in self.statements],
            self.expression.sub(old_node, new_node),
            self.context)

class IfExpressionNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, block: BlockExpressionNode, elseblock: BlockExpressionNode, context: Context):
        super().__init__(context)

        self.condition = condition
        self.block = block
        self.elseblock = elseblock

    def __eq__(self, other: object):
        if not isinstance(other, IfExpressionNode):
            return False
        return self.condition == other.condition and self.block == other.block and self.elseblock == other.elseblock
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return IfExpressionNode(
            self.condition.sub(old_node, new_node),
            self.block.sub(old_node, new_node),
            self.elseblock.sub(old_node, new_node),
            self.context)

class WhileExpressionNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, block: BlockExpressionNode, context: Context):
        super().__init__(context)

        self.condition = condition
        self.block = block

    def __eq__(self, other: object):
        if not isinstance(other, WhileExpressionNode):
            return False
        return self.condition == other.condition and self.block == other.block
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return IfExpressionNode(
            self.condition.sub(old_node, new_node),
            self.block.sub(old_node, new_node),
            self.context)

class LoopExpressionNode(ExpressionNode):
    def __init__(self, block: BlockExpressionNode, context: Context):
        super().__init__(context)

        self.block = block

    def __eq__(self, other: object):
        if not isinstance(other, LoopExpressionNode):
            return False
        return self.block == other.block
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return IfExpressionNode(
            self.block.sub(old_node, new_node),
            self.context)

# Items

class ItemNode(Node):
    def __init__(self, context: Context):
        super().__init__(context)

class FunctionDefinitionNode(ItemNode):
    def __init__(self, function_name: IdentifierNode, parameter_identifier: List[IdentifierNode], block_node: BlockExpressionNode, input_datatype: ExpressionNode, output_datatype: ExpressionNode, context: Context):
        self.function_name = function_name
        self.parameter_identifier = parameter_identifier
        self.block_node = block_node
        self.input_datatype = input_datatype
        self.output_datatype = output_datatype

    def __eq__(self, other: object):
        if not isinstance(other, FunctionDefinitionNode):
            return False
        return self.function_name == other.function_name and self.parameter_identifier == other.parameter_identifier and self.block_node == other.block_node
    
    def __repr__(self):
        return f'fn {self.function_name} ({self.parameter_identifier}: {self.input_datatype}) -> {self.output_datatype} {self.block_node}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return IfExpressionNode(
            self.function_name.sub(old_node, new_node),
            self.parameter_identifier.sub(old_node, new_node),
            self.block_node.sub(old_node, new_node),
            self.context)
    
# Head

class HeadNode(Node):
    def __init__(self, item_nodes: List[ItemNode], context: Context):
        self.item_nodes = item_nodes
        self.context = context

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HeadNode):
            return False
        for i in range(len(self.item_nodes)):
            if self.item_nodes[i] != other.item_nodes[i]:
                return False
        return True

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return HeadNode(
            [item_node.sub(old_node, new_node) for item_node in self.item_nodes],
            self.context)