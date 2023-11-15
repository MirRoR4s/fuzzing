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


router = APIRouter(prefix="/fuzz", tags=["模糊测试"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")




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


@router.post("/set/block", name="设置 Block 字段")
async def set_block(
    fuzzing_case_group_name: str,
    fuzzing_case_name: str,
    block_info: Block,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = UserManager(db).get_current_user_info(token).get("id")
    fuzz_manager = FuzzManager(db)

    return fuzz_manager.set_block(
        user_id, fuzzing_case_group_name, fuzzing_case_name, block_info
    )


@router.post("/set/static", name="设置 static 字段")
async def set_static(
    fuzzing_gourp_name: str,
    fuzzing_case_name: str,
    static_info: Static,
    block_name: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    设置不进行模糊测试的静态字段。
    """
    pass


@router.post("/set/simple", name="设置 simple 字段")
async def set_simple():
    pass


@router.post("/set/delim", name="设置 delim 字段")
async def set_delim():
    pass


@router.post("/set/group", name="设置 Group 字段")
async def set_group():
    pass


@router.post("/set/randomData", name="设置 Random Data 字段")
async def set_random_data():
    pass


@router.post("/set/string", name="设置 String 字段")
async def set_string():
    pass


@router.post("/set/fromFile", name="设置 From File 字段")
async def set_fromFile():
    pass


@router.post("/set/mirror", name="设置 Mirror 字段")
async def set_mirror():
    pass


@router.post("/set/bitField", name="设置 Bit Field 字段")
async def set_bit_field():
    pass


@router.post("/set/byte", name="设置 Byte 字段")
async def set_byte(
    fuzzing_gourp_name: str,
    fuzzing_case_name: str,
    byteinfo: Byte,
    block_name: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = UserManager(db).get_current_user_info(token).get("id")

    fuzz_manager = FuzzManager(db)

    return fuzz_manager.set_byte(
        user_id, fuzzing_gourp_name, fuzzing_case_name, byteinfo, block_name
    )


@router.post("/set/bytes", name="设置 Bytes 字段")
async def set_bytes(
    fuzzing_gourp_name: str,
    fuzzing_case_name: str,
    bytes_info: Bytes,
    block_name: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    可表示任意长度的二进制字节串模糊测试原语。
    """

    user_id = UserManager(db).get_current_user_info(token).get("id")

    fuzz_manager = FuzzManager(db)

    return fuzz_manager.set_bytes(
        user_id, fuzzing_gourp_name, fuzzing_case_name, byteinfo, block_name
    )


@router.post("/set/word", name="设置 Word 字段")
async def set_word():
    pass


@router.post("/set/dWord", name="设置 Double World 字段")
async def set_dword():
    pass


@router.post("/set/qWord", name="设置 Q Word 字段")
async def set_qword():
    pass
