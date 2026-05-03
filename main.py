"""
PicoGuard Backend Server
智能植栽監控系統 - FastAPI 後端入口
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import sensors_router
from app.api.controls import router as controls_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    print(f"🌱 PicoGuard 啟動中... 環境: {settings.environment}")
    
    # 暫時跳過資料庫初始化，讓健康檢查先通過
    try:
        from app.core.database import create_tables
        create_tables()
        print("✅ 資料庫初始化完成")
    except Exception as e:
        print(f"⚠️ 資料庫初始化失敗: {e}")
        print("🔄 繼續啟動（資料庫將在首次使用時初始化）")
    
    yield
    # 關閉時執行
    print("🌱 PicoGuard 已關閉")


app = FastAPI(
    title="PicoGuard API",
    description="智能植栽監控系統 API",
    version="1.0.0",
    docs_url=None,  # 隐藏 API 文档
    redoc_url=None,  # 隐藏 ReDoc 文档
    lifespan=lifespan,
)

# CORS 設定 - 允許所有來源，避免代理請求被攔截
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 請求日誌中介軟體（如需調試可啟用）
# @app.middleware("http")
# async def log_requests(request, call_next):
#     if request.method == "POST" and "/api/v1/sensors" in str(request.url):
#         body = await request.body()
#         print(f"[調試] POST {request.url}, Body: {body[:100]}...")
#     response = await call_next(request)
#     return response

# 註冊 API 路由
app.include_router(sensors_router)
app.include_router(controls_router, prefix="/api/v1")

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def root():
    """API 根端點"""
    return {
        "message": "Welcome to PicoGuard API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "PicoGuard API"}


@app.post("/test")
async def test_endpoint():
    """極簡測試端點 - 用於驗證 POST 請求是否到達"""
    print("!!! RECEIVED TEST !!!")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
