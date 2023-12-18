"""
所有原语所含字段信息的原型类
"""
from pydantic import BaseModel


LITTLE_ENDIAN = '<'
BIG_ENDIAN = '>'

class Fuzzable(BaseModel):
    """
    所有 primitives 和 blocks 的父类。
    """
    name: str
    default_value: int | str | bytes | None = 0
    fuzzable: bool = False
    fuzz_values: list | None = None

class FuzzableBlock(Fuzzable):
    request_name: str | None = None
    children: Fuzzable | None | list[Fuzzable] = None
    
class Static(Fuzzable):
    name: str  = 'test'
    default_value: int = 0
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "test",
                    "default_value": 0
                }
            ]
        }
    }

class Simple(Fuzzable):
    fuzzable: bool = True

class Delim(Fuzzable):
    name: str
    default_value: str
    fuzzable: bool

class Group(BaseModel):
    name: str
    values: list[bytes] | list[str]
    default_value: str
    encoding: str = 'ascii'
    fuzzable: bool = True

class RandomData(BaseModel):
    name: str
    default_value: str | bytes | None = None
    min_length: int = 0
    max_length: int = 1
    max_mutations: int
    step: int | None = None
    fuzzable: bool = True

class String(BaseModel):
    name: str
    default_value: str
    size: int | None = None
    padding: bytes = b'\x00'
    encoding: str = 'ascii'
    max_len: int | None = None
    fuzzable: bool = True

class FromFile(BaseModel):
    name: str
    default_value: bytes
    filename: str
    max_len: int = 0
    fuzzable: bool = True

class Mirror(BaseModel):
    name: str
    primitive_name: str
    request_name: str
    fuzzable: bool = True

class BitField(BaseModel):
    name: str
    default_value: int
    width: int = 8
    max_num: int | None = None
    endian: str = '>'
    output_format: str = "binary"
    signed: bool = False
    full_range: bool = False
    fuzz_values: list | None = None
    fuzzable: bool = True
    
class Byte(BaseModel):
    name: str
    default_value: int
    max_num: int
    endian: str
    output_format: str
    signed: bool
    full_range: bool
    full_values: list[int]
    fuzzable: bool
    
class Bytes(BaseModel):
    name: str
    default_value: bytes = b''
    size: int | None = None
    padding: bytes = b"\x00"
    max_len: int | None = None
    fuzz_values: list = None

class Word(BaseModel):
    name: str
    default_value: int = 0
    max_num: int | None = None
    endian: str = LITTLE_ENDIAN
    output_format: str = 'binary'
    signed: bool = False
    full_range: bool = False
    fuzz_values: list | None = None
    fuzzable: bool = True
    
class DWord(Word):
    pass

class QWord(Word):
    pass

class Block(BaseModel):
    """
    fot the detailed information, see this: http://boofuzz.readthedocs.io/
    """
    name: str
    default_value: int | None = None
    children_name: str | None = None
    group: str | None = None
    encoder: str | None = None
    dep: str | None = None
    dep_value: bytes | None = None
    dep_values: list[bytes] | None = None
    dep_compare: str | None = None
