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
    def __init__(self, input_identifier_nodes: List[IdentifierNode], expression_node: ExpressionNode, input_datatypes: List[ExpressionNode], output_datatype: ExpressionNode):
        self.input_nodes = input_identifier_nodes
        self.output_node = expression_node
        self.input_datatypes = input_datatypes
        self.output_datatype = output_datatype

    def __repr__(self) -> str:
        return f'({self.input_nodes}: {self.input_datatypes}) -> {self.output_datatype} => {self.output_node}'

# Value subclasses

class DatatypeValue(Value):
    def __init__(self, datatype: DataType):
        super().__init__(datatype, DatatypeType())

class NullValue(Value):
    def __init__(self):
        super().__init__(None, NullType())

class IntValue(Value):
    def __init__(self, raw_int: int):
        super().__init__(raw_int, IntType())

    def __add__(self, other: object) -> IntValue:
        if not isinstance(other, IntValue):
            raise AttributeError()
        return IntValue(self.value + other.value)
    
    def __sub__(self, other: object) -> IntValue:
        if not isinstance(other, IntValue):
            raise AttributeError()
        return IntValue(self.value - other.value)
    
    def __mul__(self, other: object) -> IntValue:
        if not isinstance(other, IntValue):
            raise AttributeError()
        return IntValue(self.value * other.value)
    
    def __truediv__(self, other: object) -> FloatValue:
        if not isinstance(other, IntValue):
            raise AttributeError()
        return FloatValue(self.value / other.value)
    
    def println(self):
        print(self.value)

class FloatValue(Value):
    def __init__(self, raw_float: float):
        super().__init__(raw_float, FloatType())

    def __add__(self, other: object) -> FloatValue:
        if not isinstance(other, FloatValue):
            raise AttributeError()
        return FloatValue(self.value + other.value)
    
    def __sub__(self, other: object) -> FloatValue:
        if not isinstance(other, FloatValue):
            raise AttributeError()
        return FloatValue(self.value - other.value)
    
    def __mul__(self, other: object) -> FloatValue:
        if not isinstance(other, FloatValue):
            raise AttributeError()
        return FloatValue(self.value * other.value)
    
    def __truediv__(self, other: object) -> FloatValue:
        if not isinstance(other, FloatValue):
            raise AttributeError()
        return FloatValue(self.value / other.value)
    
    def println(self):
        print(self.value)

class BoolValue(Value):
    def __init__(self, raw_bool: bool):
        super().__init__(raw_bool, BoolType())

class StringValue(Value):
    def __init__(self, raw_str: str):
        super().__init__(raw_str, StringType())

    def __repr__(self) -> str:
        return f'"{self.value}"'
    
    def __add__(self, other: object) -> StringValue:
        if not isinstance(other, StringValue):
            raise AttributeError()
        return StringValue(self.value + other.value)
    
    def println(self):
        print(self.value)

class CharValue(Value):
    def __init__(self, raw_char: str):
        # Ensure that the string is only one character long
        if len(raw_char) != 1:
            raise ValueError('char value must contain only one character')
        super().__init__(raw_char, CharType())

class FunctionValue(Value):
    def __init__(self, input_identifier_nodes: List[IdentifierNode], expression_node: ExpressionNode, input_datatypes: List[ExpressionNode], output_datatype: ExpressionNode):
        super().__init__(FunctionObject(input_identifier_nodes, expression_node, input_datatypes, output_datatype), FunctionType(input_datatypes, output_datatype))

class ArrayValue(Value):
    def __init__(self, raw_values: List[Value], datatype: ExpressionNode):
        super().__init__(raw_values, ArrayType(datatype))

class VectorValue(Value):
    def __init__(self, raw_values: List[Value], datatypes: List[ExpressionNode]):
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
    
    def println(self):
        print(f'{self.datatype} ' + '{ ' + ', '.join([f'{member.identifier}: {member.value}' for member in self.value.members]) +' }')

# Value exits

class ValueExit(Exception):
    def __init__(self):
        pass

class ReturnExit(Exception):
    def __init__(self, node: Node):
        self.node = node

class BreakExit(Exception):
    def __init__(self, node: Node):
        self.node = node

class ContinueExit(Exception):
    def __init__(self):
        pass

class RaiseExit(Exception):
    def __init__(self, node: Node):
        self.node = node

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

class DatatypeNode(LiteralNode):
    def __init__(self, value: DatatypeValue, context: Context):
        super().__init__(value, context)

class ArrayNode(LiteralNode):
    def __init__(self, value: ArrayValue, context: Context):
        super().__init__(value, context)

class VectorNode(LiteralNode):
    def __init__(self, value: VectorValue, context: Context):
        super().__init__(value, context)

