from __future__ import annotations
from dataclasses import dataclass
from typing_extensions import List

def ts_repr(ts: List[DataType]) -> str:
    return ', '.join([repr(t) for t in ts])

class IntType:
    def __repr__(self) -> str:
        return 'int'
    
class FloatType:
    def __repr__(self) -> str:
        return 'float'
    
class BoolType:
    def __repr__(self) -> str:
        return 'bool'
    
class StringType:
    def __repr__(self) -> str:
        return 'str'
    
class CharType:
    def __repr__(self) -> str:
        return 'char'
    
@dataclass
class FunctionType:
    xt: DataType
    yt: DataType

    def __repr__(self) -> str:
        repr_xt = f'({self.xt})' if type(self.xt) == FunctionType else repr(self.xt)
        return f'{repr_xt} -> {self.yt}'
    
@dataclass
class ArrayType:
    t: DataType

    def __repr__(self) -> str:
        return f'[{self.t}]'

@dataclass
class VectorType:
    ts: List[DataType]

    def __repr__(self) -> str:
        return f'({ts_repr(self.ts)})'

@dataclass
class NewType:
    name: str

    def __repr__(self) -> str:
        return self.name

DataType \
    = IntType | FloatType | BoolType \
    | StringType | CharType \
    | FunctionType | ArrayType | VectorType \
    | NewType
