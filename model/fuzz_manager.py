"""



"""


from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import select


from .sql_model import *

from .database import engine


from .schema.fuzzing_case_schema import *


class FuzzManager:

    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.db = db

    def create_fuzzing_group(self, user_id: int, name: str, desc: str | None = None):
        """
        create_test_group 创建测试用例组

        :param name: 组名
        :type name: str
        :param desc: 组描述, defaults to None
        :type desc: str | None, optional
        """

        with Session(engine) as session:
            test_case_group = TestCaseGroup(user_id=user_id, name=name, desc=desc)

            session.add(test_case_group)

            session.commit()

        return "创建成功"

    def create_fuzzing_case(
        self,
        user_id: int,
        group_name: str,
        case_name: str,
        case_attr: str | None = None,
    ):
        """



        create_fuzzing_case 创建模糊测试用例

        :param user_id: _description_

        :type user_id: int
        :param group_name: _description_

        :type group_name: str
        :param case_name: _description_

        :type case_name: str



        """

        stmt = select(TestCaseGroup).where(
            TestCaseGroup.user_id == user_id and TestCaseGroup.name == group_name
        )

        test_case_group = self.db.scalar(stmt)

        group_id = test_case_group.id

        with self.db as session:
            fuzzing_case = FuzzyTestCase(
                name=case_name,
                test_case_group_id=group_id,
            )

            session.add(fuzzing_case)

            session.commit()

            request = RequestField(name=case_name, fuzzing_case_id=fuzzing_case.id)

            session.add(request)

            session.commit()

        return f"已成功创建模糊测试用例 {case_name}！"

    def set_block(
        self, user_id: int, fuzzing_group_name: str, name: str, block_info: Block
    ):
        """
        set_block _summary_

        :param user_id: _description_
        :type user_id: int
        :param fuzzing_group_name: _description_
        :type fuzzing_group_name: str
        :param name: _description_
        :type name: str
        :param block_info: _description_
        :type block_info: Block
        :return: _description_
        :rtype: _type_
        """
        fuzzing_case_id = self.get_fuzzing_case_id(user_id, fuzzing_group_name, name)

        request_id = self.get_request_id(fuzzing_case_id)

        if fuzzing_case_id is not None and request_id is not None:
            block_field = BlockField(
                request_id=request_id,
                name=name,
                default_value=block_info.default_value,
            )

            ans = self.execute(block_field)
            return "Success!" if ans else "Failed!"

        return "Failed!"

    def set_byte(
        self,
        user_id: int,
        group_name: str,
        name: str,
        byte_info: Byte,
        block_name: str | None = None,
    ):
        """
        set_byte_field 设置 byte 原语
        
        :param user_id: _description_
        :type user_id: int
        :param group_name: _description_
        :type group_name: str
        :param name: _description_
        :type name: str
        :param byte_info: _description_
        :type byte_info: Byte
        :param block_name: _description_, defaults to None
        :type block_name: str | None, optional
        :return: _description_
        :rtype: _type_
        """

        fuzzing_case_id = self.get_fuzzing_case_id(user_id, group_name, name)

        request_id = self.get_request_id(fuzzing_case_id)

        byte_field = ByteField(
            request_id=request_id,
            name=byte_info.name,
            default_value=byte_info.default_value,
            max_num=byte_info.max_num,
            endian=byte_info.endian,
            output_format=byte_info.output_format,
            signed=byte_info.signed,
            full_range=byte_info.full_range,
            fuzz_values=byte_info.fuzz_values,
            fuzzable=byte_info.fuzzable,
        )

        if block_name is not None:
            byte_field.block_id = self.get_block_id(request_id)

        self.db.add(byte_field)

        self.db.commit()

        return "设置byte字段成功"

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

        fuzzing_case_id = self.get_fuzzing_case_id(user_id, group_name, name)

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
                bytes_field.block_id = self.get_block_id(request_id)

            self.db.add(bytes_field)

            self.db.commit()

            return "设置 bytes 字段成功!"

        return "对不起，您选择的模糊测试用例或 request 字段不存在。"
    
    def set_static():
        pass
    
    def set_simple():
        pass
    
    def set_delim():
        pass
    
    def set_group():
        pass
    
    def set_random_data():
        pass
    
    def set_string():
        pass
    
    def set_from_file():
        pass
    
    def set_mirror():
        pass
    
    def set_bit_field():
        pass
    
    def set_word():
        pass
    
    def set_dword():
        pass
    
    def set_qword():
        pass
    
        

    def get_fuzzing_case_id(self, user_id, group_name, name):
        """

        get_fuzzing_case_id _summary_

        :param user_id: _description_

        :type user_id: _type_
        :param group_name: _description_

        :type group_name: _type_
        :param name: _description_

        :type name: _type_
        :return: _description_

        :rtype: _type_



        """

        stmt = select(TestCaseGroup).where(
            TestCaseGroup.user_id == user_id and TestCaseGroup.name == group_name
        )

        group_id = self.db.scalar(stmt).id

        stmt1 = select(FuzzyTestCase).where(
            FuzzyTestCase.name == name and FuzzyTestCase.test_case_group_id == group_id
        )

        ans = self.db.scalar(stmt1)

        return ans.id if ans is not None else None

    def get_request_id(self, fuzzing_case_id: int) -> int:
        """



        get_request_id 查询数据库，获取 request id。

        :param fuzzing_case_id: _description

        :type fuzzing_case_id: int
        :return: _description_

        :rtype: int



        """

        ans = self.db.scalar(
            select(RequestField).where(RequestField.fuzzing_case_id == fuzzing_case_id)
        )

        return ans.id if ans is not None else None

    def get_block_id(self, request_id: int) -> int:
        """
        get_block_id 查询数据库，获取 block id。
        
        :param request_id: 该 block 的 request id
        :type request_id: int
        :return: _description_
        :rtype: int
        """

        ans = self.db.scalar(
            select(BlockField).where(BlockField.request_id == request_id)
        )

        return ans.id if ans is not None else None

    def execute(self, base: Base) -> bool:
        """
        execute 执行 sql 语句

        :param base: _description_
        :type base: Base
        :return: 执行成功返回真，否则返回假。
        :rtype: bool
        """
        try:
            self.db.add(base)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"发生错误：{e}")
            return False
        finally:
            self.db.close()
