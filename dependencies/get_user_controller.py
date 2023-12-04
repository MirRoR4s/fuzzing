from services.database import get_db
from fastapi import Depends
from controller.user_controller import UserController


def get_user_controller(db = Depends(get_db)):
    return UserController(db)


