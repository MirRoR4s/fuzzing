from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from schema.user_schema import UserRegister, UserInfo
from schema.user_response_schema import UserRegisterResponse
from services.user_service import UserService
from jose import jwt, JWTError
from fastapi import HTTPException, status
import logging
from exceptions.database_error import DatabaseError, DuplicateKeyError


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


class UserController:

    def __init__(self, db: Session):
        self.user_service = UserService(db)

    def register(self, username: str, password: str, email: str) -> str:
        """
        register 注册一个用户名为 username，密码为 password，邮箱为 email 的新用户

        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        """
        try:
            self.user_service.register(username, password, email)
        except DuplicateKeyError:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="用户已存在")
        except DatabaseError:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发生未知异常，服务不可用")
        else:
            return "注册成功"

    def login(self, username: str, password: str) -> str:
        """
        login 根据用户名和密码完成登录

        :param username: 用户名
        :param password: 密码
        :return: 身份令牌
        """
        try:
            user = self.user_service.read_user(username, password)
        except ValueError:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="用户名或密码错误")
        except DatabaseError:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发生未知异常，服务不可用")
        else:
            token = self.user_service.set_token(user.username)
            return token
        
    def delete(username: str, token: str):
        pass

    def get_user_id(self, token: str) -> int:
        user_info = self.get_user_info(token)
        print(user_info)
        return self.get_user_info(token).get("id")

    def get_user_info(self, token: str) -> dict:
        try:
            user_info = self.user_service.get_user_info(token)
            print(user_info)
        except ValueError:
            logging.error()
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="token 无效")
        except Exception as e:
            logging.error(f"未知异常 {e}")
        else:
            return user_info