from sqlalchemy.orm.session import Session
from sqlalchemy import select
from .sql_model import TestCaseGroup


class ProtocolLibraryManager:
    default_group = {
        
        "UMAS": {
            "Setup Communication": "建立连接"
            
        },
        
        "ENIP": {
            
        },
        
        "S7C": {
            
        }
    }

    
    def __init__(self, db: Session) -> None:
        self.db = db
    
    def select_case_group(self, user_id: int):
        stmt = select(TestCaseGroup).where(TestCaseGroup.user_id == user_id)
        result = self.db.execute(stmt)
        print(result)

        return self.default_group