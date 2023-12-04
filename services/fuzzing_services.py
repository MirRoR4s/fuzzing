from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, insert, delete, update, exc
from services.sql_model import FuzzTestCase, FuzzTestCaseGroup, RequestField, ByteField, BlockField
from schema.fuzz_test_case_schema import Block, Bytes, Byte
from exceptions.database_error import DatabaseError, DuplicateKeyError
import logging

LITTLE_ENDIAN = '<'



class FuzzingService:
    """
    模糊测试后端
    """
    
    def __init__(self, db: Session):
        self.db = db

    def read_case_group(self, user_id: int, group_name: str) -> FuzzTestCaseGroup | None:
        try:
            with self.db as session:
                stmt = select(FuzzTestCaseGroup).filter(
                    FuzzTestCaseGroup.name == group_name
                    and FuzzTestCaseGroup.user_id == user_id
                )
                return session.scalar(stmt)
        except Exception as e:
            session.rollback()
            print("检查模糊测试用例组名称是否重复时发生异常", e)
            return None

    def read_fuzz_test_case(self, group_id: int, fuzz_test_case_name: str) -> FuzzTestCase | None:
        try:
            with self.db as session:
                stmt1 = select(FuzzTestCase).filter(
                    FuzzTestCase.name == fuzz_test_case_name and FuzzTestCase.fuzz_test_case_group_id == group_id
                )
                fuzz_test_case = session.scalar(stmt1)
                return fuzz_test_case
        except Exception as e:
            session.rollback()
            print("检查模糊测试用例名称是否重复时发生异常", e)
            return True

    def create_case_group(self, user_id: int, name: str, desc: str | None = None):
        """
        create_case_group 创建模糊测试用例组

        :param user_id: 用户 id
        :param name: 组名称
        :param desc: 组描述，默认为 None
        :return: 创建成功返回 True
        """
        try:
            with self.db as session:
                    stmt = insert(FuzzTestCaseGroup).values(user_id=user_id, name=name, desc=desc)
                    session.execute(stmt)
                    session.commit()
        except exc.IntegrityError as e:
            logging.error(f"主键重复或唯一性异常 {e}")
            raise ValueError
        except Exception as e:
            raise DatabaseError

            
            
                
                
    def create_case(self, group_id: int, fuzz_test_case_name: str):
        with self.db as session:
            fuzz_test_case = FuzzTestCase(name=fuzz_test_case_name, fuzz_test_case_group_id=group_id)
            session.add(fuzz_test_case)
            session.commit()
            request = RequestField(name=fuzz_test_case_name, fuzz_test_case_id=fuzz_test_case.id)
            session.add(request)
            session.commit()


    def delete_fuzz_test_case_group(self, user_id: int, group_name: str) -> bool:
        """
        delete_fuzz_test_case_group 从数据库中删除具有指定 user id 和 group name 的模糊测试用例组

        :param user_id: _description_
        :param group_name: _description_
        :return: 删除成功返回 True，否则返回 False
        """
        with self.db as session:
            delete_stmt = delete(FuzzTestCaseGroup).filter(FuzzTestCaseGroup.user_id == user_id and FuzzTestCaseGroup.name == group_name)
            result = session.execute(delete_stmt)
            session.commit()
            # 保证仅有一条记录被删除，否则的话认为删除失败
            return True if result.rowcount == 1 else False

    def delete_fuzz_test_case(self, group_id: int, case_name: str) -> bool:
        """
        delete_fuzz_test_case 删除具有指定组 id 和用例名称的模糊测试用例

        :param user_id: _description_
        :param group_name: _description_
        :param fuzz_test_case_name: _description_
        :return: 删除成功返回 True，否则返回 False
        """
        with self.db as session:
        # 根据组 id 和用例名称删除指定用例
            delete_stmt = delete(FuzzTestCase).filter(FuzzTestCase.fuzz_test_case_group_id == group_id and FuzzTestCase.name == case_name)
            result_proxy = session.execute(delete_stmt)
            session.commit()
            return True if result_proxy == 1 else False

    def set_block(
        self, user_id: int, fuzzing_group_name: str, name: str, block_info: Block
    ) -> bool:
        try:
            with self.db as session:
                fuzzing_case_id = self.get_fuzzing_case_id(
                    user_id, fuzzing_group_name, name
                )
                request_id = self.get_request_id(fuzzing_case_id)

                if fuzzing_case_id is not None and request_id is not None:
                    default_value = block_info.default_value
                    stmt = insert(BlockField).values(
                        request_id=request_id, name=name, default_value=default_value
                    )
                    session.execute(stmt)
                    session.commit()
                    return True
        except Exception as e:
            print(e)
            return False

    def create_byte(
        self,
        request_id: int,
        block_id: int | None = None,
        name: str | None = None,
        default_value: int = 0,
        max_num: int | None = None,
        endian: str = LITTLE_ENDIAN,
        output_format: str = "binary",
        signed: bool = False,
        full_range: bool = False,
        fuzz_values: list | None = None,
        fuzzable: bool = True,

    ):
        """
        根据传入的参数将一个 byte 原语插入 byte_fields 表

        :param request_id: 包含 byte 原语的 request id
        :param block_id: 用户可能会将该原语包含在某个 block 中，在这种情况下需要将 block 包含到 request 中
        :param name: byte 原语的名称, defaults to None
        :param default_value: _description_, defaults to 0
        :param max_num: _description_, defaults to None
        :param endian: _description_, defaults to LITTLE_ENDIAN
        :param output_format: _description_, defaults to "binary"
        :param signed: _description_, defaults to False
        :param full_range: _description_, defaults to False
        :param fuzz_values: _description_, defaults to None
        :param fuzzable: _description_, defaults to True
        :return: 插入成功返回 True，否则返回 False
        """

        byte_field = ByteField(
            name=name,
            default_value=default_value,
            max_num=max_num,
            endian=endian,
            output_format=output_format,
            signed=signed,
            full_range=full_range,
            fuzz_values=fuzz_values,
            fuzzable=fuzzable,
        )

        if block_id is not None:
            byte_field.block_id = block_id
            
        else:
            byte_field.request_id = request_id
    
        self.db.add(byte_field)
        self.db.commit()

        return "设置 byte 字段成功"

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

        stmt = select(FuzzTestCaseGroup).where(
            FuzzTestCaseGroup.user_id == user_id
            and FuzzTestCaseGroup.name == group_name
        )

        group_id = self.db.scalar(stmt).id
        stmt1 = select(FuzzTestCase).where(
            FuzzTestCase.name == name and FuzzTestCase.test_case_group_id == group_id
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

    def read_block(self, request_id: int) -> BlockField | None:
        ans = self.db.scalar(
            select(BlockField).where(BlockField.request_id == request_id)
        )
        return ans
    
    def update_block_request_id(self, block_id: int, request_id: int) -> bool:
        with self.db as session:
            try:
                update_stmt = (
                    update(BlockField).
                    where(BlockField.id == block_id).
                    values(request_id=request_id)
                )
                session.execute(update_stmt)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(f'发生异常{e}')
                return False
                
                
