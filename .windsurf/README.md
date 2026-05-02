# Windsurf PicoGuard 設定說明

## 📁 目錄結構

```
.windsurf/
├── config.json              # 主設定檔
├── README.md                # 本文件
├── contexts/                # 專案上下文 (給 AI 閱讀)
│   ├── project_overview.md  # 專案總覽
│   ├── backend_context.md   # 後端子專案
│   └── firmware_context.md  # 韌體子專案
├── memories/                # 記憶儲存
│   ├── tech_stack.json      # 技術棧記錄
│   └── issue_log.md         # 問題追蹤
└── workflows/               # 工作流程腳本 (待建立)
```

## 🎯 使用方式

### 對於 AI (Cascade)
每次使用者提出請求時，應優先讀取相關上下文：

1. **總是讀取**: `contexts/project_overview.md`
2. **根據檔案類型**:
   - `backend/*.py` → 讀取 `backend_context.md`
   - `firmware/pico/*.py` → 讀取 `firmware_context.md`
3. **遇到錯誤時**: 檢查 `memories/issue_log.md` 是否為已知問題

### Token 節省策略
- 不要重複輸出專案結構說明
- 使用檔案路徑引用而非貼上完整程式碼
- 優先使用 `edit` 工具而非重寫整個檔案

## 📝 維護指南

### 新增問題記錄
1. 開啟 `memories/issue_log.md`
2. 使用 ISSUE-XXX 編號
3. 記錄：時間、症狀、解法、狀態
4. 已解決問題移動到「已解決」區段

### 更新技術棧
1. 編輯 `memories/tech_stack.json`
2. 更新 `last_updated` 日期
3. 新增/移除 key_libraries

### 新增子專案
1. 在 `contexts/` 建立 `{name}_context.md`
2. 加入 `config.json` 的 `context_files` 列表
3. 更新 `config.json` 的 `file_patterns`

## 🔍 快速參考

| 情境 | 參考檔案 |
|------|----------|
| 了解專案全貌 | `project_overview.md` |
| 後端 API 開發 | `backend_context.md` |
| Pico 韌體除錯 | `firmware_context.md` |
| 檢查已知問題 | `issue_log.md` |
| 查看技術規格 | `tech_stack.json` |

## ⚠️ 已知約束 (快速提醒)

- MicroPython **不支援** `int | None` 語法
- ESP01 AT 指令需 `\r\n` 結尾
- 土壤感測器使用 **GPIO22 防鏽設計**
- 虛擬環境啟動後才有 `uvicorn` 指令
