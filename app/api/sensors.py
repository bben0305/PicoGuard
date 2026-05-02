"""
感測器數據 API 路由
"""

from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db, create_tables
from app.models.sensor import SensorData as SensorDataModel, Device as DeviceModel

router = APIRouter(prefix="/api/v1/sensors", tags=["sensors"])


class SensorData(BaseModel):
    device_id: str
    soil_moisture: int
    soil_raw: Optional[int] = None
    temperature: Optional[float] = None
    timestamp: Optional[float] = None


class SensorDataResponse(BaseModel):
    id: int
    device_id: str
    soil_moisture: int
    soil_raw: Optional[int]
    temperature: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True


@router.post("/data", status_code=status.HTTP_201_CREATED)
async def receive_sensor_data(data: SensorData, api_key: str = Header(None), db: Session = Depends(get_db)):
    """接收 Pico 裝置的感測器數據並儲存到資料庫"""
    try:
        # 驗證 API Key
        if api_key != "picoguard-device-key-2024":
            print(f"❌ API Key 驗證失敗: {api_key}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的 API Key"
            )
        
        print(f"✅ API Key 驗證成功: {api_key}")
        # 確保資料表存在
        create_tables()
        # 記錄接收到的數據
        print(f"收到裝置 {data.device_id} 數據:")
        print(f"  土壤濕度: {data.soil_moisture}%")
        if data.temperature is not None:
            print(f"  溫度: {data.temperature}°C")
        if data.soil_raw is not None:
            print(f"  原始值: {data.soil_raw}")
        
        # 確保裝置存在，不存在則建立
        device = db.query(DeviceModel).filter(DeviceModel.device_id == data.device_id).first()
        if not device:
            device = DeviceModel(device_id=data.device_id)
            db.add(device)
            db.flush()
        
        # 更新裝置最後上線時間
        device.last_seen = datetime.utcnow()
        
        # 建立感測器數據記錄
        sensor_data = SensorDataModel(
            device_id=data.device_id,
            soil_moisture=data.soil_moisture,
            soil_raw=data.soil_raw,
            temperature=data.temperature,
            timestamp=datetime.utcnow()
        )
        
        db.add(sensor_data)
        db.commit()
        db.refresh(sensor_data)
        
        return {
            "status": "success",
            "message": "數據已儲存",
            "device_id": data.device_id,
            "data_id": sensor_data.id,
            "received_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"儲存數據時發生錯誤: {str(e)}"
        )


@router.get("/data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    device_id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """取得感測器數據"""
    try:
        # 確保資料表存在
        create_tables()
        query = db.query(SensorDataModel)
        
        # 根據裝置 ID 過濾
        if device_id:
            query = query.filter(SensorDataModel.device_id == device_id)
        
        # 限制數量並按時間倒序排列
        sensor_data = query.order_by(SensorDataModel.timestamp.desc()).limit(limit).all()
        
        return sensor_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢數據時發生錯誤: {str(e)}"
        )


@router.get("/devices")
async def get_devices(db: Session = Depends(get_db)):
    """取得所有裝置列表"""
    try:
        print("🔍 /devices API 被呼叫")
        
        # 確保資料表存在
        print("🔍 建立資料表...")
        create_tables()
        print("✅ 資料表建立完成")
        
        print("🔍 查詢裝置...")
        devices = db.query(DeviceModel).all()
        print(f"✅ 找到 {len(devices)} 個裝置")
        
        result = {
            "status": "success",
            "devices": [
                {
                    "device_id": device.device_id,
                    "name": device.name,
                    "created_at": device.created_at.isoformat() if device.created_at else None,
                    "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                }
                for device in devices
            ]
        }
        print("✅ /devices API 成功回應")
        return result
        
    except Exception as e:
        print(f"❌ /devices API 錯誤: {str(e)}")
        print(f"❌ 錯誤類型: {type(e)}")
        import traceback
        print(f"❌ 詳細錯誤: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查詢裝置時發生錯誤: {str(e)}"
        )
