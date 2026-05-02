# PicoGuard 專案概述

## 🎯 專案目標
智能植栽監控系統 - 基於 Raspberry Pi Pico + ESP01 WiFi 模組，透過 FastAPI 後端提供即時監控與澆水提醒。

## 🏗️ 系統架構
```
┌─────────────┐      WiFi      ┌─────────────┐
│  Pico +     │ ←──────────→ │  FastAPI    │
│  ESP01      │   HTTP POST  │  Backend    │
│ (感測器)    │              │ (SQLite)    │
└─────────────┘              └─────────────┘
```

## 📁 專案結構

### 第一層：主要模組
| 目錄 | 用途 | 技術 |
|------|------|------|
| `/backend` | FastAPI 後端服務 | Python 3.11+, FastAPI, SQLite |
| `/firmware/pico` | Pico MicroPython 韌體 | MicroPython, ESP01 AT 指令 |
| `/docs` | 文件與圖片 | Markdown |
| `/scripts` | 安裝與輔助腳本 | Batch/PowerShell |

### 第二層：詳細內容

#### `/backend/` - 後端服務
```
backend/
├── main.py              # FastAPI 入口
├── requirements.txt     # Python 依賴
└── app/
    ├── core/config.py   # 設定管理 (Pydantic)
    ├── api/             # API 路由 (待建立)
    ├── models/          # SQLAlchemy 模型 (待建立)
    ├── services/        # 業務邏輯 (待建立)
    └── static/          # Web 儀表板 (待建立)
```
**關鍵技術**：FastAPI, Pydantic Settings, SQLAlchemy, Uvicorn

#### `/firmware/pico/` - 硬體韌體
```
firmware/pico/
├── main.py              # 主程式 (MicroPython)
├── config.py            # 裝置設定
└── main_legacy.py       # 備份：原始 ThingSpeak 版本
```
**關鍵技術**：MicroPython, machine 模組, ESP01 AT 指令, UART 通訊

**硬體配置**：
- Pico GPIO 0/1 → ESP01 UART
- Pico GPIO 22 → 土壤感測器電源 (防鏽設計)
- Pico GPIO 26 (ADC0) → 土壤濕度訊號
- Pico GPIO 16 → DHT22 (可選)

## 🔧 開發環境

### 後端啟動
```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Pico 部署
1. 安裝 MicroPython 韌體到 Pico
2. 使用 Thonny 上傳 `config.py` + `main.py`
3. 重置 Pico 自動執行

## ✅ 系統狀態

### 已完成
- ✅ Pico 透過 ESP01 成功上傳感測數據至 Railway 後端
- ✅ 儀表板顯示即時溫度/濕度趨勢圖
- ✅ 裝置在線狀態檢測
- ✅ API Key 驗證機制
- ✅ CORS 跨域支援

### 已知限制
- MicroPython 不支援 Python 3.10+ 語法
- 僅支援 HTTP (ESP01 限制)
- 使用 SQLite (開發階段)

## 📝 版本歷史
- v0.1: 專案初始化
- v0.2: 後端 API + 儀表板完成
- v0.3: ✅ Pico-Railway 數據上傳打通，系統上線
