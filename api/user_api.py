"""
用户管理相关的 fastapi 接口，包括用户注册、用户登录、获取用户信息等。
"""
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm as LoginForm, OAuth2PasswordBearer
from schema.user_schema import UserRegister
from controller.user_controller import UserController
from schema.user_schema import UserInfo, UserToken
from schema.user_response_schema import UserRegisterResponse
from services.database import Base, engine, get_db


def get_uc(db=Depends(get_db)):
    """
    获取一个 UserController 对象。

    :param db: Sqlalchemy 数据库会话。
    :return: 一个 UserController 对象。
    """
    return UserController(db)


Base.metadata.create_all(bind=engine)  # see HERE!

router = APIRouter(prefix="/user", tags=["用户管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")



@router.post("/register", response_model=UserRegisterResponse, name="用户注册")
def register(register_data: UserRegister, uc: UserController = Depends(get_uc)):
    """
    TODO
    """
    result = uc.register(register_data.username, register_data.password, register_data.email)
    return UserRegisterResponse(**{"message": result})


@router.post("/login", response_model=UserToken, name="用户登录")
def login(user_data: Annotated[LoginForm, Depends()], uc: UserController = Depends(get_uc)):
    """
    TODO    
    """
    token = uc.login(user_data.username, user_data.password)
    token_data = {"message": "success","access_token": token, "token_type": "bearer"}
    return UserToken(**token_data)


@router.get("/info", response_model=UserInfo, name="读取用户信息")
def read_info(token = Depends(oauth2_scheme), uc: UserController = Depends(get_uc)):
    """
    TODO
    """
    result = uc.get_user_info(token)
    return UserInfo(**result)

# @router.get("/delete")
# def delete_user(
#     user_name: str,
#     user_token: Depends(oauth2_scheme),
#     user_controller: UserController = Depends(get_user_controller),
# ):
#     return user_controller.delete(user_name, user_token)
