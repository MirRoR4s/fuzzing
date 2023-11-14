from pydantic import BaseModel


class Fuzzable(BaseModel):
    name: str
    default_value: str
    fuzzable: bool
    fuzz_values: list
    
class FuzzableBlock(Fuzzable):
    request_name: str | None = None
    children: Fuzzable | None | list[Fuzzable] = None
    
class Block(FuzzableBlock):
    group: str | None = None
    encoder: str | None = None
    dep: str | None = None
    dep_value: bytes | None = None
    dep_values: list[bytes] | None = None
    dep_compare: str | None = None

# class Repeat(Fuzzable):
#     block_name: str
#     request: Request | None = None
#     min_reps: int = 0
#     max_reps: int = 25
#     step: int = 1
#     variable = None
    
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