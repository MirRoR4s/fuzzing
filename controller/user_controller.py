from sqlalchemy.orm.session import Session
from .sql_model import User
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import re

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


class UserManager:

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_name(self, username: str):
        user = self.db.query(User).filter(User.username == username).first()
        return user

    @staticmethod
    def get_password_hash(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def is_valid(email) -> bool:
        if re.fullmatch(regex, email):
            print("有效的email地址")
            return True
        return False

    def create_user(self, username: str, password: str, email: str):
        """
        根据用户名 username 、密码 password 、邮箱 email 完成注册

        :param username:    长度位于 4 到 16 之间，仅由大小写字母_-和数字组成的字符串
        :param password:    同 username
        :param email:   由域内部分、@符号、大小写不敏感的域名组成的字符串
        :return:

        样例：
            create_user("test", "test", "790356373@qq.com"),
            创建一个用户名和密码都为 test，邮箱为 790356373@qq.com
        """
        # if username is None or password is None or email is None:
        #     raise HTTPException(
        #         status_code=422,
        #         detail="参数缺失！",
        #         headers={"WWW-Authenticate": "Bearer"}
        #     )
        if not re.match('^[a-zA-Z0-9_-]{4,16}$', username) or not re.match('^[a-zA-Z0-9_-]{4,16}$', password):
            raise HTTPException(
                status_code=422,
                detail="非法用户名或密码，只能包含大小写字母、数字、_、- 等字符且长度至少为 4！",
                headers={"WWW-Authenticate": "Bearer"}
            )

        if not UserManager.is_valid(email):
            raise HTTPException(status_code=422, detail="邮箱格式不正确！", headers={"WWW-Authenticate": "Bearer"})

        if self.get_user_by_name(username):
            raise HTTPException(
                status_code=422,
                detail="用户已存在",
                headers={"WWW-Authenticate": "Bearer"}
            )
        password = UserManager.get_password_hash(password)
        new_user = User(username=username, password=password, email=email, role='normal', disabled=False)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return {"message": "注册成功"}


    def authenticate_user(self, username: str, password: str):
        user = self.get_user_by_name(username)

        if user is None or not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = self.create_access_token(user.username)
        content = {"message": "登录成功", "access_token": access_token, "token_type": "bearer"}
        response = JSONResponse(content=content)
        return response

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(username, expires_delta: timedelta | None = timedelta(minutes=30)):
        data: dict = {"sub": username}
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user_info(self, token: str) -> dict:
        """
        :return: 返回用户名、邮箱、id、角色
        :rtype: dict
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            username: str = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        else:
            user = self.get_user_by_name(username)
            if user is None:
                raise credentials_exception
            elif user.disabled is True:
                raise HTTPException(status_code=401, detail="当前用户未激活")
            return {"username": user.username, "email": user.email, "id": user.id, "role": user.role, }
