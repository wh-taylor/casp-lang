from __future__ import annotations
from dataclasses import dataclass
from typing_extensions import List
import nodes

# Returns a comma-separated string of datatypes in a list
def repr_ts(ts: List[str]) -> str:
    return ', '.join([t for t in ts])

# Singleton types

class NamespaceType:
    def __repr__(self) -> str:
        return 'Namespace'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, NamespaceType)

class NullType:
    def __repr__(self) -> str:
        return 'Null'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, NullType)

class IntType:
    def __repr__(self) -> str:
        return 'Int'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, IntType)
    
class FloatType:
    def __repr__(self) -> str:
        return 'Float'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, FloatType)
    
class BoolType:
    def __repr__(self) -> str:
        return 'Bool'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, BoolType)
    
class StringType:
    def __repr__(self) -> str:
        return 'String'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, StringType)
    
class CharType:
    def __repr__(self) -> str:
        return 'Char'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, CharType)
    
class DatatypeType:
    def __repr__(self) -> str:
        return 'Type'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, DatatypeType)
    
# Product types; types with types in them
    
@dataclass
class FunctionType:
    xts: List[DataType]
    yt: DataType

    def __repr__(self) -> str:
        repr_xts = [f'({xt})' if type(xt) == FunctionType else repr(xt) for xt in self.xts]
        return f'{repr_ts(repr_xts)} -> {self.yt}'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, FunctionType) and list(self.xts) == list(other.xts) and self.yt == other.yt
    
@dataclass
class ArrayType:
    t: DataType

    def __repr__(self) -> str:
        return f'[{self.t}]'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, ArrayType) and self.t == other.t

@dataclass
class VectorType:
    ts: List[DataType]

    def __repr__(self) -> str:
        return f'({repr_ts([repr(t) for t in self.ts])})'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, VectorType) and list(self.ts) == list(other.ts)

@dataclass
class NewType:
    name: str
    member_names: List[nodes.IdentifierNode]
    member_ts: List[DataType]

    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, NewType) and self.name == other.name and list(self.member_names) == list(other.member_names) and list(self.member_ts) == list(other.member_ts)
    
@dataclass
class AnonymousType:
    member_names: List[nodes.IdentifierNode]
    member_ts: List[DataType]

    def __repr__(self) -> str:
        repr_members = ', '.join([f'{member_name}: {member_t}' for member_name, member_t in zip(self.member_names, self.member_ts)])
        return f'struct {{{repr_members}}}'
    
    def __eq__(self, other: object) -> bool:
        return isinstance(other, NewType) and self.name == other.name and list(self.member_names) == list(other.member_names) and list(self.member_ts) == list(other.member_ts)

DataType \
    = NamespaceType | NullType | IntType | FloatType | BoolType \
    | StringType | CharType | DatatypeType \
    | FunctionType | ArrayType | VectorType \
    | NewType
