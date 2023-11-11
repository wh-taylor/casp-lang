from typing_extensions import List, Optional
from context import Context
from values import *

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

# Operation nodes

# Binary operators

class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(context)

        self.left_node = left_node
        self.right_node = right_node

# x + y
class AdditionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x - y
class SubtractionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x * y
class MultiplicationNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x / y
class DivisonNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x % y
class ModulusNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# Logical Binary Operators

# x and y
class AndNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x or y
class OrNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# Relational Binary Operators

# x == y
class EqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x != y
class NotEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x < y
class LessThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x > y
class GreaterThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x <= y
class LessThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# x >= y
class GreaterThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode, context: Context):
        super().__init__(left_node, right_node, context)

# Function application

# f x
class FunctionApplicationNode(BinaryOperatorNode):
    def __init__(self, function_node: ExpressionNode, input_node: ExpressionNode, context: Context):
        super().__init__(function_node, input_node, context)
        
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