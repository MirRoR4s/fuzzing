# routers/user_api.py
from fastapi import HTTPException
import base64
import json
from fastapi import APIRouter, Depends, Header
from loguru import logger
from services.AES import decrypt_aes
from services.user.user_status_svc import get_current_user_role_level
from schema.user_schema import DeleteUser
from controllers.user_ctrl import UserController
from schema.user_schema import Response, CommonResponse,UserLoginField, UserRegisterField, UserUpdateField, UserQueryField, SaveUserPersonalConfig
from .users_api import oauth2_scheme
from ..services.case_library import TestCaseLibrary

router = APIRouter(prefix="/testcase", tags=["测试用例管理"])

test_case_library = TestCaseLibrary

# 查看用例库
@router.post('/library', name="用例库")
async def read_library(token: str = Depends(oauth2_scheme)):
    return test_case_library.default_test_cases + test_case_library.user_test_cases

