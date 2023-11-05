from datetime import timedelta
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from ..schema.token_schema import Token
from ..schema.user_schema import UserRegister, UserInfo
from fastapi.security import OAuth2PasswordBearer
from ..controller.user_controller import UserController
from ..model.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

user_controller = UserController()

router = APIRouter(prefix="/user", tags=["用户管理"])
# 模拟一个令牌撤销列表，存储已失效的 Token
revoked_tokens = set()

@router.post("/register",response_model=Token, name="用户注册")
async def register(user_register: UserRegister) -> dict:
    """用户注册

    Args:
        user_register (UserRegister): 注册时外部传入的参数格式,包括用户名 密码 邮箱

    Returns:
        dict: 生成的 token 及其类型
    """
    access_token: str = UserController().register_user(user_register)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, name="用户登陆") 
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    # model.user
    user: User = user_controller.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_controller.create_access_token(timedelta(minutes=30)) # 设置 token 有效时间
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInfo, name="获取当前用户信息")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    if token in revoked_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token out date",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_controller.get_current_user(token)

@router.post('/logout', name="用户退出")
async def user_logout(token: str = Depends(oauth2_scheme)):
    user_controller.get_current_user(token)
    revoked_tokens.add(token)
    
    return "退出成功"
    
