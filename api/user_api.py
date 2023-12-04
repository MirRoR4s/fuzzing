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

router = APIRouter(prefix="/user")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register")
def register(
    user_register: UserRegister, 
    user_controller: UserController = Depends(get_user_controller)
    ) -> UserRegisterResponse:
    register_result = user_controller.register(user_register.username, user_register.password, user_register.email)
    response = {"message": register_result}
    return UserRegisterResponse(**response)


@router.post("/login", response_model=UserToken)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_controller: UserController = Depends(get_user_controller)
    ) -> UserToken:
    token = user_controller.login(form_data.username, form_data.password)
    token_data = {"message": "登录成功", "access_token": token, "token_type": "bearer"}
    return UserToken(**token_data)


@router.get("/info", response_model=UserInfo, name="读取用户信息")
async def read_users_me(token: str = Depends(oauth2_scheme), db= Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_controller = UserController(db)
    result = user_controller.get_user_info(token)
    print(result)
    if result == "token 无效" or result == "用户不存在":
        raise credentials_exception
    if result == "用户未激活":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="对不起，您的账户未激活")
    return UserInfo(**result)
