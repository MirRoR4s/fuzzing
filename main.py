# Author: 黄建涛
# Contact: mirror4s@birkenwald.cn
"""
漏洞挖掘系统启动文件。
"""
from fastapi import FastAPI
import uvicorn
from api import user_api, fuzz_api


app = FastAPI()
app.include_router(user_api.router)
app.include_router(fuzz_api.router)


def main():
    """
    启动 fastapi 程序
    """
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == '__main__':
    main()
