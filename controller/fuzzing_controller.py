"""
模糊测试控制器类。
"""
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from services.fuzzing_services import FuzzingService
from exceptions.database_error import DatabaseError, GroupNotExistError


class FuzzingController:
    """
    模糊测试后端
    """

    def __init__(self, db: Session):
        self.fuzzing_service = FuzzingService(db)

    def create_case_group(self, user_id, group_name, desc=None):
        """
        创建一个模糊测试用例组

        :param user_id: 用户 id，必须在数据库中存在。
        :param group_name: 用例组名称，必须在数据库中存在。
        :param desc: 对用例组的描述，默认为 None。
        :raises HTTPException: 创建一个已存在的用例组抛出 HTTP 403 异常。
        :raises HTTPException: 发生其它错误时抛出 HTTP 500 异常。
        """
        try:
            self.fuzzing_service.create_case_group(user_id, group_name, desc)
        except ValueError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用例组已存在") from e
        except DatabaseError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e

    def delete_case_group(self, user_id: int, group_name: str):
        """
        删除一个模糊测试用例组。
        
        注意：这会删除该组下所有的模糊测试用例！
        
        :param user_id: 用户id，要求在数据库中存在。
        :param group_name: 模糊测试用例组名称，要求在数据库中存在。
        :raises HTTPException: 当尝试删除一个不存在的用例组时抛出 HTTP 403 异常。
        :raises HTTPException: 当发生其它错误时抛出 HTTP 500 异常。
        """
        # 首先判断用例组是否存在并返回其id。
        group_id = self.get_group_id(user_id, group_name)
        if group_id is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用例组不存在")
        # 其次获取该用例组下所有的模糊测试用例并删除
        self.fuzzing_service.delete_cases(group_id)
        # 之后删除这些模糊测试用例下所有的原语。
        cases = self.fuzzing_service.get_cases(group_id)
        for case in cases:
            self.fuzzing_service.delete_primitives(case[0].id)
        # 最后删除当前用例组
        try:
            self.fuzzing_service.delete_case_group(group_id)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务器内部错误") from e

    def create_case(self, user_id: int, group_name: str, case_name: str):
        """
        创建一个模糊测试用例。

        :param user_id: 用户 id，必须在数据库中存在。
        :param group_name: 用例所属的组名称，必须在数据库中存在。
        :param case_name: 用例名称，必须在数据库中存在。
        :raises HTTPException: 当创建一个已存在的用例时抛出 HTTP 403 异常。
        :raises HTTPException: 当发生其它错误时抛出 HTTP 500 异常。
        :return "创建成功"
        """
        group_id = self.get_group_id(user_id, group_name)
        try:
            self.fuzzing_service.create_case(group_id, case_name)
        except ValueError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="添加失败，请检查用例名称是否重复！") from e
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e

    def delete_case(self, user_id, group_name, case_name=None):
        """
        删除一个模糊测试用例及其含有的所有原语。

        :param user_id: _description_
        :param group_name: _description_
        :param case_name: _description_
        :raises HTTPException: _description_
        :raises HTTPException: _description_
        """
        group_id = self.get_group_id(user_id, group_name)
        case = self.fuzzing_service.get_case(group_id, case_name)
        if case is None:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="删除失败，请检查用例是否存在！")
        case_id = case.id
        self.fuzzing_service.delete_primitives(case_id)
        try:
            self.fuzzing_service.delete_case(case_id)
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e
        return group_id

    def delete_primitive(self, u_id, g_name, c_name, primitive_name):
        """
        从名为 c_name 的模糊测试用例中删除一个名为 primitive_name 的原语。

        :param u_id: 用户 id，需存在于数据库中。
        :param g_name: 模糊测试用例组名称，需存在于数据库中。
        :param c_name: 模糊测试用例名称，需存在于数据库中。
        :param primitive_name: 原语名称，需存在于数据库中。
        :raises HTTPException 403: 尝试删除一个不存在的原语。
        :raises HTTPException 500: 其它异常。
        """
        case_id = self.get_case_id(u_id, g_name, c_name)
        primitive = self.fuzzing_service.get_primitive(case_id, primitive_name)
        if primitive is None:
            raise HTTPException(403, "删除失败，请检查原语是否存在！")
        try:
            self.fuzzing_service.delete_primitive(primitive.id)
        except Exception as e:
            logging.error(e)
            raise HTTPException(500, "服务端异常") from e

    def create_primitive(self, primitive_name, primitive: dict, u_id, g_name, c_name, b_name=None):
        """
        TODO
        """
        case_id = self.get_case_id(u_id, g_name, c_name)
        try:
            self.fuzzing_service.create_primitive(primitive_name, primitive, case_id, b_name)
        except ValueError as e:
            raise HTTPException(status_code=422, detail="原语已存在") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="服务端异常") from e
        return f"设置 {primitive_name} 成功"


    def get_group_id(self, user_id: int, group_name: str) -> int:
        """
        获取一个名为 group_name 的模糊测试用例组的 id。

        :param user_id: 用户 id，需在数据库中存在。
        :param group_name: 模糊测试用例组名称，需在数据库中存在。
        :raises HTTPException 403: 用例组不存在
        :raises HTTPException 500: 其它异常
        :return: 用例组 id。
        """
        try:
            group = self.fuzzing_service.get_group(user_id, group_name)
        except GroupNotExistError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用例组不存在"
                ) from e 
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常"
                ) from e
        return group.id

    def get_case_id(self, user_id, group_name, case_name) -> int:
        """
        获取一个名为 case_name 的模糊测试用例的 id。

        :param user_id: 用户 id，需在数据库中存在。
        :param group_name: 模糊测试用例组名称，需在数据库中存在。
        :param case_name: 模糊测试用例名称，需在数据库中存在。
        :raises HTTPException 403: 用例组或用例不存在 
        :raises HTTPException: 其它异常
        :return: 用例 id。
        """
        group_id = self.get_group_id(user_id, group_name)
        try:
            case = self.fuzzing_service.get_case(group_id, case_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail="服务端异常") from e
        if case is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用例不存在")
        return case.id
    
    # def get_cases(self, group_id):
    #     try:
    #         case = self.fuzzing_service.get_case(group_id)
    #     except Exception as e:
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e
    #     return case
    