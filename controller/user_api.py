from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from model.user_schema import UserRegister
from model.crud import get_db
from model.user_manager import UserManager
from model.user_schema import UserInfo
from typing import Annotated
from model.database import Base, engine

Base.metadata.create_all(bind=engine)
router = APIRouter(prefix="/user", tags=["用户管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


@router.post("/register")
def register(user_register: UserRegister, db = Depends(get_db)):
    user_manager = UserManager(db)
    user_manager.create_user(user_register.username, user_register.password, user_register.email)
    db.close()
    
    return {"message": "注册成功"}

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db = Depends(get_db)):
    user_manager = UserManager(db)
    access_token = user_manager.authenticate_user(form_data.username, form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/info", response_model=UserInfo, name="获取当前用户信息")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_manager = UserManager(db)
    return user_manager.get_current_user_info(token)
    