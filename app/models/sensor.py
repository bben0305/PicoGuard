"""
感測器數據資料庫模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from app.core.database import Base


class Device(Base):
    """裝置資訊表"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Device(device_id='{self.device_id}')>"


class SensorData(Base):
    """感測器數據表"""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False, index=True)
    soil_moisture = Column(Integer, nullable=False)  # 百分比 0-100
    soil_raw = Column(Integer, nullable=True)  # 原始 ADC 值
    temperature = Column(Float, nullable=True)  # 攝氏溫度
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 建立複合索引以優化查詢
    __table_args__ = (
        Index('idx_device_timestamp', 'device_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<SensorData(device_id='{self.device_id}', soil_moisture={self.soil_moisture}%, temperature={self.temperature})>"

    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "soil_moisture": self.soil_moisture,
            "soil_raw": self.soil_raw,
            "temperature": self.temperature,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
