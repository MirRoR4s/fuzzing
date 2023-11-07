from sqlalchemy.orm.session import Session
from .sql_model import User
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:

    def __init__(self, db: Session) -> None:
        self.db = db
    
    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, password: str, email: str):
        new_user = User(username=username, password=password, email=email)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return self.create_access_token(new_user.username)
    
    def authenticate_user(self, username: str, password: str) -> User:
        user = self.get_user_by_username(username)
        
        if not user:
            return False
        if not self.verify_password(password, user.password):
            return False
        return True
    
    def verify_password(plain_password, hashed_password):
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
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = self.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        elif user.disabled is False:
            raise HTTPException(status_code=400, detail="Inactive user")
        return {"username": user.username, "email": user.email, "id": self.user.id, "role": user.role,}

