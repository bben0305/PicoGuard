"""
PicoGuard Backend Server
智能植栽監控系統 - FastAPI 後端入口
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import sensors_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    print(f"🌱 PicoGuard 啟動中... 環境: {settings.environment}")
    
    # 初始化資料庫
    from app.core.database import create_tables
    create_tables()
    print("✅ 資料庫初始化完成")
    
    yield
    # 關閉時執行
    print("🌱 PicoGuard 已關閉")


app = FastAPI(
    title="PicoGuard API",
    description="智能植栽監控系統 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 註冊 API 路由
app.include_router(sensors_router)

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    """API 根端點"""
    return {
        "message": "Welcome to PicoGuard API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "PicoGuard API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
