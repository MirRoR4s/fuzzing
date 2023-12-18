"""
与用户管理相关的 fastapi 接口，包含的功能有用户注册、用户登录、查看用户信息等。
关于相关的接口规范已通过 fastapi doc 文档自动生成，具体参看 http://{ip}:{port}/docs
"""
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm as LoginForm, OAuth2PasswordBearer
from controller.user_controller import UserController
from schema.user_schema import UserInfo, UserToken, UserRegister
from schema.user_response_schema import UserRegisterResponse
from services.database import Base, engine, get_db

def init_user_controller(db=Depends(get_db)):
    """
    获取一个 UserController 对象，
    
    后续通过 fastapi 的依赖注入将该对象作为用户接口每个路径操作函数的参数。

    :param db: sqlalchemy.orm.sessionmaker Sqlalchemy 数据库会话。
    :return: controller.user_controller.UserController 一个 UserController 对象。
    """
    return UserController(db)

Base.metadata.create_all(bind=engine)  # see HERE!
router = APIRouter(prefix="/user", tags=["用户接口"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register", response_model=UserRegisterResponse, name="用户注册")
def register(register_data: UserRegister, uc: UserController = Depends(init_user_controller)):
    """
    注册用户。
    
        :param username: str, 用户名称。
        :param password: str, 用户密码。
        :param email: str, 用户邮箱。
        :param uc: 用户控制器类，负责调用后端方法完成注册。
        
        :return: 
    """
    uc.register(register_data.username, register_data.password, register_data.email)
    return UserRegisterResponse(**{"message": "注册成功"})


@router.post("/login", response_model=UserToken, name="用户登录")
def login(
    user_data: Annotated[LoginForm, Depends()],
    uc: UserController = Depends(init_user_controller)
):
    """
    用户登录。
    
        :param username: 用户名称，格式要求同上。
        :param password: 用户密码，格式要求同上。
        
        :return: 用户 Token。    
    """
    token = uc.login(user_data.username, user_data.password)
    token_data = {"message": "success","access_token": token, "token_type": "bearer"}
    return UserToken(**token_data)


@router.get("/info", response_model=UserInfo, name="读取用户信息")
def read_info(token = Depends(oauth2_scheme), uc: UserController = Depends(init_user_controller)):
    """
    读取用户信息。
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
