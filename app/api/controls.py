"""
PicoGuard 控制器 API
提供澆水等控制功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import time

# 簡單的記憶體存儲（生產環境建議使用資料庫）
pending_commands = []

router = APIRouter(tags=["controls"])

class WaterRequest(BaseModel):
    duration: Optional[int] = 3000  # 澆水時間（毫秒）
    device_id: Optional[str] = None

class WaterResponse(BaseModel):
    command: str
    status: str
    duration: int
    message: str

class Command(BaseModel):
    command: str
    status: str
    duration: Optional[int] = None
    timestamp: datetime

@router.post("/controls/water", response_model=WaterResponse)
async def start_watering(duration: int = 3000):
    """啟動澆水"""
    try:
        command = Command(
            command="water",
            status="on",
            duration=duration,
            timestamp=datetime.now()
        )
        
        # 添加到待處理指令
        pending_commands.append(command)
        
        response = WaterResponse(
            command="water",
            status="on",
            duration=duration,
            message=f"澆水指令已發送，持續時間: {duration}ms"
        )
        
        print(f"[控制] 收到澆水請求: {duration}ms")
        
        # 詳細記錄澆水請求
        print(f"[控制] 💧 收到澆水請求: {duration}ms")
        print(f"[控制] 📋 待處理指令數量: {len(pending_commands)}")
        print(f"[控制] 📄 新增指令: {command}")
        print(f"[控制] 📤 回應: {response}")
        
        return response
        
    except Exception as e:
        print(f"[控制] ❌ 澆水指令發送失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"澆水指令發送失敗: {str(e)}")

@router.post("/controls/water/stop", response_model=WaterResponse)
async def stop_watering():
    """停止澆水"""
    try:
        command = Command(
            command="water",
            status="off",
            duration=0,
            timestamp=datetime.now()
        )
        
        # 添加到待處理指令
        pending_commands.append(command)
        
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

@router.get("/commands/pending/{device_id}", response_model=List[Command])
async def get_pending_commands(device_id: str):
    """獲取待處理的指令"""
    try:
        # 記錄 Pico 請求
        print(f"[控制] 📱 Pico 設備請求: {device_id}")
        print(f"[控制] 📋 當前待處理指令數量: {len(pending_commands)}")
        
        # 返回並清除待處理指令
        commands_to_return = pending_commands.copy()
        pending_commands.clear()
        
        # 詳細記錄回應內容
        print(f"[控制] 📤 返回 {len(commands_to_return)} 個待處理指令給設備: {device_id}")
        if commands_to_return:
            for i, cmd in enumerate(commands_to_return):
                print(f"[控制]   指令 {i+1}: {cmd}")
        else:
            print(f"[控制]   無待處理指令")
        
        # 記錄回應 JSON 格式
        import json
        response_json = [cmd.dict() for cmd in commands_to_return]
        print(f"[控制] 📄 回應 JSON: {json.dumps(response_json, ensure_ascii=False, default=str)}")
        
        return commands_to_return
        
    except Exception as e:
        print(f"[控制] ❌ 獲取待處理指令失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取待處理指令失敗: {str(e)}")
