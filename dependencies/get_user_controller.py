from services.database import get_db
from fastapi import Depends
from controller.user_controller import UserController
from controller.fuzzing_controller import FuzzingController

def get_user_controller(db = Depends(get_db)):
    return UserController(db)

def get_fuzzing_controller(db = Depends(get_db)):
    return FuzzingController(db)


    


