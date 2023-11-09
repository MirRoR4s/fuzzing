from pydantic import BaseModel


class TestCase(BaseModel):
    test_case_group_name: str
    test_case_name: str
    desc: str
    length: int
    unit: str
    default_value: int
    endian: str
    fuzzable: bool
    parent_id: int
    