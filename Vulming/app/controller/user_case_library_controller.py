from ..services.user_case_library import UserCaseLibrary
from ..services.test_case import TestCase

class UserCaseLibraryController:

    def __init__(self, ucl: UserCaseLibrary) -> None:
        
        self.ucl = ucl
    
    def add(self, g_name: str, test_case: TestCase):

        try:
            self.ucl.case_library[g_name].append(test_case)
        
        except KeyError as e:
            raise e
    
    def delete(self, g_name: str, name: str):
        pass
    
        
        