"""
資料庫連接和會話管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# 建立資料庫引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# 建立會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立基礎模型類別
Base = declarative_base()


def get_db() -> Session:
    """取得資料庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """建立所有資料表"""
    from app.models import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """刪除所有資料表（開發用）"""
    from app.models import Base
    Base.metadata.drop_all(bind=engine)
