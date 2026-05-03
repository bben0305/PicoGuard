"""
PicoGuard 控制器 API
提供澆水等控制功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/controls", tags=["controls"])

class WaterRequest(BaseModel):
    duration: Optional[int] = 3000  # 澆水時間（毫秒）
    device_id: Optional[str] = None

class WaterResponse(BaseModel):
    command: str
    status: str
    duration: int
    message: str

@router.post("/water", response_model=WaterResponse)
async def trigger_watering(request: WaterRequest):
    """觸發澆水功能"""
    try:
        # 這裡只是返回指令，實際的澆水由 Pico 在下次數據上傳時執行
        # Pico 會解析這個 JSON 響應並執行澆水
        
        response = WaterResponse(
            command="water",
            status="on",
            duration=request.duration,
            message=f"澆水指令已發送，持續時間: {request.duration}ms"
        )
        
        print(f"[控制] 收到澆水請求: {request.duration}ms")
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"澆水指令發送失敗: {str(e)}")

@router.post("/water/stop", response_model=WaterResponse)
async def stop_watering():
    """停止澆水"""
    try:
        response = WaterResponse(
            command="water",
            status="off",
            duration=0,
            message="停止澆水指令已發送"
        )
        
        print("[控制] 收到停止澆水請求")
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止澆水指令發送失敗: {str(e)}")
