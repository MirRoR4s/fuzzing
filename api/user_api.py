"""
与用户管理相关的 fastapi 接口，包含的功能有用户注册、用户登录、查看用户信息等。
关于相关的接口规范已通过 fastapi doc 文档自动生成，具体参看 http://{ip}:{port}/docs
"""
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm as LoginForm, OAuth2PasswordBearer
from schema.user_schema import UserRegister
from controller.user_controller import UserController
from schema.user_schema import UserInfo, UserToken
from schema.user_response_schema import UserRegisterResponse
from services.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)  # see HERE!

router = APIRouter(prefix="/user", tags=["用户管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_uc(db=Depends(get_db)):
    """
    获取一个 UserController 对象，
    
    后续通过 fastapi 的依赖注入将该对象作为用户接口每个路径操作函数的参数。

    :param db: sqlalchemy.orm.sessionmaker Sqlalchemy 数据库会话。
    :return: controller.user_controller.UserController 一个 UserController 对象。
    """
    return UserController(db)

@router.post("/register", response_model=UserRegisterResponse, name="用户注册")
def register(register: UserRegister, uc: UserController = Depends(get_uc)):
    """
    注册用户。
    
        :param username: str, 用户名称。
        :param password: str, 用户密码。
        :param email: str, 用户邮箱。
        :param uc: 用户控制器类，负责调用后端方法完成注册。
        
        :return: 
    """
    uc.register(register.username, register.password, register.email)
    return UserRegisterResponse(**{"message": "注册成功"})


@router.post("/login", response_model=UserToken, name="用户登录")
def login(user_data: Annotated[LoginForm, Depends()], uc: UserController = Depends(get_uc)):
    """
    用户登录。
    
        :param username: 同 register。
        :param password: 同 register。
        
        :return: 用户 Token。    
    """
    token = uc.login(user_data.username, user_data.password)
    token_data = {"message": "success","access_token": token, "token_type": "bearer"}
    return UserToken(**token_data)


@router.get("/info", response_model=UserInfo, name="读取用户信息")
def read_info(token = Depends(oauth2_scheme), uc: UserController = Depends(get_uc)):
    """
    read user's information.

    :param token: token belongs to this user.
    :type token: str, optional
    :param uc: 
    :type uc: UserController
    :return: user's username, email, id.
    :rtype: UserInfo
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
