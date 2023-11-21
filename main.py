# main.py
from fastapi import FastAPI
import uvicorn
from controller import user_api, fuzz_api
from model.database import engine, Base

app = FastAPI()
app.include_router(user_api.router)
app.include_router(fuzz_api.router)


def main():
    """
    main 启动 fastapi 程序
    """
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == '__main__':  # 运行服务器
    main()
    # uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
