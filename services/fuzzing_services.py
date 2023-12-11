import logging
import boofuzz
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete, exc
from services.sql_model import FuzzTestCase, FuzzTestCaseGroup, Request, Block, Static, Byte
from exceptions.database_error import DatabaseError, GroupNotExistError, CaseNotExistError, UnsupportedFieldError

LITTLE_ENDIAN = '<'



class FuzzingService:
    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.db = db
        self.field_handlers = {
            "static": self.set_static,
            "block": self.set_block,
        }

    def select_case_group(self, u_id: int, g_name: str) -> FuzzTestCaseGroup:
        """
        查询一个模糊测试用例组并返回。

        :param user_id: 用户id，必须在数据库中存在。
        :param group_name: 组名称，必须在数据库中存在。
        :raises DatabaseError: 发生了未知错误时抛出该异常。
        :raises GroupNotExistError: 当数据库中不存在查询的组时抛出该异常。
        :return: 查询到的用例组对象。
        """
        try:
            with self.db as session:
                stmt = select(FuzzTestCaseGroup).filter(FuzzTestCaseGroup.name == g_name and FuzzTestCaseGroup.user_id == u_id)
                group = session.scalar(stmt)
        except Exception as e:
            logging.error("异常 %s", e)
            raise DatabaseError from e  
        if group is None:
            logging.error("读取用例组为空 user_id: %s group_name: %s", u_id, g_name)
            raise GroupNotExistError
        return group

    def get_case(self, gid: int, cname: str) -> FuzzTestCase:
        """获取一个用例组下的特定用例。

        :param group_id: 有效的组id
        :param case_name: 用例名称
        :raises DatabaseError: _description_
        :raises ValueError: _description_
        :return: _description_
        """
        try:
            with self.db as session:
                stmt1 = select(FuzzTestCase).filter(FuzzTestCase.name == cname and FuzzTestCase.group_id == gid)
                fuzz_test_case = session.scalar(stmt1)
        except Exception as e:
            logging.error("异常 %s", e)
            raise DatabaseError from e
        if fuzz_test_case is None:
            logging.error("读取模糊测试用例为空 %s %s", gid, cname)
            raise CaseNotExistError
        return fuzz_test_case
    
    def get_request(self, case_id: int) -> Request:
        """
        查询一个模糊测试用例对应的Request对象
        :param case_id: 一个有效的模糊测试用例id
        :raises DatabaseError: _description_
        :return: 对应的Request对象。
        """
        try:
            with self.db as session:
                stmt = select(Request).filter(Request.case_id == case_id)
                request = session.scalar(stmt)
        except Exception as e:
            logging.error("异常 %s", e)
            raise DatabaseError from e
        else:
            if request is None:  # 在正常的情况下，如果case存在，那么request就存在。如果发生了case存在，但查不到对应request的情况，可认为服务端出现了问题。
                logging.error("请检查服务器的数据库配置，可能发生了一些问题。")
                raise DatabaseError
            return request

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
            logging.error("主键重复或唯一性异常 %s", e)
            raise ValueError from e
        except Exception as e:
            raise DatabaseError from e

    def create_case(self, group_id: int, name: str):
        """
        向数据库中插入一个模糊测试用例，同时插入一个属于该用例的 Request 对象。

        :param group_id: 要插入的用例所属的用例组
        :param name: 用例的名称 
        :raises ValueError: 当发生了主键重复或违反了唯一性约束时抛出
        :raises DatabaseError: 当发生了其他错误时抛出
        """
        try:
            with self.db as session:
                fuzz_test_case = FuzzTestCase(name=name, group_id=group_id)
                session.add(fuzz_test_case)
                session.commit()
                request = Request(name=name, case_id=fuzz_test_case.id)
                session.add(request)
                session.commit()
        except exc.IntegrityError as e:
            logging.error("主键重复或唯一性异常 %s", e)
            raise ValueError
        except Exception as e:
            logging.error("异常 %s", e)
            raise DatabaseError


    def delete_fuzz_test_case_group(self, u_id: int, g_name: str) -> bool:
        """
        从数据库中删除模糊测试用例组。
        
        :param user_id: 用户id，要求在数据库中存在。
        :param group_name: 模糊测试用例组名称，要求在数据库中存在。
        :return: 删除成功返回 True，否则返回 False
        """
        try:
            with self.db as session:
                delete_stmt = delete(FuzzTestCaseGroup).filter(FuzzTestCaseGroup.user_id == u_id and FuzzTestCaseGroup.name == g_name)
                result = session.execute(delete_stmt)
                session.commit()
        except Exception as e:
            logging.error("发生异常 {e}")
            raise e
        else:
            # 保证仅有一条记录被删除，否则的话认为删除失败
            if result.rowcount != 1:
                raise GroupNotExistError
            
        

    def delete_fuzz_test_case(self, group_id: int, case_name: str) -> bool:
        """删除一个模糊测试用例

        :param group_id: _description_
        :param case_name: _description_
        :raises DatabaseError: _description_
        :raises ValueError: _description_
        :return: _description_
        """
        try:
            with self.db as session:
            # 根据组 id 和用例名称删除指定用例
                delete_stmt = delete(FuzzTestCase).filter(FuzzTestCase.group_id == group_id and FuzzTestCase.name == case_name)
                result_proxy = session.execute(delete_stmt)
                session.commit()
        except Exception as e:
            logging.error(f"异常 {e}")
            raise DatabaseError
        else:
            if result_proxy.rowcount != 1:
                logging.error(f"删除操作异常")
                raise ValueError

    def set_block(self, request_id: int, name: str, default_value: int = 0):
        """
        设置 block 类型的各项属性，包括其 request 的 id、名称、默认值，然后插入数据库中。

        :param request_id: 包含当前 block 的 request 类型的 id，必须是一个非负数。
        :param name: 当前 block 类型的名称。
        :param default_value: 当前 block 的默认值，必须是一个非负数，默认为零。
        :return: None
        """
        try:
            with self.db as session:
                stmt = insert(Block).values(request_id=request_id, name=name, default_value=default_value)
                session.execute(stmt)
                session.commit()
        except exc.IntegrityError as e:
            logging.error(f"{e}")
            raise ValueError
        except Exception as e:
            logging.error(f"{e}")
            raise DatabaseError

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



    def set_static(self, request_id: int, name: str, default_value: int = 0, block_name: str | None = None):
        """插入一个 static 原语。

        :param case_id: static 原语所属用例的 id。
        :param name: static 原语的名称
        :param default_value: static 原语的默认值
        :param block_name: 该原语所属的 block 的名称（可选），默认为 None
        """
        try:
            with self.db as session:
                if block_name is None:
                    stmt = insert(Static).values(request_id=request_id, name=name, default_value=default_value)
                    session.execute(stmt)
                    session.commit()
                else:
                    # 获取刚刚插入的 block id
                    stmt = select(Block).where(Block.request_id == request_id and Block.name == block_name)
                    block_id = session.scalar(stmt).id
                    stmt1 = insert(Static).values(block_id=block_id, name=name, default_value=default_value)
                    session.execute(stmt1)
                    session.commit()
        except exc.IntegrityError as e:
            logging.error("主键重复或违反唯一性约束 %s", e)
            raise ValueError from e
        except Exception as e:
            logging.error("异常 %s", e)
            raise DatabaseError from e
        
    def set_primitive(self, primitive_name: str, primitive: dict, request_id: int, block_name: str | None = None):
        """
        依据不同字段类的名称，调用不同的数据库函数。
        当字段名称为 byte，调用 set byte 插入 byte 字段信息。
        当字段名称为 bytes，调用 set bytes 插入 bytes 字段信息。

        :param field: 字段类名
        :param field: 所有字段类的共同父类，至少包含名称（不是字段类的名称，是该字段的实例变量的名称）、默认值两项。
        """
        handler = self.field_handlers.get(primitive_name)
        if handler:
            try:
                handler(primitive, request_id, block_name)
            except exc.IntegrityError as e:
                logging.error("主键重复或违反唯一性约束 %s", e)
                raise ValueError from e
            except Exception as e:
                logging.error("异常 %s", e)
                raise DatabaseError from e
        else:
            raise UnsupportedFieldError("不支持的字段功能")
                
    def set_byte(self, byte: dict, request_id: int, block_name: str| None = None):
        """
        将一个 byte 原语的信息插入到数据库中

        :param byte: byte 原语信息字典，包括如下字段：
        
            1. name: str 原语的名称
            2. default value: int 原语的默认值，默认为零。
            3. max num: int 原语可变异的最大值 
            4. endian: str 原语的端序，默认是小端，用 '<' 表示。
            5. output format: str 原语的输出格式，默认是 'binary'
            6. signed: bool 
            7. full range: bool 
            8. fuzz values: list[int]
            9. fuzzable: bool 是否变异当前原语，默认为 True。
        
        关于各字段的具体含义参见：https://boofuzz.readthedocs.io/en/stable/user/protocol-definition.html#byte
        
        :param request_id: 当前原语所属的 request 的名称，必须是一个非负数。
        :param block_name: 当前原语所属的 block 的名称，默认为 None
        """
        with self.db as session:
            name=byte.get('name'),
            default_value=byte.get('default_value'),
            max_num=byte.get("max_num"),
            endian=byte.get("endian"),
            output_format=byte.get("output_format"),
            signed=byte.get("signed"),
            full_range=byte.get("full_range"),
            fuzz_values=byte.get("fuzz_values"),
            fuzzable=byte.get("fuzzable")
            
            block_id = None
            if block_name is not None:
                # 获取刚刚插入的 block id
                stmt = select(Block).where(Block.request_id == request_id and Block.name == block_name)
                block_id = session.scalar(stmt).id
                
            stmt = insert(Byte).values(
                request_id=request_id,
                block_id=block_id,
                name=name,
                default_value=default_value,
                max_num=max_num,
                endian=endian,
                output_format=output_format,
                signed=signed,
                full_range=full_range,
                fuzz_values=fuzz_values,
                fuzzable=fuzzable
                )
            session.execute(stmt)
            session.commit()
    
    # def read_block(self, request_id: int) -> BlockField | None:
    #     ans = self.db.scalar(
    #         select(BlockField).where(BlockField.request_id == request_id)
    #     )
    #     return ans
    
    # def update_block_request_id(self, block_id: int, request_id: int) -> bool:
    #     with self.db as session:
    #         try:
    #             update_stmt = (
    #                 update(BlockField).
    #                 where(BlockField.id == block_id).
    #                 values(request_id=request_id)
    #             )
    #             session.execute(update_stmt)
    #             session.commit()
    #             return True
    #         except Exception as e:
    #             session.rollback()
    #             print(f'发生异常{e}')
    #             return False
                
                
    # def set_bytes(
    #     self,
    #     user_id: int,
    #     group_name: str,
    #     name: str,
    #     bytes_info: Bytes,
    #     block_name: str | None = None,
    # ):
    #     """
    #     set_bytes_field 设置 bytes 原语各项属性，并记录在数据库中

    #     :param user_id: 用户 id
    #     :type user_id: int
    #     :param group_name: 模糊测试用例组名称
    #     :type group_name: str
    #     :param name: 模糊测试用例名称
    #     :type name: str
    #     :param bytes_info: 各项属性信息
    #     :type bytes_info: Bytes
    #     :param block_name: 分组名称, 默认为 None
    #     :type block_name: str | None, optional
    #     """

    #     fuzzing_case_id = self.get_case(user_id, group_name, name)
    #     request_id = self.get_request_id(fuzzing_case_id)

    #     if fuzzing_case_id is not None and request_id is not None:
    #         bytes_field = BytesField(
    #             request_id=request_id,
    #             name=bytes_info.name,
    #             default_value=bytes_info.default_value,
    #             size=bytes_info.default_value,
    #             fuzzable=bytes_info.fuzzable,
    #         )

    #         if block_name is not None:
    #             bytes_field.block_id = self.get_block_id(request_id)

    #         self.db.add(bytes_field)
    #         self.db.commit()

    #         return "设置 bytes 字段成功!"
    #     return "对不起，您选择的模糊测试用例或 request 字段不存在。"