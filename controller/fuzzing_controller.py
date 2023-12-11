"""
模糊测试控制器类。
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from boofuzz import Fuzzable, Byte
from services.fuzzing_services import FuzzingService
from services.user_service import UserService
from exceptions.database_error import DatabaseError, GroupNotExistError, CaseNotExistError
from schema.fuzz_test_case_schema import Block, Byte, Bytes

class FuzzingController:
    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.user_service = UserService(db)
        self.fuzzing_service = FuzzingService(db)
        self.field_handlers = {
            "static": self.fuzzing_service.set_static,
            "block": self.fuzzing_service.set_block,
        }

    def create_case_group(self, user_id: int, group_name: str, desc: str | None = None):
        """
        TODO

        :param user_id: 
        :param group_name: 
        :param desc: , defaults to None
        :raises HTTPException: 
        :raises HTTPException: 
        """
        try:
            self.fuzzing_service.create_case_group(user_id, group_name, desc)
        except ValueError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组已存在") from e
        except DatabaseError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e

    def delete_case_group(self, user_id: int, group_name: str):
        """
        删除一个模糊测试用例组
        
        :param user_id: 用户id，要求在数据库中存在。
        :param group_name: 模糊测试用例组名称，要求在数据库中存在。
        """
        try:
            self.fuzzing_service.delete_fuzz_test_case_group(user_id, group_name)
        except GroupNotExistError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用例组不存在") from e
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务器内部错误") from e

    def create_case(self, user_id: int, group_name: str, case_name: str) -> None:
        """
        创建一个模糊测试用例

        :param user_id: 用户id
        :param group_name: 用例所属的组名称
        :param case_name: 用例名称
        """
        group_id = self.get_group_id(user_id, group_name)
        try:
            self.fuzzing_service.create_case(group_id, case_name)
        except ValueError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组或用例名称错误") from e
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e
        
    def delete_fuzz_test_case(self, token: int, group_name: str, case_name: str):
        """删除一个模糊测试用例，根据token获取用户id，随后根据用户id结合组名称获取组id，最后根据组id和用例名获取用例并删除。

        :param token: 有效的身份认证令牌
        :param group_name: 用例组名称
        :param case_name: 用例名称
        :return: None
        """
        try:
            user_id = self.user_service.get_user_info(token).get('id')
            group_id = self.fuzzing_service.select_case_group(user_id, group_name).id
            self.fuzzing_service.delete_fuzz_test_case(group_id, case_name)
        except ValueError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组或用例名称错误") from e
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e

    def set_block(self, user_id: int, g_name: str, c_name: str, block_info: dict): 
        """
        设置block类型的属性。

        :param user_id: 
        :param g_name: 
        :param c_name: 
        :param block_info: 
        :raises HTTPException: 
        :raises HTTPException: 
        """
        request_id = self.get_id(user_id, g_name, c_name)
        name = block_info.get('name')
        default_value = block_info.get('default_value')
        try:
            self.fuzzing_service.set_block(request_id, name, default_value)
        except ValueError as e:
            raise HTTPException(status_code=422, detail="block 名称重复") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="服务端异常") from e
        
    def set_byte(self, byte_primitive: dict, user_id: int, group_name: str, case_name: str, block_name: str | None = None):
        
        
        pass

    def set_bytes(
        self,
        user_id: int,
        group_name: str,
        name: str,
        bytes_info: Bytes,
        block_name: str | None = None,
    ):
        """
        set_bytes_field 设置 bytes 原语各项属性，并记录在数据库中

        :param user_id: 用户 id
        :type user_id: int
        :param group_name: 模糊测试用例组名称
        :type group_name: str
        :param name: 模糊测试用例名称
        :type name: str
        :param bytes_info: 各项属性信息
        :type bytes_info: Bytes
        :param block_name: 分组名称, 默认为 None
        :type block_name: str | None, optional
        """

        fuzzing_case_id = self.get_case_id(user_id, group_name, name)
        request_id = self.get_request_id(fuzzing_case_id)

        if fuzzing_case_id is not None and request_id is not None:
            bytes_field = BytesField(
                request_id=request_id,
                name=bytes_info.name,
                default_value=bytes_info.default_value,
                size=bytes_info.default_value,
                fuzzable=bytes_info.fuzzable,
            )

            if block_name is not None:
                bytes_field.block_id = self.read_block(request_id)

            self.db.add(bytes_field)
            self.db.commit()

            return "设置 bytes 字段成功!"
        return "对不起，您选择的模糊测试用例或 request 字段不存在。"

    def set_static(self, user_id: int, group_name: str, case_name: str, name: str, default_value: int = 0, block_name: str | None = None):
        """设定 static 原语的各项属性，包括名称、默认值。

        :param user_id: 用户 id                
        :param group_name: 模糊测试用例组名称
        :param case_name: 模糊测试用例名称
        :param block_name: 当前 static 原语所属的 block，默认为 None
        :param name: 当前 static 原语的名称
        :param default_value: 当前 static 原语的默认值
        """
        # group_id = self.get_group_id(user_id, group_name)
        # case_id = self.get_case_id(group_id, case_name)
        # request_id = self.get_request_id(case_id)
        request_id = self.get_id(user_id, group_name, case_name)
        try:
            self.fuzzing_service.set_static(request_id, name, default_value, block_name)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Static 原语重名")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")
    
    def set_block(self, user_id: int, group_name: str, case_name: str,block_info: dict):
        request_id = self.get_id(user_id, group_name, case_name)
        print(block_info)
        name = block_info.get('name')
        default_value = block_info.get('default_value')
        #  children_name = block_info.get('children_name')
        try:             
            self.fuzzing_service.set_block(request_id, name, default_value)
        except ValueError:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Block 重名")
        except Exception:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")
    
    def set_attribute(self, user_id: int, group_name: str, case_name: str, **kwargs):
        group_id = self.get_group_id(user_id, group_name)
        case_id = self.get_case_id(group_id, case_name)
        request_id = self.get_request_id(case_id)
    
    def get_id(self, user_id, group_name, case_name):
        group_id = self.get_group_id(user_id, group_name)
        case_id = self.get_case_id(group_id, case_name)
        request_id = self.get_request_id(case_id)
        return request_id
    
    def get_group_id(self, user_id:int, group_name: str) -> int:
        try:
            group = self.fuzzing_service.select_case_group(user_id, group_name)
        except GroupNotExistError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用例组不存在")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")
        return group.id
    
    def get_case_id(self, group_id: int, case_name: str) -> int:
        try:
            case = self.fuzzing_service.get_case(group_id, case_name)
        except GroupNotExistError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用例不存在")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")
        return case.id

    def get_request_id(self, case_id: int) -> int:
        """获取模糊测试用例对应的 Request 对象的 id。

        :param case_id: 模糊测试用例的 id。
        :return: Request 对象 id。
        """
        try:
            request = self.fuzzing_service.get_request(case_id)
        except Exception:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")
        return request.id
    
    # def read_block(self, request_id: int) -> BlockField | None:
    #     ans = self.db.scalar(
    #         select(BlockField).where(BlockField.request_id == request_id)
    #     )
    #     return ans
    
    def set_primitive(self, primitive_name: str, primitive: dict,  user_id: int, group_name: str, case_name: str, block_name: str | None = None,):
        """
        依据不同的原语名称，调用不同的数据库函数。
        当原语名称为 byte，调用 set byte 插入 byte 字段信息。
        当原语名称为 bytes，调用 set bytes 插入 bytes 字段信息。

        :param primitive_name: 原语名称。
        :param primitive: 含有原语各项字段的字典。
        :param block_name: 原语所属块的名称，默认为 None
        :param user_id: 用户 id。
        :param group_name: 用例组名称。
        :param case_name: 用例名称。
        :raises HTTPException: 
        :raises HTTPException: 
        """
        request_id = self.get_id(user_id, group_name, case_name)
        try:
            self.fuzzing_service.set_primitive(primitive_name, primitive, request_id, block_name)
        except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
                raise HTTPException(status_code=500, detail="服务端异常") from e
        return "设置成功"
