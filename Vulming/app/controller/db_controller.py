from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from ..model import user_model
from ..schema.user_schema import UserLogin, UserRegister
import random

from ..services.database import SessionLocal



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def login_user(db: Session, user_login: UserLogin) -> bool:
    
    db_user = db.query(user_model.User).filter(user_model.User.username == user_login.username).first()
    
    if db_user is None:
        return False
    else:
        pwd = db_user.hashed_password
        hash_password = bcrypt.hash(user_login.password)
        
        return True if pwd == hash_password else False
    
def insert_user(db: Session, user_register: UserRegister):
    # 对用户明文密码进行 hash
    hashed_password = bcrypt.hash(user_register.password)
    
    db_user = user_model.User(
        id=random.randint(0,9999),
        username=user_register.username, 
        email=user_register.email, 
        hashed_password=hashed_password,
        is_active=True,
        role="normal"
)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def select_user(db: Session, username: str):
    return db.query(user_model.User).filter(user_model.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(user_model.User).filter(user_model.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user_model.User).offset(skip).limit(limit).all()