class FunctionDatatypeNode(ExpressionNode):
    def __init__(self, input_datatype_nodes: List[ExpressionNode], output_datatype_node: ExpressionNode, context: Context):
        super().__init__(context)

        self.input_datatype_nodes = input_datatype_nodes
        self.output_datatype_node = output_datatype_node
    
    def __repr__(self) -> str:
        return f'{repr_ts([str(node) for node in self.input_datatype_nodes])} -> {self.output_datatype_node}'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FunctionDatatypeNode):
            return False
        return self.input_datatype_nodes == other.input_datatype_nodes and self.output_datatype_node == other.output_datatype_node

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
    
# x::y
class ScopeNode(ExpressionNode):
    def __init__(self, scope_node: ExpressionNode, reference_node: IdentifierNode, context: Context):
        super().__init__(context)
        
        self.scope_node = scope_node
        self.reference_node = reference_node

    def __repr__(self) -> str:
        return f'{self.scope_node}::{self.reference_node}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScopeNode):
            return False
        return self.scope_node == other.scope_node and self.reference_node == other.reference_node

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return DivisionNode(
            self.scope_node.sub(old_node, new_node),
            self.reference_node.sub(old_node, new_node),
            self.context)
    
# x.y
class MemberAccessNode(ExpressionNode):
    def __init__(self, struct_node: ExpressionNode, member_node: IdentifierNode, context: Context):
        super().__init__(context)

        self.struct_node = struct_node
        self.member_node = member_node

    def __repr__(self) -> str:
        return f'{self.struct_node}.{self.member_node}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return MemberAccessNode(
            self.struct_node.sub(old_node, new_node),
            self.member_node.sub(old_node, new_node),
            self.context)
    
LocatorNode = IdentifierNode | ScopeNode | MemberAccessNode

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
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return AdditionNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x - y
class SubtractionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '-', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return SubtractionNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x * y
class MultiplicationNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '*', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return MultiplicationNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x / y
class DivisionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '/', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return DivisionNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x % y
class ModulusNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '%', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return ModulusNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# Logical Binary Operators

# x and y
class AndNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, 'and', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return AndNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x or y
class OrNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, 'or', context)
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return OrNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# Relational Binary Operators

# x == y
class EqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '==', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return EqualToNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x != y
class NotEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '!=', context)
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return NotEqualToNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x < y
class LessThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '<', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return LessThanNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x > y
class GreaterThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '>', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return GreaterThanNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x <= y
class LessThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '<=', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return LessThanOrEqualToNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# x >= y
class GreaterThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, '>=', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return GreaterThanOrEqualToNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)

# t { m: v, ... }
class ConstructorNode(ExpressionNode):
    def __init__(self, datatype_node: ExpressionNode, member_ids: List[IdentifierNode], member_value_nodes: List[ExpressionNode], context: Context):
        super().__init__(context)

        self.datatype_node = datatype_node
        self.member_ids = member_ids
        self.member_value_nodes = member_value_nodes

    def __repr__(self) -> str:
        a = ", ".join([f'{member_id}: {member_value_node}' for member_id, member_value_node in zip(self.member_ids, self.member_value_nodes)])
        return f'{self.datatype_node} {{{a}}}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return ConstructorNode(
            self.datatype_node.sub(old_node, new_node),
            [member_id.sub(old_node, new_node) for member_id in self.member_ids],
            [member_value_node.sub(old_node, new_node) for member_value_node in self.member_value_nodes],
            self.context)

# f(x, ...)
class FunctionApplicationNode(ExpressionNode):
    def __init__(self, function_node: ExpressionNode, input_nodes: List[ExpressionNode], context: Context):
        super().__init__(context)

        self.function_node = function_node
        self.input_nodes = input_nodes

    def __repr__(self) -> str:
        return f'{self.function_node}({", ".join([str(input_node) for input_node in self.input_nodes])})'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return FunctionApplicationNode(
            self.function_node.sub(old_node, new_node),
            [input_node.sub(old_node, new_node) for input_node in self.input_nodes],
            self.context)
    
# Type cast node

# x as t
class TypeCastNode(BinaryOperatorNode):
    def __init__(self, node: ExpressionNode, datatype: ExpressionNode, context: Context):
        super().__init__(node, datatype, 'as', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return LessThanNode(
            self.left_node.sub(old_node, new_node),
            self.right_node.sub(old_node, new_node),
            self.context)
        
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

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return NegativeNode(
            self.node.sub(old_node, new_node),
            self.context)

# not x
class NotNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode, context: Context):
        super().__init__(node, 'not', context)

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return NegativeNode(
            self.node.sub(old_node, new_node),
            self.context)

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
    def __init__(self, locator: LocatorNode, expression: ExpressionNode, context: Context):
        super().__init__(context)

        self.locator = locator
        self.expression = expression

    def __repr__(self) -> str:
        return f'{self.locator} = {self.expression}'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VariableReassignmentNode):
            return False
        return self.locator == other.locator and self.expression == other.expression
    
    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return VariableReassignmentNode(
            self.locator.sub(old_node, new_node),
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
    
class AnonymousFunctionDefinitionNode(ExpressionNode):
    def __init__(self, parameter_identifiers: List[IdentifierNode], expression_node: ExpressionNode, input_datatypes: List[ExpressionNode], output_datatype: ExpressionNode, context: Context):
        super().__init__(context)
        
        self.parameter_identifiers = parameter_identifiers
        self.expression_node = expression_node
        self.input_datatypes = input_datatypes
        self.output_datatype = output_datatype

    def __eq__(self, other: object):
        if not isinstance(other, FunctionDefinitionNode):
            return False
        return self.parameter_identifiers == other.parameter_identifiers and self.expression_node == other.expression_node
    
    def __repr__(self):
        return f'fn ({self.parameter_identifiers}: {self.input_datatypes}) -> {self.output_datatype} {self.expression_node}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return FunctionDefinitionNode(
            [parameter_identifier.sub(old_node, new_node) for parameter_identifier in self.parameter_identifiers],
            self.expression_node.sub(old_node, new_node),
            self.context)
    
