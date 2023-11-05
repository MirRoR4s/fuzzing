from ..services.test_case import TestCase

class UserCaseLibrary:


    def __init__(self, case_library: dict[str, list[TestCase]] | None=None) -> None:
        
        self.case_library = case_library if case_library is not None else {}

        
        