from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from dotenv import load_dotenv
load_dotenv() 
logger.info("CEO：.env 文件已加载。")
from app.xhs_utils.database import connect_to_mongo, close_mongo_connection 

from app.routers import user_router # (你刚创建的 user_router.py)
from app.routers import note_router # (你“还”需要创建 note_router.py)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时
    logger.info("CEO：应用启动中...")
    await connect_to_mongo()
    yield
    # 应用关闭时
    logger.info("CEO：应用关闭中...")
    await close_mongo_connection()

app = FastAPI(
    title="小红书爬虫 API (重构版)",
    description="使用分层架构 (Routers, Services, Repos) 重构",
    version="2.0.0",
    lifespan=lifespan # 批判：把“开关”交给 CEO
)

app.include_router(
    user_router.router,  
    prefix="/api/users", 
    tags=["用户 (Users)"] 
)

app.include_router(
    note_router.router,
    prefix="/api/notes",
    tags=["笔记 (Notes)"]
)
