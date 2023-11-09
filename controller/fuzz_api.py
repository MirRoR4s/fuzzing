from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from model.user_schema import UserRegister
from model.crud import get_db
from model.user_manager import UserManager
from model.protocol_library_manager import ProtocolLibraryManager
from model.user_schema import UserInfo
from typing import Annotated
from model.database import Base, engine


# Base.metadata.create_all(bind=engine)  # see HERE!
router = APIRouter(prefix="/fuzz", tags=["模糊测试"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")




@router.get("/library", name="读取用例库")
async def read_library(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_manager = UserManager(db)
    user_id = user_manager.get_current_user_info(token)['id']
    return ProtocolLibraryManager(db).select_case_group(user_id)
    
@router.post("/define", name="自定义测试用例")
async def define(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    
    