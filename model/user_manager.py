from sqlalchemy.orm.session import Session
from .sql_model import User
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
import re

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:

    def __init__(self, db: Session) -> None:
        self.db = db
    
    def get_user_by_name(self, username: str):
        user = self.db.query(User).filter(User.username == username).first()
        return user
    
    def get_password_hash(self, password: str):
        return pwd_context.hash(password)

    def create_user(self, username: str, password: str, email: str):
        # 用户名只能由大小写字母和数字组成
        # 密码只能由大小写字母和数字以及
        if not re.match('^[a-zA-Z0-9_-]{4,16}$', username):
            raise HTTPException(
                status_code=400,
                detail="用户名不合法，只能包含大小写字母、数字、_-等字符且长度至少为4！",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        existing_user = self.get_user_by_name(username)
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="用户已存在",
                headers={"WWW-Authenticate": "Bearer"}
        )
        password = self.get_password_hash(password)
        new_user = User(id=0, username=username, password=password, email=email, role='normal', disabled=False)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return "注册成功!"
    
    def authenticate_user(self, username: str, password: str) -> str:
        user = self.get_user_by_name(username)
        
        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return self.create_access_token(user.username)
    
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, username, expires_delta: timedelta | None = timedelta(minutes=30)):
        data: dict = {"sub": username}
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user_info(self, token: str) -> dict:
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            print(payload)
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = self.get_user_by_name(username)
        if user is None:
            raise credentials_exception
        elif user.disabled is True:
            raise HTTPException(status_code=400, detail="Inactive user")
        return {"username": user.username, "email": user.email, "id": user.id, "role": user.role,}

