"""
"""
from sqlalchemy.orm import Session
from sqlalchemy import exc
from services.sql_model import ByteField, RequestField, BlockField
from services.fuzzing_services import FuzzingService
from services.user_service import UserService
from schema.fuzz_test_case_schema import Block, Byte, Bytes
from exceptions.database_error import DatabaseError, DuplicateKeyError
from fastapi import HTTPException, status

class FuzzingController:
    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.user_service = UserService(db)
        self.fuzzing_service = FuzzingService(db)

    def create_case_group(self, token: str, group_name: str, desc: str | None = None):
        try:
            user_id = self.user_service.get_user_info(token).get('id')
            self.fuzzing_service.create_case_group(user_id, group_name, desc)
        except ValueError:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组已存在")
        except DatabaseError:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端发生未知异常")    
        
    def delete_case_group(self, token: str, group_name: str):
        """
        删除具有指定用户 id 和名称的模糊测试用例组
        """
        try:
            user_id = self.user_service.get_user_info(token).get('id')
            self.fuzzing_service.delete_fuzz_test_case_group(user_id, group_name)
        except ValueError:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="删除的用例组不存在")
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务器内部错误")

    
    def create_case(self, token: str, group_name: str, case_name: str) -> None:
        """
        创建一个模糊测试用例

        :param token: 一个合法的用户身份令牌
        :param group_name: 用例所属的组名称
        :param case_name: 用例名称
        """
        try:
            user_id = self.user_service.get_user_info(token).get('id')
            group_id = self.fuzzing_service.read_case_group(user_id, group_name).id
            self.fuzzing_service.create_case(group_id, case_name)
        except ValueError:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组或用例名称错误")
        except Exception:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")
        
    def delete_fuzz_test_case(self, token: int, group_name: str, case_name: str):
        """删除一个模糊测试用例，根据token获取用户id，随后根据用户id结合组名称获取组id，最后根据组id和用例名获取用例并删除。

        :param token: 有效的身份认证令牌
        :param group_name: 用例组名称
        :param case_name: 用例名称
        :return: None
        """
        try:
            user_id = self.user_service.get_user_info(token).get('id')
            group_id = self.fuzzing_service.read_case_group(user_id, group_name).id
            self.fuzzing_service.delete_fuzz_test_case(group_id, case_name)
        except ValueError:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组或用例名称错误")
        except Exception:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常")

    def set_block(
        self,
        user_id: int,
        fuzz_test_case_group_name: str,
        fuzz_test_case_name: str,
        block_info: Block,
    ):        
        result = self.fuzzing_service.set_block(
            user_id, fuzz_test_case_group_name, fuzz_test_case_name, block_info
        )
        return "设置 block 字段成功" if result is True else "设置 block 字段失败"

    def set_byte_primitive(self, byte_primitive: dict, user_id: int, group_name: str, case_name: str, block_name: str | None = None):
        fuzz_test_case_id = self.fuzzing_service.read_fuzz_test_case(user_id, group_name, case_name).id
        if fuzz_test_case_id is None:
            return "模糊测试用例不存在"

        request_id = self.read_request_id(fuzz_test_case_id)
        if request_id is None:
            return "request 不存在"

        if block_name is not None:
            block_id = self.fuzzing_service.read_block(request_id).id
            if block_id is None:
                return "block 不存在"

        self.fuzzing_service.update_block_request_id(block_id, request_id)
        self.fuzzing_service.create_byte(request_id, block_id, **byte_primitive)

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
        request_id = self.read_request_id(fuzzing_case_id)

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

    def set_static(self):
        pass

    def set_simple(self):
        pass

    def set_delim(self):
        pass

    def set_group(self):
        pass

    def set_random_data(self):
        pass

    def set_string(self):
        pass

    def set_from_file(self):
        pass

    def set_mirror(self):
        pass

    def set_bit_field(self):
        pass

    def set_word(self):
        pass

    def set_dword(self):
        pass

    def set_qword(self):
        pass

    def get_case_id(self, group_id: int, case_name: str) -> int:
        case = self.fuzzing_service.read_fuzz_test_case(group_id, case_name)
        return case.id if case is not None else None

    def read_request_id(self, fuzz_test_case_id: int) -> int:
        """
        get_request_id 查询数据库，获取 request id。

        :param fuzzing_case_id: _description
        :type fuzzing_case_id: int
        :return: _description_
        :rtype: int
        """

        ans = self.db.scalar(
            select(RequestField).where(
                RequestField.fuzzing_case_id == fuzz_test_case_id
            )
        )
        return ans.id if ans is not None else None

    def read_block(self, request_id: int) -> BlockField | None:
        ans = self.db.scalar(
            select(BlockField).where(BlockField.request_id == request_id)
        )
        return ans
    
    def get_group_id(self, user_id:int, group_name: str) -> int | None:
        group = self.fuzzing_service.read_case_group(user_id, group_name)
        return group.id if group is not None else None
