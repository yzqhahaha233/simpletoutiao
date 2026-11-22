import os

from utils.exception_handlers import register_exception_handlers

# PyCharm 保存文件时会先写临时文件再替换，watchfiles 的事件监听会漏，
# 这里改用轮询模式，保证热重载稳定生效。
os.environ["WATCHFILES_FORCE_POLLING"] = "1"

from fastapi import FastAPI
from routers import news, users,favorite,history
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # 允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,  # 允许携带cookie
    allow_methods=["*"],     # 允许的请求方法
    allow_headers=["*"],     # 允许的请求头
)

@app.get('/')
async def root():
    return {'hello': 'world'}


app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)
