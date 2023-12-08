"""
模糊测试 fastapi 接口
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import exc
from services.database import get_db
from schema.fuzz_test_case_schema import Block, Static, Byte, Bytes
from controller.user_controller import UserController
from controller.fuzzing_controller import FuzzingController


router = APIRouter(prefix="/fuzz/test", tags=["模糊测试管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_fuzzing_controller(db = Depends(get_db)):
    return FuzzingController(db)

def get_user_id(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """获取用户 id

    :param token: 用户身份令牌，其中含有用户的 id
    :param db: 数据库会话
    """
    user_controller = UserController(db)
    user_id = user_controller.get_user_info(token).get("id")
    return user_id
    

@router.post("/create/group", name="创建模糊测试用例组")
async def create_case_group(
    group_name: str = Query(min_length=3, max_length=15),
    group_desc: str | None = Query(default=None, max_length=100),
    token: str = Depends(oauth2_scheme),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
) -> str:
    """
    创建一个名为 group name，描述为 group desc 的模糊测试用例组

        :param group_name: 模糊测试用例组名称，长度必须位于 3 到 15 之间。
        :param group_desc: 模糊测试用例组描述，长度必须小于等于 100。
        :param token: 用于身份认证的 token，只有通过了身份认证才可以进行当前的创建操作。
        :param db: 用于数据库操作的会话。
        :return: 一个包含着”创建成功“的字符串
    """
    fuzzing_controller.create_case_group(token, group_name, group_desc)
    return "创建成功"


@router.post("/delete/group", name="删除模糊测试用例组")
async def delete_case_group(
    group_name: str = Query(min_length=3, max_length=15),
    token: str = Depends(oauth2_scheme),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
):
    """
    删除一个名为 group name 的模糊测试用例组

        :param group_name: 组名
        :param token: 身份认证 token
        :param db: 数据库会话
        :raises HTTPException: 如果组名不存在或者发生了其他错误，抛出异常

        :return: 删除成功返回相应信息，否则返回异常
    """
    
    fuzzing_controller.delete_case_group(token, group_name)
    return "删除成功"


@router.post("/create/case", name="创建模糊测试用例")
async def create_case(
    group_name: str = Query(min_length=3, max_length=15),
    case_name: str = Query(min_length=3, max_length=15),
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
):
    """创建一个模糊测试用例

    :param group_name: _description_, defaults to Query(min_length=3, max_length=15)
    :param case_name: _description_, defaults to Query(min_length=3, max_length=15)
    :param token: _description_, defaults to Depends(oauth2_scheme)
    :param fuzzing_controller: _description_, defaults to Depends(get_fuzzing_controller)
    :return: _description_
    """
    fuzzing_controller.create_case(user_id, group_name, case_name)
    return "创建成功"
    
@router.post("/delete/case", name="删除模糊测试用例")
async def delete_fuzz_test_case(
    group_name: str = Query(min_length=3, max_length=15),
    case_name: str = Query(min_length=3, max_length=15),
    token: str = Depends(oauth2_scheme),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
):
    """删除一个模糊测试用例

    :param group_name: 用例所属用例组，长度必须满足 Query(min_length=3, max_length=15)
    :param case_name: 用例名称，长度必须满足 Query(min_length=3, max_length=15)
    :param token: 有效的用户身份认证令牌
    :param fuzzing_controller: 模糊测试接口的依赖
    :return: _description_
    """
    fuzzing_controller.delete_fuzz_test_case(token, group_name, case_name)
    return "删除成功"
    
@router.post("/set/static", name="设置 static ")
async def set_static(
    group_name: str,
    case_name: str,
    static: Static,
    block_name: str | None = None,
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller)
) -> str:
    """
    设置一个 Static 原语的属性（可能会被插入某个 Block 中）

    :param group_name: _description_
    :param case_name: _description_
    :param name: _description_
    :param default_value: _description_
    :param block_name: _description_, defaults to None
    :param user_id: _description_, defaults to Depends(get_user_id)
    :param fuzzing_controller: _description_, defaults to Depends(get_fuzzing_controller)
    :return: _description_
    """
    name = static.name
    default_value = static.default_value
    fuzzing_controller.set_static(user_id, group_name, case_name, name, default_value, block_name)
    return "设置成功"

@router.post("/set/block", name="设置 Block ")
async def set_block(
    group_name: str,
    case_name: str,
    block_info: Block,
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller)
):
    """
    set attribute of the block 

    :param group_name: 
    :param case_name: name of the fuzz test case that contain this block. 
    :param block_info: Attribute of this block, contain name, default_value, request_name 
    :param user_id: user's id.
    :param fuzzing_controller: 
    :return: _description_
    """
    fuzzing_controller.set_block(user_id, group_name, case_name, dict(block_info))
    return "设置成功"
    

@router.post("/set/byte", name="设置 Byte ")
async def set_byte(
    byte_info: Annotated[Byte, Body(embed=True)],
    group_name: str,
    case_name: str,
    block_name: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    result = fuzz_manager.set_byte_primitive(dict(byte_info), user_id, group_name, case_name, block_name)
    if result == "模糊测试用例不存在" or result == "block 不存在" or result == "request 不存在":
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=result)
    return result
    


@router.post("/set/bytes", name="设置 Bytes 字段")
async def set_bytes(
    fuzz_test_case_group_name: str,
    fuzz_test_case_name: str,
    bytes_info: Bytes,
    block_name: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    可表示任意长度的二进制字节串模糊测试原语。
    """
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    return fuzz_manager.set_bytes(
        user_id, fuzz_test_case_group_name, fuzz_test_case_name, bytes_info, block_name
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
