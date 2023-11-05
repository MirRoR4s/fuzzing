from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError

from ..schema.token_schema import TokenData
from .db_controller import select_user, get_db, insert_user

from ..schema.user_schema import UserRegister
from ..model.user_model import User
from ..services.database import SessionLocal
from passlib.context import CryptContext


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserController:
    """ _summary_
    """
    
    def __init__(self, user: User | None = None) -> None:
        self.user = user
        self.db = SessionLocal()
        
    def verify_password(self, passwd) -> bool:
        return pwd_context.verify(passwd, self.user.hashed_password)
    
    def register_user(self, user_register: UserRegister) -> str:
        self.user = insert_user(self.db, user_register)
        # token 过期时间
        access_token_expires = timedelta(minutes=30)
        # 创建 token
        access_token = self.create_access_token(expires_delta=access_token_expires)
        return access_token
    
    def create_access_token(self, expires_delta: timedelta | None = None):
        data: dict = {"sub": self.user.username}
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt


    def get_current_user(self, token: str) -> dict:
        
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        
        self.user = select_user(self.db, username=token_data.username)
        if self.user is None:
            raise credentials_exception
        elif self.user.is_active is False:
            raise HTTPException(status_code=400, detail="Inactive user")
        return {"username": self.user.username, "email": self.user.email, "id": self.user.id, "role": self.user.role, "cases": self.user.cases}

    def authenticate_user(self, username: str, password: str) -> User:
        user = select_user(self.db, username)
        if not user:
            return False
        self.user = user
        if not self.verify_password(password):
            return False
        return self.user