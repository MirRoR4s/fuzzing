from sqlalchemy.orm import Session
from .sql_model import User
from .database import SessionLocal

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, email: str):
    new_user = User(username=username, password=password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user