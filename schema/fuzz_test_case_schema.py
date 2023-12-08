from pydantic import BaseModel

class Fuzzable(BaseModel):
    name: str
    default_value: int
    fuzzable: bool = False
    fuzz_values: list[int] | None = None

class FuzzableBlock(Fuzzable):
    request_name: str | None = None
    children: Fuzzable | None | list[Fuzzable] = None
    
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

class Static(BaseModel):
    name: str  = 'test'
    default_value: int = 0
    
    
class BitField(Fuzzable):
    width: int = 8
    max_num: int | None = None
    endian: str = '>'
    output_format: str = "binary"
    signed: bool = False
    full_range: bool = False
    
class Byte(BitField):
    pass

class Bytes(Fuzzable):
    size: int | None = None
    padding: bytes = b"\x00"
    max_len: int | None = None
    fuzz_values: list = None

class Word(BitField):
    width: int = 16