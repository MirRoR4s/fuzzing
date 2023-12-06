"""
用户管理相关的 fastapi 接口，包括用户注册、用户登录、获取用户信息等。
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from schema.user_schema import UserRegister
from controller.user_controller import UserController
from schema.user_schema import UserInfo, UserToken
from schema.user_response_schema import UserRegisterResponse
from services.database import Base, engine, get_db
from dependencies.get_user_controller import get_user_controller


Base.metadata.create_all(bind=engine)  # see HERE!

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

router = APIRouter(prefix="/user", tags=["用户管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register", name="用户注册")
def register(
    user_register: UserRegister, 
    user_controller: UserController = Depends(get_user_controller)
    ) -> UserRegisterResponse:
    register_result = user_controller.register(user_register.username, user_register.password, user_register.email)
    response = {"message": register_result}
    return UserRegisterResponse(**response)

# @router.get("/delete")
# def delete_user(
#     user_name: str,
#     user_token: Depends(oauth2_scheme),
#     user_controller: UserController = Depends(get_user_controller),
# ):
#     return user_controller.delete(user_name, user_token)


@router.post("/login", response_model=UserToken, name="用户登录")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_controller: UserController = Depends(get_user_controller)
    ) -> UserToken:
    token = user_controller.login(form_data.username, form_data.password)
    token_data = {"message": "success", "access_token": token, "token_type": "bearer"}
    return UserToken(**token_data)


@router.get("/info", name="读取用户信息")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    user_controller: UserController = Depends(get_user_controller)
    ):
    result = user_controller.get_user_info(token)
    return result
