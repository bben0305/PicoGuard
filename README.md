# 🌱 PicoGuard

> 基於 Raspberry Pi Pico 與 FastAPI 的智能植栽監控系統

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com/)
[![Raspberry Pi Pico](https://img.shields.io/badge/Raspberry%20Pi%20Pico-W--MicroPython-c51a4a.svg)](https://www.raspberrypi.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 專案簡介

**PicoGuard** 是一套完整的智能植栽監控解決方案，專為喜愛園藝的現代生活設計。透過 Raspberry Pi Pico 收集環境數據，並以 FastAPI 構建的高效能後端提供即時監控與智慧提醒，讓您隨時掌握植物健康狀態。

### 核心功能

- **🌡️ 環境監測** - 即時追蹤溫度、濕度、土壤濕度與光照強度
- **💧 智慧澆水提醒** - 依據土壤濕度與天氣預報自動建議最佳澆水時機
- **📊 數據視覺化** - 透過 Web 儀表板直覺呈現歷史趨勢與當前狀態
- **🔔 即時通知** - 當環境異常時主動推送警報至行動裝置
- **📱 跨平台存取** - 響應式設計支援桌面與行動裝置無縫操作

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                        使用者端 (Client)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  網頁儀表板  │  │  手機 App   │  │    第三方通知服務     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      後端服務 (Backend)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    FastAPI 伺服器                      │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────┐ │  │
│  │  │ REST API  │  │ WebSocket │  │  資料處理  │ │ 通知模組 │ │  │
│  │  └───────────┘  └───────────┘  └───────────┘  └────────┘ │  │
│  └────────────────────┬────────────────────────────────────┘  │
└───────────────────────┼────────────────────────────────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
┌───────────────────┐    ┌───────────────────┐
│    資料庫層        │    │   硬體設備層       │
│  ┌─────────────┐  │    │  ┌─────────────────────┐  │
│  │  SQLite/    │  │    │  │   Raspberry Pi      │  │
│  │  PostgreSQL │  │    │  │      Pico           │  │
│  └─────────────┘  │    │  │  ┌───────────────┐  │  │
└───────────────────┘    │  │  │  ESP-01 WiFi  │  │  │
                       │  │  └───────┬───────┘  │  │
                       │  └──────────┼──────────┘  │
                       │             │             │
                       │    ┌────────┴────────┐    │
                       │    │                 │    │
                       │    ▼                 ▼    │
                       │ ┌───────┐           ┌───────┐│
                       │ │ DHT22 │           │ 土壤  ││
                       │ │溫濕度  │           │ 濕度  ││
                       │ │感測器 │           │ 感測器││
                       │ └───────┘           └───────┘│
                       │ ┌───────┐                  │
                       │ │ 水泵  │ (可選)           │
                       │ │控制   │                  │
                       │ └───────┘                  │
                       └────────────────────────────┘
```

---

## 📁 專案結構

```
PicoGuard/
├── 📁 backend/                 # FastAPI 後端服務
│   ├── 📁 app/
│   │   ├── 📁 api/            # API 路由
│   │   ├── 📁 core/           # 核心設定
│   │   ├── 📁 models/         # 資料模型
│   │   ├── 📁 services/       # 業務邏輯
│   │   └── 📁 static/         # 靜態資源
│   ├── 📁 tests/              # 單元測試
│   ├── 📄 requirements.txt    # Python 依賴
│   └── 📄 main.py             # 入口點
│
├── 📁 firmware/                # Pico 韌體
│   ├── 📁 pico/               # MicroPython 程式
│   │   ├── 📄 main.py         # 裝置主程式
│   │   ├── 📄 config.py       # 裝置設定
│   │   └── 📁 lib/            # 第三方函式庫
│   └── 📁 circuit/            # 電路圖與設計檔
│
├── 📁 docs/                    # 文件資源
│   ├── 📁 api/                # API 文件
│   ├── 📁 hardware/           # 硬體組裝指南
│   └── 📁 images/             # 示意圖與照片
│
├── 📁 scripts/                 # 輔助腳本
│   ├── 📄 setup.bat           # Windows 安裝腳本
│   └── 📄 setup.sh            # Linux/macOS 安裝腳本
│
├── 📄 README.md               # 本文件
├── 📄 LICENSE                 # 授權條款
└── 📄 .gitignore              # Git 忽略規則
```

---

## 🚀 快速開始

### 硬體需求

| 項目 | 規格 | 數量 | 備註 |
|------|------|------|------|
| Raspberry Pi Pico | RP2040 | 1 | 普通版（非 W） |
| ESP-01 WiFi 模組 | ESP8266 | 1 | 透過 UART 連接 Pico |
| DHT22 溫濕度感測器 | 數位輸出 | 1 | - |
| 土壤濕度感測器 | 類比輸出 | 1 | - |
| 小型水泵 | DC 3-6V | 選配 | 初階版本可不接 |
| 麵包板與杜邦線 | - | 若干 | - |

### 後端安裝

```bash
# 1. 複製專案
git clone https://github.com/yourusername/picoguard.git
cd picoguard/backend

# 2. 建立虛擬環境
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動伺服器
uvicorn main:app --reload
```

### Pico 韌體部署

```bash
# 1. 安裝 MicroPython 韌體至 Pico W
# 詳見: https://micropython.org/download/rp2-pico-w/

# 2. 複製程式碼至 Pico
ampy --port COM3 put firmware/pico/main.py /
ampy --port COM3 put firmware/pico/config.py /
ampy --port COM3 put firmware/pico/lib/ /lib

# 3. 重置 Pico 開始運作
```

---

## 🔌 API 端點

| 方法 | 端點 | 說明 |
|------|------|------|
| `GET` | `/api/v1/sensors` | 取得所有感測器最新數據 |
| `GET` | `/api/v1/sensors/{id}/history` | 取得特定感測器歷史紀錄 |
| `POST` | `/api/v1/sensors/data` | 接收 Pico 上傳的感測數據 |
| `POST` | `/api/v1/pump/water` | 觸發澆水動作 |
| `GET` | `/api/v1/plants` | 取得管理的植物清單 |
| `POST` | `/api/v1/plants` | 新增監控植物 |
| `WS` | `/ws` | WebSocket 即時數據串流 |

完整 API 文件請見：`http://localhost:8000/docs`

---

## 📊 儀表板預覽

後端啟動後，開啟瀏覽器訪問：

- **API 文件**：`http://localhost:8000/docs`
- **監控儀表板**：`http://localhost:8000/dashboard`

---

## 🛠️ 技術棧

### 後端
- **[FastAPI](https://fastapi.tiangolo.com/)** - 高效能非同步 Web 框架
- **[Pydantic](https://docs.pydantic.dev/)** - 資料驗證與設定管理
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM 資料庫操作
- **[WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)** - 即時雙向通訊

### 硬體
- **[MicroPython](https://micropython.org/)** - 微控制器 Python 實作
- **[urequests](https://docs.micropython.org/)** - HTTP 請求函式庫
- **[umqtt.simple](https://docs.micropython.org/)** - MQTT 通訊協定

### 前端
- **[TailwindCSS](https://tailwindcss.com/)** - 原子化 CSS 框架
- **[Chart.js](https://www.chartjs.org/)** - 互動式圖表繪製
- **[Lucide Icons](https://lucide.dev/)** - 簡潔的 SVG 圖示庫

---

## 📝 開發計畫

- [x] 專案架構設計
- [ ] 後端 API 實作
- [ ] Pico 韌體開發
- [ ] 前端儀表板設計
- [ ] 電路組裝指南
- [ ] 行動 App 開發
- [ ] 多語言支援

---

## 🤝 貢獻指南

歡迎提交 Issue 與 Pull Request！請遵循以下規範：

1. 使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範
2. 確保程式碼通過 `ruff` 與 `mypy` 檢查
3. 新增功能請附上對應的測試案例

---

## 📄 授權條款

本專案採用 [MIT License](LICENSE) 授權。

---

## 🙏 致謝

- [Raspberry Pi Foundation](https://www.raspberrypi.org/) - 優秀的微控制器平台
- [FastAPI Team](https://fastapi.tiangolo.com/) - 現代化的 Python Web 框架
- [MicroPython](https://micropython.org/) - 讓嵌入式開發更輕鬆

---

<p align="center">
  <strong>🌿 讓科技守護每一株綠意 🌿</strong>
</p>
