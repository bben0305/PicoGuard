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
    try:
        # 匯入模型類別，這會註冊它們到 Base
        from app.models.sensor import Device, SensorData
        print("🔍 匯入模型完成")
        
        # 檢查模型是否正確註冊
        print(f"🔍 Base 中的表: {list(Base.metadata.tables.keys())}")
        
        # 建立所有資料表
        Base.metadata.create_all(bind=engine)
        print("✅ 資料表建立完成")
        
        # 驗證表是否存在
        from sqlalchemy import inspect
        inspector_obj = inspect(engine)
        tables = inspector_obj.get_table_names()
        print(f"✅ 現有資料表: {tables}")
        
    except Exception as e:
        print(f"❌ 建立資料表時發生錯誤: {str(e)}")
        import traceback
        print(f"❌ 詳細錯誤: {traceback.format_exc()}")
        raise


def drop_tables():
    """刪除所有資料表（開發用）"""
    from app.models.sensor import Device, SensorData
    Base.metadata.drop_all(bind=engine)
