from fastapi import FastAPI
from .routers import users_api
from .services.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users_api.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


if __name__ == '__main__':        # 运行服务器
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True) 
    # uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True) 
