from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(examples=["test"], pattern="^[a-zA-Z0-9_-]{4,16}$")


class UserRegister(UserBase):
    # username: str = Field(pattern="^[a-zA-Z0-9_-]{4,16}$")
    password: str = Field(pattern="^[a-zA-Z0-9_-]{4,16}$")
    email: str = Field(pattren=r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "mirror4s",
                    "password": "mirror4s",
                    "email": "mirror4s@birkenwald.cn"
                }
            ]
        }
    }


class UserInfo(BaseModel):
    username: str
    id: int
    email: str
    role: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "mirror4s",
                    "id": 0,
                    "email": "mirror4s@birkenwald.cn",
                    "role": "normal"

                }
            ]
        }
    }


class UserToken(BaseModel):
    message: str
    access_token: str
    token_type: str = "Bearer"
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"message": "登录成功",
                 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJKaG9uIERvZSIsImV4cCI6IjExIiwiaWF0IjoxNTE2MjM5MDIyfQ.mc0XDHX04cpCoEqiXx5ARDudga4ca6IN7IfycCdskBA",
                 "token_type": "Bearer"
                 }
            ]
        }
    }
