"""
用户管理相关的 fastapi 接口，包括用户注册、用户登录、获取用户信息等。

"""
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from model.user_schema import UserRegister
from model.crud import get_db
from model.user_manager import UserManager
from model.user_schema import UserInfo
from model.database import Base, engine


Base.metadata.create_all(bind=engine)  # see HERE!
router = APIRouter(prefix="/user", tags=["用户管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")



@router.post("/register", name="用户注册")
def register(user_register: UserRegister, db = Depends(get_db)):
    """
    register 根据用户名、密码、邮箱完成注册。

    :param user_register: _description_
    :type user_register: UserRegister
    :param db: _description_, defaults to Depends(get_db)
    :type db: _type_, optional
    :return: _description_
    :rtype: _type_
    """
    user_manager = UserManager(db)
    user_manager.create_user(user_register.username, user_register.password, user_register.email)
    db.close()
    
    return {"message": "注册成功"}

@router.post("/login", name="用户登录")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db = Depends(get_db)):
    user_manager = UserManager(db)
    access_token = user_manager.authenticate_user(form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/info", response_model=UserInfo, name="获取当前用户信息")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_manager = UserManager(db)
    print(token)
    return user_manager.get_current_user_info(token)
    