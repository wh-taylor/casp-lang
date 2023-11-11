from typing_extensions import List, Optional
from values import *

# Base node

class Node:
    def __init__(self):
        pass

# Base statement node

class StatementNode(Node):
    def __init__(self):
        super().__init__()

# Base expression node

class ExpressionNode(StatementNode):
    def __init__(self):
        super().__init__()

# Value nodes

class LiteralNode(ExpressionNode):
    def __init__(self, value: Value):
        super().__init__()

        self.value = value


class IntNode(LiteralNode):
    def __init__(self, value: IntValue):
        super().__init__(value)

class FloatNode(LiteralNode):
    def __init__(self, value: FloatValue):
        super().__init__(value)

class BoolNode(LiteralNode):
    def __init__(self, value: BoolValue):
        super().__init__(value)

class StringNode(LiteralNode):
    def __init__(self, value: StringValue):
        super().__init__(value)

class CharNode(LiteralNode):
    def __init__(self, value: CharValue):
        super().__init__(value)

class ArrayNode(LiteralNode):
    def __init__(self, value: ArrayValue):
        super().__init__(value)

class VectorNode(LiteralNode):
    def __init__(self, value: VectorValue):
        super().__init__(value)


class IdentifierNode(ExpressionNode):
    def __init__(self, identifier: str):
        super().__init__()

        self.identifier = identifier

# Operation nodes

# Binary operators

class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__()

        self.left_node = left_node
        self.right_node = right_node

# x + y
class AdditionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x - y
class SubtractionNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x * y
class MultiplicationNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x / y
class DivisonNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x % y
class ModulusNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# Logical Binary Operators

# x and y
class AndNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x or y
class OrNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# Relational Binary Operators

# x == y
class EqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x != y
class NotEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x < y
class LessThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x > y
class GreaterThanNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x <= y
class LessThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# x >= y
class GreaterThanOrEqualToNode(BinaryOperatorNode):
    def __init__(self, left_node: ExpressionNode, right_node: ExpressionNode):
        super().__init__(left_node, right_node)

# Function application

# f x
class FunctionApplicationNode(BinaryOperatorNode):
    def __init__(self, function_node: ExpressionNode, input_node: ExpressionNode):
        super().__init__(function_node, input_node)
        
# Unary Operators

class UnaryOperatorNode(ExpressionNode):
    def __init__(self, node: ExpressionNode):
        super().__init__()

        self.node = node

# -x
class NegativeNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode):
        super().__init__(node)

# not x
class NotNode(UnaryOperatorNode):
    def __init__(self, node: ExpressionNode):
        super().__init__(node)

# Type cast node

# x as t
class TypeCastNode(ExpressionNode):
    def __init__(self, node: ExpressionNode, datatype: DataType):
        super().__init__()

        self.node = node
        self.datatype = datatype

# Variables

class VariableDeclarationNode(ExpressionNode):
    def __init__(self, identifier: IdentifierNode, datatype: DataType, expression: ExpressionNode):
        super().__init__()
        
        self.identifier = identifier
        self.datatype = datatype
        self.expression = expression

class VariableReassignmentNode(ExpressionNode):
    def __init__(self, identifier: IdentifierNode, expression: ExpressionNode):
        super().__init__()

        self.identifier = identifier
        self.expression = expression

# Statements

class ReturnNode(StatementNode):
    def __init__(self, node: ExpressionNode):
        super().__init__()

        self.node = node

class BreakNode(StatementNode):
    def __init__(self, node: ExpressionNode):
        super().__init__()

        self.node = node

class ContinueNode(StatementNode):
    def __init__(self, node: ExpressionNode):
        super().__init__()

        self.node = node

# Block expressions

class BlockExpressionNode(ExpressionNode):
    def __init__(self, statements: List[StatementNode], expression: Optional[ExpressionNode]):
        super().__init__()

        self.statements = statements
        self.expression = expression

class IfExpressionNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, block: BlockExpressionNode, elseblock: BlockExpressionNode):
        super().__init__()

        self.condition = condition
        self.block = block
        self.elseblock = elseblock

class WhileExpressionNode(ExpressionNode):
    def __init__(self, condition: ExpressionNode, block: BlockExpressionNode):
        super().__init__()

        self.condition = condition
        self.block = block

class LoopExpressionNode(ExpressionNode):
    def __init__(self, block: BlockExpressionNode):
        super().__init__()

        self.block = block