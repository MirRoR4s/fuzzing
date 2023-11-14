"""
模糊测试 fastapi 接口
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from model.crud import get_db
from model.user_manager import UserManager
from model.fuzz_manager import FuzzManager
from model.schema.fuzzing_case_schema import *

# Base.metadata.create_all(bind=engine)  # see HERE!
router = APIRouter(prefix="/fuzz", tags=["模糊测试"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

# @router.get("/library", name="读取用例库")
# async def read_library(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     user_manager = UserManager(db)
#     user_id = user_manager.get_current_user_info(token)['id']
#     return ProtocolLibraryManager(db).select_case_group(user_id)


@router.get("/create/group", name="创建测试用例组")
async def create_fuzzing_group(
    group_name: str,
    desc: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    传入名称和描述（可选）创建一个模糊测试用例组。
    """
    user_manager = UserManager(db)
    user_info = user_manager.get_current_user_info(token)
    user_id = user_info.get("id")
    fuzz_manager = FuzzManager(db)
    return fuzz_manager.create_fuzzing_group(user_id, group_name, desc)


@router.get("/create/fuzzing/case", name="创建模糊测试用例")
async def create_fuzzing_case(
    group_name: str,
    case_name: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    当用户选中某个模糊测试用例组后，可以传入以下的信息向组中添加一个模糊测试用例：

    1. 用例组名称
    2. 用例名称
    """
    user_manager = UserManager(db)
    user_info = user_manager.get_current_user_info(token)
    user_id = user_info.get("id")
    fuzz_manager = FuzzManager(db)
    return fuzz_manager.create_fuzzing_case(user_id, group_name, case_name)


@router.post("/set/fuzzing/case", name="设置模糊测试用例字段")
async def set_fuzzing_case_field(
    fuzzing_case_group_name: str,
    fuzzing_case_name: str,
    field_type: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),

):
    user_manager = UserManager(db)
    user_info = user_manager.get_current_user_info(token)
    user_id = user_info.get("id")
    fuzz_manager = FuzzManager(db)
    return fuzz_manager.set_fuzzing_case_field(
        user_id, fuzzing_case_group_name, fuzzing_case_name, field_type, **kwargs
    )
    
@router.post("/set/block", name = "设置 Block 字段")
async def set_block(fuzzing_case_group_name: str, fuzzing_case_name: str, block_info: Block,     token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):
    pass
