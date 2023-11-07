# main.py
from fastapi import FastAPI
import uvicorn
from controller import user_api
from model.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_api.router)

if __name__ == '__main__':        # 运行服务器
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True) 
    # uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True) 
