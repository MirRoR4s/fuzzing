"""
模糊测试后端
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete, exc
from services.sql_model import FuzzTestCase, FuzzTestCaseGroup, Block, Primitive
from exceptions.database_error import DatabaseError, GroupNotExistError

LITTLE_ENDIAN = '<'

class FuzzingService:
    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.db = db

    def get_group(self, u_id: int, g_name: str) -> FuzzTestCaseGroup:
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

    def get_case(self, gid: int, cname):
        try:
            with self.db as session:
                stmt = select(FuzzTestCase).filter(FuzzTestCase.name == cname and FuzzTestCase.group_id == gid)
                case = session.scalar(stmt)
        except Exception as e:
            logging.error("get_case 异常 %s", e)
            raise DatabaseError from e
        return case
    
    def get_cases(self, group_id):
        try:
            with self.db as session:
                stmt = select(FuzzTestCase).filter(FuzzTestCase.group_id == group_id)
                result = session.execute(stmt).fetchall()
                print(result)
        except Exception as e:
            logging.error("get_cases 异常 %s", e)
            raise DatabaseError from e
        return result

    def create_case_group(self, user_id, name, desc=None):
        try:
            with self.db as session:
                stmt = insert(FuzzTestCaseGroup).values(user_id=user_id, name=name, desc=desc)
                session.execute(stmt)
                session.commit()
        except exc.IntegrityError as e:
            logging.error("create_case_group 异常 %s", e)
            raise ValueError from e
        except Exception as e:
            raise DatabaseError from e

    def create_case(self, group_id: int, name: str):
        try:
            with self.db as session:
                fuzz_test_case = FuzzTestCase(name=name, group_id=group_id)
                session.add(fuzz_test_case)
                session.commit()
        except exc.IntegrityError as e:
            logging.error("create_case 主键重复或唯一性异常 %s", e)
            raise ValueError from e
        except Exception as e:
            logging.error("create_case 异常 %s", e)
            raise DatabaseError from e


    def delete_case_group(self, group_id):
        try:
            with self.db as session:
                delete_stmt = delete(FuzzTestCaseGroup).filter(FuzzTestCaseGroup.id == group_id)
                session.execute(delete_stmt)
                session.commit()
        except Exception as e:
            logging.error("发生异常 %s", e)
            raise e

    def delete_case(self, case_id):
        try:
            with self.db as session:
                stmt = delete(FuzzTestCase).filter(FuzzTestCase.id == case_id)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            logging.error("delete_case(%d) 异常 %r", case_id, e)
            raise DatabaseError from e
    
    def delete_cases(self, group_id: int):
        try:
            with self.db as session:
                stmt = delete(FuzzTestCase).filter(FuzzTestCase.group_id == group_id)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            logging.error("delete_cases(%d) 异常 %r", group_id, e)
            raise DatabaseError from e

    def delete_primitive(self, primitive_id):
        try:
            with self.db as session:
                stmt = delete(Primitive).filter(Primitive.id == primitive_id)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)
            logging.error('delete_primitive 发生异常 %s', e)
            raise DatabaseError from e
    
    def delete_primitives(self, case_id):
        try:
            with self.db as session:
                stmt = delete(Primitive).filter(Primitive.case_id == case_id)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            logging.error('delete_primitives 发生异常')
            raise DatabaseError from e

    def create_primitive(self, primitive_name: str, primitive: dict, case_id: int, b_name: str | None = None):
        """
        创建原语并初始化其各项字段。

        :param primitive_name: 原语名称。
        :param primitive: 包含着原语的各项字段的字典，key 是字段名称，value 是字段值。
        :param case_id: 该原语所属的模糊测试用例 id。
        :param b_name: 原语所属的 block 名称（如果有的话），默认为 None。
        :raises ValueError: 尝试创建一个已存在的原语。
        :raises DatabaseError: 其它异常。
        """
        try:
            with self.db as session:
                block_id = None
                # 如果原语是加入到组中某个 block 中的，那么就获取该 block 的 id，然后插入到原语表中去。
                if b_name is not None:
                    stmt = select(Block).where(Block.case_id == case_id and Block.name == b_name)
                    block_id = session.scalar(stmt).id
                # 插入原语信息。
                stmt = insert(Primitive).values(
                    type=primitive_name, case_id=case_id, block_id=block_id, **primitive
                )
                session.execute(stmt)
                session.commit()
        except exc.IntegrityError as e:
            logging.error("set_primitive 主键重复或违反唯一性约束 %s", e)
            raise ValueError from e
        except Exception as e:
            logging.error("set_primitive 异常 %s", e)
            raise DatabaseError from e

    def get_block_if_exists(self, request_id: int, block_name: str | None) -> Block | None:
        """
        如果 block name 存在，那么对应该名称的 block。

        :param request_id: 该 block 所属的 request id。
        :param block_name: 该 block 的名称。
        :return: Base.Block
        """
        try:
            with self.db as session:
                stmt = select(Block).where(Block.request_id == request_id and Block.name == block_name)
                return session.scalar(stmt)
        except Exception as e:
            logging.error('get_block_if_exists() 发生异常 %s', e)
            raise DatabaseError from e
        
    def get_primitive(self, case_id: int, primitive_name: str) -> Primitive:
        """
        从id为case_id的模糊测试用例中获取一个名为primitive_name的原语。

        :param case_id: 模糊测试用例的id。
        :param primitive_name: 原语的名称。
        """
        try:
            with self.db as session:
                stmt = select(Primitive).filter(
                    Primitive.case_id == case_id and Primitive.name == primitive_name
                )
                primitive = session.scalar(stmt)
                # session.commit()
        except Exception as e:
            logging.error('get_primitive %s', e)
            raise DatabaseError from e
        return primitive
        
    def get_primitives(self, case_id: int) -> tuple:
        """
        获取id为case_id的模糊测试用例下的所有原语。

        :param case_id: 模糊测试用例的id。
        :return: 该用例下的所有原语
        """
        pass
        
        