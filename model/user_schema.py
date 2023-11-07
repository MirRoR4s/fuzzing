from pydantic import BaseModel


class UserBase(BaseModel):
    username: str

class UserLogin(UserBase):
    password: str

class UserRegister(UserLogin):
    email: str

class UserInfo(UserBase):
    id: int
    role: str

