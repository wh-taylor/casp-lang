from datatypes import *
from typing_extensions import List

# Error class
class InterpreterValueError(Exception):
    pass

# Base value class
class Value:
    def __init__(self, value, datatype: DataType):
        self.value = value
        self.datatype = datatype

    def get_datatype(self):
        return self.datatype

# Value subclasses

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

class CharValue(Value):
    def __init__(self, raw_char: str):
        # Ensure that the string is only one character long
        if len(raw_char) != 1:
            raise InterpreterValueError('char value must contain only one character')
        super().__init__(raw_char, CharType())

class ArrayValue(Value):
    def __init__(self, raw_values: List[Value], datatype: DataType):
        super().__init__(raw_values, ArrayType(datatype))

class VectorValue(Value):
    def __init__(self, raw_values: List[Value], datatypes: List[DataType]):
        # Raise an error if there are too few values.
        if len(raw_values) < len(datatypes):
            raise InterpreterValueError('too few values in vector')
        
        # Raise an error if there are too many values.
        if len(raw_values) > len(datatypes):
            raise InterpreterValueError('too many values in vector')
        
        # Match the values' datatypes and expected datatypes;
        # if there is an incorrect value datatype
        for i in range(len(raw_values)):
            actual_datatype = raw_values[i].get_datatype()
            expected_datatype = datatypes[i]

            if actual_datatype != expected_datatype:
                raise InterpreterValueError(f'value had type {actual_datatype} when {expected_datatype} was expected')
        
        super().__init__(raw_values, VectorType(datatypes))