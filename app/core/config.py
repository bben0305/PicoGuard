"""
PicoGuard 配置設定
使用 Pydantic Settings 管理環境變數
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """應用程式設定"""
    
    # 應用程式基本設定
    app_name: str = "PicoGuard"
    environment: str = "development"
    debug: bool = False
    port: int = 8000
    
    # 資料庫設定
    database_url: str = "sqlite:///./picoguard.db"

    # 安全性設定
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30

    # API 設定
    api_key: str = "picoguard-device-key"
    
    # CORS 設定
    allowed_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """取得設定實例（單例模式）"""
    return Settings()


settings = get_settings()