class AnonymousStructDefinitionNode(ExpressionNode):
    def __init__(self, member_identifiers: List[IdentifierNode], member_datatypes: List[ExpressionNode], context: Context):
        super().__init__(context)
        
        self.member_identifiers = member_identifiers
        self.member_datatypes = member_datatypes

    def __eq__(self, other: object):
        if not isinstance(other, StructDefinitionNode):
            return False
        return self.member_identifiers == other.member_identifiers and self.member_datatypes == other.member_datatypes
    
    def __repr__(self):
        return f'struct {{{self.member_identifiers}: {self.member_datatypes}}}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return StructDefinitionNode(
            [parameter_identifier.sub(old_node, new_node) for parameter_identifier in self.member_identifiers],
            [parameter_datatype.sub(old_node, new_node) for parameter_datatype in self.member_datatypes],
            self.context)

# Items

class ItemNode(Node):
    def __init__(self, context: Context):
        super().__init__(context)

class ImportNode(ItemNode):
    def __init__(self, file_name_node: ExpressionNode, identifier_node: IdentifierNode, context: Context):
        super().__init__(context)

        self.file_name_node = file_name_node
        self.identifier_node = identifier_node

    def __eq__(self, other: object):
        if not isinstance(other, ImportNode):
            return False
        return self.file_name_node == other.file_name_node and self.identifier_node == other.identifier_node
    
    def __repr__(self):
        return f'import {self.file_name_node} as {self.identifier_node}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return IfExpressionNode(
            self.function_name.sub(old_node, new_node),
            [parameter_identifier.sub(old_node, new_node) for parameter_identifier in self.parameter_identifiers],
            self.expression_node.sub(old_node, new_node),
            self.context)

class FunctionDefinitionNode(ItemNode):
    def __init__(self, function_name: IdentifierNode, parameter_identifiers: List[IdentifierNode], expression_node: ExpressionNode, input_datatypes: List[ExpressionNode], output_datatype: ExpressionNode, context: Context):
        super().__init__(context)
        
        self.function_name = function_name
        self.parameter_identifiers = parameter_identifiers
        self.expression_node = expression_node
        self.input_datatypes = input_datatypes
        self.output_datatype = output_datatype

    def __eq__(self, other: object):
        if not isinstance(other, FunctionDefinitionNode):
            return False
        return self.function_name == other.function_name and self.parameter_identifiers == other.parameter_identifiers and self.expression_node == other.expression_node
    
    def __repr__(self):
        return f'fn {self.function_name} ({self.parameter_identifiers}: {self.input_datatypes}) -> {self.output_datatype} {self.expression_node}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return FunctionDefinitionNode(
            self.function_name.sub(old_node, new_node),
            [parameter_identifier.sub(old_node, new_node) for parameter_identifier in self.parameter_identifiers],
            self.expression_node.sub(old_node, new_node),
            self.context)
    
class StructDefinitionNode(ItemNode):
    def __init__(self, struct_name: IdentifierNode, member_identifiers: List[IdentifierNode], member_datatypes: List[ExpressionNode], context: Context):
        super().__init__(context)
        
        self.struct_name = struct_name
        self.member_identifiers = member_identifiers
        self.member_datatypes = member_datatypes

    def __eq__(self, other: object):
        if not isinstance(other, StructDefinitionNode):
            return False
        return self.struct_name == other.struct_name and self.member_identifiers == other.member_identifiers and self.member_datatypes == other.member_datatypes
    
    def __repr__(self):
        return f'struct {self.struct_name} {{{self.member_identifiers}: {self.member_datatypes}}}'

    def sub(self, old_node, new_node):
        if self == old_node:
            return new_node
        return StructDefinitionNode(
            self.struct_name.sub(old_node, new_node),
            [parameter_identifier.sub(old_node, new_node) for parameter_identifier in self.member_identifiers],
            [parameter_datatype.sub(old_node, new_node) for parameter_datatype in self.member_datatypes],
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