from sqlalchemy.orm.session import Session
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from services.sql_model import User
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import re
from exceptions.database_error import DatabaseError, DuplicateKeyError, UserNotExistError
import logging


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


class UserService:

    def __init__(self, db: Session) -> None:
        self.db = db

    def user_login(self, username: str, password: str) -> str:
        """
        read_user 读取用户名为 username 且密码为 password 的用户

        :param username: 用户名
        :param password: 密码
        :return: 身份令牌
        """
        try:
            with self.db as session:
                hashed_password = pwd_context.hash(password)
                print(hashed_password)
                stmt = select(User).where(User.username == username).where(User.password == hashed_password)
                user = session.scalar(stmt)
                print(user)
        except Exception as e:
            logging.error(f"发生异常 {e}")
            raise DatabaseError
        else:
            if user is None:
                logging.error(f"用户名或密码错误 username: {username} password: {password}")
                raise ValueError
            return UserService.set_token(user.username)
            
    def _is_register(self, username: str) -> bool:
        with self.db as session:
            return session.scalar(select(User).filter(User.username == username)) is not None

    @staticmethod
    def _get_password_hash(password: str):
        return pwd_context.hash(password)

    def create_user(self, username: str, passwd: str, email: str):
        """
        create_user 向 user 表的 username、

        :param username: 用户名
        :param passwd: 密码
        :param email: 邮箱
        :raises IntegrityError: 当用户已存在时，抛出该异常
        :raises DataBaseError: 对于其他可能发生的错误，抛出该异常
        """
        passwd = pwd_context.hash(passwd)  # 以哈希形式存储用户的密码，而非明文
        try:
            with self.db as session:
                # 向 users 表插入一个新用户
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
            logging.error(f"{e}")
            raise DuplicateKeyError
        except Exception as e:
            logging.error(f"{e}")
            raise DatabaseError

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def set_token(username, expires_delta: timedelta | None = timedelta(minutes=30)) -> str:
        data = {"sub": username}
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    

