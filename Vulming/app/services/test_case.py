from boofuzz.blocks import Request

class TestCase:

    def __init__(self, name: str, desc: str=None, attr: Request|None=None) -> None:
        
        self.name = name
        self.desc = desc
        self.attr = attr
        