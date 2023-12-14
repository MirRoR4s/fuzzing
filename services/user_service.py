import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm.session import Session
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError
from passlib.context import CryptContext
from services.sql_model import User
from exceptions.database_error import DatabaseError, DuplicateKeyError, UserNotExistError



# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """
    用户服务类，负责执行具体的注册、登录逻辑。
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user(self, username, password=None) -> User:
        """
        获取名称为 username，密码为 password 的指定用户。

        :param username: 用户名称，必须在数据库中存在
        :param password: 用户密码，默认情况下为空，表示不进行密码验证。若不为空，则必须在数据库中存在。
        :raises DatabaseError: 其它异常。
        :raises UserNotExistError: 用户不存在。
        :raises ValueError: 用户密码不正确。
        :return: 获取到的用户。
        """
        try:
            with self.db as session:
                stmt = select(User).where(User.username == username)
                user = session.scalar(stmt)
        except Exception as e:
            logging.error('select_user 发生异常 %s', e)
            raise DatabaseError from e
        if user is None:
            raise UserNotExistError
        if password is not None:
            if UserService.verify_password(password, user.password) is False:
                logging.error("用户名或密码错误 username: %s password: %s", username, password)
                raise ValueError
        return user

    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
        """
        - 此段代码来自 fastapi 官方文档，用于验证明文密码的哈希是否和指定哈希相等。

        :param plain_password: 明文密码。
        :param hashed_password: 目标哈希值。
        :return: 当明文密码经过哈希后的值和目标哈希值相等时返回 True，否则返回 False。
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        """
        对明文密码进行哈希。

        :param password: 明文密码。
        :return: 明文密码的哈希值。
        """
        return pwd_context.hash(password)

    def register(self, username: str, passwd: str, email: str):
        """
        用户注册。

        :param username: 用户名
        :param passwd: 密码
        :param email: 邮箱
        :raises IntegrityError: 当用户已存在时，抛出该异常
        :raises DataBaseError: 对于其他可能发生的错误，抛出该异常
        """
        passwd = pwd_context.hash(passwd)  # 以哈希形式存储用户的密码，而非明文
        try:
            with self.db as session:
                stmt = insert(User).values(
                    username=username,
                    password=passwd,
                    email=email,
                    role='normal',  # 通过该函数注册的用户默认为 normal 级别
                    disabled=False
                )
                session.execute(stmt)
                session.commit()
        except IntegrityError as e:
            logging.error("%s", e)
            raise DuplicateKeyError from e
        except Exception as e:
            logging.error("%s", e)
            raise DatabaseError from e

    @staticmethod
    def create_token(username, expires_delta: timedelta | None = timedelta(minutes=30)) -> str:
        """
        创建 token 身份令牌。

        :param username: 用户名称
        :param expires_delta: token 的有效时间，默认是 30分钟。
        :return: token 身份令牌。
        """
        data = {"sub": username}

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        data.update({"exp": expire})
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_user_info(self, token: str) -> dict:
        """
        获取当前用户信息。

        :param token: 有效的身份令牌。
        :raises ValueError: jwt 无效或是未查询到对应的用户。
        :return: 用户名称、用户id、用户邮箱、用户等级。
        """
        try:
            username: str = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        except JWTError as e:
            logging.error('JWT 解码失败 %s', e)
            raise ValueError from e
        user = self.get_user(username)
        return {"username": user.username, "id": user.id, "email": user.email, "role": user.role}
