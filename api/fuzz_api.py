"""
模糊测试 fastapi 接口
"""
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from services.database import get_db
from schema.fuzz_test_case_schema import Static, Simple, Delim, Group, RandomData, String, FromFile, Mirror, BitField, Byte, Bytes, Word, DWord, QWord, Block
from controller.user_controller import UserController
from controller.fuzzing_controller import FuzzingController


router = APIRouter(prefix="/fuzz/test", tags=["模糊测试管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_fuzzing_controller(db = Depends(get_db)):
    """
    获取一个 FuzzingController 类对象。

    :param db: sqlalchemy数据库会话。
    :return: FuzzingController 实例。
    """
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
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
) -> str:
    """
    创建一个名为 group name，描述信息为 group desc 的模糊测试用例组

        :param group_name: 模糊测试用例组名称，长度必须位于 3 到 15 之间。
        :param group_desc: 模糊测试用例组描述，长度必须小于等于 100。
        :param user_id: 有效的用户id。
        :return: 一个包含着”创建成功“的字符串
    """
    fuzzing_controller.create_case_group(user_id, group_name, group_desc)
    return "创建成功"


@router.post("/delete/group", name="删除模糊测试用例组")
async def delete_case_group(
    group_name: str = Query(min_length=3, max_length=15),
    user_id = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
):
    """
    删除一个名为 group name 的模糊测试用例组

        :param group_name: 组名
        :param user_id: 用户 id
        :param db: 数据库会话
        :raises HTTPException: 如果组名不存在或者发生了其他错误，抛出异常

        :return: 删除成功返回 "删除成功"
    """
    fuzzing_controller.delete_case_group(user_id, group_name)
    return "删除成功"


@router.post("/create/case", name="创建模糊测试用例")
async def create_case(
    group_name: str = Query(min_length=3, max_length=15),
    case_name: str = Query(min_length=3, max_length=15),
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
):
    """
    在名为 group_name 的模糊测试用例组下创建一个名为 case_name 的模糊测试用例。

        :param group_name: 模糊测试用例组名称，长度必须位于 3 到 15 之间。
        :param case_name: 模糊测试用例名称，长度必须位于 3 到 15 之间。
        :param user_id: 有效的用户 id。
        :param fuzzing_controller: 模糊测试接口控制器类实例
        :return: "创建成功"
    """
    fuzzing_controller.create_case(user_id, group_name, case_name)
    return "创建成功"

@router.post("/delete/case", name="删除模糊测试用例")
async def delete_fuzz_test_case(
    group_name: str = Query(min_length=3, max_length=15),
    case_name: str = Query(min_length=3, max_length=15),
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller),
):
    """
    删除一个模糊测试用例

    :param group_name: 用例所属用例组，长度必须满足 Query(min_length=3, max_length=15)
    :param case_name: 用例名称，长度必须满足 Query(min_length=3, max_length=15)
    :param token: 有效的用户身份认证令牌
    :param fuzzing_controller: 模糊测试接口的依赖
    :return: _description_
    """
    fuzzing_controller.delete_case(user_id, group_name, case_name)
    return "删除成功"

@router.post("/set/blocks/block", name="设置 Block ")
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

@router.post("/set/primitive", name="创建原语")
async def set_primitive(
    primitive_type: str,
    primitive_data: (
        Static | Simple | Delim | Group | RandomData | String | FromFile
        | Mirror | BitField | Byte | Bytes | Word | DWord | QWord
    ),
    group_name: str,
    case_name: str,
    block_name: str | None = None,
    user_id: int = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller)
):
    """
    创建一个 Boofuzz 原语。

    :param primitive_type: 原语的类型。
    :param primitive_data: 原语包含的字段信息。
    :param group_name: 原语所属的用例组名称。
    :param case_name: 原语所属的用例名称。
    :param block_name: 原语所属的 block 名称，默认为 None。
    :param user_id: 用户 id。
    :param fuzzing_controller: 
    :return: '创建成功'
    """
    fuzzing_controller.create_primitive(
        primitive_type, dict(primitive_data), user_id, group_name, case_name, block_name
    )
    return "创建成功"

@router.post("/delete/primitive", name="删除原语")
async def delete_primitive(
    group_name: str,
    case_name: str,
    primitive_name: str,
    user_id = Depends(get_user_id),
    fuzzing_controller: FuzzingController = Depends(get_fuzzing_controller)
) -> str:
    """
    从名为 case_name 的模糊测试用例中删除一个名为 primitive_name 的原语。

    :param group_name: 用例所属的用例组名称，需在数据库中存在。
    :param case_name: 用例名称，需在数据库中存在。
    :param primitive_name: 原语名称，需在数据库中存在。
    :param user_id: 用户 id，需在数据库中存在。
    :param fuzzing_controller: 模糊测试控制器类实例。
    :return: "删除成功"
    """
    fuzzing_controller.delete_primitive(user_id, group_name, case_name, primitive_name)
    return "删除成功"
