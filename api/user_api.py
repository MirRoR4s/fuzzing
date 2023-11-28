"""
用户管理相关的 fastapi 接口，包括用户注册、用户登录、获取用户信息等。

"""
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from model.schema.user_schema import UserRegister
from model.user_manager import UserManager
from model.schema.user_schema import UserInfo
from model.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)  # see HERE!
router = APIRouter(prefix="/user", tags=["用户管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register", name="用户注册")
def register(user_register: UserRegister, db=Depends(get_db)):
    """
        register 根据用户名 username 、密码 password 、邮箱 email 完成注册。

    样例：
    {

        username: "test",
        password: "test",
        email: "xxxxxx@qq.com"
    }
    """
    user_manager = UserManager(db)
    return user_manager.create_user(user_register.username, user_register.password, user_register.email)


@router.post("/login", name="用户登录")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db=Depends(get_db)):
    """
    传入用户名和密码进行登录

    样例如下：

        1.username=test&password=test

    """
    user_manager = UserManager(db)
    return user_manager.authenticate_user(form_data.username, form_data.password)


@router.get("/info", response_model=UserInfo, name="获取当前用户信息")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_manager = UserManager(db)
    return user_manager.get_current_user_info(token)
