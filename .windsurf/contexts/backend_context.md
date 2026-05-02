# Backend 子專案上下文

## 🎯 本模組目標
提供 REST API 接收 Pico 上傳的感測數據，並提供 WebSocket 即時監控與儀表板。

## 📁 檔案結構
```
backend/
├── main.py              # FastAPI 應用入口
├── requirements.txt     # 依賴清單
└── app/
    ├── __init__.py
    ├── core/
    │   └── config.py    # Pydantic Settings 設定
    ├── api/
    │   └── __init__.py  # (待建立) API 路由
    ├── models/
    │   └── __init__.py  # (待建立) SQLAlchemy 模型
    ├── services/
    │   └── __init__.py  # (待建立) 業務邏輯
    └── static/          # (待建立) 靜態檔案
```

## 🔧 技術棧
- **框架**: FastAPI 0.136+
- **設定**: Pydantic Settings 2.14+
- **資料庫**: SQLAlchemy 2.0+ (SQLite)
- **遷移**: Alembic (預留)
- **伺服器**: Uvicorn
- **環境**: Python 3.10+

## ⚠️ 已遇到的問題

### Issue #1: Pydantic Settings 匯入錯誤
- **錯誤**: `ModuleNotFoundError: No module named 'pydantic_settings'`
- **解法**: 安裝 `pip install pydantic-settings`
- **狀態**: ✅ 已解決

### Issue #2: Uvicorn 未安裝
- **錯誤**: `The term 'uvicorn' is not recognized`
- **解法**: 安裝 `pip install uvicorn`
- **狀態**: ✅ 已解決

### Issue #3: FastAPI 未安裝
- **錯誤**: `ModuleNotFoundError: No module named 'fastapi'`
- **解法**: 安裝 `pip install fastapi`
- **狀態**: ✅ 已解決

## 📋 待完成任務
- [ ] 建立 `app/api/sensors.py` - POST /api/v1/sensors/data
- [ ] 建立 `app/models/sensor.py` - SQLAlchemy 感測器模型
- [ ] 建立 `app/services/sensor_service.py` - 資料處理邏輯
- [ ] 建立 `app/static/dashboard.html` - 簡易儀表板

## 🔌 API 規格 (規劃中)

### POST /api/v1/sensors/data
接收 Pico 上傳的感測數據

**Request Headers:**
```
Content-Type: application/json
X-API-Key: pico-device-key
```

**Request Body:**
```json
{
  "device_id": "pico-001",
  "soil_moisture": 45,
  "soil_raw": 42000,
  "temperature": 25.3,
  "humidity": 60.5,
  "timestamp": 1714392000
}
```

**Response:**
```json
{"status": "success", "message": "Data received"}
```

## 📝 配置說明
使用 `.env` 檔案或環境變數：
```
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./picoguard.db
SECRET_KEY=your-secret-key
DEVICE_API_KEY=pico-device-key
```
