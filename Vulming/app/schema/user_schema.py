from pydantic import BaseModel, Field
from .test_case_schema import TestCase

class UserBase(BaseModel):
    username: str

class UserLogin(UserBase):
    password: str

class UserRegister(UserLogin):
    email: str

class UserInfo(UserBase):
    username: str
    id: int
    role: str
    cases: list[TestCase] = []
    
    
        

