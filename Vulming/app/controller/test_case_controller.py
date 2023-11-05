from ..services.test_case import TestCase
from boofuzz.blocks import Request

class TestCaseController:

    def __init__(self, test_case: TestCase) -> None:
        
        self.test_case = test_case

    def set_name(self, name: str):
        
        self.test_case.name = name
    
    def set_attr(self, request: Request):

        self.test_case.attr = request

    def set_desc(self, desc: str):
        self.test_case.desc = desc
    

    