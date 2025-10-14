from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from .database import engine, Base
from .api import users, categories, items, chats, transactions, reviews, favorites

# 创建数据库
Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).parent.parent

# 初始化FastAPI应用
app = FastAPI(
    title="校园闲置物品共享与置换平台",
    description="一个基于FastAPI、Vue3和MySQL的校园闲置物品共享与置换平台API",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8173"],  # Vue前端默认地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 注册路由
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类"])
app.include_router(items.router, prefix="/api/items", tags=["物品"])
app.include_router(chats.router, prefix="/api/chats", tags=["聊天"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["交易"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["评价"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["收藏"])

# 根路径
@app.get("/")
def read_root():
    return {"message": "欢迎使用校园闲置物品共享与置换平台API"}