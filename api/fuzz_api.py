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

# async def get_user_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> int:
#     user_controller = UserController(db)

def get_fuzzing_controller(db = Depends(get_db)):
    return FuzzingController(db)

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
    result = fuzzing_controller.create_case_group(token, group_name, group_desc)
    return result


@router.post("/delete/group", name="删除模糊测试用例组")
async def delete_case_group(
    group_name: str = Query(min_length=3, max_length=15),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    删除一个名为 group name 的模糊测试用例组

        :param group_name: 组名
        :param token: 身份认证 token
        :param db: 数据库会话
        :raises HTTPException: 如果组名不存在或者发生了其他错误，抛出异常

        :return: 删除成功返回相应信息，否则返回异常
    """
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    try:
        result = fuzz_manager.delete_case_group(user_id, group_name)
        if result is False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模糊测试用例组不存在")
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发生未知异常")
    else:
        return "删除成功"
        


@router.post("/create/case", name="创建模糊测试用例")
async def create_case(
    group_name: str = Query(min_length=3, max_length=15),
    case_name: str = Query(min_length=3, max_length=15),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    创建一个名为 case name，属于 group name 组的模糊测试用例

    :param fuzz_test_case_group_name: 组名称，要求同上
    :param fuzz_test_case_name: 模糊测试用例名称，要求同上
    :param token: 身份认证token
    :param db: 数据库会话
    :raises HTTPException: 当模糊测试用例组不存在或是模糊测试用例名称重复时抛出异常
    :return: 一个包含着“创建成功”的字符串
    """
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    group_id = fuzz_manager.get_group_id(user_id, group_name)
    if group_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模糊测试用例组不存在")
    
    try:
        fuzz_manager.create_case(group_id, case_name)
    except exc.IntegrityError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, detail="模糊测试用例已存在"
            )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发生未知异常"
            )
    return "创建成功"
    


@router.post("/delete/case", name="删除模糊测试用例")
async def delete_fuzz_test_case(
    group_name: str = Query(min_length=3, max_length=15),
    case_name: str = Query(min_length=3, max_length=15),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    
    try:
        group_id = fuzz_manager.get_group_id(user_id, group_name)
        
        if group_id is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="模糊测试用例组不存在")
        
        result = fuzz_manager.delete_fuzz_test_case(group_id, case_name)
        
        if result is False:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="模糊测试用例不存在")
        
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发生未知异常")
    
    return "创建成功"
    
    
@router.post("/set/block", name="设置 Block ")
async def set_block(
    fuzz_test_case_group_name: str,
    fuzz_test_case_name: str,
    block_info: Block,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    return fuzz_manager.set_block(
        user_id, fuzz_test_case_group_name, fuzz_test_case_name, block_info
    )


@router.post("/set/static", name="设置 static ")
async def set_static(
    static: Annotated[Static, Body(embed=True)],
    fuzz_test_case_group_name: str,
    fuzz_test_case_name: str,
    block_name: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    设置一个 Static 原语的属性（可能会被插入某个 Block 中）

        :param fuzz_test_case_group_name: 模糊测试用例组名称，必须在数据库中存在
        :param fuzz_test_case_name: 模糊测试用例名称，必须在数据库中存在
        :param block_name: 当前原语所属 block 的名称（可选）
        :param name: 当前原语的名称（可选，默认为 None）
        :param default_value: 当前原语的默认值（可选，默认为 None）
        :param token:
        :param db:
        :return:
    """
    user_id = UserController(db).get_user_id(token)
    fuzz_manager = FuzzingController(db)
    name, default_value = static.name, static.default_value


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
