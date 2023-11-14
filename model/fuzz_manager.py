from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .sql_model import *
from .database import engine
from sqlalchemy import select


class FuzzManager:
    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.db = db

    def create_fuzzing_group(self, user_id: int, name: str, desc: str | None = None):
        """
        create_test_group 创建测试用例组

        :param name: 组名
        :type name: str
        :param desc: 组描述, defaults to None
        :type desc: str | None, optional
        """
        with Session(engine) as session:
            test_case_group = TestCaseGroup(user_id=user_id, name=name, desc=desc)
            session.add(test_case_group)
            session.commit()
        return "创建成功"

    def create_fuzzing_case(
        self,
        user_id: int,
        group_name: str,
        case_name: str,
        case_attr: str | None = None,
    ):
        """
        create_fuzzing_case _summary_

        :param user_id: _description_
        :type user_id: int
        :param group_name: _description_
        :type group_name: str
        :param case_name: _description_
        :type case_name: str
        """
        stmt = select(TestCaseGroup).where(
            TestCaseGroup.user_id == user_id and TestCaseGroup.name == group_name
        )
        test_case_group = self.db.scalar(stmt)
        group_id = test_case_group.id
        with self.db as session:
            test_case = FuzzyTestCase(name=case_name, test_case_group_id=group_id)
            session.add(test_case)
            session.commit()
        return "创建模糊测试用例成功"

    def set_fuzzing_case_field(
        self,
        user_id: int,
        fuzzing_case_group_name: str,
        fuzzing_case_name: str,
        fuzzing_case_type: str,
        **kwargs
    ):
        stmt = select(TestCaseGroup).where(
            TestCaseGroup.user_id == user_id
            and TestCaseGroup.name == fuzzing_case_group_name
        )

        fuzzing_case_group_id = self.db.scalar(stmt).id
        stmt1 = select(FuzzyTestCase).where(
            FuzzyTestCase.name == fuzzing_case_name
            and FuzzyTestCase.test_case_group_id == fuzzing_case_group_id
        )
        fuzzing_case_id = self.db.scalar(stmt1).id
        
        
        if fuzzing_case_type == "byte":
            
            pass
        elif fuzzing_case_type == "bytes":
            pass
        elif fuzzing_case_type == "block":
            pass
        
    def set_block_field(self):
        pass
    
    def set_byte_field(self):
        pass
    
    def set_bytes_field(self):
        pass
