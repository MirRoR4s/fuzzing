"""
2023/12/8 代码格式规范化。
"""
import logging
from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status
from exceptions.database_error import DatabaseError, DuplicateKeyError, UserNotExistError
from services.user_service import UserService


class UserController:
    """
    用户控制器类，主要进行的操作在于接受用户服务类返回的结果，以及捕获相关的异常并返回给客户端。
    """
    def __init__(self, db: Session):
        self.user_service = UserService(db)

    def register(self, username: str, password: str, email: str):
        """
        register 注册一个用户名为 username，密码为 password，邮箱为 email 的新用户。

        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        """
        try:
            self.user_service.register(username, password, email)
        except DuplicateKeyError as e:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用户已存在") from e
        except DatabaseError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e

    def login(self, username, password) -> str:
        """
        用户登录。

        :param username: 用户名
        :param password: 密码
        :return: 身份令牌
        """
        try:
            user = self.user_service.get_user(username, password)
        except UserNotExistError as e:
            raise HTTPException(404, detail="用户不存在") from e
        except ValueError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用户名或密码错误") from e
        except DatabaseError as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="服务端异常") from e
        token = self.user_service.create_token(user.username)
        return token

    # def delete(username: str, token: str):
    #     pass

    def get_user_id(self, token: str) -> int:
        """
        获取用户id。

        :param token: 有效的身份令牌。
        :return: 用户id。
        """
        return self.get_user_info(token).get("id")

    def get_user_info(self, token: str) -> dict:
        """
        获取当前用户的信息。

        :param token: 身份令牌
        :return: 用户名、id、邮箱、角色。
        """
        try:
            user_info = self.user_service.get_user_info(token)
        except ValueError as e:
            logging.error(e)
            raise HTTPException(status_code=401, detail="token 无效") from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="服务端异常") from e
        return user_info